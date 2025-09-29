# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import os
from typing import Optional
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)
from semantic_kernel.functions.kernel_function_decorator import kernel_function

"""
以下範例示範如何在 Semantic Kernel 中使用已存在的
Azure AI Agent。本範例假設您已先前建立好 agent（透過程式、Portal 或 CLI）。
"""

# 載入環境變數
load_dotenv()

# 設定 Databricks SDK
os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"

DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_DATABRICKS_CONNECTION_NAME = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")

# 新增 agent_id 變數
# agent_id = "<your-agent-id>"
agent_id = "asst_EWDXzV1w5rk1frTF35IMRUAP"

# 全域變數儲存 Databricks 連接資訊
genie_api = None
genie_space_id = None
databricks_workspace_client = None

# 定義 ask_genie 函數作為 Kernel Function
@kernel_function(description="向 Databricks Genie 提問並取得回應", name="ask_genie")
def ask_genie(question: str, conversation_id: str = None) -> str:
    """
    向 Genie 提問並以 JSON 格式回傳回應。
    回應 JSON 將包含對話 ID 以及訊息內容或結果表格。
    在後續呼叫中重複使用對話 ID 以繼續對話並保持上下文。
    
    Args:
        question: 要向 Genie 提出的問題
        conversation_id: 要繼續的對話 ID。若為 None，將開始新對話
        
    Returns:
        str: JSON 格式的回應，包含對話 ID 和結果
    """
    global genie_api, genie_space_id, databricks_workspace_client
    
    if not genie_api or not genie_space_id or not databricks_workspace_client:
        return json.dumps({
            "error": "Databricks Genie API not initialized",
            "details": "Please ensure FOUNDRY_DATABRICKS_CONNECTION_NAME is set correctly"
        })
    
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

# 模擬與 agent 的對話
USER_INPUTS = [
    "What is the average transaction value",
]


async def handle_streaming_intermediate_steps(message: ChatMessageContent) -> None:
    for item in message.items or []:
        if isinstance(item, FunctionResultContent):
            print(f"Function Result:> {item.result} for function: {item.name}")
        elif isinstance(item, FunctionCallContent):
            print(f"Function Call:> {item.name} with arguments: {item.arguments}")
        else:
            print(f"{item}")


async def main() -> None:
    global genie_api, genie_space_id, databricks_workspace_client
    
    if not FOUNDRY_PROJECT_ENDPOINT:
        raise ValueError("FOUNDRY_PROJECT_ENDPOINT environment variable is required")
    if not FOUNDRY_DATABRICKS_CONNECTION_NAME:
        raise ValueError("FOUNDRY_DATABRICKS_CONNECTION_NAME environment variable is required")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds, endpoint=FOUNDRY_PROJECT_ENDPOINT) as client,
    ):
        # 設置 Databricks 連接
        try:
            # 取得 Databricks 連接資訊
            connection = await client.connections.get(name=FOUNDRY_DATABRICKS_CONNECTION_NAME)
            print(f"Retrieved connection '{FOUNDRY_DATABRICKS_CONNECTION_NAME}' from AI project")
            
            if connection.metadata.get('azure_databricks_connection_type') == 'genie':
                genie_space_id = connection.metadata.get('genie_space_id')
                print(f"Connection is of type 'genie', retrieved genie space ID: {genie_space_id}")
            else:
                raise ValueError("Connection is not of type 'genie', please check the connection type.")

            # 初始化 Databricks 工作區客戶端
            token_result = await creds.get_token(DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE)
            databricks_workspace_client = WorkspaceClient(
                host=connection.target,
                token=token_result.token,
            )
            print(f"Databricks workspace client created for host: {connection.target}")

            genie_api = GenieAPI(databricks_workspace_client.api_client)
            print("Databricks Genie API initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Databricks connection: {e}")
            return

        # 1. 根據 agent_id 取得 agent 定義
        # 2. 建立新的 agent 定義，包含 ask_genie 函數工具的定義
        # 這是關鍵：我們需要在 Azure AI 服務層面定義函數工具
        agent_definition = await client.agents.create_agent(
            model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
            name="DatabricksGenieAgent",
            description="專門使用 Databricks Genie API 分析資料的代理程式。",
            instructions="您是一個數據分析助手，專門使用 Databricks Genie API 來回答關於數據的問題。當用戶詢問數據相關問題時，請使用 ask_genie 函數來獲取準確的分析結果。",
            tools=[
                {
                    "type": "function", 
                    "function": {
                        "name": "DatabricksPlugin-ask_genie",
                        "description": "使用 Databricks Genie API 查詢和分析數據。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string", 
                                    "description": "要查詢的問題或分析請求"
                                },
                                "conversation_id": {
                                    "type": "string", 
                                    "description": "可選的對話 ID 以維持上下文"
                                }
                            },
                            "required": ["question"],
                        },
                    },
                }
            ],
        )
        print(f"Created agent definition, agent ID: {agent_definition.id}")
        
        # 3. 使用定義建立 Semantic Kernel AzureAIAgent 實例
        # 建立一個簡單的插件類別
        class DatabricksPlugin:
            @kernel_function(description="向 Databricks Genie 提問並取得回應", name="ask_genie")
            def ask_genie(self, question: str, conversation_id: Optional[str] = None) -> str:
                # 如果 conversation_id 是字串 "null"，將其設為 None
                if conversation_id == "null":
                    conversation_id = None
                return ask_genie(question, conversation_id)

        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
            plugins=[DatabricksPlugin()],  # 註冊包含實際函數實現的插件
        )
        
        print("Registered ask_genie function to agent kernel")
        print(f"Agent kernel plugins: {list(agent.kernel.plugins.keys())}")
        
        # 驗證函數是否已註冊
        if agent.kernel.plugins:
            for plugin_name, plugin in agent.kernel.plugins.items():
                print(f"{plugin_name} functions: {list(plugin.functions.keys()) if hasattr(plugin, 'functions') else 'No functions attribute'}")

        # 3. 建立 agent 對話執行緒
        # 若未提供執行緒，系統將建立並回傳含初始回應的新執行緒
        thread: AzureAIAgentThread = None

        try:
            for user_input in USER_INPUTS:
                print(f"# User: '{user_input}'")
                # 4. 以指定執行緒呼叫 agent 並串流回應
                async for response in agent.invoke_stream(
                    messages=user_input,
                    thread=thread,
                    on_intermediate_message=handle_streaming_intermediate_steps,
                ):
                    # Print the agent's response
                    print(f"{response}", end="", flush=True)
                    # Update the thread for subsequent messages
                    thread = response.thread
        finally:
            # 5. 清理資源：刪除執行緒和 agent
            # 刪除執行緒
            if thread:
                await thread.delete()
                
            # 刪除 agent 定義以釋放資源
            try:
                await client.agents.delete_agent(agent_definition.id)
                print(f"Deleted agent {agent_definition.id}")
            except Exception as e:
                print(f"Note: Could not delete agent {agent_definition.id}: {e}")

        """
        範例輸出：
        # User: 'What is the average transaction value'
        # Agent: Based on the taxi trip data, the average fare amount per trip is approximately $13.46.
        """


if __name__ == "__main__":
    asyncio.run(main())
