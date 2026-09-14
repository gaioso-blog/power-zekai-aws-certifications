# SAA-C03 — AWS Certified Solutions Architect - Associate

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

Designing secure, resilient, high-performing, and cost-optimized architectures on AWS.

## Common service families

- **Compute:** Amazon EC2, Auto Scaling, AWS Lambda, Amazon ECS, Amazon EKS, AWS Batch
- **Storage:** Amazon S3, S3 lifecycle policies, S3 storage classes, Amazon EBS, Amazon EFS, AWS Backup, AWS Storage Gateway
- **Databases:** Amazon RDS, Amazon Aurora, Amazon DynamoDB, Amazon ElastiCache, Amazon Redshift
- **Networking:** Amazon VPC, public and private subnets, route tables, NAT Gateway, Internet Gateway, VPC endpoints, VPC peering, Transit Gateway, Elastic Load Balancing, Amazon Route 53, AWS Direct Connect, Site-to-Site VPN, AWS Global Accelerator, Amazon CloudFront
- **Security:** IAM, resource policies, security groups, network ACLs, AWS KMS, AWS WAF, AWS Shield, Secrets Manager, ACM
- **Messaging and integration:** Amazon SQS, Amazon SNS, Amazon EventBridge, AWS Step Functions
- **Monitoring:** Amazon CloudWatch, AWS CloudTrail, AWS Config

## Question style

Prefer scenario questions involving high availability, disaster recovery, multi-AZ versus multi-region, decoupling, caching, cost optimization, migration patterns, least operational overhead, and secure private connectivity.

## Common traps

- Choosing Multi-Region when Multi-AZ is enough
- Choosing EC2 when managed/serverless is more appropriate
- Ignoring operational overhead
- Confusing security groups and NACLs
- Confusing Gateway Endpoint and Interface Endpoint
- Choosing NAT Gateway for private access to S3 when Gateway Endpoint is better
- Choosing EBS for shared file storage instead of EFS
- Choosing RDS read replicas for HA instead of Multi-AZ
