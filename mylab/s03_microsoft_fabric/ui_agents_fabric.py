# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此範例展示如何使用具有 Chainlit UI 的代理程式來分析 Microsoft Fabric 
    lakehouse 中的計程車行程數據。使用真實的 Fabric 連接進行數據查詢。
    功能包括範例問題提示、代理程式生命週期管理和互動式聊天介面。

必要條件:
    1) 設定包含計程車行程數據的 Microsoft Fabric lakehouse
    2) 配置具有適當模型部署的 Azure AI Foundry 專案
    3) 在 Azure AI Foundry 中建立 Fabric 連接
    
使用方法:
    chainlit run ui_agents_fabric.py
 
    執行範例前:
 
    pip install -r requirements.txt

    使用您自己的值設定這些環境變數:
    1) PROJECT_ENDPOINT - 專案端點，可在您的 Azure AI Foundry 專案概觀頁面中找到
    2) MODEL_DEPLOYMENT_NAME - AI 模型的部署名稱，可在您的 Azure AI Foundry 專案
       「模型 + 端點」分頁的「名稱」欄位下找到
    3) FABRIC_CONNECTION_NAME - Fabric 連接名稱，可在 Azure AI Foundry 專案的
       「Connected resources」中找到
"""

import os
import time
import asyncio
from typing import Optional
from dotenv import load_dotenv
import chainlit as cl

from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FabricTool, ListSortOrder
from azure.identity import DefaultAzureCredential

# 載入環境變數
load_dotenv()

# 從 sample.txt 提取的範例問題，用於定義代理程式個性並提供提示
SAMPLE_QUESTIONS = [
    "Compare the total number of taxi trips on public holidays versus regular weekdays. In addition, analyze whether the average trip distance and average fare amount differ significantly between holidays and weekdays. Provide insights into whether people travel longer distances or pay higher fares during holidays.",
    "Count the number of trips with fare amounts greater than 70. Also, calculate the percentage of these high-fare trips relative to all trips.",
    "Compare the number of trips and average fare amount between daytime (7:00–19:00) and nighttime (19:00–7:00). Additionally, show whether trip distances differ between daytime and nighttime trips.",
    "Identify the pickup zip code with the highest number of trips. Provide the top 5 pickup zip codes ranked by trip volume.",
    "Determine the most frequent passenger count value (mode) in the dataset. Provide the distribution of passenger counts across all trips."
]

# 代理程式和客戶端的全域變數
project_client: Optional[AIProjectClient] = None
current_agent = None
current_thread = None


@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話，建立代理程式和線程。"""
    global project_client, current_agent, current_thread
    
    # 檢查必要的環境變數
    required_vars = ["PROJECT_ENDPOINT", "MODEL_DEPLOYMENT_NAME", "FABRIC_CONNECTION_NAME"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        await cl.Message(
            content=f"❌ Missing required environment variables: {', '.join(missing_vars)}\n"
                   "Please set these variables in your .env file or environment."
        ).send()
        return
    
    try:
        # 建立專案客戶端
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=os.environ["PROJECT_ENDPOINT"],
        )
        
        # 取得 Fabric 連接 ID
        await cl.Message(content="🔗 正在取得 Fabric 連接...").send()
        conn_id = project_client.connections.get(os.environ["FABRIC_CONNECTION_NAME"]).id
        await cl.Message(content=f"✅ 成功取得 Fabric 連接 ID: `{conn_id}`").send()
        
        # 初始化 Fabric 工具
        fabric = FabricTool(connection_id=conn_id)
        await cl.Message(content="✅ Fabric 工具初始化完成").send()

        # 基於範例問題建立具有個性的代理程式
        agent_instructions = """您是專業的計程車數據分析助手，專門分析 Microsoft Fabric lakehouse 中的計程車行程數據。

您的專業領域包括分析：
- 國定假日與平日的行程模式和費用比較
- 高費用行程分析（行程 > $70）及其百分比分佈  
- 日間（7:00-19:00）與夜間（19:00-7:00）行程和費用模式
- 地理分析，包括熱門上車地點和郵遞區號
- 乘客數量分佈和模態分析

您應該：
1. 提供清晰、結構化的回應，包含具體數字和統計資料
2. 使用 Fabric lakehouse 中的數據進行分析
3. 基於數據分析提供洞察和趨勢
4. 以繁體中文呈現資訊，同時保留技術術語和欄位名稱的英文
5. 始終保持專業和樂於助人的語調

當使用者詢問計程車行程數據時，提供包含相關統計、趨勢和可行洞察的全面分析。"""

        current_agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="TaxiDataAnalysisAgent",
            instructions=agent_instructions,
            tools=fabric.definitions,
        )
        
        # 建立對話線程
        current_thread = project_client.agents.threads.create()
        
        # 在使用者會話中儲存代理程式資訊
        cl.user_session.set("agent_id", current_agent.id)
        cl.user_session.set("thread_id", current_thread.id)
        cl.user_session.set("project_client", project_client)
        
        # 包含代理程式 ID 和範例問題的歡迎訊息  
        welcome_msg = "🚕 **計程車數據分析助手已啟動**\n\n"
        welcome_msg += f"**🤖 Agent ID:** `{current_agent.id}`\n"
        welcome_msg += f"**🧵 Thread ID:** `{current_thread.id}`\n\n"
        welcome_msg += "我可以幫您分析 Microsoft Fabric lakehouse 中的計程車行程數據。\n\n"
        welcome_msg += "**✨ 建議的查詢問題 (點擊下方按鈕直接送出):**"
        
        await cl.Message(content=welcome_msg).send()
        
        # 為範例問題建立提示按鈕
        actions = []
        for i, question in enumerate(SAMPLE_QUESTIONS, 1):
            # 建立更清潔的按鈕文字
            button_text = f"Q{i}: {question[:45]}..."
            actions.append(
                cl.Action(
                    name=f"sample_q{i}",
                    value=question,
                    description=f"Sample Question {i}",
                    label=button_text,
                    payload={"question": question}
                )
            )
        
        await cl.Message(
            content="**📝 範例問題 - 點擊按鈕直接送出查詢:**",
            actions=actions
        ).send()
        
        # 新增代理程式狀態訊息
        status_msg = "**ℹ️ 系統狀態:**\n"
        status_msg += "- Agent 已成功建立並配置完成\n"
        status_msg += "- 對話線程已準備就緒\n"
        status_msg += "- 關閉瀏覽器時將自動清理 Agent 資源\n\n"
        status_msg += "您可以點擊上方按鈕或直接輸入問題開始對話。"
        
        await cl.Message(
            content=status_msg,
            author="System"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ 初始化失敗: {str(e)}"
        ).send()


