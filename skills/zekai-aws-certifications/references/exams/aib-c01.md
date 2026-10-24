# AIB-C01 — AWS Certified AI Business Strategist (Business)

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.
>
> **Do not confuse with AIF-C01 or AIP-C01.** AIB-C01 is the Business-category exam
> (AI Business Strategist). AIF-C01 is Foundational (AI Practitioner, technical concepts and
> AWS AI services). AIP-C01 is Professional (Generative AI Developer). The exam code is
> `AIB-C01`; some community posts misspell it as "AB1-C01". Never autocorrect.

Official guide: https://docs.aws.amazon.com/aws-certification/latest/ai-business-strategist-01/ai-business-strategist-01.html

## Main focus

Business judgment for AI decisions: which initiatives to fund, how to build the business case and
measure value, how to govern risk, and how to move from pilot to enterprise scale. The exam
prioritizes strategic decision-making over technical implementation. It does **not** assess
knowledge of AWS AI services in depth; services appear only at a strategic level.

Format: multiple choice (1 of 4) and multiple response (2+ of 5+). 130 minutes. Scaled score
100–1,000, passing 700, compensatory scoring.

## Domains and weights (from the guide)

| Domain | Weight |
|---|---|
| 1. AI Fundamentals and Literacy | 24% |
| 2. AI Strategy and Business Value Creation | 28% |
| 3. AI Governance and Responsible AI Leadership | 24% |
| 4. Business Readiness, Leadership, and AI Transformation | 24% |

## Task statements

- **1.1** Describe core AI concepts and define terminology (AI vs ML vs GenAI, structured vs unstructured data, data quality, training on historical data, ISO/IEC 23053 and 42001 awareness).
- **1.2** Identify and select appropriate AI solution types (rule-based automation vs AI, AI agents, model drift and monitoring, shadow AI and tool classification).
- **1.3** Apply GenAI concepts and techniques (prompt engineering basics, token limits and context windows, RAG and fine-tuning).
- **2.1** Develop AI strategies that align with business objectives (high-impact use cases, build-buy-partner, prioritization and scale/pause/terminate, when AI is not the answer, transition considerations).
- **2.2** Measure and demonstrate AI business value (KPIs tangible and intangible, baseline metrics, ROI frameworks, leading indicators, basic cost controls).
- **2.3** Position AI for competitive advantage (competitive landscape, business model transformation, sustainable advantage, investment level vs industry maturity).
- **3.1** Apply responsible AI principles to business decisions (fairness, explainability, privacy, safety, transparency, robustness; tradeoffs; governance by design; human oversight and guardrails).
- **3.2** Establish AI governance structures and ensure regulatory compliance (cross-functional governance, regulatory risk, access controls and data security at a governance level, risk classification).
- **3.3** Identify enterprise AI risks and direct mitigation (production monitoring, bias across the lifecycle and bias drift, harmful content and IP, reliability: hallucination, data quality degradation, drift).
- **4.1** Assess AI business readiness and maturity (readiness dimensions, maturity models, capability gaps across people/process/technology/governance, investment prioritization).
- **4.2** Establish data and infrastructure foundations for AI (data readiness and silos, data strategy/ownership/sharing, foundational technology requirements).
- **4.3** Lead enterprise-wide change and build AI-ready workforce capabilities (executive sponsorship, cross-functional teams, communication, cultural barriers, workforce development, human-AI role transition).
- **4.4** Scale AI from pilots to enterprise-wide deployments (envision/experiment/launch/scale, quick wins, centers of excellence, feedback loops and metrics, pilot-to-production, business continuity).

## In-scope AWS services and features (basic, strategic-level application only)

- **AI and ML:** Amazon Bedrock (platform, pricing tiers, Guardrails, Knowledge Bases), Amazon SageMaker AI (managed vs custom)
- **Business intelligence:** Amazon Quick (AI-powered business assistants)
- **Cloud strategy and governance:** AWS Cloud Adoption Framework (AWS CAF), AWS shared responsibility model for AI workloads, AWS Well-Architected Framework (Responsible AI Lens)
- **Pricing and cost management:** AI service pricing structures (consumption-based, instance-based, seat-based), Savings Plans, AWS Pricing Calculator, AWS Cost Explorer, AWS Marketplace (build-buy-partner)

Out of scope: configuring, deploying, or administering any AWS service. Infrastructure, compute,
networking, databases and storage, containers, DevOps tooling, IAM policy writing, AWS KMS, IoT and
media services are all outside the exam. Do not write questions that require technical
configuration, hyperparameter tuning, pipeline building, or statistical model analysis.

## Question style

Scenario-based business judgment: a leader must choose the best decision under budget, timeline,
risk, regulatory, or organizational constraints. Options are courses of action (fund, pause, pilot,
escalate, establish a governance body, measure a baseline), not service configurations. Roles to
use in scenarios: product manager, program manager, line-of-business leader, consultant, business
analyst, marketer, sales professional. Vary the decision axis: value, risk, cost, compliance,
readiness, speed to adoption.

## Common traps

- Choosing a technical fix (retrain, tune, re-architect) when the question asks for a business or governance decision
- Skipping the baseline: claiming ROI without metrics captured before the AI solution
- Treating AI as the answer when rule-based automation or a non-AI fix is the better fit
- Picking fine-tuning when RAG or better prompting meets the stated need at lower cost and effort
- Scaling a pilot before governance, data readiness, and production-grade operations are in place
- Treating responsible AI as a late-stage compliance check instead of governance by design
- Ignoring human oversight where outputs carry high risk (escalation criteria, guardrails)
- Assuming a model is "done" after launch and overlooking drift and bias drift monitoring
- Blocking all unapproved AI tools instead of classifying them (approved, blocked, under evaluation) to manage shadow AI
- Counting only tangible benefits (cost reduction) and ignoring intangible ones (customer satisfaction, productivity) when defining KPIs
- Focusing on technology readiness alone and missing leadership alignment, culture, and workforce gaps
- Confusing the shared responsibility split for AI workloads at the governance level (data and usage accountability stays with the customer)
