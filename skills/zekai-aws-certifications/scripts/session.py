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
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

SCHEMA_VERSION = 3

# Adaptive-difficulty thresholds. Single place to tune them.
STREAK_TO_OFFER_HARDER = 3
DOMAIN_ERRORS_TO_OFFER_CONCEPT = 2
PROGRESS_EVERY = 5

DIFFICULTIES = ["easy", "medium", "hard", "exam-level"]


# --------------------------------------------------------------------------
# paths / io
# --------------------------------------------------------------------------

def state_dir(cli_value=None):
    path = cli_value or os.environ.get("ZEKAI_STATE_DIR") or os.path.join(
        os.path.expanduser("~"), ".zekai"
    )
    os.makedirs(path, exist_ok=True)
    return path


def _path(base, name):
    return os.path.join(base, name)


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def out(payload, code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


def fail(detail, **extra):
    payload = {"ok": False, "error": detail}
    payload.update(extra)
    return out(payload, 1)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def topic_key(raw):
    """Normalize a topic label so paraphrases collapse to the same key.

    "RDS Multi-AZ vs Read Replica" -> "rds-multi-az-vs-read-replica"
    """
    slug = raw.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def is_official_aws_url(raw):
    """Return True only for HTTPS URLs on official AWS documentation hosts."""
    try:
        parsed = urlparse(str(raw))
    except ValueError:
        return False
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (
        host == "docs.aws.amazon.com"
        or host == "aws.amazon.com"
        or host.endswith(".aws.amazon.com")
        or host == "d1.awsstatic.com"
    )


def parse_bool(raw):
    val = str(raw).strip().lower()
    if val in ("true", "1", "yes", "y", "sim", "correct", "c"):
        return True
    if val in ("false", "0", "no", "n", "nao", "não", "incorrect", "e"):
        return False
    raise ValueError(f"cannot parse boolean from {raw!r}")


def empty_session():
    return {
        "schema": SCHEMA_VERSION,
        "active": False,
    }


def require_active(session):
    if not session.get("active"):
        raise RuntimeError(
            "no active session; run `session.py start --exam CODE --difficulty LEVEL` first"
        )


def load_active_session(base):
    """Load session.json and require an active session."""
    session = load_json(_path(base, "session.json"), empty_session())
    require_active(session)
    return session


def pct(correct, total):
    return round(100.0 * correct / total, 1) if total else 0.0


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------

def cmd_start(args, base):
    session_path = _path(base, "session.json")
    existing = load_json(session_path, empty_session())
    requested_exam = args.exam.strip().upper()

    if existing.get("active") and not args.fresh:
        if existing.get("exam") != requested_exam:
            return out({
                "ok": False,
                "error": "active_session_conflict",
                "detail": "A different exam session is active. Resume it or explicitly start fresh.",
                "active_exam": existing.get("exam"),
                "requested_exam": requested_exam,
                "has_pending_question": bool(existing.get("pending")),
                "next_actions": ["resume_active", "start_requested_with_fresh"],
            }, 1)
        return out({
            "ok": True,
            "resumed": True,
            "detail": "Matching active session found. Resuming it.",
            "session": summarize(existing),
        })

    domains = []
    if args.domains:
        try:
            parsed = json.loads(args.domains)
        except json.JSONDecodeError as exc:
            return fail(f"--domains is not valid JSON: {exc}")
        if not isinstance(parsed, list):
            return fail("--domains must be a JSON array of {name, weight} objects")
        for item in parsed:
            if not isinstance(item, dict) or "name" not in item:
                return fail("each --domains entry needs at least a 'name' field")
            domains.append({
                "name": item["name"],
                # weight is optional; when absent coverage falls back to even split
                "weight": float(item.get("weight", 0)) or None,
            })

    session = {
        "schema": SCHEMA_VERSION,
        "active": True,
        "started_at": now(),
        "updated_at": now(),
        "exam": requested_exam,
        "difficulty": args.difficulty,
        "debug": False,
        "total_planned": args.total,
        # domain plan sourced from the official exam guide by the agent, never
        # hardcoded here — keeps the anti-hallucination rule intact
        "domains": domains,
        "question_number": 0,
        "correct": 0,
        "incorrect": 0,
        "streak_correct": 0,
        "streak_incorrect": 0,
        "domain_stats": {},
        "asked_topics": [],
        "answers": [],
        # Full recoverable question state. Written before a question is shown,
        # cleared only after it is graded or explicitly skipped.
        "pending": None,
    }
    save_json(session_path, session)
    return out({"ok": True, "resumed": False, "session": summarize(session)})


def public_pending(pending):
    """Return learner-safe pending state with answer key and option grounding hidden."""
    if not pending:
        return None
    safe = {k: v for k, v in pending.items()
            if k not in {"correct_answers", "grounding"}}
    safe["grounded"] = bool(pending.get("grounding"))
    return safe


def _validate_pending_payload(payload):
    """Validate a pending question payload dict.

    Returns (normalised_answers, error_payload):
    - On success: (list[str], None)  — answers uppercased and deduplicated
    - On failure: (None, return-value-of-fail())
    """
    required = {"domain", "topic", "question", "options", "correct_answers", "grounding"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        return None, fail(
            "pending payload must be an object with domain, topic, question, options, correct_answers, and grounding",
            missing=sorted(required - set(payload if isinstance(payload, dict) else {})),
        )
    for field in ("domain", "topic", "question"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            return None, fail(f"pending {field} must be a non-empty string")
    if not isinstance(payload["options"], dict) or len(payload["options"]) < 2:
        return None, fail("pending options must be an object with at least two lettered options")
    option_keys = {str(x).strip().upper() for x in payload["options"]}
    if any(not re.fullmatch(r"[A-Z]", key) for key in option_keys):
        return None, fail("pending option keys must be single letters")
    if any(not isinstance(value, str) or not value.strip() for value in payload["options"].values()):
        return None, fail("every pending option value must be a non-empty string")
    answers = payload["correct_answers"]
    if isinstance(answers, str):
        answers = [answers]
    if not isinstance(answers, list) or not answers:
        return None, fail("pending correct_answers must be a non-empty list of option letters")
    answers = [str(x).strip().upper() for x in answers]
    if len(set(answers)) != len(answers):
        return None, fail("pending correct_answers must not contain duplicates")
    if not set(answers).issubset(option_keys):
        return None, fail("every correct answer must name a key present in options")
    if len(answers) > 3:
        return None, fail("correct_answers supports at most 3 letters (single-choice, select-two, or select-three)")
    grounding = payload["grounding"]
    if not isinstance(grounding, list) or not grounding:
        return None, fail("pending grounding must contain at least one official-source record")
    if any(not isinstance(g, dict) or g.get("status") != "verified"
           or not is_official_aws_url(g.get("source")) for g in grounding):
        return None, fail("every grounding record needs status=verified and an HTTPS URL on an official AWS host")
    return answers, None


def cmd_pending_set(args, base):
    """Persist a fully grounded question before it is shown to the learner."""
    session_path = _path(base, "session.json")
    session = load_active_session(base)

    if session.get("pending"):
        return fail(
            "a question is already pending; grade it or run pending-clear before replacing it",
            error_code="pending_question_exists",
            pending=public_pending(session["pending"]),
        )

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as exc:
        return fail(f"--payload is not valid JSON: {exc}")

    answers, err = _validate_pending_payload(payload)
    if err is not None:
        return err

    pending = dict(payload)
    pending["correct_answers"] = answers
    pending["topic_key"] = topic_key(payload["topic"])
    pending["number"] = session["question_number"] + 1
    pending["created_at"] = now()
    # timer_started_at is set by the timer-start command after the question is displayed
    pending.setdefault("timer_started_at", None)
    session["pending"] = pending
    session["updated_at"] = now()
    save_json(session_path, session)
    return out({"ok": True, "pending": public_pending(pending)})


def cmd_pending_get(args, base):
    session = load_active_session(base)
    return out({"ok": True, "has_pending_question": bool(session.get("pending")),
                "pending": public_pending(session.get("pending"))})


def cmd_pending_clear(args, base):
    session_path = _path(base, "session.json")
    session = load_active_session(base)
    cleared = session.get("pending")
    session["pending"] = None
    session["updated_at"] = now()
    save_json(session_path, session)
    return out({"ok": True, "cleared": bool(cleared)})


def cmd_timer_start(args, base):
    """Mark the moment the question was displayed so elapsed time can be computed."""
    session_path = _path(base, "session.json")
    session = load_active_session(base)
    pending = session.get("pending")
    if not pending:
        return fail("no pending question; call pending-set before timer-start",
                    error_code="no_pending_question")
    if pending.get("timer_started_at"):
        return out({"ok": True, "already_started": True,
                    "timer_started_at": pending["timer_started_at"]})
    pending["timer_started_at"] = now()
    session["updated_at"] = now()
    save_json(session_path, session)
    return out({"ok": True, "timer_started_at": pending["timer_started_at"]})


def cmd_grade(args, base):
    """Grade a response against pending state, revealing the key only after submission."""
    session = load_active_session(base)
    pending = session.get("pending")
    if not pending:
        return fail("no question is pending", error_code="no_pending_question")

    raw_letters = re.findall(r"[A-Za-z]", args.response.upper())
    selected = []
    for letter in raw_letters:
        if letter not in selected:
            selected.append(letter)
    valid_options = {str(k).upper() for k in pending["options"]}
    if not selected or any(x not in valid_options for x in selected):
        return fail("response must contain only valid option letters",
                    error_code="invalid_response", valid_options=sorted(valid_options))
    required = len(pending["correct_answers"])
    if len(selected) != required:
        return out({
            "ok": False,
            "error": "wrong_answer_count",
            "selected_count": len(selected),
            "required_count": required,
            "has_pending_question": True,
        }, 1)

    correct = set(selected) == set(pending["correct_answers"])

    # Resolve elapsed seconds: prefer explicit flag, fall back to timer_started_at
    elapsed = None
    if getattr(args, "elapsed_seconds", None) is not None:
        try:
            elapsed = float(args.elapsed_seconds)
            if elapsed < 0:
                elapsed = None
        except (TypeError, ValueError):
            pass
    if elapsed is None and pending.get("timer_started_at"):
        try:
            started = datetime.fromisoformat(pending["timer_started_at"])
            elapsed = round((datetime.now(timezone.utc) - started).total_seconds(), 1)
        except (ValueError, TypeError):
            pass

    answer_args = argparse.Namespace(
        domain=pending["domain"],
        topic=pending["topic"],
        correct=str(correct),
        difficulty=args.difficulty,
        elapsed_seconds=elapsed,
        reveal_answers=True,
        user_answers=selected,
        correct_answers=pending["correct_answers"],
    )
    return cmd_answer(answer_args, base)


def _adaptive_signals(session, stats, domain):
    """Build the list of deterministic adaptive-difficulty signals after an answer.

    These are the core signals that drive difficulty adaptation and pacing:
    - offer_increase_difficulty  when the learner is on a correct streak
    - offer_concept_explanation  when a domain has repeated errors
    - show_progress_summary      every PROGRESS_EVERY questions
    - session_complete           when the planned total is reached
    """
    signals = []
    idx = DIFFICULTIES.index(session["difficulty"]) if session["difficulty"] in DIFFICULTIES else 1
    if session["streak_correct"] >= STREAK_TO_OFFER_HARDER and idx < len(DIFFICULTIES) - 1:
        signals.append({
            "type": "offer_increase_difficulty",
            "from": session["difficulty"],
            "to": DIFFICULTIES[idx + 1],
            "reason": f"{session['streak_correct']} consecutive correct",
        })
    if stats["streak_incorrect"] >= DOMAIN_ERRORS_TO_OFFER_CONCEPT:
        signals.append({
            "type": "offer_concept_explanation",
            "domain": domain,
            "reason": f"{stats['streak_incorrect']} consecutive incorrect in this domain",
        })
    if session["question_number"] % PROGRESS_EVERY == 0:
        signals.append({"type": "show_progress_summary"})
    if session["total_planned"] and session["question_number"] >= session["total_planned"]:
        signals.append({"type": "session_complete", "reason": "planned total reached"})
    return signals


def cmd_answer(args, base):
    session_path = _path(base, "session.json")
    session = load_active_session(base)
    try:
        correct = parse_bool(args.correct)
    except ValueError as exc:
        return fail(str(exc))

    domain = args.domain.strip()
    key = topic_key(args.topic)
    pending = session.get("pending")
    if pending:
        if pending.get("domain") != domain or pending.get("topic_key") != key:
            return fail(
                "answer metadata does not match the pending question; retrieve it with pending-get",
                error_code="pending_question_mismatch",
                pending_domain=pending.get("domain"),
                pending_topic=pending.get("topic"),
            )

    session["question_number"] += 1
    if args.difficulty:
        session["difficulty"] = args.difficulty

    stats = session["domain_stats"].setdefault(
        domain, {"asked": 0, "correct": 0, "incorrect": 0, "streak_incorrect": 0}
    )
    stats["asked"] += 1

    if correct:
        session["correct"] += 1
        session["streak_correct"] += 1
        session["streak_incorrect"] = 0
        stats["correct"] += 1
        stats["streak_incorrect"] = 0
    else:
        session["incorrect"] += 1
        session["streak_incorrect"] += 1
        session["streak_correct"] = 0
        stats["incorrect"] += 1
        stats["streak_incorrect"] += 1

    if key not in session["asked_topics"]:
        session["asked_topics"].append(key)

    elapsed = getattr(args, "elapsed_seconds", None)
    session["answers"].append({
        "n": session["question_number"],
        "domain": domain,
        "topic": key,
        "correct": correct,
        "difficulty": session["difficulty"],
        "elapsed_seconds": elapsed,
        "calibration": None,
        "at": now(),
    })
    # accumulate per-domain timing
    if elapsed is not None:
        stats["total_seconds"] = round(stats.get("total_seconds", 0) + elapsed, 1)
    session["pending"] = None
    session["updated_at"] = now()
    save_json(session_path, session)

    # cross-session anti-repetition history
    history_path = _path(base, "history.json")
    history = load_json(history_path, {})
    bucket = history.setdefault(session["exam"], [])
    if key not in bucket:
        bucket.append(key)
    save_json(history_path, history)

    signals = _adaptive_signals(session, stats, domain)

    payload = {
        "ok": True,
        "recorded": {"domain": domain, "topic": key, "correct": correct},
        "signals": signals,
        "session": summarize(session),
    }
    if getattr(args, "reveal_answers", False):
        payload["grading"] = {
            "user_answers": args.user_answers,
            "correct_answers": args.correct_answers,
            "correct": correct,
        }
    return out(payload)


def cmd_calibrate(args, base):
    """Attach perceived difficulty to an existing answer without changing score."""
    session_path = _path(base, "session.json")
    session = load_active_session(base)

    answers = session.get("answers", [])
    target = None
    if args.question is not None:
        target = next((a for a in answers if a.get("n") == args.question), None)
    else:
        target = next((a for a in reversed(answers) if not a.get("calibration")), None)
    if not target:
        return fail("no matching uncalibrated answer found", error_code="answer_not_found")
    if target.get("calibration"):
        return fail("that answer is already calibrated", error_code="already_calibrated",
                    question=target["n"])

    record = {
        "at": now(),
        "exam": session["exam"],
        "question": target["n"],
        "domain": target["domain"],
        "topic": target["topic"],
        "generated_difficulty": target["difficulty"],
        "perceived_difficulty": args.perceived,
        "was_correct": target["correct"],
        "notes": args.notes or "",
    }
    target["calibration"] = {
        "perceived_difficulty": args.perceived,
        "notes": args.notes or "",
        "at": record["at"],
    }
    session["updated_at"] = now()
    save_json(session_path, session)
    with open(_path(base, "calibration.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    return out({
        "ok": True,
        "recorded": record,
        "score_unchanged": {
            "question_number": session["question_number"],
            "correct": session["correct"],
            "incorrect": session["incorrect"],
        },
    })


def summarize(session):
    if not session.get("active"):
        return {"active": False}
    weak = sorted(
        (d for d, s in session["domain_stats"].items() if s["incorrect"] > 0),
        key=lambda d: -session["domain_stats"][d]["incorrect"],
    )
    return {
        "active": True,
        "exam": session["exam"],
        "difficulty": session["difficulty"],
        "debug": session.get("debug", False),
        "question_number": session["question_number"],
        "total_planned": session.get("total_planned"),
        "correct": session["correct"],
        "incorrect": session["incorrect"],
        "score_pct": pct(session["correct"], session["correct"] + session["incorrect"]),
        "streak_correct": session["streak_correct"],
        "streak_incorrect": session["streak_incorrect"],
        "domains_with_errors": weak,
        "asked_topic_count": len(session["asked_topics"]),
        "has_pending_question": bool(session.get("pending")),
        "pending": public_pending(session.get("pending")),
    }


def cmd_status(args, base):
    session = load_json(_path(base, "session.json"), empty_session())
    return out({"ok": True, "session": summarize(session)})


def cmd_progress(args, base):
    session = load_active_session(base)
    s = summarize(session)
    current = session["answers"][-1]["domain"] if session["answers"] else None
    s["current_domain"] = current
    return out({"ok": True, "progress": s})


def cmd_asked(args, base):
    if args.scope == "history":
        history = load_json(_path(base, "history.json"), {})
        if args.exam:
            code = args.exam.strip().upper()
            return out({"ok": True, "scope": "history", "exam": code,
                        "topics": history.get(code, [])})
        return out({"ok": True, "scope": "history", "by_exam": history})

    session = load_active_session(base)
    return out({"ok": True, "scope": "session", "exam": session["exam"],
                "topics": session["asked_topics"]})


def cmd_suggest(args, base):
    """Pick the domain with the largest coverage deficit against guide weights."""
    session = load_active_session(base)

    domains = session.get("domains") or []
    history = load_json(_path(base, "history.json"), {})
    historical_topics = history.get(session["exam"], [])
    if not domains:
        return out({
            "ok": True,
            "suggested_domain": None,
            "detail": "No domain plan recorded. Re-run start with --domains from the "
                      "official exam guide to enable weighted coverage.",
            "avoid_topics": session["asked_topics"],
            "historical_topics": historical_topics,
        })

    total = session.get("total_planned") or max(session["question_number"] + 1, len(domains))
    weights = [d["weight"] for d in domains]
    use_even = any(w is None for w in weights) or sum(w or 0 for w in weights) <= 0
    even = 100.0 / len(domains)

    rows = []
    for d in domains:
        weight = even if use_even else float(d["weight"])
        asked = session["domain_stats"].get(d["name"], {}).get("asked", 0)
        expected = weight / 100.0 * total
        rows.append({
            "domain": d["name"],
            "weight_pct": round(weight, 2),
            "asked": asked,
            "expected_by_end": round(expected, 2),
            "deficit": round(expected - asked, 3),
        })

    rows.sort(key=lambda r: (-r["deficit"], r["asked"]))
    return out({
        "ok": True,
        "suggested_domain": rows[0]["domain"],
        "weighting": "even-split-fallback" if use_even else "official-guide-weights",
        "coverage": rows,
        "avoid_topics": session["asked_topics"],
        "historical_topics": historical_topics,
    })


def cmd_end(args, base):
    session_path = _path(base, "session.json")
    session = load_active_session(base)

    answered = session["correct"] + session["incorrect"]
    per_domain = []
    for domain, s in sorted(session["domain_stats"].items()):
        per_domain.append({
            "domain": domain,
            "asked": s["asked"],
            "correct": s["correct"],
            "incorrect": s["incorrect"],
            "accuracy_pct": pct(s["correct"], s["asked"]),
            "total_seconds": s.get("total_seconds"),
            "avg_seconds": (
                round(s["total_seconds"] / s["asked"], 1)
                if s.get("total_seconds") and s["asked"]
                else None
            ),
        })
    weakest = sorted(per_domain, key=lambda r: (r["accuracy_pct"], -r["incorrect"]))

    timed_answers = [a for a in session["answers"] if a.get("elapsed_seconds") is not None]
    total_seconds = round(sum(a["elapsed_seconds"] for a in timed_answers), 1) if timed_answers else None
    avg_seconds = round(total_seconds / len(timed_answers), 1) if timed_answers else None

    report = {
        "exam": session["exam"],
        "difficulty": session["difficulty"],
        "started_at": session["started_at"],
        "ended_at": now(),
        "answered": answered,
        "correct": session["correct"],
        "incorrect": session["incorrect"],
        "score_pct": pct(session["correct"], answered),
        "total_seconds": total_seconds,
        "avg_seconds_per_question": avg_seconds,
        "per_domain": per_domain,
        "weakest_domains": [r["domain"] for r in weakest if r["incorrect"] > 0][:3],
        "topics_covered": session["asked_topics"],
        "answers": session["answers"],
        "pending_question_discarded": bool(session.get("pending")),
    }

    archive = load_json(_path(base, "sessions_archive.json"), [])
    archive.append(report)
    save_json(_path(base, "sessions_archive.json"), archive)

    session["active"] = False
    session["pending"] = None
    session["ended_at"] = report["ended_at"]
    save_json(session_path, session)

    return out({"ok": True, "report": report})


def cmd_debug(args, base):
    session_path = _path(base, "session.json")
    session = load_active_session(base)
    session["debug"] = args.mode == "on"
    session["updated_at"] = now()
    save_json(session_path, session)
    return out({"ok": True, "debug": session["debug"]})


def cmd_reset(args, base):
    save_json(_path(base, "session.json"), empty_session())
    return out({"ok": True, "detail": "Session cleared. History and calibration kept."})


# --------------------------------------------------------------------------
# Architecture Challenge Mode
# --------------------------------------------------------------------------
# These four commands manage free-form architecture design challenges. They
# are intentionally separate from the multiple-choice quiz state so both
# modes can coexist in the same session without corrupting each other.
#
# State lives under the key "design_challenge" in session.json. Structure:
#
#   design_challenge: {
#     "phase":          "initial" | "adapted" | "complete",
#     "domain":         str,
#     "topic":          str,                # stable slug for anti-repetition
#     "difficulty":     str,
#     "scenario":       str,
#     "requirements":   [{id, label, weight}],   # initial requirements
#     "curveball": {
#       "label":              str,          # change of constraint or new load
#       "added_requirement":  {id, label, weight}
#     },
#     "grounding":      [{claim, source, status}],
#     "initial_result":  {score, max_score, pct, per_req, elapsed_seconds, at},
#     "adapted_result":  {score, max_score, pct, per_req, elapsed_seconds, at},
#     "started_at":     ISO8601,
#     "initial_timer_started_at": ISO8601 | null,
#     "adapted_timer_started_at": ISO8601 | null,
#   }
# --------------------------------------------------------------------------

DESIGN_PHASES = ("initial", "adapted", "complete")
SCORE_STATUSES = ("satisfied", "partial", "missed")
PARTIAL_WEIGHT = 0.5   # fraction of a requirement's weight counted as partial credit


def _validate_requirements(reqs, field_name):
    """Return (list_of_reqs, error_string). error_string is None on success."""
    if not isinstance(reqs, list) or not reqs:
        return None, f"{field_name} must be a non-empty list"
    total_weight = 0.0
    ids_seen = set()
    for r in reqs:
        if not isinstance(r, dict):
            return None, f"each entry in {field_name} must be an object"
        if not isinstance(r.get("id"), str) or not r["id"].strip():
            return None, f"each {field_name} entry needs a non-empty string 'id'"
        if not isinstance(r.get("label"), str) or not r["label"].strip():
            return None, f"each {field_name} entry needs a non-empty string 'label'"
        try:
            w = float(r.get("weight", 0))
        except (TypeError, ValueError):
            return None, f"{field_name} entry '{r.get('id')}' has non-numeric weight"
        if w <= 0:
            return None, f"{field_name} entry '{r.get('id')}' weight must be > 0"
        if r["id"] in ids_seen:
            return None, f"duplicate requirement id '{r['id']}' in {field_name}"
        ids_seen.add(r["id"])
        total_weight += w
    # Normalise weights so they always sum to 100 internally
    normalised = [
        {"id": r["id"], "label": r["label"], "weight": round(float(r["weight"]) / total_weight * 100, 4)}
        for r in reqs
    ]
    return normalised, None


def _compute_design_score(requirements, scores_list):
    """Return (score, max_score, per_req_list).

    score    – weighted points earned (0-100 scale, requirements already normalised)
    max_score – 100.0 (requirements are normalised)
    per_req  – list of {id, label, weight, status, points_earned}
    """
    score_map = {s["id"]: s["status"] for s in scores_list}
    per_req = []
    earned = 0.0
    for r in requirements:
        status = score_map.get(r["id"], "missed")
        if status == "satisfied":
            pts = r["weight"]
        elif status == "partial":
            pts = round(r["weight"] * PARTIAL_WEIGHT, 4)
        else:
            pts = 0.0
        earned += pts
        per_req.append({
            "id": r["id"],
            "label": r["label"],
            "weight": r["weight"],
            "status": status,
            "points_earned": round(pts, 4),
        })
    return round(earned, 2), 100.0, per_req


def cmd_design_start(args, base):
    """Persist a grounded architecture challenge before showing it to the learner."""
    session_path = _path(base, "session.json")
    session = load_active_session(base)

    if session.get("design_challenge") and session["design_challenge"].get("phase") not in (None, "complete"):
        dc = session["design_challenge"]
        return fail(
            "an architecture challenge is already active; grade it or run design-clear before starting another",
            error_code="design_challenge_active",
            phase=dc.get("phase"),
            topic=dc.get("topic"),
        )

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as exc:
        return fail(f"--payload is not valid JSON: {exc}")

    required_keys = {"domain", "topic", "scenario", "requirements", "curveball", "grounding"}
    if not isinstance(payload, dict) or not required_keys.issubset(payload):
        return fail(
            "design payload must contain: domain, topic, scenario, requirements, curveball, grounding",
            missing=sorted(required_keys - set(payload if isinstance(payload, dict) else {})),
        )

    for field in ("domain", "topic", "scenario"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            return fail(f"design payload '{field}' must be a non-empty string")

    reqs, err = _validate_requirements(payload["requirements"], "requirements")
    if err:
        return fail(err)

    cb = payload["curveball"]
    if not isinstance(cb, dict):
        return fail("curveball must be an object")
    if not isinstance(cb.get("label"), str) or not cb["label"].strip():
        return fail("curveball.label must be a non-empty string")
    added_req_raw = cb.get("added_requirement")
    if added_req_raw is None:
        return fail("curveball.added_requirement must be present")
    added_list, err = _validate_requirements([added_req_raw], "curveball.added_requirement")
    if err:
        return fail(err)
    added_req = added_list[0]

    # Verify grounding
    grounding = payload["grounding"]
    if not isinstance(grounding, list) or not grounding:
        return fail("grounding must be a non-empty list of official-source records")
    if any(not isinstance(g, dict) or g.get("status") != "verified"
           or not is_official_aws_url(g.get("source")) for g in grounding):
        return fail("every grounding record needs status=verified and an HTTPS URL on an official AWS host")

    dc = {
        "phase": "initial",
        "domain": payload["domain"].strip(),
        "topic": topic_key(payload["topic"]),
        "topic_label": payload["topic"].strip(),
        "difficulty": args.difficulty,
        "scenario": payload["scenario"].strip(),
        "requirements": reqs,
        "curveball": {"label": cb["label"].strip(), "added_requirement": added_req},
        "grounding": grounding,
        "initial_result": None,
        "adapted_result": None,
        "started_at": now(),
        "initial_timer_started_at": None,
        "adapted_timer_started_at": None,
    }

    session["design_challenge"] = dc
    session["updated_at"] = now()
    save_json(session_path, session)

    # Public view: hide curveball until initial phase is graded
    public_dc = {k: v for k, v in dc.items() if k not in ("curveball",)}
    public_dc["curveball_hidden"] = True
    return out({"ok": True, "design_challenge": public_dc})


def cmd_design_pending(args, base):
    """Return the current design challenge state (curveball hidden until adapted phase)."""
    session = load_active_session(base)

    dc = session.get("design_challenge")
    if not dc or dc.get("phase") in (None, "complete"):
        return out({"ok": True, "has_active_challenge": False})

    public = {k: v for k, v in dc.items() if k not in ("curveball", "grounding")}
    # Reveal curveball only once initial phase is graded
    if dc["phase"] == "adapted":
        public["curveball"] = dc["curveball"]
        public["curveball_hidden"] = False
    else:
        public["curveball_hidden"] = True
    return out({"ok": True, "has_active_challenge": True, "design_challenge": public})


def _resolve_in_scope_reqs(dc, phase):
    """Return (in_scope_reqs, error_str) for the given phase.

    For 'initial' returns the stored requirements as-is.
    For 'adapted' merges original + curveball requirement and renormalises to 100%.
    """
    if phase == "initial":
        return dc["requirements"], None
    cb_req = dc["curveball"]["added_requirement"]
    raw_reqs = [{"id": r["id"], "label": r["label"], "weight": r["weight"]} for r in dc["requirements"]]
    raw_reqs.append({"id": cb_req["id"], "label": cb_req["label"], "weight": cb_req["weight"]})
    return _validate_requirements(raw_reqs, "adapted requirements")


def _validate_scores(scores_list, in_scope_reqs):
    """Validate a scores list against in-scope requirements.

    Returns error_payload dict on failure, or None on success.
    """
    if not isinstance(scores_list, list) or not scores_list:
        return fail("--scores must be a non-empty JSON array of {id, status} objects")

    in_scope_ids = {r["id"] for r in in_scope_reqs}
    submitted_ids = set()
    for s in scores_list:
        if not isinstance(s, dict):
            return fail("each scores entry must be an object")
        if not isinstance(s.get("id"), str):
            return fail("each scores entry needs a string 'id'")
        if s.get("status") not in SCORE_STATUSES:
            return fail(f"scores entry '{s['id']}' status must be one of: {SCORE_STATUSES}")
        if s["id"] in submitted_ids:
            return fail(f"duplicate requirement id '{s['id']}' in scores")
        submitted_ids.add(s["id"])

    missing = in_scope_ids - submitted_ids
    if missing:
        return fail(
            "scores missing for some in-scope requirements",
            error_code="incomplete_scores",
            missing_ids=sorted(missing),
        )
    extra = submitted_ids - in_scope_ids
    if extra:
        return fail(
            "scores reference requirement ids not in scope for this phase",
            error_code="unknown_requirement_ids",
            unknown_ids=sorted(extra),
        )
    return None


def _resolve_design_elapsed(args, dc):
    """Resolve elapsed seconds for a design phase from explicit flag or timer."""
    elapsed = None
    if getattr(args, "elapsed_seconds", None) is not None:
        try:
            elapsed = float(args.elapsed_seconds)
            if elapsed < 0:
                elapsed = None
        except (TypeError, ValueError):
            pass
    if elapsed is None:
        timer_key = f"{args.phase}_timer_started_at"
        if dc.get(timer_key):
            try:
                started = datetime.fromisoformat(dc[timer_key])
                elapsed = round((datetime.now(timezone.utc) - started).total_seconds(), 1)
            except (ValueError, TypeError):
                pass
    return elapsed


def _advance_challenge(session, dc, phase, result, base):
    """Advance challenge state after grading a phase.

    Mutates dc and session in-place. Returns (signal, curveball).
    curveball is the curveball dict when revealing (initial phase graded), else None.
    """
    if phase == "initial":
        dc["initial_result"] = result
        dc["phase"] = "adapted"
        dc["adapted_timer_started_at"] = now()
        signal = "curveball_revealed"
        curveball = dc["curveball"]
    else:
        dc["adapted_result"] = result
        dc["phase"] = "complete"
        signal = "challenge_complete"
        curveball = None

    session["design_challenge"] = dc
    session["updated_at"] = now()

    if dc["phase"] == "complete":
        # Anti-repetition: record topic as asked
        if dc["topic"] not in session["asked_topics"]:
            session["asked_topics"].append(dc["topic"])
        history_path = _path(base, "history.json")
        history = load_json(history_path, {})
        bucket = history.setdefault(session["exam"], [])
        if dc["topic"] not in bucket:
            bucket.append(dc["topic"])
        save_json(history_path, history)

        # Archive challenge summary in answers for report aggregation
        session.setdefault("answers", [])
        session["question_number"] += 1
        avg_pct = round(
            (
                (dc["initial_result"]["pct"] if dc["initial_result"] else 0)
                + (dc["adapted_result"]["pct"] if dc["adapted_result"] else 0)
            ) / 2, 1
        )
        session["answers"].append({
            "n": session["question_number"],
            "type": "architecture_challenge",
            "domain": dc["domain"],
            "topic": dc["topic"],
            "correct": avg_pct >= 70,
            "difficulty": dc["difficulty"],
            "initial_pct": dc["initial_result"]["pct"] if dc["initial_result"] else None,
            "adapted_pct": dc["adapted_result"]["pct"] if dc["adapted_result"] else None,
            "elapsed_seconds": (
                (dc["initial_result"].get("elapsed_seconds") or 0)
                + (dc["adapted_result"].get("elapsed_seconds") or 0)
            ) or None,
            "at": now(),
        })
        # Update domain stats for report
        domain = dc["domain"]
        stats = session["domain_stats"].setdefault(
            domain, {"asked": 0, "correct": 0, "incorrect": 0, "streak_incorrect": 0}
        )
        stats["asked"] += 1
        if avg_pct >= 70:
            session["correct"] += 1
            session["streak_correct"] += 1
            session["streak_incorrect"] = 0
            stats["correct"] += 1
            stats["streak_incorrect"] = 0
        else:
            session["incorrect"] += 1
            session["streak_incorrect"] += 1
            session["streak_correct"] = 0
            stats["incorrect"] += 1
            stats["streak_incorrect"] += 1

    return signal, curveball


def cmd_design_grade(args, base):
    """Record rubric scores for the current phase and advance the challenge state."""
    session_path = _path(base, "session.json")
    session = load_active_session(base)

    dc = session.get("design_challenge")
    if not dc or dc.get("phase") == "complete":
        return fail("no active architecture challenge", error_code="no_active_challenge")

    if args.phase not in ("initial", "adapted"):
        return fail("--phase must be 'initial' or 'adapted'")
    if args.phase != dc["phase"]:
        return fail(
            f"challenge is in '{dc['phase']}' phase; cannot grade '{args.phase}'",
            error_code="wrong_phase",
            current_phase=dc["phase"],
        )

    in_scope_reqs, err = _resolve_in_scope_reqs(dc, args.phase)
    if err:
        return fail(f"internal error normalising adapted requirements: {err}")

    try:
        scores_list = json.loads(args.scores)
    except json.JSONDecodeError as exc:
        return fail(f"--scores is not valid JSON: {exc}")

    validation_error = _validate_scores(scores_list, in_scope_reqs)
    if validation_error is not None:
        return validation_error

    score, max_score, per_req = _compute_design_score(in_scope_reqs, scores_list)
    score_pct = round(score / max_score * 100, 1) if max_score else 0.0
    elapsed = _resolve_design_elapsed(args, dc)

    result = {
        "score": score,
        "max_score": max_score,
        "pct": score_pct,
        "per_req": per_req,
        "elapsed_seconds": elapsed,
        "at": now(),
    }

    signal, curveball = _advance_challenge(session, dc, args.phase, result, base)
    save_json(session_path, session)

    response = {
        "ok": True,
        "phase_graded": args.phase,
        "result": result,
        "signal": signal,
        "session": summarize(session),
    }
    if curveball is not None:
        response["curveball"] = curveball
    if args.phase == "adapted":
        response["initial_result"] = dc["initial_result"]
        response["adapted_result"] = dc["adapted_result"]
        response["combined_pct"] = round(
            (dc["initial_result"]["pct"] + dc["adapted_result"]["pct"]) / 2, 1
        )
    return out(response)


def cmd_design_clear(args, base):
    """Discard the active architecture challenge without grading."""
    session_path = _path(base, "session.json")
    session = load_active_session(base)
    had = bool(session.get("design_challenge") and session["design_challenge"].get("phase") not in (None, "complete"))
    session["design_challenge"] = None
    session["updated_at"] = now()
    save_json(session_path, session)
    return out({"ok": True, "cleared": had})


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
