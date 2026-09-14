# Question Output Templates

Output templates for all question types and modes. Use the template matching the
active mode and question type.

## How to read this file

- All labels below are written in **English**. This is the canonical template
  language. Translate every label to the language the user is writing in
  (Core rule 1) — a user writing in Portuguese must see "Resposta correta", not
  "Correct answer". English is the baseline precisely so translation always goes
  in one predictable direction.
- `{{placeholder}}` markers are slots to fill. Never emit a `{{...}}` marker literally.
- Lines starting with `WITHHELD:` are instructions to you, never rendered to the user.
- Omit a section entirely rather than emitting it with empty or filler content.
- **Options must always render as a markdown list, one per line** — use `- **A.** {{option_a}}`
  exactly as shown in the templates below. Never join options into a single paragraph or
  separate them with plain line breaks; letters like "A." are not valid ordered-list syntax
  in markdown, so without the leading `- ` bullet, renderers may collapse the options onto
  one line.

---

## Study Mode — Single-choice question

### Question {{number}} — {{domain}}

**Exam:** {{exam_name}}
**Code:** {{exam_code}}
**Level:** {{difficulty}}
**Domain:** {{domain}}
**Topic:** {{topic}}
**Guide reference:** {{exam_guide_reference}}

{{question}}

- **A.** {{option_a}}
- **B.** {{option_b}}
- **C.** {{option_c}}
- **D.** {{option_d}}

**Correct answer:** {{correct_answer}}

**Why it's correct:**
{{correct_explanation}}

**Why the others are wrong:**
- **A:** {{option_a_explanation}}
- **B:** {{option_b_explanation}}
- **C:** {{option_c_explanation}}
- **D:** {{option_d_explanation}}

**Why this question is difficult:**
{{why_question_is_difficult}}

**Exam trap:**
{{exam_trap}}

**Revision summary:**
{{summary}}

**Recommended AWS documentation:**
{{recommended_docs}}

---

## Interactive Quiz Mode — Before user answers (single-choice)

### Question {{number}} — {{domain}}

**Exam:** {{exam_name}}
**Code:** {{exam_code}}
**Level:** {{difficulty}}
**Domain:** {{domain}}
**Topic:** {{topic}}

{{question}}

- **A.** {{option_a}}
- **B.** {{option_b}}
- **C.** {{option_c}}
- **D.** {{option_d}}

Answer with only **A, B, C, or D**.

WITHHELD: emit nothing beyond this point — no correct answer, no explanation, no
WITHHELD: "why difficult", no trap, no summary, no docs, no hints. See Core rule 5.

---

## Interactive Quiz Mode — After user answers (single-choice)

## Result

**Your answer:** {{user_answer}}
**Correct answer:** {{correct_answer}}
**Status:** {{Correct | Incorrect}}
**Time:** {{elapsed_seconds}}s

## Verdict

WITHHELD: pick the one branch that applies; do not render the other.
- If correct: Correct. You got it right because {{short_reason}}.
- If incorrect: Incorrect. Option **{{user_answer}}** looks plausible, but it's wrong because {{why_user_answer_is_wrong}}.

## Why the correct option is the best answer

{{correct_explanation_full}}

## Why the others are wrong

- **A:** Looks plausible because {{why_tempting}}. However, it fails because {{specific_failure}}.
- **B:** {{option_b_explanation}}
- **C:** {{option_c_explanation}}
- **D:** {{option_d_explanation}}

## Why this question is difficult

{{why_question_is_difficult}}

## Official AWS references

{{aws_docs}}

## Exam trap

{{exam_trap}}

## Revision summary

{{summary}}

## Next step

Want me to generate the next question?

---

## Study Mode — Multiple-response question

### Question {{number}} — {{domain}}

**Exam:** {{exam_name}}
**Code:** {{exam_code}}
**Level:** {{difficulty}}
**Type:** Multiple response
**Number of correct answers:** {{number_of_correct_answers}}
**Domain:** {{domain}}
**Topic:** {{topic}}
**Guide reference:** {{exam_guide_reference}}

{{question}}

- **A.** {{option_a}}
- **B.** {{option_b}}
- **C.** {{option_c}}
- **D.** {{option_d}}
- **E.** {{option_e}}

