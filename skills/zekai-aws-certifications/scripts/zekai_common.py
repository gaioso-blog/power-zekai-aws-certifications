"""Shared constants, file I/O and small helpers for the zekai session scripts."""

import json
import os
import re
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


def public_pending(pending):
    """Return learner-safe pending state with answer key and option grounding hidden."""
    if not pending:
        return None
    safe = {k: v for k, v in pending.items()
            if k not in {"correct_answers", "grounding"}}
    safe["grounded"] = bool(pending.get("grounding"))
    return safe
