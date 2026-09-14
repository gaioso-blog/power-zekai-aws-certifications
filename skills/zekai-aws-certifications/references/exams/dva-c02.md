# DVA-C02 — AWS Certified Developer - Associate

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

Developing, deploying, securing, and troubleshooting applications on AWS.

## Common service families

- **Compute:** AWS Lambda, Amazon EC2, Elastic Beanstalk, Amazon ECS
- **Serverless and integration:** API Gateway, AWS Step Functions, Amazon EventBridge, Amazon SQS, Amazon SNS
- **Databases:** Amazon DynamoDB, Amazon RDS, ElastiCache
- **Storage:** Amazon S3, presigned URLs, S3 event notifications
- **Security:** IAM roles and policies, Cognito, KMS, Secrets Manager, Systems Manager Parameter Store
- **CI/CD:** CodeCommit, CodeBuild, CodeDeploy, CodePipeline, SAM, CloudFormation, CDK
- **Observability:** CloudWatch Logs, CloudWatch Metrics, X-Ray, Lambda Powertools

## Question style

Prefer questions involving SDK usage, Lambda configuration, API Gateway integrations, DynamoDB access patterns, error handling, retries and DLQs, deployment strategies, IAM permissions for applications, and observability and tracing.

## Common traps

- Putting credentials in code instead of using IAM roles
- Using synchronous invocation when async/event-driven is better
- Missing idempotency
- Ignoring Lambda timeout, memory, and concurrency
- Confusing Parameter Store and Secrets Manager
- Confusing SQS visibility timeout with message retention
- Using scans in DynamoDB when query/index design is needed
