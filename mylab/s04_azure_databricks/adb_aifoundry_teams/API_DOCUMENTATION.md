# Azure Databricks Teams Sample App - API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Authentication APIs](#authentication-apis)
3. [Core Application APIs](#core-application-apis)
4. [Genie Integration APIs](#genie-integration-apis)
5. [Storage APIs](#storage-apis)
6. [Teams Integration APIs](#teams-integration-apis)
7. [Error Handling](#error-handling)
8. [Request/Response Examples](#requestresponse-examples)

## Overview

This document provides detailed API documentation for the Azure Databricks Teams Sample App. The application exposes various internal APIs for authentication, data processing, visualization, and Teams integration.

## Authentication APIs

### `getadbtoken(passed_user_access_token)`

Acquires Azure Databricks access token using On-Behalf-Of (OBO) flow.

**Parameters:**
- `passed_user_access_token` (str): User's access token from Teams authentication

**Returns:**
- `str`: Azure Databricks access token

**Process:**
1. Retrieves AI Foundry project connection details
2. Extracts Genie space ID from connection metadata
3. Performs OAuth 2.0 token exchange
4. Returns Databricks-scoped access token

**OAuth Flow Details:**
```python
# Token exchange request
data = {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default",  # Databricks scope
    "requested_token_use": "on_behalf_of",
    "assertion": passed_user_access_token,
}
```

**Error Conditions:**
- Invalid user token
- Missing service principal credentials
- AI Foundry connection not found
- Databricks connection not configured as 'genie' type

**Exceptions:**
- `TeamsAppCustomException`: "Error obtaining Azure Databricks Connection from Azure Foundry Project or unable to get ADB token via OBO Flow!"

### `getgraphtoken(passed_user_access_token)`

Acquires Microsoft Graph access token for user profile operations.

**Parameters:**
- `passed_user_access_token` (str): User's access token from Teams authentication

**Returns:**
- `str`: Microsoft Graph access token

**Scope:**
- `https://graph.microsoft.com/.default`

**Error Conditions:**
- Invalid user credentials
- Service principal authentication failure
- Token exchange failure

**Exceptions:**
- `TeamsAppCustomException`: "Error obtaining the user's profile via graph api!"

## Core Application APIs

### Agent Application Decorators

#### `@AGENT_APP.activity(ActivityTypes.invoke)`
**Function:** `invoke(context: TurnContext, state: TurnState)`

Handles template expansion or function invocation activities.

**Parameters:**
- `context` (TurnContext): Teams conversation context
- `state` (TurnState): Current conversation state

**Returns:**
- `str`: Processing result

#### `@AGENT_APP.on_sign_in_success`
**Function:** `handle_sign_in_success(context: TurnContext, state: TurnState, handler_id: str)`

Processes successful authentication events.

**Parameters:**
- `context` (TurnContext): Teams conversation context
- `state` (TurnState): Current conversation state
- `handler_id` (str, optional): Authentication handler identifier

**Returns:**
- `bool`: Success indicator

#### `@AGENT_APP.conversation_update("membersAdded")`
**Function:** `on_members_added(context: TurnContext, _state: TurnState)`

Handles new member additions to Teams conversation.

**Parameters:**
- `context` (TurnContext): Teams conversation context
- `_state` (TurnState): Current conversation state (unused)

**Returns:**
- `bool`: Always returns `True`

**Response Message:**
```
"Welcome to the ADB-AIFoundry-Teams demo!"
"For OAuth flows, enter the 6-digit verification code when prompted."
```

#### `@AGENT_APP.error`
**Function:** `on_error(context: TurnContext, error: Exception)`

Global error handler for unhandled exceptions.

**Parameters:**
- `context` (TurnContext): Teams conversation context
- `error` (Exception): Caught exception

**Actions:**
1. Logs error to console/stderr
2. Prints stack trace
3. Sends error message to user

### Main Message Processing

#### `@AGENT_APP.message(re.compile(r".*", re.IGNORECASE), auth_handlers=["GRAPH"])`
**Function:** `on_message(context: TurnContext, state: TurnState)`

Primary message handler with authentication integration.

**Parameters:**
- `context` (TurnContext): Teams conversation context containing user message
- `state` (TurnState): Current conversation state

**Authentication:**
- Requires GRAPH authentication handler
- Automatically acquires user tokens

**Process Flow:**
1. Extract user prompt from `context.activity.text`
2. Send "thinking" message to user
3. Acquire Databricks token if needed
4. Process message through AI agent
5. Return response with optional visualizations

**Error Handling:**
- `TeamsAppCustomException`: Authentication or configuration errors
- General exceptions: Stack trace sent to user

## Genie Integration APIs

### `ask_genie(question: str, conversation_id: str = None)`

Core function for interacting with Databricks Genie API.

**Parameters:**
- `question` (str): Natural language query
- `conversation_id` (str, optional): Existing conversation ID for context continuity

**Returns:**
- `tuple[str, str]`: Response content and image URL (if generated)

**Response Format (JSON):**
```json
{
    "conversation_id": "string",
    "table": {
        "columns": ["column1", "column2"],
        "rows": [["value1", "value2"]]
    }
}
```

**OR**

```json
{
    "conversation_id": "string", 
    "message": "text response"
}
```

**Error Response:**
```json
{
    "error": "An error occurred while talking to Genie.",
    "details": "specific error message"
}
```

**Data Type Formatting:**
- `DECIMAL/DOUBLE/FLOAT`: Formatted with commas and 2 decimal places
- `INT/BIGINT/LONG`: Formatted with commas
- `NULL`: Displayed as "NULL"
- Other types: String conversion

**Genie API Operations:**
1. **New Conversation**: `genie_api.start_conversation_and_wait()`
2. **Continue Conversation**: `genie_api.create_message_and_wait()`
3. **Retrieve Results**: `genie_api.get_message_query_result()`
4. **Format Response**: Structure data for consumption

### `processmessage(question: str, conversation_id: str = None)`

Main AI agent processing function integrating Genie functionality.

**Parameters:**
- `question` (str): User's natural language question
- `conversation_id` (str, optional): Conversation context

**Returns:**
- `tuple[str, str]`: (response_text, image_filename)

**AI Agent Configuration:**
```python
{
    "name": "my-assistant",
    "model": "gpt-4o",  # Configurable via MODEL_DEPLOYMENT_NAME
    "instructions": "Sales and pipeline analysis specialist",
    "toolset": [AsyncFunctionTool, CodeInterpreterTool]
}
```

**Tool Execution Flow:**
1. Create agent with Genie function tool
2. Initialize conversation thread
3. Submit user message
4. Poll for completion with required action handling
5. Execute function calls and code interpretation
6. Extract response and generated files
7. Clean up agent resources

**File Processing:**
- **Text Content**: Direct response text
- **Image Files**: PNG visualizations saved to local directory
- **Blob Upload**: Automatic upload to Azure Storage
- **Adaptive Cards**: Teams-compatible rich content

## Storage APIs

### `upload_blob_file(imagefilename)`

Uploads visualization files to Azure Blob Storage for public access.

**Parameters:**
- `imagefilename` (str): Local filename to upload

**Configuration:**
- **Account URL**: `https://{STORAGE_ACCTNAME}.blob.core.windows.net`
- **Container**: `{STORAGE_CONTNAME}`
- **Authentication**: DefaultAzureCredential
- **Content Type**: `image/jpg`

**Required Permissions:**
- **Storage Blob Data Contributor** role on storage account/container

**Process:**
1. Initialize BlobServiceClient with DefaultAzureCredential
2. Read local file from `./images/` directory
3. Upload with appropriate content settings
4. Enable public access for Teams display

**Error Conditions:**
- Missing authentication credentials
- Insufficient RBAC permissions
- Network connectivity issues
- Storage account configuration problems

### `del_blob_file(imagefilename)`

Deletes files from Azure Blob Storage (currently unused).

**Parameters:**
- `imagefilename` (str): Blob filename to delete

**Status:** Implementation present but not currently invoked

**Exceptions:**
- `TeamsAppCustomException`: "Error deleting file from Azure Blob Storage Container."

## Teams Integration APIs

### `_send_custom_card(turn_context: TurnContext, imageurl: str)`

Sends rich adaptive cards with visualizations to Teams.

**Parameters:**
- `turn_context` (TurnContext): Teams conversation context
- `imageurl` (str): Local filename of image to display

**Adaptive Card Schema:**
```json
{
    "type": "AdaptiveCard",
    "$schema": "https://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.5",
    "body": [
        {
            "type": "Image",
            "id": "0001",
            "url": "https://{STORAGE_ACCTNAME}.blob.core.windows.net/{STORAGE_CONTNAME}/{imageurl}"
        }
    ]
}
```

**Content Type:** `application/vnd.microsoft.card.adaptive`

**Process:**
1. Construct blob URL from storage configuration
2. Create adaptive card JSON structure
3. Generate Teams attachment
4. Send via MessageFactory.attachment()

**Error Handling:**
- Exception details sent to user via text message
- Graceful degradation if card rendering fails

## Error Handling

### Custom Exception Class

```python
class TeamsAppCustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
```

### Common Error Scenarios

#### Authentication Errors
- **Invalid Credentials**: Service principal configuration issues
- **Token Expiration**: Need for token refresh
- **Permission Denied**: Insufficient RBAC roles

#### Configuration Errors
- **Missing Environment Variables**: Required settings not provided
- **Invalid Endpoints**: Incorrect service URLs
- **Connection Failures**: Network or service unavailability

#### API Errors
- **Genie API Limits**: Rate limiting or quota exceeded
- **Model Deployment Issues**: AI model not available
- **Storage Access Denied**: Blob storage permission problems

### Error Response Patterns

**Authentication Failure:**
```
"Error occurred while fetching ADB token."
```

**Configuration Issues:**
```
"Azure Foundry URL is either incorrect or the Databaricks Genie connection isn't configured for the Azure AI Foundry project."
```

**General Errors:**
```
Stack trace details sent directly to Teams conversation
```

## Request/Response Examples

### Example 1: Simple Data Query

**User Input:**
```
"What is the total pipeline amount by region?"
```

**Genie API Call:**
```python
ask_genie("What is the total pipeline amount by region?", None)
```

**Genie Response:**
```json
{
    "conversation_id": "conv_12345",
    "table": {
        "columns": ["Region", "Total Pipeline Amount"],
        "rows": [
            ["APAC", "153,997.21"],
            ["LATAM", "136,002.08"],
            ["EMEA", "141,998.18"],
            ["AMER", "60,003.91"]
        ]
    }
}
```

**Teams Response:**
```
Here is the total pipeline amount by region:

| Region | Total Pipeline Amount |
|--------|----------------------|
| APAC   | 153,997.21          |
| LATAM  | 136,002.08          |
| EMEA   | 141,998.18          |
| AMER   | 60,003.91           |

Please let me know if you would like a visualization of this data.
```

### Example 2: Visualization Request

**User Input:**
```
"Show the top sales reps by pipeline in a pie chart"
```

**Processing Flow:**
1. `ask_genie()` retrieves sales rep data
2. Code Interpreter generates pie chart
3. Image saved as PNG file
4. File uploaded to blob storage
5. Adaptive card sent to Teams

**Teams Response:**
1. **Text Response:**
   ```
   Here is the data for the top sales reps by the pipeline generated:
   
   | Name | Total Pipeline |
   |------|---------------|
   | Alejandro Baldwin | 1,583,989.86 |
   
   The top sales rep is Alejandro Baldwin, who has generated a pipeline of $1,583,989.86.
   ```

2. **Visual Response:**
   - Adaptive card with embedded pie chart image
   - Image hosted on Azure Blob Storage
   - Interactive display within Teams

### Example 3: Conversation Continuation

**First Message:**
```
"What is the average transaction value?"
```

**Response includes:**
```json
{
    "conversation_id": "conv_67890",
    "message": "The average transaction value is $45,250."
}
```

**Second Message:**
```
"How many transactions were above that value?"
```

**Processing:**
- Uses `conversation_id: "conv_67890"` to maintain context
- Genie understands "that value" refers to previous $45,250
- Returns contextually aware response

### Example 4: Error Scenarios

**Authentication Error:**
```
User Input: "Show me the sales data"
Response: "Error occurred while fetching ADB token."
```

**Configuration Error:**
```
User Input: "Generate a report"
Response: "Azure Foundry URL is either incorrect or the Databaricks Genie connection isn't configured for the Azure AI Foundry project."
```

**API Error:**
```json
{
    "error": "An error occurred while talking to Genie.",
    "details": "Rate limit exceeded for Genie API calls"
}
```

## API Rate Limits and Constraints

### Azure Databricks Genie
- **Rate Limiting**: Subject to Databricks workspace limits
- **Concurrent Requests**: Limited by token availability
- **Query Complexity**: Large dataset queries may timeout

### Azure AI Foundry
- **Model Tokens**: Subject to deployment quota limits
- **Request Frequency**: Standard Azure API throttling
- **Agent Lifecycle**: New agent created per conversation

### Azure Blob Storage
- **Upload Limits**: Standard blob size restrictions
- **Request Limits**: Subject to storage account throttling
- **Public Access**: Requires appropriate container permissions

## Security Considerations

### Token Security
- **In-Memory Storage**: Tokens not persisted between requests
- **Scope Limitation**: Minimum required permissions
- **Automatic Expiration**: Tokens refresh as needed

### Data Privacy
- **User Data**: Only processed for current conversation
- **Temporary Files**: Local images deleted after upload
- **Conversation Context**: Not persisted beyond session

### Access Control
- **RBAC Enforcement**: Azure role-based permissions
- **Authentication Required**: No anonymous access
- **Audit Logging**: Standard Azure service logs