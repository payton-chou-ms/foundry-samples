# Azure Databricks Teams Sample App - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Azure Resource Setup](#azure-resource-setup)
3. [Environment Configuration](#environment-configuration)
4. [Local Development Setup](#local-development-setup)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Security Best Practices](#security-best-practices)

## Prerequisites

### Required Azure Services
- **Azure Subscription**: With appropriate permissions to create resources
- **Azure AI Foundry Hub & Project**: For AI model deployment
- **Azure Databricks Workspace**: With Genie space configured
- **Azure Storage Account**: For visualization storage
- **Azure Bot Service**: For Teams integration
- **Azure Active Directory**: For authentication and authorization

### Required Software
- **Python 3.13+**: Development environment
- **Azure CLI**: For resource management and authentication
- **DevTunnel**: For local development tunneling
- **VS Code**: Recommended IDE
- **Teams Admin Access**: For app deployment

### Required Permissions
- **Azure Subscription Contributor**: For resource creation
- **Teams Admin**: For bot and app registration
- **Azure AD Application Administrator**: For app registration

## Azure Resource Setup

### 1. Azure AI Foundry Setup

#### Create AI Foundry Hub
```bash
# Using Azure CLI
az extension add --name ml
az ml workspace create \
  --resource-group <resource-group> \
  --name <ai-foundry-hub-name> \
  --location <location> \
  --kind hub
```

#### Create AI Foundry Project
```bash
az ml workspace create \
  --resource-group <resource-group> \
  --name <ai-foundry-project-name> \
  --location <location> \
  --kind project \
  --hub-id /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.MachineLearningServices/workspaces/<hub-name>
```

#### Deploy AI Model
1. Navigate to AI Foundry Studio (https://ai.azure.com)
2. Select your project
3. Go to "Models + endpoints"
4. Deploy GPT-4o or compatible model
5. Note the **deployment name** for configuration

#### Create Databricks Connection
1. In AI Foundry Studio, go to "Connected Resources"
2. Click "Add Connection"
3. Select "Azure Databricks"
4. Configure connection with:
   - **Connection Name**: Record for `ADB_CONNECTION_NAME`
   - **Databricks Workspace URL**: Your workspace URL
   - **Connection Type**: Genie
   - **Genie Space ID**: Your configured Genie space

### 2. Azure Databricks Setup

#### Create Workspace
```bash
az databricks workspace create \
  --resource-group <resource-group> \
  --name <databricks-workspace-name> \
  --location <location> \
  --sku premium
```

#### Configure Genie Space
1. Access Databricks workspace
2. Navigate to SQL Warehouse
3. Create or configure Genie space
4. Upload sample dataset (recommended: Sales Pipeline data)
5. Test Genie queries to ensure functionality

### 3. Azure Storage Account Setup

#### Create Storage Account
```bash
az storage account create \
  --name <storage-account-name> \
  --resource-group <resource-group> \
  --location <location> \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot
```

#### Create Blob Container
```bash
az storage container create \
  --name <container-name> \
  --account-name <storage-account-name> \
  --public-access container
```

#### Configure RBAC Permissions
```bash
# Grant Storage Blob Data Contributor to your user account
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee <your-user-object-id> \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>"
```

### 4. Azure Bot Service Setup

#### Create Azure Bot
```bash
az bot create \
  --resource-group <resource-group> \
  --name <bot-name> \
  --kind registration \
  --endpoint https://<your-devtunnel-url>/api/messages \
  --appid <app-registration-id> \
  --password <app-registration-secret>
```

#### Configure Teams Channel
1. Go to Azure Portal → Bot Service → Channels
2. Click "Microsoft Teams"
3. Enable Teams channel
4. Configure messaging endpoint: `https://<your-devtunnel-url>/api/messages`

### 5. App Registration Setup

#### Create App Registration
```bash
az ad app create \
  --display-name <app-name> \
  --sign-in-audience AzureADMultipleOrgs
```

#### Configure API Permissions
Required permissions:
- **Microsoft Graph**: `User.Read` (delegated)
- **Azure Databricks**: `user_impersonation` (delegated)

#### Create Client Secret
```bash
az ad app credential reset \
  --id <app-id> \
  --display-name "Teams Bot Secret"
```

#### Configure Authentication
Add redirect URI: `https://token.botframework.com/.auth/web/redirect`

## Environment Configuration

### Create .env File
Copy `.env.TEMPLATE` to `.env` and configure:

```bash
# Agent Configuration
AGENT_APP=AdbAgent

# Service Principal Configuration
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<app-registration-id>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=<app-registration-secret>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<azure-tenant-id>

# OAuth Handler Configuration
AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GRAPH__SETTINGS__AZUREBOTOAUTHCONNECTIONNAME=MSFTAAD
AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GRAPH__SETTINGS__OBOCONNECTIONNAME=SERVICE_CONNECTION

# Azure Services Configuration
DATABRICKS_HOST=<databricks-workspace-url>
FOUNDRY_URL=<ai-foundry-project-endpoint>
ADB_CONNECTION_NAME=<databricks-connection-name>
MODEL_DEPLOYMENT_NAME=<deployed-model-name>

# Storage Configuration
STORAGE_ACCTNAME=<storage-account-name>
STORAGE_CONTNAME=<blob-container-name>
```

### Configuration Value Sources

#### AI Foundry Project Endpoint
- Location: AI Foundry Studio → Project Overview → Endpoint URL
- Format: `https://<project-name>.<region>.api.azureml.ms`

#### Databricks Workspace URL
- Location: Azure Portal → Databricks Workspace → URL
- Format: `https://<workspace-id>.<region>.azuredatabricks.net`

#### Model Deployment Name
- Location: AI Foundry Studio → Models + endpoints → Name column
- Example: `gpt-4o-deployment-001`

## Local Development Setup

### 1. DevTunnel Configuration

#### Install DevTunnel
```bash
# Windows
winget install Microsoft.devtunnel
```

#### Create Persistent Tunnel
```bash
# Create tunnel
devtunnel create my-tunnel -a

# Add HTTP port
devtunnel port create my-tunnel -p 3978

# Host tunnel
devtunnel host my-tunnel
```

#### Record Tunnel URL
Note the HTTPS URL (e.g., `https://dl5zst7j-3978.usw3.devtunnels.ms`)

### 2. Python Environment Setup

#### Create Virtual Environment
```bash
python -m venv adb-teams-env
source adb-teams-env/bin/activate  # Linux/Mac
# or
adb-teams-env\Scripts\activate  # Windows
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Verify Installation
```bash
python -c "import azure.ai.projects; print('Dependencies installed successfully')"
```

### 3. Azure CLI Authentication

#### Login to Azure
```bash
az login
```

#### Set Default Subscription
```bash
az account set --subscription <subscription-id>
```

#### Verify Authentication
```bash
az account show
```

### 4. Teams App Manifest

#### Create Manifest
1. Go to https://dev.teams.microsoft.com/
2. Create new app
3. Configure basic information:
   - **App Name**: Azure Databricks Genie Bot
   - **Developer Name**: Your organization
   - **App Description**: AI-powered data analytics for Teams

#### Configure Bot
1. In manifest editor, go to "App features" → "Bot"
2. Add bot ID: `<your-app-registration-id>`
3. Set messaging endpoint: `https://<your-devtunnel-url>/api/messages`
4. Enable required scopes:
   - `personal`
   - `team`
   - `groupchat`

#### Download Manifest
1. Go to "Publish" → "Download app package"
2. Save `.zip` file for Teams upload

### 5. Teams Admin Center Configuration

#### Upload App
1. Go to https://admin.teams.microsoft.com/
2. Navigate to "Teams apps" → "Manage apps"
3. Click "Upload new app"
4. Select manifest `.zip` file
5. Approve app for organization

## Production Deployment

### 1. Azure App Service Deployment

#### Create App Service Plan
```bash
az appservice plan create \
  --name <app-service-plan-name> \
  --resource-group <resource-group> \
  --sku B1 \
  --is-linux
```

#### Create Web App
```bash
az webapp create \
  --resource-group <resource-group> \
  --plan <app-service-plan-name> \
  --name <webapp-name> \
  --runtime "PYTHON:3.11"
```

#### Configure Application Settings
```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group <resource-group> \
  --name <webapp-name> \
  --settings \
    FOUNDRY_URL="<ai-foundry-project-endpoint>" \
    ADB_CONNECTION_NAME="<databricks-connection-name>" \
    MODEL_DEPLOYMENT_NAME="<deployed-model-name>" \
    # ... add all other environment variables
```

#### Deploy Code
```bash
# Using local Git deployment
git remote add azure https://<webapp-name>.scm.azurewebsites.net/<webapp-name>.git
git push azure main
```

### 2. Update Bot Configuration

#### Update Messaging Endpoint
```bash
az bot update \
  --resource-group <resource-group> \
  --name <bot-name> \
  --endpoint https://<webapp-name>.azurewebsites.net/api/messages
```

### 3. Configure Managed Identity (Recommended)

#### Enable System-Assigned Identity
```bash
az webapp identity assign \
  --resource-group <resource-group> \
  --name <webapp-name>
```

#### Grant Storage Permissions
```bash
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee <webapp-managed-identity-id> \
  --scope "/subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.Storage/storageAccounts/<storage-account-name>"
```

### 4. Application Insights (Optional)

#### Create Application Insights
```bash
az extension add --name application-insights
az monitor app-insights component create \
  --resource-group <resource-group> \
  --app <app-insights-name> \
  --location <location>
```

#### Configure Monitoring
```bash
az webapp config appsettings set \
  --resource-group <resource-group> \
  --name <webapp-name> \
  --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY="<instrumentation-key>"
```

## Troubleshooting

### Common Issues

#### Authentication Errors

**Symptom**: "Error occurred while fetching ADB token"
**Causes**:
- Invalid service principal credentials
- Incorrect tenant ID
- Missing app registration permissions

**Solutions**:
1. Verify service principal credentials in Azure Portal
2. Check tenant ID matches Azure subscription
3. Ensure API permissions are granted and admin consent given
4. Test token acquisition manually:
   ```bash
   az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d
   ```

#### Configuration Issues

**Symptom**: "Azure Foundry URL is either incorrect or the Databaricks Genie connection isn't configured"
**Causes**:
- Incorrect AI Foundry project endpoint
- Missing or misconfigured Databricks connection
- Connection not configured as 'genie' type

**Solutions**:
1. Verify project endpoint in AI Foundry Studio
2. Check connection configuration in "Connected Resources"
3. Ensure Genie space ID is properly set
4. Test connection manually in AI Foundry

#### Teams Integration Issues

**Symptom**: Bot not responding in Teams
**Causes**:
- Incorrect messaging endpoint
- Bot not properly registered
- DevTunnel not running (local development)

**Solutions**:
1. Verify messaging endpoint in Bot Service configuration
2. Check DevTunnel status: `devtunnel show my-tunnel`
3. Test endpoint directly: `curl https://<endpoint>/api/messages`
4. Check bot registration in Teams Admin Center

#### Storage Upload Failures

**Symptom**: Visualization images not displaying
**Causes**:
- Missing Storage Blob Data Contributor role
- Container not configured for public access
- Network connectivity issues

**Solutions**:
1. Verify RBAC assignments:
   ```bash
   az role assignment list --assignee <user-or-service-principal-id>
   ```
2. Check container public access settings
3. Test blob upload manually:
   ```bash
   az storage blob upload --account-name <account> --container-name <container> --name test.png --file test.png
   ```

### Debugging Techniques

#### Enable Verbose Logging
Add to Python code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Test Individual Components

**Test Genie Connection**:
```python
from databricks.sdk import WorkspaceClient
client = WorkspaceClient(host="<host>", token="<token>")
# Test basic connectivity
```

**Test AI Foundry Connection**:
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
client = AIProjectClient("<endpoint>", DefaultAzureCredential())
# Test project access
```

**Test Storage Access**:
```python
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
client = BlobServiceClient("<account-url>", DefaultAzureCredential())
# Test container access
```

#### Monitor Resource Logs

**Azure App Service**:
```bash
az webapp log tail --resource-group <resource-group> --name <webapp-name>
```

**Application Insights**:
- Check exception traces
- Monitor API call patterns
- Review performance metrics

## Security Best Practices

### Authentication Security

#### Service Principal Management
- Use separate service principals for dev/test/prod
- Rotate client secrets regularly (recommended: 90 days)
- Apply principle of least privilege
- Monitor service principal usage in audit logs

#### Token Security
- Never log access tokens
- Implement token refresh logic
- Use shortest possible token lifetime
- Validate token scopes before use

### Network Security

#### Production Deployment
- Enable HTTPS only for web app
- Configure custom domain with SSL certificate
- Implement IP restrictions if required
- Use Azure Front Door or Application Gateway for additional protection

#### Databricks Security
- Enable IP access lists if applicable
- Use private endpoints for enhanced security
- Implement conditional access policies
- Monitor workspace access logs

### Data Privacy

#### Storage Security
- Enable blob encryption at rest
- Configure lifecycle policies for automatic cleanup
- Implement soft delete for blob recovery
- Monitor storage access logs

#### Compliance Considerations
- Implement data retention policies
- Consider data residency requirements
- Ensure GDPR compliance if applicable
- Document data processing activities

### Monitoring and Alerting

#### Key Metrics to Monitor
- Authentication failure rates
- API response times
- Storage upload success rates
- Bot message processing times
- Error rates by component

#### Recommended Alerts
- Authentication failures > threshold
- Storage quota approaching limit
- High error rate in bot responses
- Databricks connection failures
- AI model quota exhaustion

#### Security Monitoring
- Failed authentication attempts
- Unusual access patterns
- Service principal credential changes
- Resource configuration modifications

### Backup and Recovery

#### Configuration Backup
- Export app registration settings
- Document environment variable configurations
- Backup Teams app manifest
- Save deployment scripts and documentation

#### Data Recovery
- Configure blob storage soft delete
- Implement cross-region replication if required
- Test disaster recovery procedures
- Document recovery time objectives (RTO) and recovery point objectives (RPO)

This deployment guide provides comprehensive instructions for setting up and maintaining the Azure Databricks Teams Sample App in both development and production environments. Follow the security best practices to ensure a robust and secure deployment.