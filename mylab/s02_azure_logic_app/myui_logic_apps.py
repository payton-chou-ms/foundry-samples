# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此範例展示如何使用 Chainlit UI 搭配代理程式和 Logic Apps 來執行發送電子郵件的任務。
    這是 cli_logic_apps.py 的 UI 版本，提供互動式介面和快速動作按鈕。

前置條件:
    1) 在 Azure 入口網站中，於與您的 Azure AI 專案相同的資源群組內建立 Logic App
    2) 若要設定您的 Logic App 來發送電子郵件，您必須包含一個 HTTP 要求觸發器，
    該觸發器設定為接受包含 'to'、'subject' 和 'body' 的 JSON。
    建立 Logic App 工作流程的指南可在此處找到：
    https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/assistants-logic-apps#create-logic-apps-workflows-for-function-calling
    
使用方式:
    chainlit run myui_logic_apps.py
 
    執行範例前:
 
    pip install azure-ai-projects azure-identity chainlit python-dotenv

    請使用您自己的值設定以下環境變數:
    1) PROJECT_ENDPOINT - 專案端點，可在您的 Azure AI Foundry 專案概觀頁面中找到。
    2) MODEL_DEPLOYMENT_NAME - AI 模型的部署名稱，可在您的 Azure AI Foundry 專案
       「模型 + 端點」頁籤的「名稱」欄位中找到。
    3) AZURE_SUBSCRIPTION_ID - 您的 Azure 訂用帳戶 ID
    4) AZURE_RESOURCE_GROUP - 您的資源群組名稱
    5) LOGIC_APP_NAME - 您所建立的 Logic App 名稱
    6) TRIGGER_NAME - Logic App 中觸發器的名稱
    7) RECIPIENT_EMAIL - 收件人的電子郵件地址
