# Distractor Engineering

Load this file when constructing **hard** or **exam-level** questions, or when the user
asks why a distractor works. Easy and medium questions do not need it.

## Hard question construction

1. Pick the domain and task statement from the official guide.
2. Choose a realistic AWS architecture scenario.
3. Layer constraints: business, technical, security, operational, and cost/resilience/performance.
4. Build one correct solution that satisfies all of them.
5. Build distractors that each fail for one subtle reason:
   - violates exactly one stated requirement
   - higher operational overhead than the scenario allows
   - solves only part of the problem
   - availability risk, or misses the stated RTO/RPO
   - hidden cost issue at the stated scale
   - wrong integration pattern
   - valid for a different scenario, but not this one
6. Equalize all options in length, specificity, and quality of best-practice language.
7. Confirm the answer cannot be reached by keyword matching alone.

## What makes a distractor good

- Uses a real AWS service correctly in another context
- Partially satisfies the scenario
- Sounds attractive: cost, simplicity, familiarity, managed-service appeal
- Fails on one specific, nameable requirement
- Tests a known AWS exam confusion

## What makes a distractor bad

- Obviously unrelated or technically impossible
- Much shorter or less detailed than the correct option
- Uses a service nonsensically
- Eliminable without any AWS knowledge
- Leans on "always", "never", or "all traffic" outside a deliberate edge case

## Additional requirements for hard and exam-level

- 2 or more wrong options close enough to tempt a beginner
- At least 1 near-miss that fails a single requirement
- At least 1 option built on a common exam trap
- Uniform length and tone across all options
- A correct option that is not identifiable as the only detailed, managed, or
  best-practice-sounding choice

## Near-miss patterns

Each of these would be correct if one requirement were removed from the scenario.

- RDS Read Replica instead of Multi-AZ for HA
- NAT Gateway instead of S3 Gateway Endpoint for private S3 access
- Interface Endpoint instead of Gateway Endpoint for cost-effective private S3 access
- SNS instead of SQS when retention and backpressure are required
- CloudFront instead of Global Accelerator for non-HTTP/TCP acceleration
- AWS managed KMS key instead of a customer managed key for cross-account control
- DynamoDB Scan with FilterExpression instead of Query with proper key design
- Spot Instances for interruption-intolerant workloads
- RDS backup/restore instead of Aurora Global Database for low RTO/RPO
- EventBridge instead of Kinesis for ordered high-throughput streams
- Kinesis instead of EventBridge for simple event routing with SaaS targets
- Multi-Region deployment when Multi-AZ satisfies the stated availability target
- Aurora Serverless v2 when the workload is steady-state and reserved capacity is cheaper

## Comparison sets

Pull distractors from the same set as the correct answer — that is what forces real
elimination instead of keyword matching.

**Messaging and events**
- SQS Standard vs SQS FIFO vs EventBridge vs Kinesis
- SNS + SQS fanout vs EventBridge rules vs direct Lambda invocation
- Lambda async invocation vs SQS event source mapping vs EventBridge rule
- Step Functions Standard vs Express vs SQS + Lambda

**Data and databases**
- RDS Multi-AZ vs Read Replica vs Aurora Global Database vs backup/restore
- DynamoDB GSI vs LSI vs Scan + FilterExpression vs duplicated table
- OpenSearch vs Athena vs Redshift vs DynamoDB
- Glue Crawler vs Glue Job vs Athena CTAS vs EMR

**Networking and edge**
- Gateway Endpoint vs Interface Endpoint vs NAT Gateway vs PrivateLink
- CloudFront vs Global Accelerator vs Route 53 latency routing
- Direct Connect Gateway vs Transit Gateway vs Site-to-Site VPN vs Cloud WAN
- API Gateway REST vs HTTP API vs ALB vs CloudFront

**Security**
- KMS key policy vs IAM policy vs bucket policy vs SCP
- GuardDuty vs Security Hub vs Detective vs AWS Config
- AWS WAF vs Shield Advanced vs Network Firewall vs Security Groups

**Storage and cost**
- EFS vs EBS vs FSx vs S3
- Savings Plans vs Reserved Instances vs Spot vs On-Demand

**AI and generative AI**
- Bedrock Knowledge Bases vs custom RAG vs Kendra vs OpenSearch vector search
- Bedrock Agents vs Step Functions for tool orchestration
