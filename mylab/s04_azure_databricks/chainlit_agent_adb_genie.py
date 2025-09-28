# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use the Databricks connector in 
    Azure AI Foundry with Databricks to access Genie (using the Genie API)
    through a Chainlit UI with sample question buttons and agent lifecycle management.

USAGE:
    chainlit run chainlit_agent_adb_genie.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity databricks-sdk chainlit

    Set these environment variables in .env file:
    1) FOUNDRY_PROJECT_ENDPOINT - The endpoint of your Azure AI Foundry project, as found in the "Overview" tab
       in your Azure AI Foundry project.
    2) FOUNDRY_DATABRICKS_CONNECTION_NAME - The name of the Databricks connection, as found in the "Connected Resources" under "Management Center" tab
       in your Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import json
import os
from databricks.sdk import WorkspaceClient
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from databricks.sdk.service.dashboards import GenieAPI
from azure.ai.agents.models import (FunctionTool, ToolSet)
from typing import Any, Callable, Set
from dotenv import load_dotenv
import chainlit as cl

# 從 .env 檔案載入環境變數
load_dotenv()

os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"

DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default" 

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_DATABRICKS_CONNECTION_NAME = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")

if not FOUNDRY_PROJECT_ENDPOINT:
    raise ValueError("FOUNDRY_PROJECT_ENDPOINT environment variable is required")
if not FOUNDRY_DATABRICKS_CONNECTION_NAME:
    raise ValueError("FOUNDRY_DATABRICKS_CONNECTION_NAME environment variable is required")

# sample.txt 中的指令
AGENT_INSTRUCTIONS = """
You are a data analysis agent connected to the Databricks "samples.nyctaxi.trips" dataset. 
Your role is to help users explore and analyze taxi trip data. 
You should respond to natural language queries by generating SQL queries and summarizing results.

You can answer the following types of questions:
1. Fare statistics: e.g., average, maximum, or minimum fare amount.
2. Time-based trends: e.g., trip counts by hour, day, or week.
3. Distance vs fare analysis: e.g., correlation between distance and fare, fare distribution by distance.
4. Geographic comparisons: e.g., which pickup or dropoff zip codes have the highest average fare.
5. Outlier detection: e.g., identify trips with unusually high fares relative to distance.

Always explain your answer clearly, and when relevant, show both the query and a short natural-language summary of the results.
"""

# sample.txt 中的範例問題
SAMPLE_QUESTIONS = [
    "What is the average fare amount per trip? (平均車資)",
    "How does the number of trips vary by hour of the day or day of the week? (依時間的趨勢)",
    "What is the correlation between trip distance and fare amount? (距離 vs 車資關係)",
    "Which pickup zip codes have the highest average fares? (地區比較)",
    "Are there any outlier trips with unusually high fare amounts compared to their distance? (異常值分析)"
]

##################
# agent 元件的全域變數
credential = None
project_client = None
genie_api = None
genie_space_id = None
databricks_workspace_client = None

def ask_genie(question: str, conversation_id: str = None) -> str:
    """
    向 Genie 提問並以 JSON 格式回傳回應。
    回應 JSON 將包含對話 ID 以及訊息內容或結果表格。
    在後續呼叫中重複使用對話 ID 以繼續對話並保持上下文。
    
    param question: 要向 Genie 提出的問題。
    param conversation_id: 要繼續的對話 ID。若為 None，將開始新對話。
    """
    try:
        if conversation_id is None:
            message = genie_api.start_conversation_and_wait(genie_space_id, question)
            conversation_id = message.conversation_id
        else:
            message = genie_api.create_message_and_wait(genie_space_id, conversation_id, question)

        query_result = None
        if message.query_result:
            query_result = genie_api.get_message_query_result(
                genie_space_id, message.conversation_id, message.id
            )

        message_content = genie_api.get_message(genie_space_id, message.conversation_id, message.id)

        # 嘗試解析結構化資料（如果有的話）
        if query_result and query_result.statement_response:
            statement_id = query_result.statement_response.statement_id
            results = databricks_workspace_client.statement_execution.get_statement(statement_id)
            columns = results.manifest.schema.columns
            data = results.result.data_array
            headers = [col.name for col in columns]
            rows = []
            for row in data:
                formatted_row = []
                for value, col in zip(row, columns):
                    if value is None:
                        formatted_value = "NULL"
                    elif col.type_name in ["DECIMAL", "DOUBLE", "FLOAT"]:
                        formatted_value = f"{float(value):,.2f}"
                    elif col.type_name in ["INT", "BIGINT", "LONG"]:
                        formatted_value = f"{int(value):,}"
                    else:
                        formatted_value = str(value)
                    formatted_row.append(formatted_value)
                rows.append(formatted_row)
            return json.dumps({
                "conversation_id": conversation_id,
                "table": {
                    "columns": headers,
                    "rows": rows
                }
            })

        # 回退到純文字訊息
        if message_content.attachments:
            for attachment in message_content.attachments:
                if attachment.text and attachment.text.content:
                    return json.dumps({
                        "conversation_id": conversation_id,
                        "message": attachment.text.content
                    })

        return json.dumps({
            "conversation_id": conversation_id,
            "message": message_content.content or "No content returned."
        })

    except Exception as e:
        return json.dumps({
            "error": "An error occurred while talking to Genie.",
            "details": str(e)
        })