**Correct answers:** {{correct_letters}}

**Why they're correct:**
- **{{letter_1}}:** {{explanation}}
- **{{letter_2}}:** {{explanation}}

**Why the others are wrong:**
- **A:** {{option_a_explanation}}
- **B:** {{option_b_explanation}}
- **C:** {{option_c_explanation}}
- **D:** {{option_d_explanation}}
- **E:** {{option_e_explanation}}

**Why this question is difficult:**
{{why_question_is_difficult}}

**Exam trap:**
{{exam_trap}}

**Revision summary:**
{{summary}}

**Recommended AWS documentation:**
{{recommended_docs}}

---

## Interactive Quiz Mode — Before user answers (multiple-response)

### Question {{number}} — {{domain}}

**Exam:** {{exam_name}}
**Code:** {{exam_code}}
**Level:** {{difficulty}}
**Type:** Multiple response
**Number of correct answers:** {{number_of_correct_answers}}
**Domain:** {{domain}}
**Topic:** {{topic}}

{{question}}

- **A.** {{option_a}}
- **B.** {{option_b}}
- **C.** {{option_c}}
- **D.** {{option_d}}
- **E.** {{option_e}}
- **F.** {{option_f}}

WITHHELD: include the "F." line only for select-three (6 options); omit it entirely for select-two.

Answer with **{{number_of_correct_answers}} options**, for example: **A, C** or **A, C, E**.

WITHHELD: emit nothing beyond this point — no correct answers, no explanations, no
WITHHELD: "why difficult", no trap, no summary, no docs, no hints. See Core rule 5.

---

## Interactive Quiz Mode — After user answers (multiple-response)

## Result

**Your answer:** {{user_answers}}
**Correct answers:** {{correct_letters}}
**Status:** {{Correct | Partially correct | Incorrect}}
**Time:** {{elapsed_seconds}}s

## Verdict

WITHHELD: pick the one branch that applies; do not render the others.
- If the letter count is wrong: You selected {{n}} option(s), but this question requires {{required}}. Please resend your answer with {{required}} options, for example: **A, C** or **A, C, E**.
  WITHHELD: stop here. Do not reveal the correct set, the status, or any explanation.
- If fully correct: Correct. You selected all the correct options.
- If partial: Partially correct. You got {{correct_selected}} right, but missed {{missing_letters}}. See the explanation below.
- If incorrect: Incorrect. See the explanation below to understand why each option is right or wrong.

## Why the correct options are the best answers

- **{{correct_letter_1}}:** {{explanation}}
- **{{correct_letter_2}}:** {{explanation}}

## Why the others are wrong

- **A:** {{option_a_explanation}}
- **B:** {{option_b_explanation}}
- **C:** {{option_c_explanation}}
- **D:** {{option_d_explanation}}
- **E:** {{option_e_explanation}}

## Why this question is difficult

{{why_question_is_difficult}}

## Official AWS references

{{aws_docs}}

## Exam trap

{{exam_trap}}

## Revision summary

{{summary}}

## Next step

Want me to generate the next question?

---

## Session progress summary

Show when `scripts/session.py grade` returns the `show_progress_summary` signal, or on request.

**Progress:** Question {{n}} | Correct: {{correct}} | Incorrect: {{incorrect}} | Current domain: {{domain}}

---

## Adaptive difficulty prompts

Emit only when the corresponding signal is returned by `scripts/session.py grade`.

On `offer_increase_difficulty`:

> You've gotten {{streak}} in a row correct. Want to move up to **{{to}}** level?

On `offer_concept_explanation`:

> You've missed {{n}} in a row on **{{domain}}**. Want a quick concept explanation before the next question?

---

## End-of-session summary

## Final Result

**Score:** {{correct}}/{{total}} ({{percent}}%)

**Performance by domain:**
| Domain | Questions | Correct | Accuracy |
|---|---|---|---|
| {{domain}} | {{asked}} | {{correct}} | {{accuracy_pct}}% |

**Domains with errors:**
{{domains_with_errors}}

**Review recommendation:**
{{review_recommendation}}

**Suggested AWS documentation:**
{{aws_docs_for_weak_areas}}

