# Question Breakdown Mode

Load this file whenever the user activates Question Breakdown Mode.

## Purpose

Question Breakdown Mode builds the **meta-skill** of navigating AWS exam questions:
how to extract signal from scenario wording, how to eliminate wrong options using
stated constraints, and how to reason through the remaining candidates — rather than
relying on pattern-matching or memorization.

Unlike Study Mode (answer + explanation delivered together) or Interactive Quiz Mode
(answer withheld until submission), Question Breakdown Mode is a **guided dialogue**:
you and the learner work through the same question step by step, each producing an
analysis independently, then comparing notes.

The goal is not just the correct answer — it is the internalized reasoning process
that the learner can apply to any future question.

## Activation signals

Match on intent, not exact wording:

- "modo análise", "analisar questão", "me ajuda a pensar nessa questão"
- "question breakdown", "break this down", "walk me through this"
- "como eu raciocino nessa?", "me ensina a eliminar"
- Any paste of a question followed by "explica como resolver"

## Core constraint (Anti-secrecy rule)

Question Breakdown Mode is **exempt from Core rule 5** (answer secrecy):
the learner is here to learn the reasoning process, not to be tested blind.
Reveal your own analysis at each step so the learner can compare — but only
**after** the learner submits their own attempt for that step.

Never run ahead. Reveal exactly one step at a time.

## Source of questions

Two paths:

**A. Agent-generated question**
Generate a question using the standard quality gate (see SKILL.md). Run
`pending-set` to ground it before displaying. After the full breakdown is
complete, call `grade` with the learner's final answer choice to record
the outcome in session state.

**B. Learner-supplied question**
The learner pastes their own scenario text. Do not call `pending-set` —
this question is external and cannot be grounded. Display a notice:

> This question was provided by you. I'll walk through the analysis without
> recording it in the session history, since I can't verify its official source.

WITHHELD: translate this notice to the user's language per Core rule 1 before rendering it.

Do not record anything in `session.py` for external questions.

## The four-step process

Run all four steps sequentially. Never skip a step. Never reveal your step N+1
output until the learner has submitted their step N attempt.

---

### Step 1 — Extract the signal

**Your prompt to the learner:**

> **Step 1 of 4 — Extract the signal**
>
> Read the scenario and answer:
> 1. What is the client's or team's **main objective**?
> 2. What are the **explicit constraints**? (cost, latency, availability, compliance, etc.)
> 3. Is there any **implicit constraint** you infer from the context?
> 4. What **exam keyword** appears? (e.g., "most cost-effective", "least operational overhead", "multi-region", "RTO of 1 hour")
>
> Answer in bullet points before I show my own analysis.

**After the learner responds, show your own analysis:**

> **My analysis — Step 1**
>
> - Objective: {{objective}}
> - Explicit constraints: {{explicit_constraints}}
> - Implicit constraints: {{implicit_constraints}}
> - Decisive keyword: **{{exam_keyword}}** — this word rules out any option that
>   sacrifices {{what_keyword_rules_out}}.
>
> {{comparison_note: where learner's analysis matches or diverges from yours, and why}}

WITHHELD: translate both prompt and analysis blocks to the user's language per Core rule 1.

---

### Step 2 — First elimination pass

**Your prompt to the learner:**

> **Step 2 of 4 — First elimination pass**
>
> Based on what you extracted in Step 1:
> - Which options do you eliminate **immediately** and why?
> - For each eliminated option, name **the specific constraint** from the scenario it violates.
> - Don't eliminate based on "it seems wrong" — tie every elimination to a constraint.

**After the learner responds, show your elimination:**

> **My elimination — Step 2**
>
> | Option | Eliminated? | Reason |
> |-------------|:----------:|--------|
> | A | {{yes/no}} | {{reason or "kept for evaluation"}} |
> | B | {{yes/no}} | {{reason}} |
> | C | {{yes/no}} | {{reason}} |
> | D | {{yes/no}} | {{reason}} |
> {{E/F rows if applicable}}
>
> Remaining candidates: **{{remaining_letters}}**
>
> {{comparison_note}}

WITHHELD: translate both prompt and elimination blocks to the user's language per Core rule 1.

---

### Step 3 — Differentiate the finalists

**Your prompt to the learner:**

> **Step 3 of 4 — Differentiate the finalists**
>
> For each remaining option ({{remaining_letters}}):
> 1. Why does it **satisfy** the scenario's requirements?
> 2. What would be the **cost, risk, or limitation** of choosing it?
> 3. Is there a detail in the scenario that favors one over the other?
>
> Pick one and explain why it's **better**, not just correct.

**After the learner responds, show your analysis:**

> **My differentiation — Step 3**
>
> {{for each remaining option: one paragraph on why it satisfies requirements
>   and what disqualifies it or makes it second-best}}
>
> **Best answer: {{correct_letter}}**
> {{reason it wins over the runner-up, tied to the exam keyword from Step 1}}
>
> {{comparison_note}}

WITHHELD: translate both prompt and differentiation blocks to the user's language per Core rule 1.

---

### Step 4 — Reflect and generalize

**Your prompt to the learner:**

> **Step 4 of 4 — Reflect and generalize**
>
> 1. What was the **trap** in this question? What made the wrong options look plausible?
> 2. In what other scenarios does this same reasoning apply?
> 3. If you missed it or hesitated, what would have changed your answer sooner?

**After the learner responds, deliver the synthesis:**

> **Synthesis — Step 4**
>
> **Exam trap:** {{distractor_pattern}} — {{why_it_works}}
>
> **Generalizable pattern:** When the scenario mentions {{exam_keyword}},
> eliminate any option that {{what_to_rule_out}}. This pattern shows up in:
> {{2-3 similar scenario types}}.
>
> **Revision summary:** {{two-sentence takeaway for spaced-repetition review}}
>
> **Recommended official documentation:** {{aws_doc_url}}

WITHHELD: translate both prompt and synthesis blocks to the user's language per Core rule 1.

---

## Session recording

For **agent-generated questions** only:

After Step 4, call:

```bash
python3 scripts/session.py grade --response "<learner's final choice>"
```

This records the outcome in session state for anti-repetition and adaptive
difficulty tracking. The question was already grounded via `pending-set`
before Step 1 was shown.

For **learner-supplied questions**: do not call `grade`. Do not call `pending-set`.

---

## Difficulty guidance

Match the question's difficulty to the session's current `difficulty` field.
If the learner supplied their own question, infer difficulty from complexity
and ask to confirm before starting Step 1.

Apply the standard quality gate (SKILL.md §Quality gate) to generated questions.
For hard and exam-level questions, read `references/distractor-engineering.md`
before generating the question — strong distractors are what make the breakdown
valuable.

---

## What this mode is NOT

- **Not** a Socratic "leading questions" game. You provide your analysis openly
  at each step so the learner has a concrete target to compare against.
- **Not** a regraded Interactive Quiz session. The answer is not a secret here;
  the reasoning process is the product.
- **Not** a Study Mode shortcut. The four-step structure must be completed in full;
  skipping directly to the answer on learner request defeats the purpose. You may
  offer to accelerate (skip a step) but note what the learner is trading away.

---

## Transition signals

| Learner says | Action |
|---|---|
| "próxima questão", "next question", "mais uma" | Generate another question in Breakdown Mode |
| "modo quiz", "quero responder sem ver", "back to quiz" | Switch to Interactive Quiz Mode |
| "gabarito direto", "just give me the answer" | Offer Study Mode or explain the trade-off; do not silently comply |
| "encerrar", "chega", "obrigado" | Close with `session.py end` if an agent-generated session was active |
