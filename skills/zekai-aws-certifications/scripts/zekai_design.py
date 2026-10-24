"""Architecture Challenge Mode commands: design-start, design-pending, design-grade, design-clear."""

import json
from datetime import datetime, timezone

from zekai_common import (
    _path,
    fail,
    is_official_aws_url,
    load_active_session,
    load_json,
    now,
    out,
    save_json,
    topic_key,
)
from zekai_summary import summarize


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