WITHHELD: populate all fields above from the JSON returned by `scripts/session.py end`.
WITHHELD: never compute the score by re-reading the transcript.

---

## Study Mode — Multiple-response select-three

### Question {{number}} — {{domain}}

**Exam:** {{exam_name}}
**Code:** {{exam_code}}
**Level:** {{difficulty}}
**Type:** Multiple response (select **3**)
**Domain:** {{domain}}
**Topic:** {{topic}}
**Guide reference:** {{exam_guide_reference}}

{{question}}

- **A.** {{option_a}}
- **B.** {{option_b}}
- **C.** {{option_c}}
- **D.** {{option_d}}
- **E.** {{option_e}}
- **F.** {{option_f}}

**Correct answers:** {{correct_letters}}

**Why they're correct:**
- **{{letter_1}}:** {{explanation}}
- **{{letter_2}}:** {{explanation}}
- **{{letter_3}}:** {{explanation}}

**Why the others are wrong:**
- **A:** {{option_a_explanation}}
- **B:** {{option_b_explanation}}
- **C:** {{option_c_explanation}}
- **D:** {{option_d_explanation}}
- **E:** {{option_e_explanation}}
- **F:** {{option_f_explanation}}

**Why this question is difficult:**
{{why_question_is_difficult}}

**Exam trap:**
{{exam_trap}}

**Revision summary:**
{{summary}}

**Recommended AWS documentation:**
{{recommended_docs}}

---

## Markdown report offer

Show immediately after rendering the end-of-session summary, before the next prompt.

> Want me to save a complete markdown report?
> It includes: scaled score, average time per question, domain performance with a progress bar, a log of every question, and review recommendations.
>
> If so, let me know where to save it (or leave it blank to use the current directory).

WITHHELD: if the user confirms, run:
WITHHELD: `python3 scripts/export_report.py [--output-dir <path>]`
WITHHELD: and report the saved file path.

---

## End-of-session summary (updated with timing)

## Final Result

**Exam:** {{exam}} | **Difficulty:** {{difficulty}}

**Score:** {{correct}}/{{total}} ({{percent}}%) — Estimated scaled score: **{{scaled_score}}/1000**
**Verdict:** {{PASSED ✅ | NEEDS MORE STUDY ❌}} (threshold: {{passing_score}}/1000)

**Total time:** {{total_time}} | **Average time per question:** {{avg_time}}

**Performance by domain:**
| Domain | Questions | Correct | Accuracy | Avg time |
|---|---|---|---|---|
| {{domain}} | {{asked}} | {{correct}} | {{accuracy_pct}}% | {{avg_seconds}}s |

**Domains with the most difficulty:**
{{domains_with_errors}}

**Review recommendation:**
{{review_recommendation}}

**Suggested AWS documentation:**
{{aws_docs_for_weak_areas}}

WITHHELD: populate all fields above from the JSON returned by `scripts/session.py end`.
WITHHELD: compute scaled_score as: 100 + (score_pct / 100) * 900, rounded to integer.
WITHHELD: never compute the score by re-reading the transcript.

---

## Architecture Challenge Mode — Initial Phase (present to learner)

### 🏗️ Architecture Challenge — {{domain}}

**Exam:** {{exam_name}} ({{exam_code}})
**Level:** {{difficulty}}
**Domain:** {{domain}}

---

#### Scenario

{{scenario}}

---

#### Requirements your architecture must meet

