# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with Chainlit UI to analyze taxi trip data 
    from Microsoft Fabric lakehouse. Features include sample question hints, agent lifecycle 
    management, and interactive chat interface.

PREREQUISITES:
    1) Set up a Microsoft Fabric lakehouse with taxi trip data
    2) Configure your Azure AI Foundry project with appropriate model deployment
    
USAGE:
    chainlit run chainlit_app.py
 
    Before running the sample:
 
    pip install -r requirements.txt

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
import time
from typing import Optional
from dotenv import load_dotenv
import chainlit as cl

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Import taxi query functions
from taxi_query_functions import taxi_query_functions

# Load environment variables
load_dotenv()

# Sample questions extracted from sample.txt to define agent personality and provide hints
SAMPLE_QUESTIONS = [
    "Compare the total number of taxi trips on public holidays versus regular weekdays. In addition, analyze whether the average trip distance and average fare amount differ significantly between holidays and weekdays. Provide insights into whether people travel longer distances or pay higher fares during holidays.",
    "Count the number of trips with fare amounts greater than 70. Also, calculate the percentage of these high-fare trips relative to all trips.",
    "Compare the number of trips and average fare amount between daytime (7:00–19:00) and nighttime (19:00–7:00). Additionally, show whether trip distances differ between daytime and nighttime trips.",
    "Identify the pickup zip code with the highest number of trips. Provide the top 5 pickup zip codes ranked by trip volume.",
    "Determine the most frequent passenger count value (mode) in the dataset. Provide the distribution of passenger counts across all trips."
]

# Global variables for agent and client
project_client: Optional[AIProjectClient] = None
current_agent = None
current_thread = None


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session with agent and thread creation."""
    global project_client, current_agent, current_thread
    
    # Check required environment variables
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        await cl.Message(
            content=f"❌ Missing required environment variables: {', '.join(missing_vars)}\n"
                   "Please set these variables in your .env file or environment."
        ).send()
        return
    
    try:
        # Create the project client
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=os.environ["PROJECT_ENDPOINT"],
        )
        
        # Create function tool with taxi query functions
        functions = FunctionTool(functions=taxi_query_functions)
        toolset = ToolSet()
        toolset.add(functions)
        
        # Enable automatic function calls
        project_client.agents.enable_auto_function_calls(toolset)

        # Create agent with personality based on sample questions
        agent_instructions = """You are a professional taxi data analysis assistant specializing in analyzing taxi trip data from Microsoft Fabric lakehouse.

Your expertise includes analyzing:
- Public holidays vs weekdays trip patterns and fare comparisons
- High-fare trip analysis (trips > $70) and their percentage distribution  
- Daytime (7:00-19:00) vs nighttime (19:00-7:00) trip and fare patterns
- Geographic analysis including top pickup locations and zip codes
- Passenger count distributions and modal analysis

You should:
1. Provide clear, structured responses with specific numbers and statistics
2. Use appropriate functions to retrieve real data from the lakehouse
3. Offer insights and trends based on the data analysis
4. Present information in Traditional Chinese while preserving technical terms and field names in English
5. Always maintain a professional and helpful tone

