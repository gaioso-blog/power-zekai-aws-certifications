# DOP-C02 — AWS Certified DevOps Engineer - Professional

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

CI/CD, automation, observability, incident response, configuration management, resilience, and governance.

## Common service families

- **CI/CD:** CodePipeline, CodeBuild, CodeDeploy, CodeArtifact, CodeDeploy deployment strategies, CloudFormation, CDK, SAM
- **Operations:** CloudWatch, X-Ray, EventBridge, CloudTrail, AWS Config, Systems Manager, OpsCenter, Incident Manager
- **Compute:** EC2, Auto Scaling, ECS, EKS, Lambda
- **Security and governance:** IAM, KMS, Organizations, SCPs, Secrets Manager, Parameter Store
- **Resilience:** Route 53, ELB, Auto Scaling, Backup, multi-region patterns

## Question style

Prefer scenarios involving deployment automation, blue/green and canary, rollback, monitoring and alerting, compliance automation, IaC drift detection, multi-account pipelines, and incident response.

## Common traps

- Confusing CodeDeploy deployment strategies with Auto Scaling instance refresh
- Assuming a CloudFormation rollback restores data as well as resource state
- Confusing AWS Config remediation with Systems Manager Automation runbooks
- Using CloudWatch alarms where EventBridge rules are the correct trigger
- Ignoring CloudFormation stack drift on manually changed resources
- Choosing a single-account pipeline when the scenario requires cross-account deployment roles
- Confusing canary deployment with a canary synthetic monitor in CloudWatch
