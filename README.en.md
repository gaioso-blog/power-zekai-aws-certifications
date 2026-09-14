# zekai-aws-certifications

> 🇧🇷 [Documentação em português disponível em README.md](README.md)

A Kiro Power that turns the IDE into a full-featured AWS certification study engine.
Generates officially grounded practice questions, interactive quizzes, mock exams,
architecture design challenges, flashcards, study plans, and service comparisons for
any current AWS Certification exam — Foundational, Associate, Professional, and Specialty.

> Every answer cites official AWS documentation. No guessing, no hallucinations,
> no AWS credentials required.

---

## Table of contents

- [Why this power?](#why-this-power)
- [Features](#features)
- [Supported exams](#supported-exams)
- [Installation](#installation)
- [Study modes](#study-modes)
  - [Study Mode](#study-mode)
  - [Interactive Quiz Mode](#interactive-quiz-mode)
  - [Architecture Challenge Mode](#architecture-challenge-mode)
  - [Question Breakdown Mode](#question-breakdown-mode)
- [Session state](#session-state)
- [Scripts reference](#scripts-reference)
  - [session.py](#sessionpy)
  - [resolve_exam.py](#resolve_exampy)
  - [export_report.py](#export_reportpy)
- [File structure](#file-structure)
- [Configuration](#configuration)
- [Recommended models](#recommended-models)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)

---

## Why this power?

AWS certification exams test architectural thinking, not memorisation. Passive study
(videos, flashcards) only takes you so far. You need active practice: realistic
scenarios, weighted feedback grounded in official sources, and design exercises that
force you to propose solutions before seeing the answer.

This power gives you four complementary study modes inside Kiro. Install once and
you have a complete study toolkit that adapts to any AWS certification you're
preparing for, including newly launched exams verified against the live official index.

---

## Features

- **Always-on exam context** — every response is tailored to your chosen exam: domain
  mapping, official documentation citations, and language adaptation.
- **Four study modes** — Study, Interactive Quiz, Architecture Challenge, and Question
  Breakdown, each targeting a different cognitive skill.
- **Persistent session state** — score, streaks, asked topics, and pending questions
  survive context compaction and new chat sessions via on-disk state (`~/.zekai`).
- **Per-question timer** — each question in Interactive Quiz Mode is timed from the
  moment it appears to the moment you submit. Elapsed time is shown in the post-answer
  block and aggregated in the final report with per-domain averages.
- **Weighted domain coverage** — question selection mirrors the official exam guide's
  domain weights, not intuition.
- **Anti-repetition** — per-session and cross-session topic history prevents the same
  scenario from appearing twice in the same learning arc.
- **Adaptive difficulty** — automatic signals from `session.py` prompt difficulty
  increases after consecutive correct answers and concept explanations after streaks of
  errors.
- **Architecture Challenge Mode** — free-form design proposals graded against a weighted
  rubric, with an unexpected constraint change ("curveball") that forces real adaptation.
- **Quality gate** — 12-item checklist runs silently before every hard/exam-level
  question; activatable in debug mode for full audit output.
- **Difficulty calibration** — perceived-difficulty feedback after hard questions is
  recorded and used to close the gap between generated and actual exam difficulty.
- **Markdown exam reports** — full session reports saved to `ExamResults/<EXAM_CODE>/`
  with scaled score, per-domain accuracy, per-question timing, and a complete question log.
- **Multilingual** — responds in the language the user writes in.
- **Official sources only** — every factual claim verified via the bundled AWS
  Documentation MCP server against `docs.aws.amazon.com`.

---

## Supported exams

The power works with any current AWS certification exam. At session start, Kiro looks
up the exam structure (domains, weights, question count, time limit, passing score)
from the official AWS exam guides index in real time.

Local metadata is pre-loaded for these exams:

| Level | Code | Name |
|---|---|---|
| Foundational | CLF-C02 | AWS Certified Cloud Practitioner |
| Foundational | AIF-C01 | AWS Certified AI Practitioner |
| Associate | SAA-C03 | AWS Certified Solutions Architect – Associate |
| Associate | DVA-C02 | AWS Certified Developer – Associate |
| Associate | SOA-C03 | AWS Certified CloudOps Engineer – Associate |
| Associate | DEA-C01 | AWS Certified Data Engineer – Associate |
| Associate | MLA-C01 | AWS Certified Machine Learning Engineer – Associate |
| Professional | SAP-C02 | AWS Certified Solutions Architect – Professional |
| Professional | DOP-C02 | AWS Certified DevOps Engineer – Professional |
| Professional | AIP-C01 | AWS Certified Generative AI Developer – Professional |
| Specialty | ANS-C01 | AWS Certified Advanced Networking – Specialty |
| Specialty | SCS-C02 | AWS Certified Security – Specialty |

Any exam code not in this list is verified against the live official index automatically.
Newly launched exams are supported without requiring a power update.

---

## Installation

**Prerequisites**

| Requirement | Purpose |
|---|---|
| Kiro IDE | Runs the power |
| `uv` | Runs the bundled AWS Documentation MCP server |

Install `uv` if not already present:
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS via Homebrew
brew install uv
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

No AWS account or credentials needed — the MCP server only reads public documentation.

**Steps**

1. Open Kiro and go to the Powers panel in the sidebar.
2. Choose **Add Custom Power**.
3. Select **Import power from GitHub**.
4. Enter the repository URL: `https://github.com/gaioso-blog/power-zekai-aws-certifications`.
5. Click **Install**.
6. Open any workspace folder, Kiro requires a folder open for powers to activate.

**Verify**

```
I'm studying for the SAA-C03. What is Amazon S3?
```

Kiro will confirm the exam, look up its structure from the official guide, and respond
with domain-mapped content.

---

## Study modes

### Study Mode

Delivers the complete answer immediately: question, all options, correct answer,
explanation of the correct option, explanation of each wrong option, exam trap, revision
summary, and official documentation links.

**Activation signals:** "with answer key", "with explanations", "com gabarito",
"com explicação", "questões resolvidas"

**Default batch size:** 5 questions. Requests for 6+ are delivered in batches of 5.

Does not use `session.py` state unless the user explicitly asks for score tracking.

---

### Interactive Quiz Mode

One question at a time. The answer and all source metadata are withheld until the
learner submits. After submission, the full explanation is revealed.

**Activation signals:** "quiz", "mock exam", "test me", "one at a time",
"modo quiz", "simulado interativo", "faça como prova"

**Default:** enters this mode silently when the signal is ambiguous.

**Question formats:**
- Single choice: pick 1 of 4 options (A–D)
- Multiple response – select two: pick 2 of 5 options (A–E)
- Multiple response – select three: pick 3 of 6 options (A–F) — Professional and Specialty only

**Per-question timer:** the timer starts automatically when the question is displayed
(via `session.py timer-start`) and stops when you submit your answer. Elapsed time
appears in the result block immediately below your answer, and is stored in every
answer record. The final report shows:
- Total session time
- Average time per question
- Average time per domain
- Individual time for each question in the question log

This lets you identify which domains cost you the most time — useful for managing pacing
on the real exam.

**Adaptive difficulty:** after 3 consecutive correct answers, the agent offers to move
up a difficulty level. After 2 consecutive errors in the same domain, it offers a
concept explanation.

**Anti-repetition:** `session.py suggest` selects the domain with the largest weighted
deficit and returns `avoid_topics` (current session) and `historical_topics`
(cross-session) to prevent reuse.

---

### Architecture Challenge Mode

The learner proposes a free-form AWS architecture for a realistic business scenario,
receives weighted rubric feedback, then adapts their design after an unexpected
constraint change (the curveball).

**Activation signals:** "architecture challenge", "design challenge", "propose an architecture",
"modo desafio", "desafio de arquitetura", "projete uma arquitetura"

**How it works:**

1. **Initial phase** — the learner receives a scenario and a list of 3–5 requirements
   (no multiple choice options, no hints). The learner proposes a complete architecture
   in free text.
2. **Rubric scoring** — the agent evaluates each requirement as `satisfied`, `partial`
   (0.5× credit), or `missed`, then calls `session.py design-grade --phase initial`.
3. **Curveball reveal** — after grading, a new business constraint is revealed (e.g.,
   "the client now requires a read replica in a third region"). The curveball is never
   hinted at before this point.
4. **Adapted phase** — the learner amends their architecture. The scoring now includes
   all original requirements plus the curveball's added requirement (renormalised to 100).
5. **Final report** — combined score (average of both phases), per-requirement breakdown,
   architectural principle demonstrated, strengths, exam trap, and documentation links.

**Rubric statuses:**

| Status | Criterion | Points |
|---|---|---|
| `satisfied` | Correct service named with justification that addresses the requirement | Full weight |
| `partial` | Correct direction but wrong specific service, or correct service without justification | 50% of weight |
| `missed` | Requirement ignored, wrong service, or right service for the wrong reason | 0 |

**Verdict thresholds (combined %):**

| Score | Verdict |
|---|---|
| ≥ 80% | ✅ Excellent — solid architecture |
| ≥ 70% | ✅ Pass — good grasp of requirements |
| ≥ 50% | ⚠️ Partial — review the missed requirements |
| < 50% | ❌ Needs work — revisit the recommended documentation |

**Session integration:** completed challenges are recorded in `session.py` answers and
`domain_stats`, contributing to anti-repetition, weighted coverage, and the end-of-session
report just like multiple-choice questions.

---

### Question Breakdown Mode

A guided four-step reasoning dialogue. The learner and the agent analyse the same
question independently at each step, the agent reveals its own analysis only after
the learner submits theirs.

**Activation signals:** "question breakdown", "break this down", "walk me through",
"modo análise", "analisar questão", "me ajuda a pensar", "me ensina a eliminar"

**The four steps:**

1. **Extract the signal** — identify the objective, explicit constraints, implicit
   constraints, and the exam keyword that drives elimination.
2. **First elimination pass** — eliminate options that violate a specific stated
   constraint. Each elimination must name the constraint, not just "it seems wrong".
3. **Differentiate the finalists** — for each remaining option, explain why it satisfies
   requirements and what disqualifies it or makes it second-best.
4. **Reflect and generalise** — identify the exam trap, the generalisable reasoning
   pattern, and a two-sentence summary for spaced-repetition review.

The answer is not secret in this mode, the reasoning process is the product.

---

## Session state

All interactive state lives on disk in `~/.zekai` (overridable via `$ZEKAI_STATE_DIR`).

| File | Contents |
|---|---|
| `session.json` | Active session: exam, difficulty, score, domain stats, pending question, design challenge state |
| `history.json` | Asked topics per exam, across all sessions (cross-session anti-repetition) |
| `calibration.jsonl` | Append-only log of perceived vs generated difficulty per question |
| `sessions_archive.json` | Completed session summaries used by `export_report.py` |

State survives context compaction, IDE restarts, and new chat sessions.

---

## Scripts reference

### session.py

`scripts/session.py` is the single source of truth for all interactive session state.
It outputs JSON on stdout and uses exit code 0 for success, 1 for errors.

**State directory:** resolved in order: `--state-dir` flag → `$ZEKAI_STATE_DIR` → `~/.zekai`

#### Quiz / Simulation commands

| Command | Arguments | Description |
|---|---|---|
| `start` | `--exam CODE --difficulty LEVEL [--total N] [--domains JSON] [--fresh]` | Start or resume a session. `--domains` is a JSON array from the official guide: `[{"name":"...", "weight":30}]`. Use `--fresh` to discard an active session. |
| `status` | — | Print current session summary (score, domain stats, pending question). |
| `pending-set` | `--payload JSON` | Persist a fully grounded question before showing it to the learner. Required fields: `domain`, `topic`, `question`, `options`, `correct_answers`, `grounding`. |
| `pending-get` | — | Retrieve the learner-safe pending question (answer key and grounding redacted). |
| `pending-clear` | — | Skip and discard the pending question without grading. |
| `timer-start` | — | Record the display timestamp. Call immediately after `pending-set` and before showing the question. `grade` auto-computes elapsed time from this timestamp. |
| `grade` | `--response LETTERS [--elapsed-seconds N] [--difficulty LEVEL]` | Grade the pending question. Reveals the answer key only after submission. Returns adaptive `signals` array. Use `--elapsed-seconds N` to override the auto-computed time. |
| `calibrate` | `--perceived LEVEL [--question N] [--notes TEXT]` | Attach perceived difficulty to an existing answer without changing the score. Appends to `calibration.jsonl`. |
| `suggest` | — | Return the domain with the largest weighted coverage deficit, plus `avoid_topics` and `historical_topics`. |
| `asked` | `[--exam CODE] [--scope session\|history]` | List already-used topic slugs for the current session or full history. |
| `progress` | — | Print a learner-facing progress block (score, domain, streak). |
| `debug` | `on\|off` | Toggle the 12-item quality-gate block before hard/exam-level questions. |
| `end` | `[--output-dir PATH]` | Close the session, write to `sessions_archive.json`, return the final report JSON. |
| `reset` | — | Discard the current session. History and calibration are kept. |

**`grade` adaptive signals:**

| Signal | Condition | Agent action |
|---|---|---|
| `offer_increase_difficulty` | 3 consecutive correct | Offer to move up one difficulty level |
| `offer_concept_explanation` | 2 consecutive errors in same domain | Offer a brief concept explanation |
| `show_progress_summary` | Every 5 questions | Emit the progress block |
| `session_complete` | `question_number >= total_planned` | Offer to end the session |

**Per-question timer flow:**

```
1. session.py pending-set --payload '...'   → persist the question
2. session.py timer-start                   → record display timestamp
3. [show the question to the learner]
4. [learner submits answer]
5. session.py grade --response A            → elapsed auto-computed from timer-start
                                              (or pass --elapsed-seconds N to override)
```

Each answer record stores `elapsed_seconds`. The `end` command aggregates
`total_seconds`, `avg_seconds_per_question`, and per-domain timing in the final report.

#### Architecture Challenge Mode commands

| Command | Arguments | Description |
|---|---|---|
| `design-start` | `--payload JSON --difficulty LEVEL` | Persist a grounded challenge before showing it. Payload: `domain`, `topic`, `scenario`, `requirements` (`[{id, label, weight}]`), `curveball` (`{label, added_requirement: {id, label, weight}}`), `grounding`. Weights are normalised to 100 internally. |
| `design-pending` | — | Return active challenge state. Curveball is hidden (`curveball_hidden: true`) until the initial phase is graded. |
| `design-grade` | `--phase initial\|adapted --scores JSON [--elapsed-seconds N]` | Record rubric scores and advance the phase. `--scores` is `[{id, status}]` where `status` is `satisfied`, `partial`, or `missed`. Returns `signal: curveball_revealed` after initial, `signal: challenge_complete` after adapted. |
| `design-clear` | — | Discard the active challenge without grading. |

**Scoring:** `satisfied` = full weight, `partial` = 50% of weight, `missed` = 0. Weights are normalised to sum to 100 per phase. The adapted phase merges original requirements with the curveball's added requirement and renormalises.

---

### resolve_exam.py

`scripts/resolve_exam.py <CODE>` validates an exam code against the local catalog.

| Return status | Meaning | Agent action |
|---|---|---|
| `local_catalog_match` | Code found in local cache | Use enriched metadata; verify against live guide |
| `needs_online_verification` | Code absent from local cache | Search official index; may be a newly launched exam |
| `known_retired` | Code is superseded or retired | Explain to user; do not proceed |
| `malformed` | Empty input | Ask user for the exact code; never autocorrect |

The local catalog is a convenience cache, not an allowlist. Exit code 0 for matches and
online-verification candidates; exit code 1 for retired and malformed codes.

```bash
python3 scripts/resolve_exam.py SAA-C03   # check a single code
python3 scripts/resolve_exam.py --list    # list all locally cached exams
```

---

### export_report.py

`scripts/export_report.py` generates a full markdown exam report from a completed session.

```bash
python3 scripts/export_report.py                          # latest session
python3 scripts/export_report.py --index 2               # 3rd session (0-based)
python3 scripts/export_report.py --output-dir ./reports  # custom output root
python3 scripts/export_report.py --stdout                # print to stdout instead of file
```

Output file: `<output-dir>/ExamResults/<EXAM_CODE>/<EXAM_CODE>_<YYYYMMDD_HHMMSS>.md`

**Report contents:**
- Summary card: exam, dates, score, scaled score (100–1000), pass/fail verdict
- Domain performance table with ASCII progress bars, accuracy %, and average time per question
- Per-question log: domain, topic, result, difficulty, elapsed time
- Recommended review: weakest domains in priority order
- Topics covered this session

**Scaled score formula:** `100 + (raw_pct / 100) × 900`, rounded to integer.

**Passing thresholds used:**

| Exams | Threshold |
|---|---|
| CLF-C02, AIF-C01 | 700 / 1000 |
| SAA-C03, DVA-C02, SOA-C03, DEA-C01, MLA-C01 | 720 / 1000 |
| SAP-C02, DOP-C02, AIP-C01, ANS-C01, SCS-C02 | 750 / 1000 |
| All others | 720 / 1000 (AWS default) |

---

## File structure

```
zekai-aws-certifications/
├── plugin.json                                    # Power manifest (Agent Plugins v1.0.0)
├── mcp.json                                       # AWS Documentation MCP server config
├── README.md                                      # Main documentation (Portuguese)
├── README.en.md                                   # This file (English)
└── skills/
    └── zekai-aws-certifications/
        ├── SKILL.md                               # Main skill: all modes, rules, startup sequence
        ├── scripts/
        │   ├── session.py                         # Session state engine (quiz + architecture challenge)
        │   ├── resolve_exam.py                    # Exam code validator and metadata cache
        │   └── export_report.py                   # Markdown report generator
        ├── references/
        │   ├── session-workflow.md                # Interactive Quiz Mode: exact command order
        │   ├── question-breakdown.md              # Question Breakdown Mode: four-step process
        │   ├── architecture-challenge.md          # Architecture Challenge Mode: full workflow
        │   ├── documentation-grounding.md         # How to verify AWS facts before generating content
        │   ├── distractor-engineering.md          # How to build hard/exam-level distractors
        │   ├── explanation-template.md            # Templates for summaries, comparisons, flashcards
        │   ├── mcp-retrieval.md                   # MCP tool discovery, retry ladder, fallbacks
        │   ├── exam-guides.md                     # Official exam guides index URL and structure
        │   ├── aws-service-by-exam.md             # Fallback service-to-exam index
        │   └── exams/
        │       ├── aif-c01.md                     # Study map: AWS AI Practitioner
        │       ├── aip-c01.md                     # Study map: Generative AI Developer Professional
        │       ├── ans-c01.md                     # Study map: Advanced Networking Specialty
        │       ├── clf-c02.md                     # Study map: Cloud Practitioner
        │       ├── dea-c01.md                     # Study map: Data Engineer Associate
        │       ├── dop-c02.md                     # Study map: DevOps Engineer Professional
        │       ├── dva-c02.md                     # Study map: Developer Associate
        │       ├── mla-c01.md                     # Study map: Machine Learning Engineer Associate
        │       ├── saa-c03.md                     # Study map: Solutions Architect Associate
        │       ├── sap-c02.md                     # Study map: Solutions Architect Professional
        │       ├── scs-c02.md                     # Study map: Security Specialty
        │       └── soa-c03.md                     # Study map: CloudOps Engineer Associate
        └── assets/
            └── question-output-template.md        # Output templates for all modes and question types
```

---

## Configuration

The MCP server is configured in `mcp.json` at the power root:

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "aws-docs": {
      "type": "stdio",
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

**State directory:** defaults to `~/.zekai`. Override with the environment variable
`ZEKAI_STATE_DIR` to use a different path (e.g., a project-specific directory).

---

## Recommended models

| Mode | Recommended model | Why |
|---|---|---|
| Interactive Quiz Mode | Claude Sonnet or Opus | Sonnet handles most questions well; use Opus for exam-level difficulty where evaluation accuracy matters most |
| Architecture Challenge Mode | Claude Opus | Multi-requirement evaluation with weighted scoring requires strong attention to detail |
| Question Breakdown Mode | Claude Opus | Evaluates the learner's reasoning at each of the four steps |
| Study Mode | Claude Sonnet | Concept explanations and citations; no answer evaluation needed |

> **Note:** the models above are the ones I personally tested and validated as good fits for each mode. This doesn't mean they're the only compatible options, other models can be tested and evaluated, and contributions reporting results with other models are welcome.

---

## Troubleshooting

**The power doesn't seem to activate**
- Open a workspace folder. Kiro requires a folder open to activate powers.
- Check the Powers panel, confirm the power is listed as installed and enabled.
- Restart Kiro. Newly installed powers sometimes require a restart.

**`uv` / `uvx` command not found**
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```
```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Then restart Kiro so it picks up the new PATH.

**MCP server fails to connect**
```bash
uv --version                                          # verify uv is installed
uvx awslabs.aws-documentation-mcp-server@latest --help  # test the server directly
```
Open Kiro's command palette and search for "MCP" to check server status.

**Session state seems lost**
State lives in `~/.zekai/session.json`. Check:
```bash
python3 scripts/session.py status
```
If the session is inactive, start a new one. History and calibration in `history.json`
and `calibration.jsonl` are preserved across resets.

**Architecture challenge curveball revealed too early**
The agent must call `design-grade --phase initial` before the curveball is accessible.
If the curveball appears before grading, run `design-clear` and start a fresh challenge.

**Exam code not recognised**
- The local catalog is a convenience cache. If your code returns `needs_online_verification`,
  the agent will search the live official index, this is normal for newly launched exams.
- Never autocorrect a code (e.g., AIF-C01 and AIP-C01 are different exams).

**Kiro seems to have forgotten which exam I'm studying for**
This can happen after very long sessions. Say your exam code again
(e.g., "I'm studying for SAA-C03") and the agent will re-establish context.

---

## Disclaimer

This power is an independent study aid. It is not an official AWS Certification product
and is not affiliated with, endorsed by, or sponsored by Amazon Web Services or the AWS
Certification program. Practice questions are generated dynamically by the AI model
based on public AWS documentation, they do not come from official AWS question banks.
Passing a practice session does not predict actual exam results.

Always verify critical details against official AWS documentation. Use this power
alongside official exam prep resources (AWS Skill Builder, exam guides, whitepapers),
not as your sole study source.
