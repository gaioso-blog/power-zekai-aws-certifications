"""Read-side and lifecycle commands: status, progress, asked, suggest, end, debug, reset."""

from zekai_common import (
    _path,
    empty_session,
    load_active_session,
    load_json,
    now,
    out,
    pct,
    public_pending,
    save_json,
)


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
