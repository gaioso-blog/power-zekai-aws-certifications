#!/usr/bin/env python3
"""Deterministic session state for interactive quiz / exam simulation mode.

Replaces the fragile in-context `[STATE: ...]` marker. Everything that must
survive context compaction (or an entirely new session) lives on disk here,
including the consecutive-streak counters that adaptive difficulty depends on
and the asked-topic history that anti-repetition depends on.

State directory resolution order:
    1. --state-dir <path>
    2. $ZEKAI_STATE_DIR
    3. ~/.zekai

Files written:
    <state-dir>/session.json       current session
    <state-dir>/calibration.jsonl  append-only difficulty calibration log
    <state-dir>/history.json       asked topics across sessions, per exam

Every command prints JSON on stdout. Exit code 0 on success, 1 on usage or
state errors.

Commands
--------
start        --exam CODE --difficulty LEVEL [--total N] [--domains JSON] [--fresh]
status
pending-set  --payload JSON
pending-get
timer-start  (marks question display time; call right before showing the question)
grade        --response LETTERS [--elapsed-seconds N] [--difficulty LEVEL]
pending-clear
calibrate    --perceived LEVEL [--question N] [--notes TEXT]
asked        [--exam CODE] [--scope session|history]
suggest
progress
debug        on|off
end          [--output-dir PATH]  (saves session JSON; use export_report.py for markdown)
reset

Architecture Challenge Mode (free-form design + weighted rubric, not multiple-choice)
---------------------------------------------------------------------------------------
design-start  --payload JSON --difficulty LEVEL
              (payload: domain, topic, scenario, requirements[{id,label,weight}],
               curveball{label, added_requirement{id,label,weight}}, grounding[])
design-pending
              (curveball stays hidden until the initial phase has been graded)
design-grade  --phase initial|adapted --scores JSON [--elapsed-seconds N]
              (scores: [{id, status: satisfied|partial|missed}], one entry per
               requirement id currently in scope for that phase)
design-clear

Timer flow
----------
1. After pending-set succeeds, call `timer-start` immediately before displaying the
   question to the learner.
2. When the learner submits an answer, pass the elapsed wall-clock seconds to grade:
   `--elapsed-seconds N`  (integer or float; omit if you don't track time)
3. Each answer record stores `elapsed_seconds`. The end report aggregates
   `total_seconds`, `avg_seconds_per_question`, and per-domain timing.

Multiple-response (select-three)
---------------------------------
Professional and Specialty exams include questions requiring exactly 3 correct answers
out of 6 options (A–F). Set `correct_answers` to a list of 3 letters in pending-set.
The `grade` command enforces the count before revealing the key.
"""

import argparse
import sys

from zekai_common import DIFFICULTIES, fail, state_dir
from zekai_design import (
    cmd_design_clear,
    cmd_design_grade,
    cmd_design_pending,
    cmd_design_start,
)
from zekai_quiz import (
    cmd_calibrate,
    cmd_grade,
    cmd_pending_clear,
    cmd_pending_get,
    cmd_pending_set,
    cmd_start,
    cmd_timer_start,
)
from zekai_summary import (
    cmd_asked,
    cmd_debug,
    cmd_end,
    cmd_progress,
    cmd_reset,
    cmd_status,
    cmd_suggest,
)


