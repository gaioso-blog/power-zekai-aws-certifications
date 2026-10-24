# MLA-C02 — AWS Certified Machine Learning Engineer - Associate

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.
>
> **Version note.** MLA-C02 replaced MLA-C01, which was in use until September 28, 2026;
> MLA-C02 is in use beginning September 29, 2026. Do not mix content between versions.
> MLA-C02 adds foundation models (FMs), RAG, agents and AI-specific operations to the
> traditional ML scope.

Official guide: https://docs.aws.amazon.com/aws-certification/latest/machine-learning-engineer-associate-02/machine-learning-engineer-associate-02.html

## Main focus

Building, operationalizing, deploying, and maintaining AI and ML solutions and pipelines on AWS,
for both traditional ML models and foundation models. Target candidate: 1+ year with Amazon
SageMaker AI, Amazon Bedrock and related services, in a role such as backend developer, DevOps
developer, data engineer, or data scientist.

Format: multiple choice (1 of 4) and multiple response (2+ of 5+). 50 scored plus 15 unscored
questions. Scaled score 100–1,000, passing 720, compensatory scoring.

Out of scope for the candidate: designing full end-to-end AI/ML architectures, setting ML strategy,
integrating a wide array of new tools, working deeply in two or more ML domains.

## Domains and weights (from the guide)

| Domain | Weight |
|---|---|
| 1. Data Preparation for ML and AI | 28% |
| 2. ML Model and Foundation Model (FM) Development | 24% |
| 3. Deployment and Orchestration of ML and AI Workflows | 24% |
| 4. Operating, Monitoring, and Securing ML and AI Solutions | 24% |

## Task statements

- **1.1** Collect and store data (data sources, storage decisions, streaming ingestion, formats such as Parquet/JSON/CSV/ORC, merging sources, vector databases, diverse data types, SageMaker Feature Store ingestion).
- **1.2** Perform data transformation, feature engineering, and pre-processing (Glue, DataBrew, EMR Spark, SageMaker Data Wrangler, Feature Store, streaming transforms, embeddings, text pre-processing, RAG document preparation, masking/redaction/anonymization, FM fine-tuning/continuous pre-training/distillation data).
- **1.3** Validate data quality and manage bias (Glue Data Quality, labeling, bias mitigation, multimodal bias metrics, class imbalance, training data integrity and content safety screening, cleaning).
- **2.1** Choose appropriate modeling approaches (FM selection in Bedrock, fine-tuning strategies, model and algorithm selection, custom vs managed vs pre-trained vs FM tradeoffs, RAG patterns, performance/time/cost and performance/latency/cost tradeoffs, AWS AI services).
- **2.2** Train, fine-tune, and customize models (SageMaker built-in algorithms, script mode, hyperparameter optimization/AMT, early stopping and distributed training, overfitting/underfitting/catastrophic forgetting, model ensembles, hyperparameters, prompt engineering and fine-tuning, retrieval and embedding optimization).
- **2.3** Analyze and evaluate performance (MLflow on SageMaker AI, Bedrock evaluations, baselines and drift detection, shadow vs production variants, explainability, convergence debugging, human evaluation, BLEU/ROUGE/BERTScore, LLM-as-a-judge, RAG retrieval accuracy).
- **3.1** Manage deployment infrastructure (compute environments, orchestrators and multi-model/multi-container, real-time vs batch inference, FM deployment options, Bedrock Custom Model Import, agents, RAG configuration with reranking).
- **3.2** Provision and configure resources (on-demand vs provisioned, IaC provisioning, containers, SageMaker endpoints in a VPC, programmatic deployment, auto scaling metrics, Bedrock knowledge bases, retrieval pipelines, agent state management, GPU scaling, agentic workflow infrastructure).
- **3.3** Implement orchestration and CI/CD for MLOps and AI workloads (deployment strategies and rollback, CodeBuild/CodeCommit/CodeDeploy/CodePipeline/CodeConnections, training and inference jobs, automated testing, retraining, Model Registry and MLflow, Bedrock Prompt Management, agent pipelines, prompt testing, FM deployment automation, RAG refresh cycles).
- **4.1** Monitor inference and performance (CloudWatch generative AI observability, Bedrock Model Evaluation, drift detection, data distribution changes, A/B testing, agent coordination and tool failures).
- **4.2** Optimize infrastructure costs and performance (inference instance families, CloudWatch/AgentCore Observability/X-Ray, dashboards, capacity, cost quotas and tools, purchasing options, FM inference cost, token/embedding/vector storage cost patterns).
- **4.3** Secure ML and AI workloads and endpoints (CI/CD vulnerability checks with CodeGuru/Inspector, least privilege to artifacts, IAM, CloudTrail/Config auditing, VPC isolation, FM credential types such as Bedrock API keys vs IAM credentials, Bedrock Guardrails).

## In-scope AWS services (non-exhaustive, from the guide)

- **ML and AI:** Amazon SageMaker AI, Amazon Bedrock, Amazon Bedrock AgentCore, Amazon Comprehend, Amazon Comprehend Medical, Amazon Lex, Amazon Personalize, Amazon Polly, Amazon Rekognition, Amazon Textract, Amazon Transcribe, Amazon Translate, Amazon CodeGuru, Amazon DevOps Guru, AWS HealthLake
- **Analytics:** Athena, Data Firehose, EMR, Glue (DataBrew, Data Quality), Kinesis, Lake Formation, Managed Service for Apache Flink, OpenSearch Service, Amazon Quick, Redshift
- **Application integration:** EventBridge, MWAA, SNS, SQS, Step Functions
- **Compute and containers:** AWS Batch, EC2, Lambda, ECR, ECS, EKS
- **Databases:** DocumentDB, DynamoDB, ElastiCache, Neptune, RDS
- **Developer tools:** AWS CDK, CodeArtifact, CodeBuild, CodeCommit, CodeConnections, CodeDeploy, CodePipeline, X-Ray
- **Management and governance:** Auto Scaling, CloudFormation, CloudTrail, CloudWatch, Compute Optimizer, Config, Organizations, Service Catalog, Systems Manager, Trusted Advisor
- **Cost management:** Billing and Cost Management, Budgets, Cost Explorer
- **Networking, security, storage:** API Gateway, CloudFront, Direct Connect, VPC, IAM, Inspector, KMS, Macie, Secrets Manager, EBS, EFS, FSx, S3, S3 Glacier, Storage Gateway, DataSync, Kinesis Video Streams

## Question style

Scenarios an ML engineer would face: choosing between real-time, asynchronous, batch and serverless
inference, picking a FM and customization approach (prompt engineering vs RAG vs fine-tuning),
building and refreshing RAG pipelines, detecting drift, controlling FM inference cost, securing
endpoints, and automating MLOps pipelines with rollback.

## Common traps

- Choosing a real-time endpoint when batch transform or asynchronous inference fits the workload
- Confusing SageMaker Clarify (bias and explainability) with Model Monitor (drift in production)
- Confusing data drift with concept drift
- Ignoring training/serving skew when SageMaker Feature Store would resolve it
- Choosing a multi-model endpoint when the scenario requires isolated scaling per model
- Treating hyperparameter tuning as a fix for a data quality problem
- Fine-tuning an FM when prompt engineering or RAG meets the requirement at lower cost and effort
- Using RAG when the requirement is a change in model style or behavior rather than added knowledge
- Ignoring chunking, embedding, and reranking choices when retrieval quality is the actual problem
- Ignoring token usage and embedding costs when optimizing FM inference spend
- Using long-term IAM credentials where a scoped credential type for Bedrock access fits the scenario
- Assuming a larger instance fixes latency caused by model or payload design
