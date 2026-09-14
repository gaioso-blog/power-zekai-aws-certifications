# AWS Certification Exam Guides

## Source of truth

Official exam guides index:
https://docs.aws.amazon.com/aws-certification/latest/examguides/aws-certification-exam-guides.html

An official guide normally contains: target candidate description, exam content outline,
domains, task statements, in-scope services, out-of-scope services, question format,
exam duration, and scoring information.

Map every generated question to a domain or task statement from the guide.

## Resolving codes and guide URLs

The live index above is the current complete exam list. `scripts/resolve_exam.py` is an
offline convenience catalog with enriched metadata for common exams, not an allowlist:

```bash
python3 scripts/resolve_exam.py <exam-code>   # local match or online-verification route
python3 scripts/resolve_exam.py --list        # locally enriched exams (not exhaustive)
```

A well-formed code absent from the catalog returns `needs_online_verification`; search
the live index for that exact code before accepting or rejecting it. The script also
recognizes known retired/superseded codes and never silently autocorrects near matches.

Do not restate the catalog in this file or `SKILL.md`; it drifts. User-facing READMEs may
show the offline catalog but must label it non-exhaustive.

## Fallbacks

- If a direct guide URL returns 404, fall back to the official index page above.
- For recently launched exams, confirm the guide is generally available before
  generating authoritative domain-mapped questions.
- If no guide can be retrieved, say so explicitly and use non-authoritative wording.
  Never fabricate domains, task statements, or domain percentages.
