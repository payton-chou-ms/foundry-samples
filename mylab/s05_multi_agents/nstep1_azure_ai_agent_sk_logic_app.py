# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import json
import requests
from typing import Any, Callable, Set
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)
from semantic_kernel.functions import kernel_function

"""
以下範例示範如何在 Semantic Kernel 中使用 Azure AI Agent 結合 Logic Apps。
本範例整合了 Logic Apps 工作流程功能，提供電子郵件發送和業務流程自動化。
"""

# 載入環境變數
load_dotenv()

# 從環境變數取得設定
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")
LOGIC_APP_NAME = os.getenv("LOGIC_APP_NAME", "<LOGIC_APP_NAME>")
TRIGGER_NAME = os.getenv("TRIGGER_NAME", "When_a_HTTP_request_is_received")

# 模擬與 agent 的對話
USER_INPUTS = [
    "發送一封會議通知郵件給團隊",
    "建立一個客戶服務工作流程",
    "設定自動化的報告發送程序",
]


class LogicAppPlugin:
    def __init__(self):
        self.logic_app_connected = False
        self.workflow_base_url = None
        
    async def initialize_logic_app_connection(self):
        """初始化 Logic App 連接"""
        try:
            print("正在初始化 Logic App 連接...")
            # 建立 Logic App 工作流程的基本 URL
            # 實際實作時需要從 Azure 取得正確的 Logic App URL
            self.workflow_base_url = f"https://{LOGIC_APP_NAME}.azurewebsites.net/api/{TRIGGER_NAME}"
            self.logic_app_connected = True
            print("Logic App 連接已初始化")
        except Exception as e:
            print(f"Logic App 初始化失敗: {e}")

    @kernel_function
    def send_email(self, to: str, subject: str, body: str) -> str:
        """透過 Logic App 發送電子郵件"""
        if not self.logic_app_connected:
            return "錯誤: Logic App 未連接"
            
        try:
            # 模擬發送電子郵件
            email_data = {
                "to": to,
                "subject": subject,
                "body": body,
                "timestamp": "2024-01-15T10:30:00Z"
            }
            
            # 實際實作時會呼叫真實的 Logic App
            # response = requests.post(self.workflow_base_url, json=email_data)
            
            print(f"模擬發送電子郵件至 Logic App: {json.dumps(email_data, ensure_ascii=False, indent=2)}")
            return f"✅ 電子郵件已成功透過 Logic App 發送至 {to}，主旨: {subject}"
            
        except Exception as e:
            return f"❌ 發送電子郵件失敗: {e}"

    @kernel_function
    def create_workflow(self, workflow_type: str, description: str) -> str:
        """建立自動化工作流程"""
        workflow_templates = {
            "客戶服務": {
                "步驟": ["接收客戶查詢", "分類問題", "分配給適當部門", "發送確認郵件", "追蹤處理狀態"],
                "觸發器": "HTTP 請求",
                "預估時間": "5-10 分鐘"
            },
            "報告發送": {
                "步驟": ["定期觸發", "從資料庫取得資料", "產生報告", "發送給相關人員", "記錄發送日誌"],
                "觸發器": "排程觸發器",
                "預估時間": "每日自動執行"
            },
            "會議通知": {
                "步驟": ["讀取會議資料", "準備通知內容", "發送給與會者", "設定提醒", "追蹤回覆狀態"],
                "觸發器": "手動觸發或排程",
                "預估時間": "即時執行"
            }
        }
        
        # 找到匹配的工作流程類型
        for key, template in workflow_templates.items():
            if key in workflow_type:
                return f"""
🔧 **已建立 {workflow_type} 工作流程**

📋 **工作流程步驟:**
{chr(10).join(f"   {i+1}. {step}" for i, step in enumerate(template["步驟"]))}

🎯 **觸發器類型:** {template["觸發器"]}
⏱️ **執行時間:** {template["預估時間"]}
📝 **描述:** {description}

✅ 工作流程已在 Logic App 中配置完成，可立即使用。
"""
        
        return f"已建立自訂工作流程: {workflow_type}。描述: {description}。工作流程將根據需求自動執行相關步驟。"

    @kernel_function
    def trigger_workflow(self, workflow_name: str, parameters: str = "") -> str:
        """觸發指定的工作流程"""
        try:
            trigger_data = {
                "workflow": workflow_name,
                "parameters": parameters,
                "triggered_at": "2024-01-15T10:30:00Z",
                "user": "system"
            }
            
            print(f"觸發工作流程: {json.dumps(trigger_data, ensure_ascii=False, indent=2)}")
            return f"🚀 工作流程 '{workflow_name}' 已成功觸發，參數: {parameters or '無'}"
            
        except Exception as e:
            return f"❌ 觸發工作流程失敗: {e}"

    @kernel_function
    def monitor_workflow_status(self, workflow_id: str) -> str:
        """監控工作流程執行狀態"""
        # 模擬工作流程狀態
        import random
        statuses = ["執行中", "已完成", "等待中", "失敗", "已暫停"]
        status = random.choice(statuses)
        
        status_details = {
            "執行中": "工作流程正在處理，預估剩餘時間: 2 分鐘",
            "已完成": "工作流程成功完成，所有步驟執行正常",
            "等待中": "工作流程在佇列中等待，預估開始時間: 30 秒後",
            "失敗": "工作流程執行失敗，需要檢查設定或重新執行",
            "已暫停": "工作流程已暫停，等待手動介入或條件滿足"
        }
        
        return f"📊 工作流程 {workflow_id} 狀態: **{status}**\n詳情: {status_details[status]}"


