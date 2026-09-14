# SOA-C03 — AWS Certified CloudOps Engineer - Associate

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.
>
> SOA-C03 replaced SOA-C02 (AWS Certified SysOps Administrator - Associate) on
> September 30, 2025. Containers and container orchestration are now explicitly
> in scope, alongside the operations fundamentals carried over from SOA-C02.

## Content domains (official weightings)

1. Monitoring, Logging, Analysis, Remediation, and Performance Optimization — 22%
2. Reliability and Business Continuity — 22%
3. Deployment, Provisioning, and Automation — 22%
4. Security and Compliance — 16%
5. Networking and Content Delivery — 18%

## Main focus

Operations, monitoring, automation, deployment, networking, security, containers, and cost-aware
troubleshooting. Well-Architected Framework alignment runs through every domain.

## Common service families

- **Monitoring and operations:** CloudWatch, CloudWatch Alarms, CloudWatch Logs, EventBridge, CloudTrail, AWS Config, Systems Manager, Trusted Advisor, AWS Health
- **Compute:** EC2, Auto Scaling, Elastic Load Balancing, AMIs, EBS, Lambda
- **Containers:** ECS, EKS basics, container orchestration fundamentals, ECR
- **Networking:** VPC, route tables, NAT Gateway, Internet Gateway, security groups, NACLs, VPC Flow Logs, Route 53
- **Security:** IAM, KMS, Secrets Manager, AWS Organizations, SCPs
- **Backup and resilience:** AWS Backup, EBS snapshots, RDS snapshots, Multi-AZ
- **IaC:** CloudFormation basics for deployment and provisioning tasks

## Question style

Prefer operational troubleshooting: alarms, metric interpretation, failed deployments, permissions, networking reachability, backup and restore, patching, container orchestration issues, and automation with Systems Manager.

## Out of scope for this exam

Per the official guide: designing distributed architectures, designing CI/CD pipelines, designing hybrid/multi-VPC networking, developing software, defining security/compliance/governance requirements, capacity planning, and cost/billing analysis. These are design and planning tasks — SOA-C03 tests operating and troubleshooting what already exists.

## Common traps

- Expecting memory and disk metrics in CloudWatch without the unified agent installed
- Confusing CloudTrail (API auditing) with CloudWatch Logs (application and system logs)
- Confusing AWS Config (configuration compliance over time) with CloudTrail
- Misreading Auto Scaling cooldown, health check grace period, and termination policies
- Confusing ALB, NLB, and CLB target and protocol capabilities
- Forgetting that NACLs are stateless while security groups are stateful
- Assuming an SCP grants permissions rather than only limiting them
- Treating container troubleshooting (ECS task failures, ECR pull errors) as out of scope — it is now tested
