# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with Chainlit UI to execute Logic Apps workflows
    including sending emails and other automated tasks. Features include sample action buttons,
    agent lifecycle management, and interactive chat interface.

PREREQUISITES:
    1) Create a Logic App within the same resource group as your Azure AI Project in Azure Portal
    2) Configure your Logic App to send emails with HTTP request trigger accepting JSON with 
       'to', 'subject', and 'body' parameters
    3) Set up your Azure AI Foundry project with appropriate model deployment
    
USAGE:
    chainlit run ui_logic_apps.py
 
    Before running the sample:
 
    pip install azure-ai-projects azure-identity python-dotenv chainlit

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The project endpoint from your Azure AI Foundry project
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model
    3) AZURE_SUBSCRIPTION_ID - Your Azure subscription ID
    4) AZURE_RESOURCE_GROUP - Your Azure resource group name
    5) LOGIC_APP_NAME - The name of your Logic App
    6) TRIGGER_NAME - The name of the trigger in your Logic App
    7) RECIPIENT_EMAIL - Default recipient email address
"""

import os
import time
import asyncio
from typing import Optional, Set
from dotenv import load_dotenv
import chainlit as cl

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential

# Import user functions and Logic App utilities
# 匯入用戶函數和 Logic App 工具
from user_functions import fetch_current_datetime, fetch_weather, send_email, calculate_sum
from user_logic_apps import AzureLogicAppTool, create_send_email_function

# Load environment variables
# 載入環境變數
load_dotenv()

# Sample actions/tasks for Logic Apps
# Logic Apps 的範例動作/任務
SAMPLE_ACTIONS = [
    "Send an email with current date and time to the recipient",
    "Send a weather update email for New York to the recipient", 
    "Send a meeting reminder email with subject 'Team Meeting' to the recipient",
    "Calculate the sum of 25 and 35, then send the result via email",
    "Send a welcome email with subject 'Welcome!' and a friendly greeting"
]

# Global variables for agent and client
# agent 和 client 的全域變數
project_client: Optional[AIProjectClient] = None
current_agent = None
current_thread = None
logic_app_tool = None


@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話，建立 Logic Apps agent 和執行緒。"""
    global project_client, current_agent, current_thread, logic_app_tool
    
    # 檢查必要的環境變數
    required_vars = [
        "PROJECT_ENDPOINT", 
        "MODEL_DEPLOYMENT_NAME",
        "AZURE_SUBSCRIPTION_ID",
        "AZURE_RESOURCE_GROUP", 
        "LOGIC_APP_NAME",
        "TRIGGER_NAME",
        "RECIPIENT_EMAIL"
    ]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        await cl.Message(
            content=f"❌ Missing required environment variables: {', '.join(missing_vars)}\n"
                   "Please set these variables in your .env file or environment."
        ).send()
        return
    
    try:
        # 建立專案用戶端
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=os.environ["PROJECT_ENDPOINT"],
        )
        
        # 初始化 Logic App 工具
        subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
        resource_group = os.environ["AZURE_RESOURCE_GROUP"]
        logic_app_name = os.environ["LOGIC_APP_NAME"]
        trigger_name = os.environ["TRIGGER_NAME"]
        
        await cl.Message(content="🔧 正在初始化 Logic App 連線...").send()
        
        # 建立並註冊 Logic App 工具
        logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
        logic_app_tool.register_logic_app(logic_app_name, trigger_name)
        
        # 建立專用的郵件函數
        send_email_func = create_send_email_function(logic_app_tool, logic_app_name)
        
        # 為 agent 準備函數工具
        functions_to_use: Set = {
            fetch_current_datetime,
            fetch_weather,
            send_email_func,  # Logic App 郵件函數
            calculate_sum,
        }
        
        # 建立函數工具和工具集
        functions = FunctionTool(functions=functions_to_use)
        toolset = ToolSet()
        toolset.add(functions)
        
        # 啟用自動函數調用
        project_client.agents.enable_auto_function_calls(toolset)

        # 建立具有 Logic Apps 功能的 agent
        agent_instructions = """您是一位專業的 Logic Apps 自動化助手，專精於透過 Azure Logic Apps 執行工作流程。

您的專業領域包括:
- 透過 Logic Apps 工作流程傳送自動化電子郵件
- 擷取目前日期/時間資訊 
- 取得地點的天氣資訊
- 執行計算和運算
- 整合多個函數以建立全面的工作流程

您應該:
1. 當被要求時，使用 Logic Apps 工作流程來傳送電子郵件
2. 針對任務執行提供清晰、結構化的回應
3. 使用適當的函數來擷取即時資料
4. 以繁體中文呈現資訊，但保留英文的技術術語
5. 始終保持專業且樂於助人的語調
6. 確認 Logic Apps 工作流程的成功完成

當用戶要求發送電子郵件或自動化任務時，透過 Logic Apps 整合執行它們，並提供結果確認。"""

        current_agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="LogicAppsAgent",
            instructions=agent_instructions,
            toolset=toolset,
        )
        
        # 建立對話執行緒
        current_thread = project_client.agents.threads.create()
        
        # 儲存會話資訊
        cl.user_session.set("agent_id", current_agent.id)
        cl.user_session.set("thread_id", current_thread.id)
        cl.user_session.set("project_client", project_client)
        cl.user_session.set("logic_app_name", logic_app_name)
        cl.user_session.set("recipient_email", os.environ["RECIPIENT_EMAIL"])
        
        # 歡迎訊息
        welcome_msg = "⚡ **Logic Apps 自動化助手已啟動**\n\n"
        welcome_msg += f"**🤖 Agent ID:** `{current_agent.id}`\n"
        welcome_msg += f"**🧵 Thread ID:** `{current_thread.id}`\n"
        welcome_msg += f"**📧 Logic App:** `{logic_app_name}`\n"
        welcome_msg += f"**📬 預設收件人:** `{os.environ['RECIPIENT_EMAIL']}`\n\n"
        welcome_msg += "我可以幫您執行 Logic Apps 工作流程，包括發送郵件和其他自動化任務。\n\n"
        welcome_msg += "**⚡ 建議的自動化任務 (點擊下方按鈕直接執行):**"
        
        await cl.Message(content=welcome_msg).send()
        
        # 為範例任務建立動作按鈕
        actions = []
        for i, action in enumerate(SAMPLE_ACTIONS, 1):
            button_text = f"任務{i}: {action[:40]}..."
            actions.append(
                cl.Action(
                    name=f"action_{i}",
                    value=action,
                    description=f"Logic App Task {i}",
                    label=button_text,
                    payload={"action": action}
                )
            )
        
        await cl.Message(
            content="**🚀 快速執行任務 - 點擊按鈕直接執行 Logic Apps 工作流程:**",
            actions=actions
        ).send()
        
        # 新增狀態訊息
        status_msg = "**ℹ️ 系統狀態:**\n"
        status_msg += "- Logic Apps Agent 已成功建立並配置完成\n"
        status_msg += "- Logic App 連線已建立並註冊完成\n"
        status_msg += "- 對話線程已準備就緒\n"
        status_msg += "- 關閉瀏覽器時將自動清理 Agent 資源\n\n"
        status_msg += "您可以點擊上方按鈕執行預設任務，或直接輸入自訂指令。"
        
        await cl.Message(
            content=status_msg,
            author="System"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ 初始化失敗: {str(e)}\n\n"
                   "請確認:\n"
                   "1. Logic App 存在於指定的資源群組中\n"
                   "2. Trigger 名稱完全正確 (區分大小寫)\n"
                   "3. 您有適當的 Azure 權限"
        ).send()


