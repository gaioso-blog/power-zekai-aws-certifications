#!/usr/bin/env python3
"""Generate a markdown exam report from a finished zekai session.

Reads the last entry in sessions_archive.json (or a specific one via --index)
and writes a structured .md file to ExamResults/<EXAM_CODE>/.

Usage
-----
    python3 scripts/export_report.py                        # latest session
    python3 scripts/export_report.py --index 2             # 3rd session (0-based)
    python3 scripts/export_report.py --output-dir ./reports # custom output root
    python3 scripts/export_report.py --state-dir /path/to/.zekai

Exit codes: 0 on success, 1 on error.

Output file naming
------------------
    <output-dir>/<EXAM_CODE>/<EXAM_CODE>_<YYYYMMDD_HHMMSS>.md

The file is UTF-8. Section headers are in English by default; the SKILL.md
rule 1 (translate to user's language) applies only to agent-rendered output,
not to this script — the markdown file is a persistent record, English headers
make it readable across languages.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def state_dir(cli_value=None):
    path = cli_value or os.environ.get("ZEKAI_STATE_DIR") or os.path.join(
        os.path.expanduser("~"), ".zekai"
    )
    return path


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return default


def fmt_seconds(secs):
    """Format seconds as m:ss or N/A."""
    if secs is None:
        return "N/A"
    secs = int(round(secs))
    return f"{secs // 60}:{secs % 60:02d}"


def fmt_pct(value):
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def progress_bar(accuracy_pct, width=20):
    """Simple ASCII progress bar."""
    if accuracy_pct is None:
        return " " * width
    filled = round(accuracy_pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def scaled_score(score_pct):
    """Map 0-100% to the 100-1000 AWS scaled score range."""
    return int(round(100 + (score_pct / 100) * 900))


def passing_score_for(exam_code):
    """Return the passing scaled score for known exams; 720 is the AWS default."""
    thresholds = {
        "CLF-C02": 700,
        "AIF-C01": 700,
        "SAA-C03": 720,
        "DVA-C02": 720,
        "SOA-C03": 720,
        "DEA-C01": 720,
        "MLA-C01": 720,
        "SAP-C02": 750,
        "DOP-C02": 750,
        "AIP-C01": 750,
        "ANS-C01": 750,
        "SCS-C02": 750,
    }
    return thresholds.get(exam_code.upper(), 720)


# ---------------------------------------------------------------------------
# markdown builder
# ---------------------------------------------------------------------------

def build_report(report: dict) -> str:
    exam = report.get("exam", "UNKNOWN")
    difficulty = report.get("difficulty", "—")
    started_at = report.get("started_at", "")
    ended_at = report.get("ended_at", "")
    answered = report.get("answered", 0)
    correct = report.get("correct", 0)
    incorrect = report.get("incorrect", 0)
    score_pct = report.get("score_pct", 0.0)
    total_sec = report.get("total_seconds")
    avg_sec = report.get("avg_seconds_per_question")
    per_domain = report.get("per_domain", [])
    weakest = report.get("weakest_domains", [])
    topics = report.get("topics_covered", [])
    answers = report.get("answers", [])
    discarded = report.get("pending_question_discarded", False)

    ss = scaled_score(score_pct)
    passing = passing_score_for(exam)
    passed = ss >= passing
    verdict = "✅ PASSED" if passed else "❌ NEEDS MORE STUDY"

    lines = []

    # ── title ────────────────────────────────────────────────────────────────
    lines.append(f"# Exam Session Report — {exam}")
    lines.append("")
    lines.append(f"> Generated: {ended_at}  ")
    lines.append(f"> Difficulty: {difficulty}")
    lines.append("")

    # ── summary card ─────────────────────────────────────────────────────────
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Exam | {exam} |")
    lines.append(f"| Session started | {started_at} |")
    lines.append(f"| Session ended | {ended_at} |")
    lines.append(f"| Questions answered | {answered} |")
    lines.append(f"| Correct | {correct} |")
    lines.append(f"| Incorrect | {incorrect} |")
    lines.append(f"| Raw score | {fmt_pct(score_pct)} |")
    lines.append(f"| Scaled score (est.) | {ss} / 1000 |")
    lines.append(f"| Passing threshold | {passing} / 1000 |")
    lines.append(f"| Verdict | {verdict} |")
    lines.append(f"| Total time | {fmt_seconds(total_sec)} |")
    lines.append(f"| Avg time / question | {fmt_seconds(avg_sec)} |")
    if discarded:
        lines.append("| Note | 1 pending question was discarded at session end |")
    lines.append("")

    # ── domain breakdown ─────────────────────────────────────────────────────
    lines.append("## Domain Performance")
    lines.append("")
    lines.append("| Domain | Asked | Correct | Accuracy | Time (total) | Avg/Q | Progress |")
    lines.append("|--------|------:|--------:|---------:|:------------:|------:|----------|")
    for d in per_domain:
        domain_name = d.get("domain", "—")
        d_asked = d.get("asked", 0)
        d_correct = d.get("correct", 0)
        d_acc = d.get("accuracy_pct")
        d_total_sec = d.get("total_seconds")
        d_avg_sec = d.get("avg_seconds")
        indicator = "⚠️" if domain_name in weakest else "✅" if d_acc and d_acc >= 70 else "❌"
        lines.append(
            f"| {indicator} {domain_name} | {d_asked} | {d_correct} "
            f"| {fmt_pct(d_acc)} | {fmt_seconds(d_total_sec)} "
            f"| {fmt_seconds(d_avg_sec)} | `{progress_bar(d_acc)}` |"
        )
    lines.append("")

    # ── per-question log ──────────────────────────────────────────────────────
    if answers:
        lines.append("## Question Log")
        lines.append("")
        lines.append("| # | Domain | Topic | Result | Difficulty | Time |")
        lines.append("|--:|--------|-------|:------:|:----------:|-----:|")
        for a in answers:
            n = a.get("n", "—")
            dom = a.get("domain", "—")
            topic = a.get("topic", "—").replace("-", " ").title()
            result = "✅" if a.get("correct") else "❌"
            diff = a.get("difficulty", "—")
            elapsed = a.get("elapsed_seconds")
            lines.append(
                f"| {n} | {dom} | {topic} | {result} | {diff} | {fmt_seconds(elapsed)} |"
            )
        lines.append("")

    # ── weakest domains ───────────────────────────────────────────────────────
    if weakest:
        lines.append("## Recommended Review")
        lines.append("")
        lines.append("Focus your next study session on these domains, in priority order:")
        lines.append("")
        for i, w in enumerate(weakest, 1):
            lines.append(f"{i}. **{w}**")
        lines.append("")
        lines.append(
            "> Tip: use Interactive Quiz Mode and ask specifically for questions "
            "from these domains to rebuild accuracy before your next simulation."
        )
        lines.append("")

    # ── topics covered ────────────────────────────────────────────────────────
    if topics:
        lines.append("## Topics Covered This Session")
        lines.append("")
        for t in topics:
            lines.append(f"- {t.replace('-', ' ').title()}")
        lines.append("")

    # ── footer ────────────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append(
        "_This report was generated by zekai-aws-certifications. "
        "Scaled scores and pass/fail projections are estimates based on practice "
        "performance and do not predict actual AWS exam results._"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# file output
# ---------------------------------------------------------------------------

def write_report(report: dict, output_root: str) -> str:
    """Write the markdown report and return the output file path."""
    exam = report.get("exam", "UNKNOWN").upper()
    ended_at = report.get("ended_at", "")

    # Parse timestamp for filename; fall back to now()
    try:
        dt = datetime.fromisoformat(ended_at)
    except (ValueError, TypeError):
        dt = datetime.now(timezone.utc)

    timestamp = dt.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(output_root, "ExamResults", exam)
    os.makedirs(out_dir, exist_ok=True)

    filename = f"{exam}_{timestamp}.md"
    filepath = os.path.join(out_dir, filename)

    content = build_report(report)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content)

    return filepath


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv):
    p = argparse.ArgumentParser(
        prog="export_report.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--state-dir", dest="state_dir", default=None,
                   help="override state directory (default $ZEKAI_STATE_DIR or ~/.zekai)")
    p.add_argument("--output-dir", dest="output_dir", default=None,
                   help="root directory for ExamResults/ output (default: current working dir)")
    p.add_argument("--index", type=int, default=None,
                   help="0-based index into sessions_archive.json (default: last)")
    p.add_argument("--stdout", action="store_true",
                   help="print the markdown to stdout instead of writing a file")

    args = p.parse_args(argv[1:])

    base = state_dir(args.state_dir)
    archive_path = os.path.join(base, "sessions_archive.json")
    archive = load_json(archive_path, [])

    if not archive:
        print(json.dumps({
            "ok": False,
            "error": "no_sessions_found",
            "detail": f"sessions_archive.json not found or empty at {archive_path}. "
                      "Run a session and call `session.py end` first.",
        }, indent=2))
        return 1

    idx = args.index if args.index is not None else len(archive) - 1
    if idx < 0 or idx >= len(archive):
        print(json.dumps({
            "ok": False,
            "error": "index_out_of_range",
            "detail": f"index {idx} is out of range; archive has {len(archive)} session(s).",
        }, indent=2))
        return 1

    report = archive[idx]

    if args.stdout:
        print(build_report(report))
        return 0

    output_root = args.output_dir or os.getcwd()
    filepath = write_report(report, output_root)
    print(json.dumps({"ok": True, "file": filepath}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
