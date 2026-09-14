# Interactive Session Workflow

Load this file on every Interactive Quiz Mode or exam-simulation turn.

## Resume before exam selection

For `continue`, `resume`, `continuar`, or equivalent without an exam code, run:

```bash
python3 scripts/session.py status
```

- Active with `pending`: reshow that exact pending question; never create another.
- Active without `pending`: continue the stored exam.
- Inactive: ask which exam to study.

## Start

```bash
python3 scripts/session.py start --exam <CODE> --difficulty <level> [--total N] \
  --domains '[{"name":"<official domain>","weight":<published pct>}, ...]'
```

Pass only guide-published weights. A matching exam resumes. On
`active_session_conflict`, ask whether to resume `active_exam` or start
`requested_exam` with `--fresh`; never mix exams. Use `--fresh` only after the user
chooses to discard the active session.

## Every question

1. Run `python3 scripts/session.py suggest`. Use `suggested_domain` unless the user chose
   one. Never reuse `avoid_topics`; prefer topics absent from `historical_topics` until
   the domain is exhausted.
2. Construct the question and complete official grounding. Before displaying it, run:
   ```bash
   python3 scripts/session.py pending-set --payload '<JSON>'
   ```
   Required fields: `domain`, stable `topic`, `question`, letter-keyed `options`,
   `correct_answers` (list of 1, 2, or 3 letters), and `grounding` records with
   `status:"verified"` plus an official `source` URL. If the command fails, do not
   show the question.
3. Immediately after `pending-set` succeeds, start the question timer:
   ```bash
   python3 scripts/session.py timer-start
   ```
   Call this **before** emitting the question to the learner. This records the
   display timestamp so elapsed time is computed automatically on `grade`.
4. Emit the pre-answer template with no source metadata, then wait.
5. On an answer, recover the learner-safe question with `pending-get` if needed, then grade and record exactly once:
   ```bash
   python3 scripts/session.py grade --response "<submitted letter(s)>"
   ```
   `grade` auto-computes elapsed seconds from `timer_started_at`. Pass
   `--elapsed-seconds N` to override. Only this post-submission response reveals
   `correct_answers`; it also clears `pending`.
   `wrong_answer_count` is not graded and leaves the question pending.
6. Emit the post-answer explanation (include elapsed time from the `grading` response),
   act on every returned `signals` entry, then ask whether to continue.

On an explicit skip, call `pending-clear`. If an off-topic question arrives while an
answer is pending, reply in 2-3 sentences without hinting, then reshow the pending
options.

## Recovery invariant

`status` and `pending-get` return the question and options but redact answer key and
grounding details. Submit the learner's response to `grade`; only its post-submission
output reveals the key. Never reconstruct state from conversation memory or emit a
`[STATE: ...]` marker.