@cl.action_callback("sample_q1")
async def on_sample_q1(action):
    """處理範例問題 1。"""
    await process_query(action.payload.get("question", SAMPLE_QUESTIONS[0]))


@cl.action_callback("sample_q2") 
async def on_sample_q2(action):
    """處理範例問題 2。"""
    await process_query(action.payload.get("question", SAMPLE_QUESTIONS[1]))


@cl.action_callback("sample_q3")
async def on_sample_q3(action):
    """處理範例問題 3。"""
    await process_query(action.payload.get("question", SAMPLE_QUESTIONS[2]))


@cl.action_callback("sample_q4")
async def on_sample_q4(action):
    """處理範例問題 4。"""
    await process_query(action.payload.get("question", SAMPLE_QUESTIONS[3]))


@cl.action_callback("sample_q5")
async def on_sample_q5(action):
    """處理範例問題 5。"""
    await process_query(action.payload.get("question", SAMPLE_QUESTIONS[4]))


async def process_query(query_content: str):
    """透過代理程式處理使用者查詢。"""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        thread_id = cl.user_session.get("thread_id")
        
        if not all([project_client, agent_id, thread_id]):
            await cl.Message(content="❌ 會話未正確初始化，請重新載入頁面").send()
            return
        
        # 顯示使用者查詢
        await cl.Message(content=f"**您的查詢:** {query_content}", author="User").send()
        
        # 顯示處理訊息
        processing_msg = await cl.Message(content="🔄 正在處理查詢...").send()
        
        # 在線程中建立訊息
        project_client.agents.messages.create(
            thread_id=thread_id,
            role="user",
            content=query_content
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
                
                # 等待完成
                while run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(1)
                    run = project_client.agents.runs.get(thread_id=thread_id, run_id=run.id)
                
                if run.status == "completed":
                    break
                elif run.status == "failed":
                    error_msg = f"❌ 處理失敗 (嘗試 {attempt + 1}/{max_retries}): {run.last_error}"
                    if attempt == max_retries - 1:
                        processing_msg.content = error_msg
                        await processing_msg.update()
                        return
                else:
                    processing_msg.content = f"⚠️ 處理完成，狀態: {run.status}"
                    await processing_msg.update()
                    return
                    
            except Exception as e:
                error_msg = f"❌ 處理錯誤 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                if attempt == max_retries - 1:
                    processing_msg.content = error_msg
                    await processing_msg.update()
                    return
                await asyncio.sleep(2)  # 重試前等待
        
        if run and run.status == "completed":
            # 取得最新的助手訊息
            messages = project_client.agents.messages.list(
                thread_id=thread_id, 
                order=ListSortOrder.ASCENDING
            )
            
            # 顯示所有助手的回應
            assistant_responses = []
            for msg in messages:
                if msg.role == "assistant":
                    if msg.text_messages:
                        for text_msg in msg.text_messages:
                            assistant_responses.append(text_msg.text.value)
            
            if assistant_responses:
                # 使用最後一個回應更新處理訊息
                processing_msg.content = f"**助手回覆:**\n\n{assistant_responses[-1]}"
                await processing_msg.update()
        else:
            processing_msg.content = "❌ 查詢處理失敗，請重試"
            await processing_msg.update()
            
    except Exception as e:
        await cl.Message(content=f"❌ 處理過程中發生錯誤: {str(e)}").send()


@cl.on_message
async def on_message(message: cl.Message):
    """處理傳入的使用者訊息。"""
    await process_query(message.content)


@cl.on_chat_end
async def on_chat_end():
    """聊天會話結束時清理資源。"""
    try:
        project_client = cl.user_session.get("project_client")
        agent_id = cl.user_session.get("agent_id")
        
        if project_client and agent_id:
            project_client.agents.delete_agent(agent_id)
            print(f"🧹 Cleaned up agent {agent_id}")
    except Exception as e:
        print(f"⚠️ Error cleaning up resources: {str(e)}")


if __name__ == "__main__":
    # 本地開發用 - 請改用 `chainlit run chainlit_app.py`
    pass