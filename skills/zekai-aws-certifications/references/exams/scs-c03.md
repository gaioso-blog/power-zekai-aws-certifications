# SCS-C03 — AWS Certified Security - Specialty

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.
>
> **Version note.** SCS-C03 replaced SCS-C02, which was in use until December 1, 2025;
> SCS-C03 is in use beginning December 2, 2025. The domain structure changed: threat
> detection, incident response and logging were regrouped into Detection and Incident
> Response, and generative AI protections were added. Do not mix content between versions.

Official guide: https://docs.aws.amazon.com/aws-certification/latest/security-specialty-03/security-specialty-03.html

## Main focus

Securing AWS workloads: detection and logging, incident response, infrastructure protection,
identity and access, data protection, and multi-account governance. Target candidate: about
3–5 years of experience securing cloud solutions.

Format: multiple choice, multiple response, **ordering** (3–5 steps in the correct order) and
**matching** (pairs for 3–7 prompts). 50 scored plus 15 unscored questions. Scaled score
100–1,000, passing 750, compensatory scoring.

Out of scope for the candidate: designing cryptographic algorithms, packet-level traffic
analysis, architecting overall cloud deployments, managing end-user compute, training ML models.
Security aspects of a service can be in scope even if the service itself is not (for example, an
S3 bucket policy is in scope, S3 replication setup is not).

## Domains and weights (from the guide)

| Domain | Weight |
|---|---|
| 1. Detection | 16% |
| 2. Incident Response | 14% |
| 3. Infrastructure Security | 18% |
| 4. Identity and Access Management | 20% |
| 5. Data Protection | 18% |
| 6. Security Foundations and Governance | 14% |

## Task statements

- **1.1** Design and implement monitoring and alerting for an AWS account or organization (GuardDuty, Security Lake, Security Hub, Macie; Config conformance packs; Systems Manager State Manager).
- **1.2** Design and implement logging solutions (organization CloudTrail trail, dedicated CloudWatch logging account, Security Lake and third-party integration, CloudWatch Logs Insights, Athena, OpenSearch, VPC/transit gateway flow logs, Route 53 Resolver logs).
- **1.3** Troubleshoot security monitoring, logging, and alerting (Lambda/API Gateway/CloudFront logging, CloudWatch Agent, missing logs).
- **2.1** Design and test an incident response plan (runbooks, Systems Manager OpsCenter, blast radius, Shield Advanced, Fault Injection Service, Resilience Hub, automated remediation, Automated Forensics Orchestrator for EC2).
- **2.2** Respond to security events (forensic artifacts, log correlation, validating findings, containment/eradication/recovery, root cause analysis with Detective).
- **3.1** Design, implement, and troubleshoot network edge security (edge strategy, WAF, CloudFront headers, Shield Advanced, rate limiting and geo rules, OCSF and third-party integrations).
- **3.2** Security controls for compute workloads (hardened AMIs and images, instance/service/execution roles, Inspector and GuardDuty scanning, Patch Manager, Session Manager, pipeline vulnerability tools, guardrails for generative AI applications including OWASP Top 10 for LLM applications).
- **3.3** Design and troubleshoot network security controls (security groups, NACLs, Network Firewall, hybrid connectivity with Site-to-Site VPN/Direct Connect/MACsec, Verified Access, segmentation, Network Access Analyzer).
- **4.1** Authentication strategies (IAM Identity Center, Cognito, MFA, IdP integration, STS temporary credentials, presigned URLs, troubleshooting).
- **4.2** Authorization strategies (Verified Permissions, IAM Roles Anywhere, resource policies and cross-account access, trust policies, ABAC/RBAC, least privilege with permission boundaries and session policies, Policy Simulator, IAM Access Analyzer).
- **5.1** Controls for data in transit (ELB security policies and TLS enforcement, PrivateLink/VPC endpoints/Client VPN/Verified Access, inter-node and Nitro encryption).
- **5.2** Controls for data at rest (KMS vs CloudHSM, client-side vs server-side encryption, S3 Object Lock/Glacier Vault Lock/versioning, lifecycle and retention, AWS Backup, Data Lifecycle Manager, ransomware protection, DataSync).
- **5.3** Protect confidential data, credentials, secrets, and key material (Secrets Manager rotation, imported vs AWS-generated key material, external key stores, masking with CloudWatch Logs data protection and SNS message data protection, customer managed KMS keys across Regions, AWS Private CA).
- **6.1** Centrally deploy and manage accounts (Organizations, Control Tower, SCPs/RCPs/AI service opt-out/declarative policies, delegated administrators, root user credential management and break-glass).
- **6.2** Secure and consistent resource deployment (CloudFormation StackSets, CloudFormation Guard and cfn-lint, tagging, Firewall Manager, Service Catalog, AWS RAM).
- **6.3** Evaluate compliance (Config rules and remediation, Security Hub, Audit Manager, Artifact, Well-Architected Tool).

## In-scope AWS services (non-exhaustive, from the guide)

- **Security, identity, compliance:** IAM, IAM Identity Center, STS, Cognito, Directory Service, Verified Permissions, KMS, CloudHSM, Secrets Manager, ACM, Private CA, GuardDuty, Security Hub, Security Lake, Detective, Inspector, Macie, WAF, Shield and Shield Advanced, Network Firewall, Firewall Manager, Audit Manager, Artifact, Automated Forensics Orchestrator for EC2
- **Management and governance:** CloudTrail, CloudTrail Lake, CloudWatch, Config, Control Tower, Organizations, Systems Manager, CloudFormation, Service Catalog, RAM, Trusted Advisor, Well-Architected Tool, Resilience Hub, User Notifications, Managed Grafana
- **Networking and edge:** VPC (NACLs, security groups, endpoints, flow logs, Site-to-Site VPN), Client VPN, Verified Access, Network Access Analyzer, CloudFront, Route 53 (including Resolver DNS Firewall), Direct Connect, ELB, Transit Gateway, Application Recovery Controller
- **Compute and apps:** EC2 (Image Builder, Instance Connect), EKS, EMR, Lambda, API Gateway, SNS, Step Functions, Fault Injection Service
- **Storage and data:** S3, AWS Backup, DataSync, EFS, FSx for Lustre, Data Lifecycle Manager, Athena, OpenSearch Service
- **AI and other:** Amazon Bedrock, SageMaker AI, Amazon Q Business, Amazon Q Developer, CodeGuru Security, IoT Core

## Question style

Scenarios with security constraints: investigate a GuardDuty finding, contain a compromised instance,
fix a cross-account access failure, choose between KMS and CloudHSM, enforce guardrails with
SCPs/RCPs, centralize logs, or protect a generative AI application. Ordering questions
(sequence of response steps) and matching questions can appear on this exam.

## Common traps

- Confusing IAM policy and KMS key policy
- Forgetting CloudTrail data events for S3 object-level activity
- Choosing access keys instead of roles
- Applying an SCP and expecting it to grant permissions (SCPs only limit; RCPs limit resource access)
- Confusing GuardDuty (threat detection), Detective (investigation), Security Hub (aggregation/posture), Config (resource compliance), and Macie (sensitive data in S3)
- Containing an incident by deleting evidence instead of isolating and preserving forensic artifacts
- Confusing imported key material with AWS-generated key material (rotation and control differences)
- Choosing KMS when a requirement calls for single-tenant HSM control with CloudHSM
- Ignoring organization-level guardrails and delegated administrators in multi-account scenarios
- Confusing Shield Standard with Shield Advanced, or WAF with Network Firewall (layer 7 web requests vs VPC traffic filtering)
