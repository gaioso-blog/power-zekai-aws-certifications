# DEA-C01 — AWS Certified Data Engineer - Associate

> Helper study map. The official exam guide is always the primary source of truth.
> Never claim a service is in scope unless the guide supports it.

## Main focus

Data ingestion, transformation, orchestration, storage, governance, monitoring, and data pipeline operations.

## Common service families

- **Data ingestion:** Kinesis Data Streams, Kinesis Data Firehose, Amazon MSK, AWS DMS, AWS DataSync
- **Storage:** S3, Lake Formation, Glue Data Catalog
- **Processing:** AWS Glue, Glue Studio, Glue Crawlers, EMR, Lambda, Step Functions
- **Analytics:** Athena, Redshift, OpenSearch, QuickSight
- **Governance and security:** Lake Formation, IAM, KMS, Macie, CloudTrail

## Question style

Prefer scenarios involving batch versus streaming, schema evolution, data cataloging, partitioning, compression, ETL job design, pipeline monitoring, data quality, and least privilege for data lakes.

## Common traps

- Confusing Kinesis Data Streams (retention and replay) with Firehose (managed delivery, no replay)
- Choosing a Glue Crawler when an explicit schema definition is required
- Ignoring partitioning and file size when the scenario stresses Athena cost or performance
- Confusing Lake Formation permissions with plain IAM and S3 bucket policies
- Choosing EMR when a serverless Glue job meets the operational overhead requirement
- Assuming Redshift is appropriate for high-concurrency low-latency key lookups
- Confusing Glue job bookmarks with Kinesis checkpoints for incremental processing
