# UI Logic Apps - Chainlit Interface

This sample demonstrates how to use Azure AI Agents with Chainlit UI to execute Logic Apps workflows including sending emails and other automated tasks.

## Features

- Interactive Chainlit web interface
- Logic Apps workflow integration  
- Pre-configured sample action buttons
- Real-time task execution with status updates
- Automatic resource cleanup
- Traditional Chinese UI with English technical terms

## Prerequisites

1. **Azure AI Foundry Project**: Set up with model deployment
2. **Azure Logic App**: Create within the same resource group as your AI Project
3. **Logic App Configuration**: Set up HTTP trigger accepting JSON with 'to', 'subject', and 'body' parameters

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables by copying `.env.example` to `.env` and filling in your values:
```bash
cp .env.example .env
# Edit .env with your actual values
```

3. Required environment variables:
- `PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
- `MODEL_DEPLOYMENT_NAME`: Your AI model deployment name
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `AZURE_RESOURCE_GROUP`: Your resource group name
- `LOGIC_APP_NAME`: Your Logic App name
- `TRIGGER_NAME`: Your Logic App trigger name (usually "When_a_HTTP_request_is_received")
- `RECIPIENT_EMAIL`: Default email recipient address

## Usage

Run the Chainlit application:
```bash
chainlit run ui_logic_apps.py
```

The web interface will open at `http://localhost:8000` (or the port shown in terminal).

## Features

### Sample Actions
The interface provides 5 pre-configured action buttons:
1. **Send email with current date/time** - Fetches current timestamp and sends via email
2. **Send weather update** - Gets weather info for New York and emails it
3. **Send meeting reminder** - Sends a team meeting reminder
4. **Calculate and email result** - Performs calculation and sends result via email  
5. **Send welcome email** - Sends a friendly welcome message

### Custom Commands
You can also type custom commands in the chat interface, such as:
- "Send an email to user@example.com with subject 'Test' and body 'Hello world'"
- "Get the current weather for Tokyo and send it to the recipient"
- "Calculate the sum of 100 and 200, then email the result"

### Agent Capabilities
The Logic Apps agent can:
- Execute Logic Apps workflows
- Send automated emails
- Retrieve real-time data (date/time, weather)
- Perform calculations
- Integrate multiple functions into workflows

## File Structure

- `ui_logic_apps.py` - Main Chainlit application
- `logic_apps.py` - Original console version
- `user_logic_apps.py` - Logic Apps tool implementation
- `user_functions.py` - Utility functions
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `README.md` - This documentation

## Troubleshooting

### Common Issues

1. **Logic App registration fails**:
   - Verify Logic App exists in the specified resource group
   - Check trigger name matches exactly (case sensitive)
   - Ensure you have proper Azure permissions

2. **Environment variables not found**:
   - Make sure `.env` file is in the same directory
   - Verify all required variables are set
   - Check for typos in variable names

3. **Agent initialization fails**:
   - Verify Azure AI Foundry project endpoint is correct
   - Check model deployment name is valid
   - Ensure Azure credentials are properly configured

### Logs and Debugging

- Agent and thread IDs are displayed in the welcome message
- Status messages show execution progress
- Error messages provide specific failure details
- Console output shows resource cleanup information

## Comparison with Original Version

| Feature | `logic_apps.py` | `ui_logic_apps.py` |
|---------|----------------|-------------------|
| Interface | Console/CLI | Web UI (Chainlit) |
| Interaction | Single execution | Interactive chat |
| Sample tasks | None | 5 pre-configured buttons |
| Status updates | Basic print statements | Real-time UI updates |
| Error handling | Console output | Rich UI messages |
| Language | English | Traditional Chinese + English |
| Resource cleanup | Manual | Automatic on session end |

The UI version provides a much more user-friendly experience with visual feedback, interactive elements, and better error handling.