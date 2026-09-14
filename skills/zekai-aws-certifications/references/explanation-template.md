# Explanation Template — Supplementary Structures

> Core rules, modes, difficulty calibration, and the quality gate live in `SKILL.md`.
> Distractor construction lives in `references/distractor-engineering.md`.
> Standard question output formats live in `assets/question-output-template.md`.
> This file holds only the supplementary templates not covered by those: domain summaries,
> service comparisons, flashcards, and study plans.
>
> Section labels below are written in **English** as the canonical baseline —
> translate them to the user's language per Core rule 1.

---

## Domain summary

When the user asks for a summary of an exam domain:

## {{exam_code}} — {{domain_name}}

### What this domain covers

Explain the domain in plain language.

### Key services and concepts

List relevant services and concepts.

### What you need to know for the exam

Practical bullets covering:
- service behavior and limits
- common architectures and integration patterns
- security, cost, performance trade-offs
- operational overhead and troubleshooting

### Comparisons that show up often

Use comparison tables. Examples:
- SQS vs SNS vs EventBridge
- NAT Gateway vs VPC Endpoint
- RDS Multi-AZ vs Read Replica
- Security Group vs NACL
- KMS key policy vs IAM policy
- DynamoDB Query vs Scan
- CloudFront vs Global Accelerator
- Interface Endpoint vs Gateway Endpoint
- Direct Connect Gateway vs Transit Gateway
- GuardDuty vs Security Hub vs Detective vs Config
- Step Functions Standard vs Express

### Common exam traps

List most common exam traps for this domain.

### Final mini-summary

5-8 short revision bullets.

---

## Service comparison

When the user asks to compare AWS services:

## Comparison — {{service_a}} vs {{service_b}}

| Criterion | {{service_a}} | {{service_b}} |
|---|---|---|
| Primary use case | | |
| Operational model | | |
| Scalability | | |
| Security | | |
| Resilience | | |
| Performance | | |
| Cost | | |
| When to choose | | |
| When to avoid | | |
| Exam trap | | |

### How the exam usually tests this

Explain the exam angle.

### Rule of thumb

Simple decision rule for the learner.

---

## Flashcard

## Flashcard {{number}}

**Front:**
{{question_or_concept}}

**Back:**
{{answer}}

**Exam trap:**
{{exam_trap}}

**Summary:**
{{short_revision_note}}

---

## Study plan

## Study plan — {{exam_code}}

### Goal

Goal of the plan.

### Assumptions

- available study time
- current level
- target date if provided
- preferred learning style if provided

### Week {{number}} — {{theme}}

- domains to cover
- services to study
- documentation topics
- hands-on labs
- practice questions (quantity and difficulty)
- review checkpoint

### Mock exams and review

- official practice question sets
- official practice exams
- weak-area review strategy
- flashcard usage
- hands-on reinforcement