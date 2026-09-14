# SAP-C02 — AWS Certified Solutions Architect - Professional

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

Complex architecture design, multi-account, hybrid networking, migration, cost optimization, governance, and advanced resilience.

## Common service families

- **Organizations and governance:** AWS Organizations, SCPs, Control Tower, IAM Identity Center, AWS Config, CloudTrail, Security Hub
- **Networking:** Transit Gateway, Direct Connect, Site-to-Site VPN, Route 53, CloudFront, Global Accelerator, VPC endpoints, PrivateLink
- **Migration:** Application Migration Service, Database Migration Service, DataSync, Storage Gateway, Migration Hub
- **Compute and containers:** EC2, Auto Scaling, ECS, EKS, Lambda
- **Data:** RDS, Aurora, DynamoDB, Redshift, ElastiCache, S3
- **Integration:** SQS, SNS, EventBridge, Step Functions, API Gateway

## Question style

Prefer long scenario questions involving multiple accounts, multiple regions, enterprise governance, hybrid connectivity, migration constraints, disaster recovery strategies, cost/performance trade-offs, and least operational overhead at scale.

## Common traps

- Overengineering versus meeting stated requirements
- Ignoring governance requirements
- Choosing a service-level solution when org-level control is required
- Misreading RTO/RPO
- Confusing backup and restore, pilot light, warm standby, and active-active
- Choosing VPN when Direct Connect is required by bandwidth or consistency
