# ANS-C01 — AWS Certified Advanced Networking - Specialty

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

Advanced AWS networking, hybrid connectivity, routing, DNS, network security, and troubleshooting.

## Common service families

- **Core networking:** VPC, subnets, route tables, security groups, NACLs, VPC Flow Logs, Traffic Mirroring
- **Hybrid:** Direct Connect, Direct Connect Gateway, Site-to-Site VPN, Transit Gateway, Customer Gateway, Virtual Private Gateway
- **DNS:** Route 53, Resolver inbound endpoints, Resolver outbound endpoints, private hosted zones, DNSSEC
- **Edge:** CloudFront, Global Accelerator, AWS WAF, Shield
- **Private access:** VPC endpoints, gateway endpoints, interface endpoints, PrivateLink
- **Network security:** Network Firewall, AWS Firewall Manager, security groups, NACLs

## Question style

Prefer troubleshooting and design scenarios involving BGP, route propagation, asymmetric routing, overlapping CIDRs, high availability Direct Connect, hybrid DNS, centralized inspection, and multi-account VPC architecture.

## Common traps

- Confusing Direct Connect Gateway and Transit Gateway
- Misunderstanding BGP attributes
- Choosing VPN when bandwidth and consistency require Direct Connect
- Forgetting route propagation
- Forgetting security group and NACL statefulness behavior
- Confusing Route 53 Resolver inbound versus outbound endpoints