"""

# <imports>
import os
import time
import asyncio
from typing import Optional, Set
from dotenv import load_dotenv
import chainlit as cl

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

# 預設快速動作任務
QUICK_ACTIONS = [
    "發送日期時間郵件",
    "發送測試郵件",
    "發送問候郵件"
]

# 全域變數
project_client: Optional[AIProjectClient] = None
current_agent = None
current_thread = None
logic_app_tool = None


@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話，建立 Logic Apps agent 和執行緒。"""
    global project_client, current_agent, current_thread, logic_app_tool
    
    # 檢查必要的環境變數
    required_env_vars = {
        "PROJECT_ENDPOINT": os.environ.get("PROJECT_ENDPOINT"),
        "MODEL_DEPLOYMENT_NAME": os.environ.get("MODEL_DEPLOYMENT_NAME"),
        "AZURE_SUBSCRIPTION_ID": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "AZURE_RESOURCE_GROUP": os.environ.get("AZURE_RESOURCE_GROUP"),
        "LOGIC_APP_NAME": os.environ.get("LOGIC_APP_NAME"),
        "TRIGGER_NAME": os.environ.get("TRIGGER_NAME"),
        "RECIPIENT_EMAIL": os.environ.get("RECIPIENT_EMAIL"),
    }
    
    missing_vars = [var for var, value in required_env_vars.items() 
                   if not value or value.startswith("your-")]
    
    if missing_vars:
        error_msg = f"❌ 錯誤: 缺少必要的環境變數: {', '.join(missing_vars)}\n\n"
        error_msg += "請在您的 .env 檔案中設定這些變數:\n"
        for var in missing_vars:
            error_msg += f"   {var}=<your_value>\n"
        await cl.Message(content=error_msg).send()
        return
    
    try:
        # 建立專案用戶端
        await cl.Message(content="🔧 正在初始化 Azure AI 用戶端...").send()
        
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=required_env_vars["PROJECT_ENDPOINT"],
        )
        
        # 從環境變數取得組態
        subscription_id = required_env_vars["AZURE_SUBSCRIPTION_ID"]
        resource_group = required_env_vars["AZURE_RESOURCE_GROUP"]
        logic_app_name = required_env_vars["LOGIC_APP_NAME"]
        trigger_name = required_env_vars["TRIGGER_NAME"]
        recipient_email = required_env_vars["RECIPIENT_EMAIL"]
        
        # 顯示組態資訊
        config_msg = "📋 **組態資訊:**\n"
        config_msg += f"- 訂用帳戶 ID: `{subscription_id[:8]}...`\n"
        config_msg += f"- 資源群組: `{resource_group}`\n"
        config_msg += f"- Logic App: `{logic_app_name}`\n"
        config_msg += f"- 觸發器: `{trigger_name}`\n"
        config_msg += f"- 收件人: `{recipient_email}`\n"
        await cl.Message(content=config_msg).send()
        
        # 建立並註冊 Logic App 工具
        await cl.Message(content="🔗 正在註冊 Logic App...").send()
        
        logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
        logic_app_tool.register_logic_app(logic_app_name, trigger_name)
        
        await cl.Message(content=f"✅ 成功註冊 Logic App '{logic_app_name}' 觸發器 '{trigger_name}'").send()
        
        # 為 agent 準備函數工具
        send_email_func = create_send_email_function(logic_app_tool, logic_app_name)
        
        functions_to_use: Set = {
            fetch_current_datetime,
            send_email_func,
        }
        
        # 建立函數工具和工具集
        functions = FunctionTool(functions=functions_to_use)
        toolset = ToolSet()
        toolset.add(functions)
        
        # 啟用自動函數調用
        project_client.agents.enable_auto_function_calls(toolset)
        
        await cl.Message(content="🤖 正在建立 AI Agent...").send()
        
        # 建立 agent
        agent_instructions = """您是一個專門發送電子郵件的代理。
        
當用戶請求發送郵件時，請:
1. 使用 fetch_current_datetime 函數取得當前日期和時間（如果需要）
2. 使用 send_email_via_logic_app 函數透過 Logic App 發送電子郵件
3. 確認郵件發送成功並提供清楚的回饋

請以繁體中文回應，並保持專業友善的語調。"""

        current_agent = project_client.agents.create_agent(
            model=required_env_vars["MODEL_DEPLOYMENT_NAME"],
            name="SendEmailAgent",
            instructions=agent_instructions,
            toolset=toolset,
        )
        
        # 建立通訊執行緒
        current_thread = project_client.agents.threads.create()
        
        # 儲存會話資訊
        cl.user_session.set("project_client", project_client)
        cl.user_session.set("agent_id", current_agent.id)
        cl.user_session.set("thread_id", current_thread.id)
        cl.user_session.set("recipient_email", recipient_email)
        
        # 歡迎訊息
        welcome_msg = "🎉 **Logic Apps 郵件代理已啟動!**\n\n"
        welcome_msg += f"**Agent ID:** `{current_agent.id}`\n"
        welcome_msg += f"**Thread ID:** `{current_thread.id}`\n\n"
        welcome_msg += "我可以幫您透過 Logic Apps 發送電子郵件。\n"
        welcome_msg += "您可以點擊下方的快速動作按鈕，或直接輸入自訂指令。"
        
        await cl.Message(content=welcome_msg).send()
        
        # 建立快速動作按鈕
        actions = [
            cl.Action(
                name="action_datetime",
                value=f"發送郵件到 {recipient_email}，內容包含以 '%Y-%m-%d %H:%M:%S' 格式的日期和時間",
                description="發送包含當前日期時間的郵件",
                label="📅 發送日期時間郵件",
            ),
            cl.Action(
                name="action_test",
                value=f"發送測試郵件到 {recipient_email}，主旨為 'Test Email'，內容為 '這是一封測試郵件。'",
                description="發送測試郵件",
                label="📧 發送測試郵件",
            ),
            cl.Action(
                name="action_greeting",
                value=f"發送問候郵件到 {recipient_email}，主旨為 'Hello'，內容為 '您好！這是來自 AI Agent 的問候。'",
                description="發送問候郵件",
                label="👋 發送問候郵件",
            ),
        ]
        
        await cl.Message(
            content="**⚡ 快速動作** - 點擊按鈕執行預設任務:",
            actions=actions
        ).send()
        
    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}\n\n"
        error_msg += "請確認:\n"
        error_msg += "1. Logic App 存在於指定的資源群組中\n"
        error_msg += "2. 觸發器名稱完全相符 (區分大小寫)\n"
        error_msg += "3. 您有適當的 Azure 權限"
        await cl.Message(content=error_msg).send()