async def handle_streaming_intermediate_steps(message: ChatMessageContent) -> None:
    for item in message.items or []:
        if isinstance(item, FunctionResultContent):
            print(f"Function Result:> {item.result} for function: {item.name}")
        elif isinstance(item, FunctionCallContent):
            print(f"Function Call:> {item.name} with arguments: {item.arguments}")
        else:
            print(f"{item}")


async def create_logic_app_agent(client) -> AzureAIAgent:
    """建立具有 Logic App 功能的 Azure AI Agent"""
    
    # 建立 Logic App 插件
    logic_app_plugin = LogicAppPlugin()
    await logic_app_plugin.initialize_logic_app_connection()
    
    # 建立 agent 定義
    agent_definition = await client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME or "gpt-4o",
        name="LogicAppOrchestrator",
        description="專精於使用 Logic Apps 進行業務流程自動化和工作流程管理的助手",
        instructions="""
        您是一位業務流程自動化專家，專門使用 Azure Logic Apps。
        您能夠:
        1. 設計和建立自動化工作流程
        2. 發送電子郵件和通知
        3. 整合不同的服務和系統
        4. 監控和管理工作流程執行狀態
        
        請提供清晰的步驟說明和實用的自動化建議。
        確保工作流程設計符合業務需求並具有良好的錯誤處理機制。
        """,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-send_email",
                    "description": "透過 Logic App 發送電子郵件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "收件人電子郵件地址"},
                            "subject": {"type": "string", "description": "郵件主旨"},
                            "body": {"type": "string", "description": "郵件內容"}
                        },
                        "required": ["to", "subject", "body"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-create_workflow",
                    "description": "建立自動化工作流程",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_type": {"type": "string", "description": "工作流程類型"},
                            "description": {"type": "string", "description": "工作流程描述"}
                        },
                        "required": ["workflow_type", "description"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-trigger_workflow",
                    "description": "觸發指定的工作流程",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_name": {"type": "string", "description": "工作流程名稱"},
                            "parameters": {"type": "string", "description": "觸發參數 (可選)"}
                        },
                        "required": ["workflow_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-monitor_workflow_status",
                    "description": "監控工作流程執行狀態",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_id": {"type": "string", "description": "工作流程識別碼"}
                        },
                        "required": ["workflow_id"],
                    },
                },
            },
        ],
    )
    
    # 建立 Semantic Kernel 對應的 Azure AI Agent
    agent = AzureAIAgent(
        client=client,
        definition=agent_definition,
        plugins=[logic_app_plugin],
    )
    
    return agent


async def main() -> None:
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 建立 Logic App agent
        agent = await create_logic_app_agent(client)
        
        print(f"已建立 Logic App Agent，ID: {agent.id}")
        
        # 建立 agent 對話執行緒
        thread: AzureAIAgentThread = None

        try:
            for user_input in USER_INPUTS:
                print(f"\n# User: '{user_input}'")
                print("-" * 50)
                
                # 以指定執行緒呼叫 agent 並串流回應
                async for response in agent.invoke_stream(
                    messages=user_input,
                    thread=thread,
                    on_intermediate_message=handle_streaming_intermediate_steps,
                ):
                    # Print the agent's response
                    print(f"{response}", end="", flush=True)
                    # Update the thread for subsequent messages
                    thread = response.thread
                
                print("\n" + "=" * 50)
        finally:
            # 清理資源：刪除執行緒和 agent
            if thread:
                await thread.delete()
            await client.agents.delete_agent(agent.id)
            print(f"\n已清理 Logic App Agent 資源")

        """
        範例輸出：
        # User: '發送一封會議通知郵件給團隊'
        Function Call:> LogicAppPlugin-send_email with arguments: {"to": "team@company.com", "subject": "會議通知 - 週例會", "body": "親愛的團隊成員，\n\n本週例會時間如下：\n日期：2024年1月15日\n時間：上午10:00\n地點：會議室A\n\n請準時參加。\n\n謝謝"}
        Function Result:> ✅ 電子郵件已成功透過 Logic App 發送至 team@company.com，主旨: 會議通知 - 週例會 for function: LogicAppPlugin-send_email
        
        📧 **會議通知已發送**
        
        我已透過 Logic App 成功發送會議通知郵件：
        - 收件人：team@company.com
        - 主旨：會議通知 - 週例會
        - 狀態：✅ 成功發送
        
        郵件包含了會議的基本資訊，團隊成員應該很快就會收到通知。
        """


if __name__ == "__main__":
    asyncio.run(main())