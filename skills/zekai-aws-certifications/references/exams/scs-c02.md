# SCS-C02 — AWS Certified Security - Specialty

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

AWS security architecture, identity, detection, infrastructure protection, data protection, and incident response.

## Common service families

- **Identity:** IAM, IAM Identity Center, Organizations, SCPs, resource-based policies, permission boundaries, STS
- **Detection and response:** GuardDuty, Security Hub, Detective, CloudTrail, CloudWatch, Config, EventBridge
- **Infrastructure protection:** WAF, Shield, Network Firewall, security groups, NACLs, VPC endpoints
- **Data protection:** KMS, CloudHSM, Secrets Manager, ACM, S3 encryption, EBS encryption, RDS encryption

## Question style

Prefer scenarios involving least privilege, cross-account access, key policies, incident investigation, threat detection, logging and auditability, encryption requirements, and data exfiltration prevention.

## Common traps

- Confusing IAM policy and KMS key policy
- Forgetting CloudTrail data events for S3 object-level activity
- Choosing access keys instead of roles
- Ignoring organization-level guardrails
- Confusing GuardDuty, Detective, Security Hub, and Config