When users ask about taxi trip data, provide comprehensive analysis including relevant statistics, trends, and actionable insights."""

        current_agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="TaxiDataAnalysisAgent",
            instructions=agent_instructions,
            toolset=toolset,
        )
        
        # Create thread for conversation
        current_thread = project_client.agents.threads.create()
        
        # Store agent info in user session
        cl.user_session.set("agent_id", current_agent.id)
        cl.user_session.set("thread_id", current_thread.id)
        cl.user_session.set("project_client", project_client)
        
        # Welcome message with agent ID and sample questions
        welcome_msg = f"🚕 **計程車數據分析助手已啟動**\n\n"
        welcome_msg += f"**Agent ID:** `{current_agent.id}`\n\n"
        welcome_msg += "我可以幫您分析 Microsoft Fabric lakehouse 中的計程車行程數據。\n\n"
        welcome_msg += "**建議的查詢問題:**"
        
        await cl.Message(content=welcome_msg).send()
        
        # Create hint buttons for sample questions
        actions = []
        for i, question in enumerate(SAMPLE_QUESTIONS, 1):
            # Truncate question for button display
            button_text = question[:60] + "..." if len(question) > 60 else question
            actions.append(
                cl.Action(
                    name=f"sample_q{i}",
                    value=question,
                    description=f"Question {i}",
                    label=f"📝 Q{i}: {button_text}"
                )
            )
        
        await cl.Message(
            content="點擊下方按鈕可直接送出範例問題:",
            actions=actions
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ 初始化失敗: {str(e)}"
        ).send()


@cl.action_callback("sample_q1")
async def on_sample_q1(action):
    """Handle sample question 1."""
    await process_query(action.value)


@cl.action_callback("sample_q2") 
async def on_sample_q2(action):
    """Handle sample question 2."""
    await process_query(action.value)


@cl.action_callback("sample_q3")
async def on_sample_q3(action):
    """Handle sample question 3."""
    await process_query(action.value)


@cl.action_callback("sample_q4")
async def on_sample_q4(action):
    """Handle sample question 4."""
    await process_query(action.value)


@cl.action_callback("sample_q5")
async def on_sample_q5(action):
    """Handle sample question 5."""
    await process_query(action.value)


async def process_query(query_content: str):
    """Process a user query through the agent."""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        thread_id = cl.user_session.get("thread_id")
        
        if not all([project_client, agent_id, thread_id]):
            await cl.Message(content="❌ 會話未正確初始化，請重新載入頁面").send()
            return
        
        # Show user query
        await cl.Message(content=f"**您的查詢:** {query_content}", author="User").send()
        
        # Show processing message
        processing_msg = await cl.Message(content="🔄 正在處理查詢...").send()
        
        # Create message in thread
        project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=query_content
        )
        
        # Process with retry mechanism
        max_retries = 3
        run = None
        
        for attempt in range(max_retries):
            try:
                # Create and process the run
                run = project_client.agents.runs.create_and_process(
                    thread_id=thread_id,
                    agent_id=agent_id
                )
                
                # Wait for completion
                while run.status in ["queued", "in_progress"]:
                    time.sleep(1)
                    run = project_client.agents.runs.get(thread_id=thread_id, run_id=run.id)
                
                if run.status == "completed":
                    break
                elif run.status == "failed":
                    error_msg = f"❌ 處理失敗 (嘗試 {attempt + 1}/{max_retries}): {run.last_error}"
                    if attempt == max_retries - 1:
                        await processing_msg.update(content=error_msg)
                        return
                else:
                    await processing_msg.update(content=f"⚠️ 處理完成，狀態: {run.status}")
                    return
                    
            except Exception as e:
                error_msg = f"❌ 處理錯誤 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                if attempt == max_retries - 1:
                    await processing_msg.update(content=error_msg)
                    return
                time.sleep(2)  # Wait before retry
        
        if run and run.status == "completed":
            # Get the latest assistant message
            messages = project_client.agents.messages.list(thread_id=thread_id)
            message_list = list(messages)
            
            for message in message_list:
                if message.role == "assistant":
                    # Update processing message with result
                    await processing_msg.update(content=f"**助手回覆:**\n\n{message.content}")
                    break
        else:
            await processing_msg.update(content="❌ 查詢處理失敗，請重試")
            
    except Exception as e:
        await cl.Message(content=f"❌ 處理過程中發生錯誤: {str(e)}").send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages."""
    await process_query(message.content)


@cl.on_chat_end
async def on_chat_end():
    """Clean up resources when chat session ends."""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        
        if project_client and agent_id:
            project_client.agents.delete_agent(agent_id)
            print(f"🧹 Cleaned up agent {agent_id}")
    except Exception as e:
        print(f"⚠️ Error cleaning up resources: {str(e)}")


if __name__ == "__main__":
    # For local development - use `chainlit run chainlit_app.py` instead
    pass