# Action callbacks for sample tasks
# 範例任務的動作回呼函數
@cl.action_callback("action_1")
async def on_action_1(action):
    """處理範例動作 1。"""
    recipient = cl.user_session.get("recipient_email")
    task = f"{action.payload.get('action', SAMPLE_ACTIONS[0])} 收件人: {recipient}"
    await process_logic_app_task(task)


@cl.action_callback("action_2") 
async def on_action_2(action):
    """處理範例動作 2。"""
    recipient = cl.user_session.get("recipient_email")
    task = f"{action.payload.get('action', SAMPLE_ACTIONS[1])} 收件人: {recipient}"
    await process_logic_app_task(task)


@cl.action_callback("action_3")
async def on_action_3(action):
    """處理範例動作 3。"""
    recipient = cl.user_session.get("recipient_email")
    task = f"{action.payload.get('action', SAMPLE_ACTIONS[2])} 收件人: {recipient}"
    await process_logic_app_task(task)


@cl.action_callback("action_4")
async def on_action_4(action):
    """處理範例動作 4。"""
    recipient = cl.user_session.get("recipient_email")
    task = f"{action.payload.get('action', SAMPLE_ACTIONS[3])} 收件人: {recipient}"
    await process_logic_app_task(task)


@cl.action_callback("action_5")
async def on_action_5(action):
    """處理範例動作 5。"""
    recipient = cl.user_session.get("recipient_email")
    task = f"{action.payload.get('action', SAMPLE_ACTIONS[4])} 收件人: {recipient}"
    await process_logic_app_task(task)


