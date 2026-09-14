# MLA-C01 — AWS Certified Machine Learning Engineer - Associate

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

ML workloads, data preparation, model development, deployment, monitoring, and operationalization.

## Common service families

- **ML platform:** Amazon SageMaker, SageMaker Studio, SageMaker Pipelines, SageMaker Feature Store, SageMaker Model Registry, SageMaker Clarify, SageMaker Model Monitor, SageMaker Canvas
- **Data:** S3, Glue, Athena, Redshift, Kinesis
- **Compute:** EC2, Lambda, ECS, EKS
- **Security and monitoring:** IAM, KMS, CloudWatch, CloudTrail

## Question style

Prefer scenarios involving feature engineering, model training, model deployment, endpoint scaling, model monitoring, bias and explainability, data drift, pipeline automation, and cost/performance trade-offs.

## Common traps

- Choosing a real-time endpoint when batch transform or async inference fits the workload
- Confusing SageMaker Clarify (bias and explainability) with Model Monitor (drift in production)
- Confusing data drift with concept drift
- Ignoring training/serving skew when a Feature Store would resolve it
- Choosing a multi-model endpoint when the scenario requires isolated scaling per model
- Treating hyperparameter tuning as a fix for a data quality problem
- Assuming a larger instance solves a latency issue caused by model or payload design
