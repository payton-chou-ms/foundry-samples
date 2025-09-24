# Azure Databricks Teams Sample App - Architecture Documentation

## Overview

This is a Microsoft Teams bot application that integrates Azure AI Foundry with Azure Databricks Genie to provide intelligent data analytics through natural language conversations. The application enables users to query Databricks datasets directly from Teams and receive responses with visualizations and tabular data.

## Architecture Components

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Teams Client  │◄──►│  Teams Bot App  │◄──►│ Azure AI Agent  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Azure Blob      │    │ Azure Databricks│
                       │ Storage         │    │ Genie API       │
                       └─────────────────┘    └─────────────────┘
```

### Technology Stack

- **Framework**: Microsoft Agents SDK (aiohttp-based)
- **Authentication**: Microsoft Authentication Library (MSAL) with On-Behalf-Of (OBO) flow
- **AI Integration**: Azure AI Foundry Project with GPT-4o model
- **Data Source**: Azure Databricks with Genie Space
- **Storage**: Azure Blob Storage for visualization assets
- **Hosting**: Local development with DevTunnel (production deployment required)

## Key Features

### 1. Conversational AI Agent
- Natural language processing of business queries
- Context-aware conversations using conversation threading
- Specialized for sales pipeline and customer data analysis

### 2. Authentication & Authorization
- **On-Behalf-Of (OBO) Flow**: Acquires Azure Databricks tokens using user credentials
- **Microsoft Graph Integration**: Access to user profile information
- **Service Principal Authentication**: Backend service authentication

### 3. Data Analytics Integration
- **Genie API Integration**: Direct connection to Databricks Genie spaces
- **Dynamic Query Execution**: Real-time data retrieval and processing
- **Structured Data Handling**: Automatic formatting of query results

### 4. Visualization Capabilities
- **Code Interpreter Tool**: Dynamic chart and graph generation
- **Image Processing**: PNG visualization creation
- **Adaptive Cards**: Rich content display in Teams
- **Azure Blob Integration**: Secure image hosting for Teams

## Detailed Component Analysis

### 1. Application Entry Point (`app.py`)

#### Core Initialization
```python
# Global state management
adbtoken = None           # Azure Databricks access token
genie_spaceid = None      # Databricks Genie space identifier
project_client = None     # Azure AI Project client
agent = None              # AI Agent instance
thread = None             # Conversation thread
```

#### Key Configuration Classes
- **AgentApplication**: Main application framework
- **CloudAdapter**: Teams message handling
- **MsalConnectionManager**: Authentication management
- **Authorization**: Access control and token management

### 2. Authentication System

#### Token Acquisition Functions

**`getadbtoken(passed_user_access_token)`**
- **Purpose**: Acquires Azure Databricks token via OBO flow
- **Process**: 
  1. Retrieves AI Foundry project connection details
  2. Extracts Genie space ID from connection metadata
  3. Performs OAuth 2.0 token exchange for Databricks scope
  4. Returns access token for Genie API calls

**`getgraphtoken(passed_user_access_token)`**
- **Purpose**: Acquires Microsoft Graph token for user profile access
- **Scope**: `https://graph.microsoft.com/.default`

#### Authentication Flow
```
User Login → Teams Token → OBO Exchange → Databricks Token → Genie API Access
```

### 3. Message Processing Pipeline

#### Main Message Handler
**`on_message(context, state)`**
- **Decorators**: 
  - `@AGENT_APP.message(re.compile(r".*", re.IGNORECASE))`
  - `auth_handlers=["GRAPH"]`
- **Process**:
  1. Extract user prompt from Teams message
  2. Acquire necessary authentication tokens
  3. Process message through AI agent
  4. Return formatted response with optional visualizations

#### Core Processing Function
**`processmessage(question, conversation_id)`**
- **Agent Configuration**:
  - **Model**: GPT-4o (configurable via `MODEL_DEPLOYMENT_NAME`)
  - **Tools**: AsyncFunctionTool (Genie integration) + CodeInterpreterTool
  - **Instructions**: Specialized for sales and pipeline analytics

- **Agent Execution Flow**:
  1. Create agent with custom toolset
  2. Initialize conversation thread
  3. Submit user message
  4. Poll for completion with tool call handling
  5. Process results and generate visualizations
  6. Clean up agent resources

### 4. Databricks Genie Integration

#### Genie Query Function
**`ask_genie(question, conversation_id)`**
- **Connection Setup**:
  ```python
  workspace_client = WorkspaceClient(
      host=DATABRICKS_HOST,
      token=adbtoken  # OBO-acquired token
  )
  genie_api = GenieAPI(workspace_client.api_client)
  ```

- **Query Processing**:
  1. Start new conversation or continue existing one
  2. Submit question to Genie
  3. Retrieve structured query results
  4. Format response as JSON with conversation context

- **Data Formatting**:
  - **Tabular Data**: Markdown table format
  - **Numeric Data**: Proper formatting with commas and decimals
  - **Null Handling**: Explicit NULL representation

### 5. Visualization System

#### Image Processing Workflow
1. **Generation**: AI agent creates PNG visualizations using Code Interpreter
2. **Local Storage**: Temporary storage in `./images/` directory
3. **Upload**: Transfer to Azure Blob Storage for public access
4. **Display**: Embed in Teams Adaptive Cards
5. **Cleanup**: Automatic file deletion (implementation pending)