async def process_logic_app_task(task_content: str):
    """透過 agent 處理 Logic Apps 任務。"""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        thread_id = cl.user_session.get("thread_id")
        
        if not all([project_client, agent_id, thread_id]):
            await cl.Message(content="❌ 會話未正確初始化，請重新載入頁面").send()
            return
        
        # 顯示用戶任務
        await cl.Message(content=f"**您的任務:** {task_content}", author="User").send()
        
        # 顯示處理中訊息
        processing_msg = await cl.Message(content="⚡ 正在執行 Logic Apps 工作流程...").send()
        
        # 在執行緒中建立訊息
        project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=task_content
        )
        
        # 使用重試機制處理
        max_retries = 3
        run = None
        
        for attempt in range(max_retries):
            try:
                # 建立並處理執行
                run = project_client.agents.runs.create_and_process(
                    thread_id=thread_id,
                    agent_id=agent_id
                )
                
                # 等待完成並設定超時
                timeout = 60  # 60 秒超時
                start_time = time.time()
                
                while run.status in ["queued", "in_progress"]:
                    if time.time() - start_time > timeout:
                        processing_msg.content = f"⚠️ 工作流程執行超時 (嘗試 {attempt + 1}/{max_retries})"
                        await processing_msg.update()
                        break
                    
                    await asyncio.sleep(1)
                    run = project_client.agents.runs.get(thread_id=thread_id, run_id=run.id)
                
                if run.status == "completed":
                    break
                elif run.status == "failed":
                    error_msg = f"❌ 工作流程執行失敗 (嘗試 {attempt + 1}/{max_retries})"
                    if run.last_error:
                        error_msg += f": {run.last_error}"
                    if attempt == max_retries - 1:
                        processing_msg.content = error_msg
                        await processing_msg.update()
                        return
                else:
                    processing_msg.content = f"⚠️ 工作流程完成，狀態: {run.status}"
                    await processing_msg.update()
                    return
                    
            except Exception as e:
                error_msg = f"❌ 執行過程發生錯誤 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                if attempt == max_retries - 1:
                    processing_msg.content = error_msg
                    await processing_msg.update()
                    return
                await asyncio.sleep(2)  # 重試前等待
        
        if run and run.status == "completed":
            # 取得最新的助手訊息
            messages = project_client.agents.messages.list(thread_id=thread_id)
            message_list = list(messages)
            
            for message in message_list:
                if message.role == "assistant":
                    # 以結果更新處理中訊息
                    processing_msg.content = f"**⚡ Logic Apps 執行結果:**\n\n{message.content}"
                    await processing_msg.update()
                    break
        else:
            processing_msg.content = "❌ Logic Apps 工作流程執行失敗，請重試"
            await processing_msg.update()
            
    except Exception as e:
        await cl.Message(content=f"❌ 處理過程中發生錯誤: {str(e)}").send()


@cl.on_message
async def on_message(message: cl.Message):
    """處理傳入的用戶訊息。"""
    await process_logic_app_task(message.content)


@cl.on_chat_end
async def on_chat_end():
    """聊天會話結束時清理資源。"""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        
        if project_client and agent_id:
            project_client.agents.delete_agent(agent_id)
            print(f"🧹 已清理 Logic Apps agent {agent_id}")
    except Exception as e:
        print(f"⚠️ 清理資源時發生錯誤: {str(e)}")


if __name__ == "__main__":
    # 本地開發用 - 請改用 `chainlit run ui_logic_apps.py`
    pass