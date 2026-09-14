# AWS Services by Exam — Index

This file is an index only. The per-exam study maps live in `references/exams/`.

**Load exactly one file — the one for the exam being asked about.** Do not load the
whole directory. Resolve the correct path by running:

```bash
python3 scripts/resolve_exam.py <exam-code>
```

The `reference` field in that JSON output is the file to read.

| Exam code | Study map |
|---|---|
| CLF-C02 | `references/exams/clf-c02.md` |
| AIF-C01 | `references/exams/aif-c01.md` |
| SAA-C03 | `references/exams/saa-c03.md` |
| DVA-C02 | `references/exams/dva-c02.md` |
| SOA-C03 | `references/exams/soa-c03.md` |
| DEA-C01 | `references/exams/dea-c01.md` |
| MLA-C01 | `references/exams/mla-c01.md` |
| SAP-C02 | `references/exams/sap-c02.md` |
| DOP-C02 | `references/exams/dop-c02.md` |
| AIP-C01 | `references/exams/aip-c01.md` |
| ANS-C01 | `references/exams/ans-c01.md` |
| SCS-C02 | `references/exams/scs-c02.md` |

## Global rules for every study map

1. Do not claim a service is in scope unless the official exam guide supports it.
2. Do not invent domains, task statements, or percentages.
3. If a study map conflicts with the official exam guide, follow the guide.
4. If the user provides a specific guide URL, use that guide over these references.
5. Treat these files as study maps, not authoritative blueprints.
6. Map every generated question to: exam code, domain, task statement (when available),
   service or concept, and difficulty level.