#### Blob Storage Integration
**`upload_blob_file(imagefilename)`**
- **Authentication**: DefaultAzureCredential with Blob Contributor role
- **Content Type**: Configured as `image/jpg`
- **Public Access**: Required for Teams display

#### Adaptive Cards
**`_send_custom_card(turn_context, imageurl)`**
- **Schema**: Adaptive Card v1.5
- **Content**: Image display with public blob URL
- **Integration**: Native Teams rich content support

## Configuration Management

### Environment Variables

#### Authentication Configuration
```bash
# Service Principal Credentials
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID=<client-id>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTSECRET=<client-secret>
CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID=<tenant-id>

# OAuth Flow Configuration
AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GRAPH__SETTINGS__AZUREBOTOAUTHCONNECTIONNAME=MSFTAAD
AGENTAPPLICATION__USERAUTHORIZATION__HANDLERS__GRAPH__SETTINGS__OBOCONNECTIONNAME=SERVICE_CONNECTION
```

#### Service Endpoints
```bash
# Azure AI Foundry
FOUNDRY_URL=<ai-foundry-project-endpoint>
ADB_CONNECTION_NAME=<databricks-connection-name>
MODEL_DEPLOYMENT_NAME=<deployed-model-name>

# Azure Databricks
DATABRICKS_HOST=<databricks-workspace-url>

# Azure Storage
STORAGE_ACCTNAME=<storage-account-name>
STORAGE_CONTNAME=<blob-container-name>
```

## Security Considerations

### Authentication & Authorization
- **Multi-layered Authentication**: Service principal + user tokens + OBO flow
- **Least Privilege Access**: Specific scopes for each service
- **Token Management**: Secure token acquisition and storage

### Data Security
- **In-Transit Encryption**: HTTPS for all API communications
- **At-Rest Security**: Azure-managed encryption for blob storage
- **Access Control**: Role-based access to storage and Databricks resources

### Required Azure RBAC Roles
- **Storage Blob Data Contributor**: For visualization uploads
- **AI Foundry Project Access**: For model and connection management
- **Databricks Workspace Access**: For Genie API operations

## Error Handling & Monitoring

### Custom Exception Handling
```python
class TeamsAppCustomException(Exception):
    """Custom exception for application-specific errors"""
```

### Key Error Scenarios
1. **Authentication Failures**: Invalid credentials or expired tokens
2. **Connection Issues**: Databricks workspace or AI Foundry unavailability
3. **Configuration Errors**: Missing or invalid environment variables
4. **API Limitations**: Genie API rate limits or query failures

### Logging Strategy
- **Development**: Console logging with stack traces
- **Production**: Azure Application Insights integration recommended

## Performance Considerations

### Optimization Strategies
1. **Token Caching**: Reuse valid tokens across requests
2. **Agent Lifecycle**: Create and destroy agents per request to prevent state issues
3. **Async Processing**: Non-blocking I/O for external API calls
4. **Resource Cleanup**: Automatic deletion of temporary files and agent instances

### Scalability Factors
- **Stateless Design**: No persistent state between requests
- **Connection Pooling**: Efficient resource utilization
- **Horizontal Scaling**: Support for multiple application instances

## Development Workflow

### Local Development Setup
1. **DevTunnel Configuration**: Secure tunneling for Teams integration
2. **Environment Configuration**: Local .env file setup
3. **Dependency Management**: Requirements.txt-based package installation
4. **Testing**: Manual testing through Teams interface

### Deployment Considerations
- **Production Hosting**: Azure App Service or Container Instances
- **CI/CD Pipeline**: Automated deployment with environment-specific configurations
- **Monitoring**: Application insights and health checks
- **Security Scanning**: Regular dependency and code security audits

## API Integration Details

### Microsoft Agents SDK
- **Version**: Latest compatible with Azure AI Foundry
- **Core Components**: Hosting, Authentication, Activity processing
- **Extension Points**: Custom tool integration and message handling

### Azure AI Projects SDK
- **Agent Management**: Dynamic agent creation and lifecycle
- **Tool Integration**: Function calling and code interpretation
- **Thread Management**: Conversation context preservation

### Databricks SDK
- **Genie API**: Direct integration with Databricks intelligence layer
- **Authentication**: Entra ID token-based access
- **Query Processing**: Structured data retrieval and formatting

## Future Enhancements

### Recommended Improvements
1. **Advanced Caching**: Redis integration for token and response caching
2. **Enhanced Security**: Certificate-based authentication
3. **Monitoring**: Comprehensive telemetry and alerting
4. **Multi-language Support**: Internationalization capabilities
5. **Advanced Visualizations**: Support for additional chart types
6. **Batch Processing**: Multiple query support in single conversation

### Production Readiness
- **High Availability**: Multi-region deployment
- **Disaster Recovery**: Backup and restore procedures
- **Performance Testing**: Load testing and optimization
- **Security Hardening**: Advanced threat protection integration

## Conclusion

This architecture provides a robust foundation for integrating Teams with Azure Databricks through AI-powered natural language processing. The modular design supports extensibility while maintaining security and performance standards suitable for enterprise deployment.