# --------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(prog="session.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--state-dir", dest="state_dir", default=None,
                   help="override state directory (default $ZEKAI_STATE_DIR or ~/.zekai)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("start", help="start or resume a session")
    s.add_argument("--exam", required=True)
    s.add_argument("--difficulty", default="medium", choices=DIFFICULTIES)
    s.add_argument("--total", type=int, default=None,
                   help="planned number of questions (enables completion signal)")
    s.add_argument("--domains", default=None,
                   help='JSON array from the official guide, e.g. '
                        '\'[{"name":"Design Secure Architectures","weight":30}]\'')
    s.add_argument("--fresh", action="store_true", help="discard any active session")
    s.set_defaults(func=cmd_start)

    ps = sub.add_parser("pending-set", help="persist a grounded question before displaying it")
    ps.add_argument("--payload", required=True, help="question JSON including grounding records")
    ps.set_defaults(func=cmd_pending_set)

    pg = sub.add_parser("pending-get", help="retrieve the recoverable pending question")
    pg.set_defaults(func=cmd_pending_get)

    g = sub.add_parser("grade", help="grade pending question; reveal key only after submission")
    g.add_argument("--response", required=True, help="submitted option letter(s), e.g. B or A,C or A,C,E")
    g.add_argument("--elapsed-seconds", dest="elapsed_seconds", type=float, default=None,
                   help="wall-clock seconds the learner spent on this question (optional override)")
    g.add_argument("--difficulty", default=None, choices=DIFFICULTIES,
                   help="accepted new difficulty to apply from this answer onward")
    g.set_defaults(func=cmd_grade)

    pc = sub.add_parser("pending-clear", help="skip and clear the pending question")
    pc.set_defaults(func=cmd_pending_clear)

    c = sub.add_parser("calibrate", help="attach perceived difficulty without changing score")
    c.add_argument("--perceived", required=True, choices=DIFFICULTIES)
    c.add_argument("--question", type=int, default=None, help="question number; defaults to latest uncalibrated")
    c.add_argument("--notes", default=None)
    c.set_defaults(func=cmd_calibrate)

    d = sub.add_parser("debug", help="toggle the quality-check debug block")
    d.add_argument("mode", choices=["on", "off"])
    d.set_defaults(func=cmd_debug)

    k = sub.add_parser("asked", help="list already-used topics")
    k.add_argument("--exam", default=None)
    k.add_argument("--scope", default="session", choices=["session", "history"])
    k.set_defaults(func=cmd_asked)

    for name, fn, helptext in [
        ("status", cmd_status, "print current session summary"),
        ("timer-start", cmd_timer_start, "mark the moment a question is displayed to start timing"),
        ("progress", cmd_progress, "print learner-facing progress block"),
        ("suggest", cmd_suggest, "suggest next domain by weighted coverage deficit"),
        ("end", cmd_end, "close the session and emit the final report"),
        ("reset", cmd_reset, "discard the current session"),
    ]:
        sp = sub.add_parser(name, help=helptext)
        sp.set_defaults(func=fn)

    # ── Architecture Challenge Mode ──────────────────────────────────────────
    ds = sub.add_parser(
        "design-start",
        help="persist a grounded architecture challenge before showing it to the learner",
    )
    ds.add_argument(
        "--payload", required=True,
        help="JSON with domain, topic, scenario, requirements, curveball, and grounding",
    )
    ds.add_argument(
        "--difficulty", default="medium", choices=DIFFICULTIES,
        help="difficulty label for this challenge (default: medium)",
    )
    ds.set_defaults(func=cmd_design_start)

    dp = sub.add_parser(
        "design-pending",
        help="return active challenge state (curveball hidden until adapted phase)",
    )
    dp.set_defaults(func=cmd_design_pending)

    dg = sub.add_parser(
        "design-grade",
        help="record rubric scores for a phase and advance to the next",
    )
    dg.add_argument(
        "--phase", required=True, choices=("initial", "adapted"),
        help="which design phase is being graded",
    )
    dg.add_argument(
        "--scores", required=True,
        help='JSON array: [{id, status}] where status in (satisfied|partial|missed)',
    )
    dg.add_argument(
        "--elapsed-seconds", dest="elapsed_seconds", type=float, default=None,
        help="wall-clock seconds spent on this phase (optional override; auto-computed from timer)",
    )
    dg.set_defaults(func=cmd_design_grade)

    dcl = sub.add_parser("design-clear", help="discard the active architecture challenge without grading")
    dcl.set_defaults(func=cmd_design_clear)

    return p


def main(argv):
    args = build_parser().parse_args(argv[1:])
    base = state_dir(args.state_dir)
    try:
        return args.func(args, base)
    except RuntimeError as exc:
        return fail(str(exc))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