@cl.action_callback("action_datetime")
async def on_action_datetime(action):
    """處理日期時間郵件動作。"""
    await process_task(action.value)


@cl.action_callback("action_test")
async def on_action_test(action):
    """處理測試郵件動作。"""
    await process_task(action.value)


@cl.action_callback("action_greeting")
async def on_action_greeting(action):
    """處理問候郵件動作。"""
    await process_task(action.value)


async def process_task(task_content: str):
    """透過 agent 處理任務。"""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        thread_id = cl.user_session.get("thread_id")
        
        if not all([project_client, agent_id, thread_id]):
            await cl.Message(content="❌ 會話未正確初始化，請重新載入頁面").send()
            return
        
        # 顯示用戶任務
        await cl.Message(content=f"**執行任務:** {task_content}", author="User").send()
        
        # 顯示處理中訊息
        processing_msg = await cl.Message(content="⚙️ 正在處理您的請求...").send()
        
        # 在執行緒中建立訊息
        project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=task_content
        )
        
        # 建立並處理執行
        start_time = time.time()
        run = project_client.agents.runs.create_and_process(
            thread_id=thread_id,
            agent_id=agent_id
        )
        
        # 等待完成
        timeout = 60  # 60 秒超時
        while run.status in ["queued", "in_progress"]:
            if time.time() - start_time > timeout:
                processing_msg.content = "⚠️ 執行超時，請稍後重試"
                await processing_msg.update()
                return
            
            await asyncio.sleep(1)
            run = project_client.agents.runs.get(thread_id=thread_id, run_id=run.id)
        
        execution_time = time.time() - start_time
        
        if run.status == "completed":
            # 取得最新的助手訊息
            messages = project_client.agents.messages.list(thread_id=thread_id)
            
            for message in messages:
                if message.role == "assistant":
                    response_content = ""
                    if hasattr(message, 'content') and message.content:
                        for content_item in message.content:
                            if hasattr(content_item, 'text') and content_item.text:
                                response_content = content_item.text.value
                                break
                    
                    if response_content:
                        result_msg = f"✅ **執行成功** (耗時: {execution_time:.2f}秒)\n\n"
                        result_msg += response_content
                        processing_msg.content = result_msg
                    else:
                        processing_msg.content = f"✅ 執行完成 (耗時: {execution_time:.2f}秒)"
                    
                    await processing_msg.update()
                    break
        elif run.status == "failed":
            error_msg = f"❌ 執行失敗 (耗時: {execution_time:.2f}秒)"
            if run.last_error:
                error_msg += f"\n錯誤: {run.last_error}"
            processing_msg.content = error_msg
            await processing_msg.update()
        else:
            processing_msg.content = f"⚠️ 執行完成，狀態: {run.status}"
            await processing_msg.update()
            
    except Exception as e:
        await cl.Message(content=f"❌ 處理過程中發生錯誤: {str(e)}").send()


@cl.on_message
async def on_message(message: cl.Message):
    """處理傳入的用戶訊息。"""
    recipient = cl.user_session.get("recipient_email")
    
    # 如果訊息中沒有提到收件人，自動加上
    task_content = message.content
    if recipient and "收件人" not in task_content and recipient not in task_content:
        task_content = f"{task_content} (收件人: {recipient})"
    
    await process_task(task_content)


@cl.on_chat_end
async def on_chat_end():
    """聊天會話結束時清理資源。"""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        
        if project_client and agent_id:
            # 注意: 在實際應用中，您可能想要保留 agent 以供重複使用
            # 這裡我們選擇清理以避免資源累積
            # project_client.agents.delete_agent(agent_id)
            print(f"🧹 會話結束，Agent ID: {agent_id}")
    except Exception as e:
        print(f"⚠️ 清理資源時發生錯誤: {str(e)}")


if __name__ == "__main__":
    # 本地開發用 - 請改用 `chainlit run myui_logic_apps.py`
    print("請使用以下命令執行此應用:")
    print("  chainlit run myui_logic_apps.py")
