# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with Logic Apps to execute the task of sending an email.
 
PREREQUISITES:
    1) Create a Logic App within the same resource group as your Azure AI Project in Azure Portal
    2) To configure your Logic App to send emails, you must include an HTTP request trigger that is 
    configured to accept JSON with 'to', 'subject', and 'body'. The guide to creating a Logic App Workflow
    can be found here: 
    https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistants-logic-apps#create-logic-apps-workflows-for-function-calling
    
USAGE:
    python logic_apps.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.

    Replace the following values in the sample with your own values:
    1) <LOGIC_APP_NAME> - The name of the Logic App you created.
    2) <TRIGGER_NAME> - The name of the trigger in the Logic App you created (the default name for HTTP
        triggers in the Azure Portal is "When_a_HTTP_request_is_received").
    3) <RECIPIENT_EMAIL> - The email address of the recipient.
"""

# <imports>
import os
import requests
from typing import Set
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# Example user function
from user_functions import fetch_current_datetime

# Import AzureLogicAppTool and the function factory from user_logic_apps
from user_logic_apps import AzureLogicAppTool, create_send_email_function
# </imports>

# <client_initialization>
# Create the project client
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
# </client_initialization>

# <logic_app_tool_setup>
# Get subscription ID and resource group from environment variables
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
resource_group = os.environ.get("AZURE_RESOURCE_GROUP")

# Get Logic App configuration from environment variables
logic_app_name = os.environ.get("LOGIC_APP_NAME")
trigger_name = os.environ.get("TRIGGER_NAME")
recipient_email = os.environ.get("RECIPIENT_EMAIL")

# Check if required values are provided
required_env_vars = {
    "AZURE_SUBSCRIPTION_ID": subscription_id,
    "AZURE_RESOURCE_GROUP": resource_group,
    "LOGIC_APP_NAME": logic_app_name,
    "TRIGGER_NAME": trigger_name,
    "RECIPIENT_EMAIL": recipient_email,
}

missing_vars = []
for var_name, var_value in required_env_vars.items():
    if not var_value or var_value.startswith("your-"):
        missing_vars.append(var_name)

if missing_vars:
    print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in your .env file:")
    for var in missing_vars:
        print(f"   {var}=<your_value>")
    exit(1)

print(f"Using subscription ID: {subscription_id}")
print(f"Using resource group: {resource_group}")
print(f"Using Logic App name: {logic_app_name}")
print(f"Using trigger name: {trigger_name}")
print(f"Using recipient email: {recipient_email}")

print(f"Attempting to register Logic App: {logic_app_name}")
print(f"With trigger: {trigger_name}")

try:
    # Create and initialize AzureLogicAppTool utility
    logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
    logic_app_tool.register_logic_app(logic_app_name, trigger_name)
    print(f"✅ Successfully registered logic app '{logic_app_name}' with trigger '{trigger_name}'.")
except Exception as e:
    print(f"❌ Failed to register Logic App: {str(e)}")
    print("Please ensure:")
    print("1. The Logic App exists in the specified resource group")
    print("2. The trigger name matches exactly (case sensitive)")
    print("3. You have proper Azure permissions")
    exit(1)
# </logic_app_tool_setup>

# <function_creation>
# Create the specialized "send_email_via_logic_app" function for your agent tools
send_email_func = create_send_email_function(logic_app_tool, logic_app_name)

# Prepare the function tools for the agent
functions_to_use: Set = {
    fetch_current_datetime,
    send_email_func,  # This references the AzureLogicAppTool instance via closure
}
# </function_creation>

with project_client:
    # <agent_creation>
    # Create an agent
    functions = FunctionTool(functions=functions_to_use)
    toolset = ToolSet()
    toolset.add(functions)
    
    # Enable automatic function calls
    project_client.agents.enable_auto_function_calls(toolset)

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SendEmailAgent",
        instructions="You are a specialized agent for sending emails.",
        toolset=toolset,
    )
    print(f"Created agent, ID: {agent.id}")
    # </agent_creation>

    # <thread_management>
    # Create a thread for communication
    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create a message in the thread
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Hello, please send an email to {recipient_email} with the date and time in '%Y-%m-%d %H:%M:%S' format.",
    )
    print(f"Created message, ID: {message.id}")
    # </thread_management>

    # <message_processing>
    # Create and process an agent run in the thread
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    # </message_processing>

    # <cleanup>
    # Fetch and log all messages
    messages = project_client.agents.messages.list(thread_id=thread.id)
    print("\n=== 訊息歷史 ===")
    for message in messages:
        print(f"角色: {message.role}")
        if hasattr(message, 'content') and message.content:
            for content_item in message.content:
                if hasattr(content_item, 'text') and content_item.text:
                    print(f"內容: {content_item.text.value}")
        print("---")

    # Delete the agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")
