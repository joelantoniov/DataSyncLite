DataSyncLite Setup Guide
Prerequisites

Azure subscription with Owner role
Python 3.9
Terraform 1.5+
Azure CLI
Azure DevOps project with service connection
Databricks CLI
python-dotenv for local environment variable management

Environment Setup

Install Dependencies:
pip install -r requirements.txt


Set Up Local Environment:

Create a .env file in the project root based on .env.example:cp .env.example .env


Update .env with local/development credentials (e.g., SQL Server, Key Vault URLs). Never commit .env to version control.


Provision Infrastructure:
cd terraform
terraform init
terraform apply -var="sql_admin_password=<secure-password>"


Configure Key Vault:

Store SQL Server password as sqlserver-password-prod.
Assign RBAC roles for Databricks and pipeline service principal.


Set Up Databricks:

Create a premium-tier cluster (lite-cluster-001) with Runtime 10.4 LTS.
Install the datasync_lite wheel:python setup.py bdist_wheel
databricks fs cp dist/datasync_lite-0.1-py3-none-any.whl dbfs:/FileStore/wheels/


Install wheel on cluster via Databricks UI.


Initialize SQL Server:

Create sales table:CREATE TABLE sales (
    sales_id INT PRIMARY KEY,
    sales_amount DECIMAL(10,2),
    date DATE,
    updated_at DATETIME
);
CREATE TABLE watermark_log (
    watermark DATETIME,
    pipeline_id VARCHAR(50)
);





CI/CD Setup

Configure Azure DevOps pipeline using azure-pipelines.yml.
Set variables: DATABRICKS_WORKSPACE_URL, AzureServiceConnection.
Enable linting, testing, and deployment stages.

Scheduling

Create a Databricks Workflow:
Task: Run python src/datasync_lite/main.py --config configs/prod.yaml
Schedule: Daily at 1 AM UTC
Cluster: lite-cluster-001



Monitoring

Enable Azure Monitor in prod.yaml.
Configure Azure Monitor alerts:
Rule: Trigger email to ops@company.com on pipeline_errors > 0.


Create a dashboard for pipeline_runs and pipeline_errors metrics.

Security

Use Azure AD for authentication.
Enable audit logging in SQL Server and Key Vault.
Restrict SQL Server access to Azure services only.

Backup

Storage account uses Geo-Redundant Storage (GRS).
SQL Database retains backups for 30 days.

Local Testing

Load environment variables from .env:python -m dotenv run python src/datasync_lite/main.py --config configs/dev.yaml
