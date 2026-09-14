# Architecture Challenge Mode

Load this file on every Architecture Challenge Mode turn.

## Purpose

Architecture Challenge Mode trains the learner to **design first, then defend**.
Instead of picking between pre-built options (as in Interactive Quiz Mode), the
learner proposes a free-form AWS architecture that satisfies a realistic business
scenario. The agent then grades the proposal against a weighted rubric of explicit
requirements, reveals a sudden constraint change ("curveball"), and asks the learner
to adapt — all grounded in official AWS documentation.

The cognitive goal: build the muscle of translating ambiguous business requirements
into defensible architectural decisions, not just recognising the correct answer
among four options.

## Difference from other modes

| | Interactive Quiz Mode | Question Breakdown Mode | Architecture Challenge Mode |
|---|---|---|---|
| Answer format | Letter (A–D) | Free text per step | Free-form architecture proposal |
| Agent role | Withholds answer | Reveals analysis step-by-step | Scores proposal against rubric |
| Core skill trained | Pattern recognition, elimination | Meta-skill: how to read a question | Design reasoning, requirement mapping |
| Session state | `pending-set` / `grade` | `pending-set` / `grade` (agent-generated) | `design-start` / `design-grade` |
| Anti-repetition | `avoid_topics` + `historical_topics` | Same | Same (`topic` recorded in history) |

## Activation signals

Match on intent, not exact wording:

- "modo desafio", "desafio de arquitetura", "me dá um desafio"
- "architecture challenge", "design challenge", "projete uma arquitetura"
- "proponha uma solução", "como você arquitetaria isso"
- "quero treinar design", "me dá um cenário aberto"
- Any message asking the learner to propose (not pick) a solution

Do **not** activate on "gere questões", "simulado", or "quiz" — those route to
Interactive Quiz Mode.

## Core constraints for this mode

1. **Retrieval before feedback.** The learner always proposes first. Never provide
   hints, partial frameworks, or "consider X" prompts before the proposal is submitted.
2. **Grounded rubric.** Every requirement in the rubric must be anchored to an official
   AWS documentation source. Run `references/documentation-grounding.md` before calling
   `design-start`.
3. **Curveball is secret.** The curveball is never revealed — not even as "there will be
   a twist" — until `design-grade --phase initial` has been called and succeeded.
4. **Weighted scoring.** Requirements carry weights (summing to 100). Partial credit
   (0.5×) is awarded when the learner's proposal addresses the requirement but
   incompletely or with a caveat. Never award partial credit speculatively.
5. **Anti-repetition.** Run `session.py suggest` before constructing a challenge. Never
   reuse a topic from `avoid_topics`; avoid `historical_topics` unless the domain is
   exhausted. Pass a stable `--topic` slug that reflects the core service decision
   being tested, not the scenario cover story.
6. **One challenge at a time.** If `design-pending` returns `has_active_challenge: true`,
   reshow the existing challenge; do not call `design-start` again.

## Startup sequence

1. Check for a resume intent ("continuar desafio", "retomar", "back to the challenge"):
   run `python3 scripts/session.py design-pending`. If `has_active_challenge: true`,
   reshow the scenario and requirements; continue from the stored phase.

2. If no active challenge, verify an exam session is running (`session.py status`).
   If not, start one per the standard startup sequence in SKILL.md before proceeding.

3. Run `python3 scripts/session.py suggest` to choose the domain and check
   `avoid_topics` / `historical_topics`.

4. Construct the challenge: pick a scenario, write 3–5 requirements, design the
   curveball, and ground all factual premises via `references/documentation-grounding.md`.

5. Call `design-start` to persist the challenge before presenting it.

6. Present the challenge to the learner using the template in
   `assets/question-output-template.md` (section: Architecture Challenge — Initial Phase).

## Challenge construction

### Scenario

