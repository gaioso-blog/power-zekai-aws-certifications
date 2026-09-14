#!/usr/bin/env python3
"""Local catalog and normalization helper for AWS certification exam codes.

Usage:
    python3 scripts/resolve_exam.py <code>     Check the local catalog
    python3 scripts/resolve_exam.py --list     List locally enriched exams

Output is always JSON. A code absent from this catalog is NOT rejected: it
returns ``needs_online_verification`` so the agent checks the live official
exam-guides index. This prevents a newly launched AWS exam from being blocked
by a stale skill release.

Exit codes: 0 for catalog matches and online-verification candidates; 1 for
malformed input and known retired/superseded exams.
"""

import json
import sys

# Locally enriched metadata for common exams. This is a cache/convenience, not
# an exhaustive allowlist. The live official exam-guides index is authoritative.
EXAMS = {
    "CLF-C02": {
        "exam_name": "AWS Certified Cloud Practitioner",
        "level": "Foundational",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-cloud-practitioner/AWS-Certified-Cloud-Practitioner_Exam-Guide.pdf",
        "reference": "references/exams/clf-c02.md",
    },
    "AIF-C01": {
        "exam_name": "AWS Certified AI Practitioner",
        "level": "Foundational",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-ai-practitioner/AWS-Certified-AI-Practitioner_Exam-Guide.pdf",
        "reference": "references/exams/aif-c01.md",
    },
    "SAA-C03": {
        "exam_name": "AWS Certified Solutions Architect - Associate",
        "level": "Associate",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-sa-assoc/AWS-Certified-Solutions-Architect-Associate_Exam-Guide.pdf",
        "reference": "references/exams/saa-c03.md",
    },
    "DVA-C02": {
        "exam_name": "AWS Certified Developer - Associate",
        "level": "Associate",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-dev-associate/AWS-Certified-Developer-Associate_Exam-Guide.pdf",
        "reference": "references/exams/dva-c02.md",
    },
    "SOA-C03": {
        "exam_name": "AWS Certified CloudOps Engineer - Associate",
        "level": "Associate",
        "guide_url": "https://docs.aws.amazon.com/aws-certification/latest/sysops-administrator-associate-03/sysops-administrator-associate-03.html",
        "reference": "references/exams/soa-c03.md",
    },
    "DEA-C01": {
        "exam_name": "AWS Certified Data Engineer - Associate",
        "level": "Associate",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-data-engineer-associate/AWS-Certified-Data-Engineer-Associate_Exam-Guide.pdf",
        "reference": "references/exams/dea-c01.md",
    },
    "MLA-C01": {
        "exam_name": "AWS Certified Machine Learning Engineer - Associate",
        "level": "Associate",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-machine-learning-engineer-associate/AWS-Certified-Machine-Learning-Engineer-Associate_Exam-Guide.pdf",
        "reference": "references/exams/mla-c01.md",
    },
    "SAP-C02": {
        "exam_name": "AWS Certified Solutions Architect - Professional",
        "level": "Professional",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Exam-Guide.pdf",
        "reference": "references/exams/sap-c02.md",
    },
    "DOP-C02": {
        "exam_name": "AWS Certified DevOps Engineer - Professional",
        "level": "Professional",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-devops-pro/AWS-Certified-DevOps-Engineer-Professional_Exam-Guide.pdf",
        "reference": "references/exams/dop-c02.md",
    },
    "AIP-C01": {
        "exam_name": "AWS Certified Generative AI Developer - Professional",
        "level": "Professional",
        "guide_url": "https://docs.aws.amazon.com/aws-certification/latest/examguides/ai-professional-01.html",
        "reference": "references/exams/aip-c01.md",
    },
    "ANS-C01": {
        "exam_name": "AWS Certified Advanced Networking - Specialty",
        "level": "Specialty",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-advnetworking-spec/AWS-Certified-Advanced-Networking-Specialty_Exam-Guide.pdf",
        "reference": "references/exams/ans-c01.md",
    },
    "SCS-C02": {
        "exam_name": "AWS Certified Security - Specialty",
        "level": "Specialty",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-security-spec/AWS-Certified-Security-Specialty_Exam-Guide.pdf",
        "reference": "references/exams/scs-c02.md",
    },
}

