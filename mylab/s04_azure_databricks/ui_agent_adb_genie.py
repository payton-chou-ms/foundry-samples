# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此範例展示如何在 Azure AI Foundry 中使用 Databricks 連接器搭配 Databricks 
    來存取 Genie (使用 Genie API)，透過具有範例問題按鈕和 agent 生命週期管理的 Chainlit UI。

使用方式:
    chainlit run chainlit_agent_adb_genie.py

    執行範例前:

    pip install azure-ai-projects azure-ai-agents azure-identity databricks-sdk chainlit

    請在 .env 檔案中設定以下環境變數:
    1) FOUNDRY_PROJECT_ENDPOINT - 您的 Azure AI Foundry 專案端點，可在 Azure AI Foundry 
       專案的「概觀」頁籤中找到。
    2) FOUNDRY_DATABRICKS_CONNECTION_NAME - Databricks 連接的名稱，可在 Azure AI Foundry 
       專案「管理中心」頁籤下的「連接的資源」中找到。
    3) MODEL_DEPLOYMENT_NAME - AI 模型的部署名稱，可在 Azure AI Foundry 專案
       「模型 + 端點」頁籤的「名稱」欄位中找到。
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
您是一個連接到 Databricks "samples.nyctaxi.trips" 資料集的數據分析代理。
您的角色是協助使用者探索和分析計程車行程數據。
您應該透過產生 SQL 查詢並總結結果來回應自然語言查詢。

您可以回答以下類型的問題：
1. 車資統計：例如，平均、最高或最低車資金額。
2. 時間趨勢：例如，依小時、日期或週別計算的行程次數。
3. 距離與車資分析：例如，距離與車資的相關性、依距離分布的車資。
4. 地理比較：例如，哪些接載或下車郵遞區號具有最高的平均車資。
5. 異常值偵測：例如，識別相較於距離具有異常高車資的行程。

請始終清楚解釋您的答案，並在相關時同時顯示查詢和結果的簡短自然語言摘要。
"""

# sample.txt 中的範例問題
SAMPLE_QUESTIONS = [
    "每趟行程的平均車資金額是多少？ (平均車資)",
    "行程數量如何依一天中的小時或一週中的日期變化？ (依時間的趨勢)",
    "行程距離與車資金額之間的相關性是什麼？ (距離 vs 車資關係)",
    "哪些接載郵遞區號具有最高的平均車資？ (地區比較)",
    "是否有相較於距離具有異常高車資金額的異常行程？ (異常值分析)"
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
        welcome_msg = f"""# 歡迎使用 Databricks 計程車數據分析代理！ 🚕

**代理 ID：** `{agent.id}`

我在這裡協助您分析 NYC 計程車行程資料集。您可以詢問我關於車資統計、時間趨勢、距離與車資關係、地理比較和異常值偵測的問題。

**試試這些範例問題：**"""

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
            content="點擊下方任一按鈕來提出範例問題：",
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