Write a realistic business scenario in 3–6 sentences that:
- Names an industry or company archetype (bank, e-commerce, healthcare startup…)
- States at least one hard technical constraint (RTO/RPO, throughput, latency, compliance)
- Contains at least one business constraint (budget ceiling, team size, time-to-market)
- Does **not** name the correct AWS services — the learner must derive them

Avoid: overly academic setups, trivial single-service scenarios, scenery that contains
the answer (e.g., "they want to use Aurora Global Database").

### Requirements

Define 3–5 requirements. Each must:
- Be independently verifiable (the learner's proposal either satisfies it or doesn't)
- Be anchored to a documented AWS capability or Well-Architected principle
- Carry a weight proportional to its criticality to the scenario

Typical weight splits:
- 3 requirements: 40 / 35 / 25
- 4 requirements: 30 / 25 / 25 / 20
- 5 requirements: 25 / 20 / 20 / 20 / 15

Do not use equal weights — that signals to the learner that all requirements matter
equally, which is never true in real architectures.

### Curveball

The curveball is a constraint change or a new business event that invalidates or
complicates part of the initial design. It must:
- Be plausible given the scenario (no "now the client also runs a moon base")
- Require the learner to add, replace, or reconfigure at least one service
- Introduce exactly one new requirement with a weight of 15–30 (will be merged into
  the adapted scoring, then renormalised by `design-grade`)

Good curveball patterns:
- Scale jump: traffic volume × 10, new region required, new compliance scope
- Cost constraint tightened: "budget cut by 40%, must reduce reserved capacity"
- New integration required: "partner now sends data via a different protocol"
- Availability target raised: SLA moves from 99.9% → 99.99%
- Data residency: "EU customers' data must stay in the eu-west-1 region"

Bad curveball patterns (avoid):
- Requires a completely different architecture (too disruptive for a single adaptation)
- Only cosmetic (rename a tag, change a log retention period)
- Hints at the correct initial answer ("actually they want RDS, not Aurora")

### Difficulty calibration

| Level | Scenario complexity | Requirements | Curveball |
|---|---|---|---|
| **easy** | Single domain, 1–2 services | 3, clear constraints | Incremental change |
| **medium** | 2–3 services, 1 integration | 4, mix of explicit/implicit | Adds new integration |
| **hard** | Multi-service, cross-account/region | 4–5, some implicit | Changes a core constraint |
| **exam-level** | Multi-domain, compliance + cost + HA | 5, explicit trade-offs required | Triggers architecture trade-off |

## Grading rubric — how to score each requirement

After the learner submits a proposal, evaluate it requirement by requirement
**before** calling `design-grade`. Apply these criteria:

| Status | Criterion |
|---|---|
| `satisfied` | Proposal explicitly names the correct service/pattern AND explains why it satisfies the requirement |
| `partial` | Correct general direction (right category of service) but wrong specific choice, OR correct service without justification, OR correct service that partially satisfies the requirement |
| `missed` | Proposal ignores the requirement, names a clearly wrong service, or names the right service for the wrong reason |

**Be consistent.** Do not award `satisfied` for vague answers like "use a managed
database" when the requirement is "RPO < 1 minute cross-region" — that demands
Aurora Global Database or equivalent.

**Never round up.** If genuinely between `partial` and `satisfied`, default to `partial`.

## Phase flow

### Phase: initial

1. The learner receives the scenario and the requirement list (no weights shown,
   no curveball).
2. The learner proposes a complete architecture in free text.
3. The agent evaluates the proposal against each requirement and calls:
   ```bash
   python3 scripts/session.py design-grade --phase initial \
     --scores '[{"id":"<req_id>","status":"satisfied|partial|missed"}, ...]'
   ```
4. `design-grade` returns `signal: curveball_revealed` and the curveball object.
5. The agent presents the initial phase feedback (scores, explanations) and then
   **immediately** reveals the curveball.

### Phase: adapted

1. The learner amends their architecture to handle the curveball.
2. The agent evaluates the amended proposal against all original requirements **plus**
   the curveball's added requirement (the script merges and renormalises automatically).
