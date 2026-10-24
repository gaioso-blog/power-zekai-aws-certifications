"""Interactive Quiz Mode commands: start, pending-*, timer-start, grade, calibrate."""

import argparse
import json
import re
from datetime import datetime, timezone

from zekai_common import (
    DIFFICULTIES,
    DOMAIN_ERRORS_TO_OFFER_CONCEPT,
    PROGRESS_EVERY,
    SCHEMA_VERSION,
    STREAK_TO_OFFER_HARDER,
    _path,
    empty_session,
    fail,
    is_official_aws_url,
    load_active_session,
    load_json,
    now,
    out,
    parse_bool,
    public_pending,
    save_json,
    topic_key,
)
from zekai_summary import summarize


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
