# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此範例展示如何在 Azure AI Foundry 中使用 Databricks 連接器搭配 Databricks 
    來存取 Genie (使用 Genie API)。
    在此我們向 Genie 提出兩個問題，並在兩個問題之間保持對話上下文。

使用方式:
    python sample_agents_functions.py

    執行範例前:

    pip install azure-ai-projects azure-ai-agents azure-identity databricks-sdk

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

# 從 .env 檔案載入環境變數
load_dotenv()

os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"

DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default" 
# Azure Databricks 的已知 Entra ID 對象 - https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/user-aad-token

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_DATABRICKS_CONNECTION_NAME = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")
GENIE_QUESTION_1 = os.getenv("GENIE_QUESTION_1")
GENIE_QUESTION_2 = os.getenv("GENIE_QUESTION_2")

if not FOUNDRY_PROJECT_ENDPOINT:
    raise ValueError("FOUNDRY_PROJECT_ENDPOINT environment variable is required")
if not FOUNDRY_DATABRICKS_CONNECTION_NAME:
    raise ValueError("FOUNDRY_DATABRICKS_CONNECTION_NAME environment variable is required")
if not GENIE_QUESTION_1:
    raise ValueError("GENIE_QUESTION_1 environment variable is required")
if not GENIE_QUESTION_2:
    raise ValueError("GENIE_QUESTION_2 environment variable is required")

##################
# 工具函數

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

##################


credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)


project_client = AIProjectClient(
    FOUNDRY_PROJECT_ENDPOINT,
    credential
)
print(f"AI Project client created for project endpoint: {FOUNDRY_PROJECT_ENDPOINT}")


connection = project_client.connections.get(FOUNDRY_DATABRICKS_CONNECTION_NAME)
print(f"Retrieved connection '{FOUNDRY_DATABRICKS_CONNECTION_NAME}' from AI project")

if connection.metadata['azure_databricks_connection_type'] == 'genie':
    genie_space_id = connection.metadata['genie_space_id']
    print(f"Connection is of type 'genie', retrieved genie space ID: {genie_space_id}")
else:
    raise ValueError("Connection is not of type 'genie', please check the connection type.")


databricks_workspace_client = WorkspaceClient(
    host=connection.target,
    token = credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default").token,
)
print(f"Databricks workspace client created for host: {connection.target}")

genie_api = GenieAPI(databricks_workspace_client.api_client)

toolset = ToolSet()
user_functions: Set[Callable[..., Any]] = { ask_genie }
functions = FunctionTool(functions=user_functions)
toolset.add(functions)


with project_client:
    # 使用 ask_genie 函數建立 agent 並執行使用者請求
    project_client.agents.enable_auto_function_calls(toolset)

    agent = project_client.agents.create_agent(
        model='gpt-4o',
        name="Databricks Agent",
        instructions="你是一個有幫助的助理，使用 Databricks Genie 來回答問題。" \
        "使用第一次呼叫 ask_genie 函數回傳的 conversation_id 來在 Genie 中繼續對話。",
        toolset=toolset,
    )

    print(f"Agent '{agent.name}' created with model '{agent.model}'")

    thread = project_client.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    agent_message_1 = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=GENIE_QUESTION_1,
    )
    print(f"Created message 1 with question: {GENIE_QUESTION_1}, ID: {agent_message_1.id}")

    print("Creating and processing Run 1")

    run_1 = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id  
    )

    print(f"Run 1 completed with status: {run_1.status}")

    agent_message_2 = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=GENIE_QUESTION_2,
    )
    print(f"Created message 1 with question: {GENIE_QUESTION_2}, ID: {agent_message_2.id}")

    print("Creating and processing Run 2")

    run_2 = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id  
    )

    print(f"Run 2 completed with status: {run_2.status}")

    # 完成時刪除 agent
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # 擷取並記錄所有訊息
    messages = project_client.agents.messages.list(thread_id=thread.id)
    for message in messages:
        print(f"Message ID: {message.id}, Role: {message.role}, Content: {message.content}")

    # 擷取並記錄所有執行步驟
    print("\n\nSteps in Run 1:")
    steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run_1.id)
    for step in steps:
        print(json.dumps(step.as_dict(), indent=2))

    print("\n\nSteps in Run 2:")
    steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run_2.id)
    for step in steps:
        print(json.dumps(step.as_dict(), indent=2))