3. The agent calls:
   ```bash
   python3 scripts/session.py design-grade --phase adapted \
     --scores '[{"id":"<req_id>","status":"..."}, ..., {"id":"<curveball_req_id>","status":"..."}]'
   ```
4. `design-grade` returns `signal: challenge_complete`, `initial_result`,
   `adapted_result`, and `combined_pct`.
5. The agent renders the full final report (see template).

## Feedback quality guidelines

### Initial phase feedback

For each requirement, provide:
- The score status and points earned
- If `missed` or `partial`: the correct service/pattern and the official doc that confirms it
- If `satisfied`: a one-sentence reinforcement of why the choice is correct
- One sentence on the near-miss distractor (why the alternative the learner may have
  considered would have failed)

Keep individual requirement explanations to 3 sentences maximum. The learner will read
all of them — density matters.

### Curveball reveal

Present the curveball as a client update, not as a test announcement:
> "The client just informed us that..." / "Update from the client: ..."

Then immediately ask: "How do you adapt your architecture to meet this new requirement?"

WITHHELD: translate both lines to the user's language per Core rule 1 before rendering them.

Do not explain what needs to change — that defeats the purpose.

### Final report

After the adapted phase is graded:
1. Present the combined score with a verdict (use the template).
2. For each requirement: final status, points, and a one-sentence explanation.
3. One paragraph on the architectural principle demonstrated by the challenge.
4. Strengths to carry forward (what the learner did well in either phase).
5. One "exam trap" — the common exam mistake this scenario is designed to catch.
6. Official documentation links for the 1–2 most important services tested.
7. If `combined_pct < 70`: offer a follow-up concept explanation before the next challenge.

## Anti-repetition and domain coverage

- Run `suggest` before constructing every challenge, not just the first one.
- The topic slug must reflect the service decision being tested:
  `"aurora-global-database-vs-rds-multi-az"`, not `"bank-transaction-system"`.
- `design-grade` records the topic in `asked_topics` and `history.json` on completion.
- Cross-session deduplication works the same as in Interactive Quiz Mode —
  the topic key is normalised to lowercase-hyphenated by `session.py`.

## Calibration feedback

After the final report, ask how the challenge felt:
> "Did this challenge feel like the right level, easier, or harder than you expected?"

WITHHELD: translate this question to the user's language per Core rule 1 before rendering it.

Record with:
```bash
python3 scripts/session.py calibrate --perceived <level> --notes "<user's words>"
```

Never ask for calibration while a proposal is pending (before `design-grade` is called).

## Transition signals

| Learner says | Action |
|---|---|
| "próximo desafio", "mais um", "next challenge" | New challenge in Architecture Challenge Mode |
| "modo quiz", "quero responder questões" | Switch to Interactive Quiz Mode |
| "modo análise", "breakdown" | Switch to Question Breakdown Mode |
| "encerrar", "chega", "obrigado" | `session.py end`, render final report |
| "pula o curveball", "skip the twist" | Decline; explain that the adaptation phase is part of the mode. Offer to move to a new challenge instead |
| "me dá a resposta", "just tell me" | Offer Study Mode. Explain what the learner trades away |

## Error paths

**`design-start` returns `error: design_challenge_active`**
Run `design-pending` to reshow the existing challenge. Never start a new one.

**`design-grade` returns `error: incomplete_scores`**
One or more requirement ids were missing from `--scores`. List the missing ids, re-evaluate,
and call `design-grade` again with the complete set.

**`design-grade` returns `error: wrong_phase`**
The challenge advanced (or was cleared) since the last check. Run `design-pending` to
confirm the current phase before grading.

**Documentation MCP unavailable during challenge construction**
Apply the same rule as in Interactive Quiz Mode: do not call `design-start` or show
the challenge until all grounding records are `status: verified`. Retry on the next
user attempt.
