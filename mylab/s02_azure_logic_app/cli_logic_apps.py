# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此範例展示如何使用代理程式搭配 Logic Apps 來執行發送電子郵件的任務。
 
前置條件:
    1) 在 Azure 入口網站中，於與您的 Azure AI 專案相同的資源群組內建立 Logic App
    2) 若要設定您的 Logic App 來發送電子郵件，您必須包含一個 HTTP 要求觸發器，
    該觸發器設定為接受包含 'to'、'subject' 和 'body' 的 JSON。
    建立 Logic App 工作流程的指南可在此處找到：
    https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistants-logic-apps#create-logic-apps-workflows-for-function-calling
    
使用方式:
    python logic_apps.py
 
    執行範例前:
 
    pip install azure-ai-projects azure-identity

    請使用您自己的值設定以下環境變數:
    1) PROJECT_ENDPOINT - 專案端點，可在您的 Azure AI Foundry 專案概觀頁面中找到。
    2) MODEL_DEPLOYMENT_NAME - AI 模型的部署名稱，可在您的 Azure AI Foundry 專案
       「模型 + 端點」頁籤的「名稱」欄位中找到。

    請將範例中的以下值替換為您自己的值:
    1) <LOGIC_APP_NAME> - 您所建立的 Logic App 名稱。
    2) <TRIGGER_NAME> - 您在 Logic App 中建立的觸發器名稱（Azure 入口網站中 HTTP 
        觸發器的預設名稱為「When_a_HTTP_request_is_received」）。
    3) <RECIPIENT_EMAIL> - 收件人的電子郵件地址。
"""

# <imports>
import os
import requests
from typing import Set
from dotenv import load_dotenv

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# 載入環境變數
load_dotenv()

# 範例用戶函數
from user_functions import fetch_current_datetime

# 從 user_logic_apps 匯入 AzureLogicAppTool 和函數工廠
from user_logic_apps import AzureLogicAppTool, create_send_email_function
# </imports>

# <client_initialization>
# 建立專案用戶端
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)
# </client_initialization>

# <logic_app_tool_setup>
# 從環境變數取得訂用帳戶 ID 和資源群組
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
resource_group = os.environ.get("AZURE_RESOURCE_GROUP")

# 從環境變數取得 Logic App 組態
logic_app_name = os.environ.get("LOGIC_APP_NAME")
trigger_name = os.environ.get("TRIGGER_NAME")
recipient_email = os.environ.get("RECIPIENT_EMAIL")

# 檢查是否提供必要的值
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
    print(f"❌ 錯誤: 缺少必要的環境變數: {', '.join(missing_vars)}")
    print("請在您的 .env 檔案中設定這些變數:")
    for var in missing_vars:
        print(f"   {var}=<your_value>")
    exit(1)

print(f"使用訂用帳戶 ID: {subscription_id}")
print(f"使用資源群組: {resource_group}")
print(f"使用 Logic App 名稱: {logic_app_name}")
print(f"使用觸發器名稱: {trigger_name}")
print(f"使用收件人郵件: {recipient_email}")

print(f"嘗試註冊 Logic App: {logic_app_name}")
print(f"觸發器: {trigger_name}")

try:
    # 建立並初始化 AzureLogicAppTool 工具
    logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
    logic_app_tool.register_logic_app(logic_app_name, trigger_name)
    print(f"✅ 成功註冊 logic app '{logic_app_name}' 觸發器 '{trigger_name}'。")
except Exception as e:
    print(f"❌ 註冊 Logic App 失敗: {str(e)}")
    print("請確保:")
    print("1. Logic App 存在於指定的資源群組中")
    print("2. 觸發器名稱完全相符 (區分大小寫)")
    print("3. 您有適當的 Azure 權限")
    exit(1)
# </logic_app_tool_setup>

# <function_creation>
# 為您的 agent 工具建立專用的 "send_email_via_logic_app" 函數
send_email_func = create_send_email_function(logic_app_tool, logic_app_name)

# 為 agent 準備函數工具
functions_to_use: Set = {
    fetch_current_datetime,
    send_email_func,  # 這通過閉包參考 AzureLogicAppTool 實例
}
# </function_creation>

with project_client:
    # <agent_creation>
    # 建立 agent
    functions = FunctionTool(functions=functions_to_use)
    toolset = ToolSet()
    toolset.add(functions)
    
    # 啟用自動函數調用
    project_client.agents.enable_auto_function_calls(toolset)

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="SendEmailAgent",
        instructions="您是一個專門發送電子郵件的代理。",
        toolset=toolset,
    )
    print(f"已建立 agent，ID: {agent.id}")
    # </agent_creation>

    # <thread_management>
    # 建立通訊執行緒
    thread = project_client.agents.threads.create()
    print(f"已建立執行緒，ID: {thread.id}")

    # 在執行緒中建立訊息
    message = project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"您好，請發送一封郵件到 {recipient_email}，內容包含以 '%Y-%m-%d %H:%M:%S' 格式的日期和時間。",
    )
    print(f"已建立訊息，ID: {message.id}")
    # </thread_management>

    # <message_processing>
    # 在執行緒中建立並處理 agent 執行
    run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"執行完成，狀態: {run.status}")

    if run.status == "failed":
        print(f"執行失敗: {run.last_error}")
    # </message_processing>

    # <cleanup>
    # 取得並記錄所有訊息
    messages = project_client.agents.messages.list(thread_id=thread.id)
    print("\n=== 訊息歷史 ===")
    for message in messages:
        print(f"角色: {message.role}")
        if hasattr(message, 'content') and message.content:
            for content_item in message.content:
                if hasattr(content_item, 'text') and content_item.text:
                    print(f"內容: {content_item.text.value}")
        print("---")

    # 完成後刪除 agent
    project_client.agents.delete_agent(agent.id)
    print("已刪除 agent")
