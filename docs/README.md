DataSyncLite
DataSyncLite is a production-grade ETL pipeline for near-real-time sales data processing. It extracts data from SQL Server, transforms it using PySpark on Databricks, and loads it into Azure Data Lake Gen2 (Delta Lake) for analytics.
Architecture

Extract: Incremental load from SQL Server using watermarking.
Transform: PySpark DataFrames for data cleaning, aggregation, and schema validation.
Load: Append to Delta Lake with schema evolution support.
Data Quality: Great Expectations for robust validation (nulls, positive values, date formats).
Security: Azure Key Vault, Azure AD, encryption at-rest/in-transit.
Observability: Azure Monitor with custom metrics, logs, and email alerts.
Automation: Azure DevOps CI/CD, Databricks Workflows, Terraform IaC.

Features

Reliability: Retries, circuit breakers, and 99.9% uptime.
Scalability: Dynamic resource allocation in Databricks.
Security: Least-privilege RBAC, audit logging.
Monitoring: Real-time metrics and dashboards in Azure Monitor.
Compliance: Audit trails for GDPR and internal policies.

Setup
See setup.md for detailed environment configuration and deployment steps.
Usage
Run the pipeline:
python src/datasync_lite/main.py --config configs/prod.yaml

Technology Stack

Core: Python 3.9, PySpark 3.3, Databricks Runtime 10.4 LTS
Databases: SQL Server on Azure, Delta Lake
Cloud: Microsoft Azure (Key Vault, Monitor, DevOps)
Tools: Great Expectations, pytest, Terraform, retry, circuitbreaker