{{#each requirements}}
- **{{label}}**
{{/each}}

---

> Propose your architecture in free text. Name the AWS services, explain how each
> one satisfies the requirements above, and justify your design choices.
>
> There are no predefined options — the solution is yours.

WITHHELD: do not show weights, do not hint at the curveball, do not suggest services.
WITHHELD: wait for the learner's full proposal before calling design-grade.

---

## Architecture Challenge Mode — Initial Phase Feedback (after design-grade initial)

### Result — Initial Phase

**Initial score:** {{initial_score}}/100 ({{initial_pct}}%)
**Time:** {{initial_elapsed}}s

#### Evaluation by requirement

| Requirement | Status | Weight | Points |
|-----------|:------:|-----:|-------:|
{{#each per_req}}
| {{label}} | {{status_icon}} {{status}} | {{weight}}% | {{points_earned}} |
{{/each}}

WITHHELD: status_icon: satisfied → ✅ / partial → ⚠️ / missed → ❌

#### Detailed analysis

{{#each per_req}}
**{{label}}** — {{status_icon}} {{status}}
{{explanation_3_sentences}}

{{/each}}

---

### ⚡ Client update

> {{curveball_label}}

**New requirement added:** {{curveball_added_requirement_label}}

How do you adapt your architecture to meet this change?

WITHHELD: present the curveball as a client update, not as a test announcement.
WITHHELD: do not explain what needs to change. Wait for the learner's amended proposal.
WITHHELD: the adapted_timer_started_at was already set by design-grade; no extra timer call needed.

---

## Architecture Challenge Mode — Final Report (after design-grade adapted)

### 📊 Final Report — Architecture Challenge

**Exam:** {{exam_name}} ({{exam_code}}) | **Domain:** {{domain}} | **Level:** {{difficulty}}

---

#### Consolidated scoreboard

| Phase | Score | % |
|------|----------:|--:|
| Initial | {{initial_score}}/100 | {{initial_pct}}% |
| Adapted (with curveball) | {{adapted_score}}/100 | {{adapted_pct}}% |
| **Combined** | — | **{{combined_pct}}%** |

**Verdict:** {{verdict_icon}} {{verdict_label}}

WITHHELD: verdict_icon / verdict_label:
WITHHELD:   combined_pct >= 80 → ✅ Excellent — solid architecture
WITHHELD:   combined_pct >= 70 → ✅ Pass — good grasp of the requirements
WITHHELD:   combined_pct >= 50 → ⚠️ Partial — review the missed requirements
WITHHELD:   combined_pct <  50 → ❌ Needs work — revisit the recommended documentation

---

#### Requirements — Initial Phase

| Requirement | Status | Weight | Points |
|-----------|:------:|-----:|-------:|
{{#each initial_per_req}}
| {{label}} | {{status_icon}} {{status}} | {{weight}}% | {{points_earned}} |
{{/each}}

#### Requirements — Adapted Phase (includes curveball)

| Requirement | Status | Renormalised weight | Points |
|-----------|:------:|-------------:|-------:|
{{#each adapted_per_req}}
| {{label}} | {{status_icon}} {{status}} | {{weight}}% | {{points_earned}} |
{{/each}}

---

#### Architectural principle demonstrated

{{architectural_principle_paragraph}}

---

#### What you got right

{{strengths_bullet_list}}

#### Areas to reinforce

{{improvement_bullet_list}}

---

#### Exam trap

**{{exam_trap_label}}:** {{exam_trap_explanation}}

---

#### Recommended AWS documentation

{{#each recommended_docs}}
- [{{title}}]({{url}})
{{/each}}

WITHHELD: populate initial_per_req and adapted_per_req from the JSON returned by design-grade.
WITHHELD: combined_pct comes directly from the design-grade adapted response field "combined_pct".
WITHHELD: if combined_pct < 70, after rendering this report offer a concept explanation:
WITHHELD:   > "Want me to explain the core concept behind this challenge before the next one?"

---

## Architecture Challenge Mode — Resume banner (design-pending returns active challenge)

### 🏗️ Resuming challenge — {{domain}}

You have an architecture challenge in progress in the **{{phase}}** phase.

{{#if phase == "initial"}}
**Scenario:** {{scenario_first_sentence}}…

Your architecture proposal is pending. Send it whenever you're ready.
{{/if}}

{{#if phase == "adapted"}}
**Active curveball:** {{curveball_label}}

Your adapted proposal is pending. Send it whenever you're ready.
{{/if}}

WITHHELD: use design-pending output to fill phase, scenario, and curveball fields.
WITHHELD: do not call design-start again if has_active_challenge is true.

---

## Architecture Challenge Mode — Progress block (mid-session, on request)

**Challenges:** {{challenges_completed}} completed | **Average combined:** {{avg_combined_pct}}% | **Current phase:** {{phase}}

WITHHELD: challenges_completed = count of answers with type == "architecture_challenge" from session.py status.
WITHHELD: avg_combined_pct = mean of all adapted_pct values for completed challenges this session.