@cl.on_chat_start
async def start():
    """聊天開始時初始化 agent 和 UI 元件。"""
    global credential, project_client, genie_api, genie_space_id, databricks_workspace_client
    
    try:
        # 初始化 Azure 憑證和客戶端
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        
        project_client = AIProjectClient(
            FOUNDRY_PROJECT_ENDPOINT,
            credential
        )
        
        connection = project_client.connections.get(FOUNDRY_DATABRICKS_CONNECTION_NAME)
        
        if connection.metadata['azure_databricks_connection_type'] == 'genie':
            genie_space_id = connection.metadata['genie_space_id']
        else:
            raise ValueError("Connection is not of type 'genie', please check the connection type.")

        databricks_workspace_client = WorkspaceClient(
            host=connection.target,
            token=credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default").token,
        )

        genie_api = GenieAPI(databricks_workspace_client.api_client)

        # 建立工具組
        toolset = ToolSet()
        user_functions: Set[Callable[..., Any]] = {ask_genie}
        functions = FunctionTool(functions=user_functions)
        toolset.add(functions)

        # 建立 agent
        project_client.agents.enable_auto_function_calls(toolset)
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT_NAME,
            name="Databricks Taxi Data Analysis Agent",
            instructions=AGENT_INSTRUCTIONS,
            toolset=toolset,
        )

        # 建立執行緒
        thread = project_client.agents.threads.create()

        # 儲存至會話
        cl.user_session.set("agent", agent)
        cl.user_session.set("thread", thread)
        cl.user_session.set("project_client", project_client)
        cl.user_session.set("conversation_id", None)

        # 發送歡迎訊息，包含 agent ID 和範例問題
        welcome_msg = f"""# Welcome to Databricks Taxi Data Analysis Agent! 🚕

**Agent ID:** `{agent.id}`

I'm here to help you analyze the NYC taxi trip dataset. You can ask me questions about fare statistics, time-based trends, distance vs fare relationships, geographic comparisons, and outlier detection.

**Try these sample questions:**"""

        await cl.Message(content=welcome_msg).send()

        # 建立範例問題按鈕
        actions = []
        for i, question in enumerate(SAMPLE_QUESTIONS):
            actions.append(
                cl.Action(
                    name=f"sample_question_{i}",
                    payload={"question": question.split("(")[0].strip()},  # 新增必要的 payload 欄位
                    label=f"📊 {question}",
                    description=f"Ask: {question.split('(')[0].strip()}"
                )
            )

        await cl.Message(
            content="Click any button below to ask a sample question:",
            actions=actions
        ).send()

    except Exception as e:
        error_msg = f"❌ **Error initializing agent:** {str(e)}"
        await cl.Message(content=error_msg).send()
        raise

@cl.action_callback("sample_question_0")
async def sample_question_0(action):
    await handle_sample_question(action.payload["question"])

@cl.action_callback("sample_question_1") 
async def sample_question_1(action):
    await handle_sample_question(action.payload["question"])

@cl.action_callback("sample_question_2")
async def sample_question_2(action):
    await handle_sample_question(action.payload["question"])

@cl.action_callback("sample_question_3")
async def sample_question_3(action):
    await handle_sample_question(action.payload["question"])

@cl.action_callback("sample_question_4")
async def sample_question_4(action):
    await handle_sample_question(action.payload["question"])

async def handle_sample_question(question):
    """處理範例問題按鈕點擊。"""
    # 將問題作為使用者訊息發送
    await cl.Message(
        content=question,
        author="You"
    ).send()
    
    # 處理問題
    await process_question(question)

async def process_question(content):
    """透過 agent 處理問題。"""
    agent = cl.user_session.get("agent")
    thread = cl.user_session.get("thread")
    project_client = cl.user_session.get("project_client")
    
    if not all([agent, thread, project_client]):
        await cl.Message(content="❌ Agent not properly initialized. Please refresh the page.").send()
        return

    try:
        # 顯示處理中訊息
        processing_msg = cl.Message(content="🤔 Analyzing your question...")
        await processing_msg.send()

        # 建立訊息並執行
        project_client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=content,
        )

        run = project_client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id
        )

        # 更新處理中訊息
        processing_msg.content = f"✅ Analysis completed (Status: {run.status})"
        await processing_msg.update()

        # 取得最新訊息並顯示 agent 的回應
        messages = project_client.agents.messages.list(thread_id=thread.id)
        
        # 尋找最新的助理訊息
        for message in messages:
            if message.role == "assistant":
                response_content = ""
                for content_item in message.content:
                    if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                        response_content = content_item.text.value
                        break
                
                if response_content:
                    await cl.Message(
                        content=response_content,
                        author="Databricks Agent"
                    ).send()
                break

    except Exception as e:
        await cl.Message(content=f"❌ **Error processing question:** {str(e)}").send()

@cl.on_message
async def main(message: cl.Message):
    """處理使用者訊息。"""
    await process_question(message.content)

@cl.on_stop
async def on_stop():
    """會話結束時清理 agent。"""
    agent = cl.user_session.get("agent")
    project_client = cl.user_session.get("project_client")
    
    if agent and project_client:
        try:
            project_client.agents.delete_agent(agent.id)
            print(f"🧹 Deleted agent {agent.id}")
        except Exception as e:
            print(f"❌ Error deleting agent: {str(e)}")

if __name__ == "__main__":
    print("To run this Chainlit app, use: chainlit run chainlit_agent_adb_genie.py")