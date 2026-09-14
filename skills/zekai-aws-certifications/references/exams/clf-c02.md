# CLF-C02 — AWS Certified Cloud Practitioner (Foundational)

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

Foundational understanding of AWS Cloud, billing, security, support, shared responsibility, and core services.

## Common service families

- **Compute:** Amazon EC2, AWS Lambda, AWS Elastic Beanstalk, Amazon ECS, Amazon EKS
- **Storage:** Amazon S3, Amazon EBS, Amazon EFS, S3 Glacier storage classes
- **Databases:** Amazon RDS, Amazon DynamoDB, Amazon Aurora, Amazon Redshift
- **Networking:** Amazon VPC, security groups, network ACLs, Amazon Route 53, Elastic Load Balancing, AWS Direct Connect, AWS VPN
- **Security:** AWS IAM, AWS Organizations, AWS Control Tower, AWS CloudTrail, Amazon GuardDuty, AWS Shield, AWS WAF, AWS KMS, AWS Secrets Manager
- **Monitoring and management:** Amazon CloudWatch, AWS Config, AWS Systems Manager, AWS Trusted Advisor, AWS Health Dashboard
- **Billing and cost:** AWS Budgets, AWS Cost Explorer, AWS Pricing Calculator, Savings Plans, Reserved Instances

## Question style

Prefer conceptual questions about the shared responsibility model, cloud value proposition, pricing models, support plans, basic service selection, and high-level security and compliance.

Avoid deep implementation details.

## Common traps

- Confusing what the customer secures versus what AWS secures under shared responsibility
- Confusing Basic, Developer, Business, and Enterprise support plan entitlements
- Confusing AWS Budgets (alerting on thresholds) with Cost Explorer (analysis and forecasting)
- Confusing Savings Plans with Reserved Instances commitment scope
- Treating Trusted Advisor as a monitoring service rather than a best-practice checker
- Assuming high availability comes automatically without multi-AZ design
