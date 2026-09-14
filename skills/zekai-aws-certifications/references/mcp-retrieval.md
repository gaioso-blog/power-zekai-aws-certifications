# Retrieving AWS Exam Documentation in Kiro

Load this file when establishing or refreshing exam context.

## Find the tool by capability, not identifier

Use the bundled/recommended `awslabs.aws-documentation-mcp-server`, which provides
`read_documentation`, `read_sections`, `search_documentation`, and `recommend`.

Do not hardcode a full tool identifier. Kiro assembles it from the user's MCP server key:

- IDE: `mcp_<sanitized-server-key>_read_documentation`
- CLI: `<server-alias>___read_documentation`

The prefix therefore varies. Inspect this session's tools and match the stable trailing
capability: `read_documentation`, `read_sections`, or `search_documentation`.

## Exam list and exact-code lookup

If the user has not supplied an exam, read this live index and present every current exam
grouped by level:

https://docs.aws.amazon.com/aws-certification/latest/examguides/aws-certification-exam-guides.html

If a code is absent from the local catalog, search the index for that exact code. Never
replace it with a similar code; AIF-C01 and AIP-C01 are different exams. A code is rejected
only when the live official index has no exact match.

## Guide fallback ladder

A transport error may be transient. Retry the failed MCP operation once, then stop at the
first step that succeeds:

1. Read a resolver- or user-supplied `guide_url` with the MCP page reader.
2. Search the exact code plus `certification exam guide domains task statements`, then
   read the top official result.
3. Fetch the guide or official index with a generic web-fetch capability.
4. If nothing succeeds, disclose verification failure and pause the requested graded content.

A user-supplied guide URL wins at every step. Extract domains, weights, task statements,
and in/out-of-scope services as the primary source and the `--domains` payload for
`scripts/session.py start`.

On total failure, say:

> I could not verify the deciding AWS facts against current official documentation, so
> I will not generate or grade this question yet. Please retry; the documentation service
> may be temporarily unavailable.

Do not emit a question, answer, explanation, domain mapping, or score update while its
deciding claims are unverified. Never invent domains, percentages, or session weights.
Retry MCP on the next user attempt; failure is not permanent session state.
