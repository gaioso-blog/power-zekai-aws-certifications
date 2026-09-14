# AWS Documentation Grounding

Load this file before generating or explaining any question. It defines how to verify
the factual premises behind the correct answer and every distractor.

## What must be verified

Before output, list the minimum factual claims the question depends on:

- capabilities and unsupported behaviors of each service in the options
- service limits or quotas that affect elimination
- availability, durability, ordering, consistency, networking, and security behavior
- pricing-model characteristics when cost determines the answer
- integration requirements and supported event or protocol paths
- the best-practice or Well-Architected principle used to break a tie

Do not verify generic scenario prose. Verify the AWS facts that make one option correct
and the others wrong.

## Procedure

1. Group related claims to minimize calls. One focused documentation search may ground
   multiple options in the same comparison set.
2. Use the AWS documentation MCP server first. Prefer `read_sections` when available;
   it is more precise than loading an entire page.
3. Accept only official AWS sources (`docs.aws.amazon.com`, `aws.amazon.com`, or
   `d1.awsstatic.com`). Blogs may help locate a concept but are not the authority.
4. Keep the source URLs. In Study Mode, cite them with the question. In Interactive
   Quiz Mode, withhold them until after the answer because a page title can be a hint.
5. If documentation contradicts a planned option, rewrite or discard the option.
6. If a claim cannot be verified, remove it. Never turn memory into a factual premise.

## Transient failure

A transport error is not evidence that documentation does not exist.

1. Retry the failed MCP operation once in the current step.
2. If it still fails, try the generic web-fetch fallback against an official URL.
3. If official verification remains unavailable, stop the requested graded content and say:

   > I could not verify the deciding AWS facts against current official documentation,
   > so I will not generate or grade this question yet. Please retry; the documentation
   > service may be temporarily unavailable.

4. Do not emit a question, answer, explanation, or score update while a deciding claim
   is unverified. Do not call `session.py pending-set` or `session.py grade`.
5. Retry the MCP server on the next user attempt. Failure is never permanent session state.

## Verification record (internal)

Before output, maintain this small internal record; do not show it unless debug mode is on:

```text
claim: <fact that determines correctness/elimination>
source: <official URL and section title>
options supported: <A/B/C/D or all>
status: verified | unverified
```

In debug mode, report only the aggregate (`claims grounded: N/N`). Do not reveal which
claim supports which option before the learner answers.