# Codes that must be actively refused with an explanation rather than a
# generic "not supported" message.
RETIRED = {
    "MLS-C01": "AWS Certified Machine Learning - Specialty is retired and no longer offered.",
    "SAA-C02": "Superseded by SAA-C03.",
    "CLF-C01": "Superseded by CLF-C02.",
    "DVA-C01": "Superseded by DVA-C02.",
    "SOA-C01": "Superseded by SOA-C03 (AWS Certified CloudOps Engineer - Associate).",
    "SOA-C02": "Retired September 29, 2025. Superseded by SOA-C03 (AWS Certified CloudOps Engineer - Associate), which added containers to scope.",
    "SAP-C01": "Superseded by SAP-C02.",
    "DOP-C01": "Superseded by DOP-C02.",
    "SCS-C01": "Superseded by SCS-C02.",
}

# Frequently confused pairs the agent must never conflate.
DISAMBIGUATION = {
    "AIF-C01": "AIF-C01 is AI Practitioner (Foundational). Not a variant of AIP-C01.",
    "AIP-C01": "AIP-C01 is Generative AI Developer (Professional). Not a variant of AIF-C01.",
}

ALL_CODES = sorted(EXAMS)


def normalize(raw):
    """Normalize case and surrounding whitespace without correcting the code."""
    return raw.strip().upper()


def resolve(raw):
    code = normalize(raw)

    if code in EXAMS:
        payload = {
            "valid": True,
            "status": "local_catalog_match",
            "code": code,
            "input": raw,
        }
        payload.update(EXAMS[code])
        if code in DISAMBIGUATION:
            payload["disambiguation"] = DISAMBIGUATION[code]
        return payload, 0

    if code in RETIRED:
        return {
            "valid": False,
            "status": "known_retired",
            "code": code,
            "input": raw,
            "reason": "retired",
            "detail": RETIRED[code],
            "local_catalog_codes": ALL_CODES,
        }, 1

    # Do not impose today's code grammar on future AWS exams and never repair
    # near matches. Every non-empty exact token absent from the catalog goes to
    # live verification; the official index, not this script, decides validity.
    if not code:
        return {
            "valid": False,
            "status": "malformed",
            "code": code,
            "input": raw,
            "reason": "empty",
            "detail": "Exam code is empty. Ask the user for the exact code; do not guess.",
            "local_catalog_codes": ALL_CODES,
        }, 1

    return {
        "valid": None,
        "status": "needs_online_verification",
        "code": code,
        "input": raw,
        "reason": "not_in_local_catalog",
        "detail": "Code is not in the local catalog. Verify the exact code against the live official AWS exam-guides index.",
        "verification_query": f'"{code}" AWS certification exam guide',
        "official_index_url": "https://docs.aws.amazon.com/aws-certification/latest/examguides/aws-certification-exam-guides.html",
        "local_catalog_codes": ALL_CODES,
    }, 0


def list_all():
    return {
        "catalog_is_exhaustive": False,
        "detail": "This is an offline convenience catalog. Fetch the official exam-guides index for the current complete list.",
        "local_catalog_count": len(EXAMS),
        "exams": [{"code": code, **EXAMS[code]} for code in ALL_CODES],
    }


def main(argv):
    if len(argv) != 2:
        print(json.dumps({
            "valid": False,
            "reason": "usage",
            "detail": "Usage: resolve_exam.py <exam-code> | --list",
            "local_catalog_codes": ALL_CODES,
        }, ensure_ascii=False, indent=2))
        return 1

    arg = argv[1]
    if arg in ("--list", "-l"):
        print(json.dumps(list_all(), ensure_ascii=False, indent=2))
        return 0

    payload, code = resolve(arg)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
