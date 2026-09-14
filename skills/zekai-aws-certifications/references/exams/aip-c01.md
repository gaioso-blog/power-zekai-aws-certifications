# AIP-C01 — AWS Certified Generative AI Developer - Professional

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.
>
> **Do not confuse with AIF-C01.** AIP-C01 is Professional (Generative AI Developer).
> AIF-C01 is Foundational (AI Practitioner). AIP-C01 is not a version of AIF-C01.

## Main focus

Building, evaluating, securing, and operationalizing generative AI applications on AWS.

## Common service families

- **Generative AI:** Amazon Bedrock, Bedrock Knowledge Bases, Bedrock Agents, Bedrock Guardrails, Bedrock Flows, Bedrock model evaluation
- **Data and retrieval:** S3, OpenSearch Serverless, Aurora PostgreSQL with pgvector, Knowledge Bases, vector stores, embeddings, chunking, metadata filtering
- **Application integration:** Lambda, API Gateway, Step Functions, EventBridge, SQS, SNS
- **Security:** IAM, KMS, Secrets Manager, VPC endpoints, CloudTrail, CloudWatch
- **MLOps / LLMOps:** evaluation, monitoring, prompt versioning, grounding, RAG quality, guardrail testing, model selection

## Question style

Prefer scenarios involving RAG architecture, prompt engineering, grounding, hallucination mitigation, model evaluation, cost/latency trade-offs, security for generative AI apps, orchestration with agents and tools, and responsible AI controls.

## Common traps

- Choosing fine-tuning when RAG addresses the freshness or grounding requirement
- Ignoring chunking strategy and metadata filtering as the cause of poor retrieval quality
- Confusing Bedrock Guardrails with IAM-based access control
- Choosing a custom RAG stack when Knowledge Bases meets the operational overhead constraint
- Assuming a larger context window removes the need for retrieval
- Confusing Bedrock Agents (tool orchestration) with Step Functions (deterministic workflow)
- Overlooking per-token cost and latency when the scenario constrains both
- Treating embedding model choice as interchangeable across an existing vector index
