# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import os
import datetime
import requests
from typing import Optional
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)
from semantic_kernel.functions.kernel_function_decorator import kernel_function

"""
以下範例示範如何在 Semantic Kernel 中使用 Azure AI Agent
並提供 Logic App 函式工具進行電子郵件發送。

環境變數設定：
必要:
- PROJECT_ENDPOINT 或 FOUNDRY_PROJECT_ENDPOINT: Azure AI Foundry 專案端點
- MODEL_DEPLOYMENT_NAME: 模型部署名稱（預設: gpt-4o-mini）

Logic App 設定（二選一）:
選項 1 - 直接 URL:
- LOGIC_APP_EMAIL_TRIGGER_URL: Logic App 的完整 HTTP 觸發器 URL

選項 2 - Azure Management API:
- AZURE_SUBSCRIPTION_ID: Azure 訂用帳戶 ID
- AZURE_RESOURCE_GROUP: 資源群組名稱
- LOGIC_APP_NAME: Logic App 名稱  
- TRIGGER_NAME: 觸發器名稱（通常是 "When_a_HTTP_request_is_received"）

選用:
- RECIPIENT_EMAIL: 預設收件人郵件地址（預設: payton.chou@microsoft.com）

前置條件:
1. pip install azure-ai-projects azure-identity azure-mgmt-logic (如使用 Azure Management API)
2. 在 Azure 入口網站建立 Logic App 並設定 HTTP 觸發器
3. Logic App 應接受包含 'to', 'subject', 'body' 的 JSON 請求
"""

# 載入環境變數
load_dotenv()

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")

# 使用 PROJECT_ENDPOINT 或 FOUNDRY_PROJECT_ENDPOINT 作為後備
endpoint = PROJECT_ENDPOINT or FOUNDRY_PROJECT_ENDPOINT

# Logic App 相關設定
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
resource_group = os.environ.get("AZURE_RESOURCE_GROUP")
logic_app_name = os.environ.get("LOGIC_APP_NAME")
trigger_name = os.environ.get("TRIGGER_NAME")
recipient_email = os.environ.get("RECIPIENT_EMAIL")

# 後備選項：如果設定了 LOGIC_APP_EMAIL_TRIGGER_URL，則使用直接 URL 方式
LOGIC_APP_EMAIL_TRIGGER_URL = os.getenv("LOGIC_APP_EMAIL_TRIGGER_URL")

# 檢查必要環境變數
def check_environment_variables():
    """檢查並驗證必要的環境變數"""
    if not endpoint:
        raise ValueError("需要設定 PROJECT_ENDPOINT 或 FOUNDRY_PROJECT_ENDPOINT 環境變數")
    
    # 檢查是否有 Logic App 設定（任一種方式）
    has_logic_app_config = bool(
        LOGIC_APP_EMAIL_TRIGGER_URL or 
        (subscription_id and resource_group and logic_app_name and trigger_name)
    )
    
    if not has_logic_app_config:
        print("⚠️  警告: 未檢測到完整的 Logic App 設定")
        print("請設定以下任一組環境變數:")
        print("選項 1 - 直接 URL:")
        print("   LOGIC_APP_EMAIL_TRIGGER_URL=<your_logic_app_url>")
        print("選項 2 - Azure 管理設定:")
        print("   AZURE_SUBSCRIPTION_ID=<your_subscription_id>")
        print("   AZURE_RESOURCE_GROUP=<your_resource_group>")
        print("   LOGIC_APP_NAME=<your_logic_app_name>")
        print("   TRIGGER_NAME=<your_trigger_name>")
    
    return has_logic_app_config

# 驗證環境變數
has_logic_app_config = check_environment_variables()

# 添加 Logic App 管理類別
try:
    from azure.mgmt.logic import LogicManagementClient
    LOGIC_MGMT_AVAILABLE = True
except ImportError:
    LOGIC_MGMT_AVAILABLE = False
    print("⚠️  azure-mgmt-logic 套件未安裝，將使用直接 URL 模式")

class LogicAppManager:
    """管理 Logic App 調用的類別，支援兩種模式：直接 URL 或 Azure Management API"""
    
    def __init__(self):
        self.callback_url = None
        self.logic_client = None
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.logic_app_name = logic_app_name
        self.trigger_name = trigger_name
        
        # 初始化 Logic App 連接
        self._initialize_logic_app()
    
    def _initialize_logic_app(self):
        """初始化 Logic App 連接"""
        if LOGIC_APP_EMAIL_TRIGGER_URL:
            # 使用直接 URL 模式
            self.callback_url = LOGIC_APP_EMAIL_TRIGGER_URL
            print(f"✅ 使用直接 Logic App URL 模式")
            return
        
        if (LOGIC_MGMT_AVAILABLE and self.subscription_id and 
            self.resource_group and self.logic_app_name and self.trigger_name):
            # 使用 Azure Management API 模式
            try:
                credential = SyncDefaultAzureCredential()
                self.logic_client = LogicManagementClient(credential, self.subscription_id)
                
                callback = self.logic_client.workflow_triggers.list_callback_url(
                    resource_group_name=self.resource_group,
                    workflow_name=self.logic_app_name,
                    trigger_name=self.trigger_name,
                )
                
                if callback.value:
                    self.callback_url = callback.value
                    print(f"✅ 成功註冊 Logic App '{self.logic_app_name}' 觸發器 '{self.trigger_name}'")
                else:
                    print(f"❌ Logic App '{self.logic_app_name}' 未回傳回呼 URL")
                    
            except Exception as e:
                print(f"❌ 註冊 Logic App 失敗: {str(e)}")
                print("將使用模擬模式")
    
    def send_email(self, recipient: str, subject: str, body: str) -> dict:
        """發送郵件的統一介面"""
        if not self.callback_url:
            return {
                "status": "warning",
                "message": "Logic App URL 未設定，使用模擬模式",
                "result": "模擬寄送: OK",
                "recipient": recipient,
                "subject": subject
            }
        
        payload = {"to": recipient, "subject": subject, "body": body}
        try:
            resp = requests.post(self.callback_url, json=payload, timeout=30)
            resp.raise_for_status()
            return {
                "status": "success",
                "message": "寄送成功",
                "recipient": recipient,
                "subject": subject
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"寄送失敗: {e}",
                "recipient": recipient,
                "subject": subject
            }

# 建立全域 Logic App 管理器實例
logic_app_manager = LogicAppManager() if has_logic_app_config else None

# 新增 agent_id 變數
agent_id = "asst_y0FKQgpgmVOzhJZWBM8Tmxrk"

# 定義工具函式作為 Kernel Functions
@kernel_function(description="以指定格式取得目前時間", name="fetch_current_datetime")
def fetch_current_datetime(time_format: Optional[str] = None) -> str:
    """以 JSON 字串形式取得目前時間，可選擇性地格式化。
    
    Args:
        time_format: 返回目前時間的格式。預設為 None，將使用標準格式。
    
    Returns:
        目前的 UTC 日期時間
    """
    current_time = datetime.datetime.now(datetime.timezone.utc)
    if time_format:
        try:
            return current_time.strftime(time_format)
        except ValueError:
            # 如果格式無效，回傳 ISO 格式
            pass
    return current_time.isoformat()


@kernel_function(description="透過 Logic App 傳送電子郵件", name="send_email_via_logic_app")
def send_email_via_logic_app(recipient: str, subject: str, body: str) -> str:
    """透過以給定的收件人、主旨和內容調用指定的 Logic App 來傳送電子郵件。
    
    Args:
        recipient: 收件人的電子郵件地址。
        subject: 電子郵件的主旨。
        body: 電子郵件的內容。
    
    Returns:
        寄送結果訊息的 JSON 字串
    """
    if not logic_app_manager:
        return json.dumps({
            "status": "warning",
            "message": "Logic App 未正確設定，使用模擬模式",
            "result": "模擬寄送: OK",
            "recipient": recipient,
            "subject": subject
        })
    
    result = logic_app_manager.send_email(recipient, subject, body)
    return json.dumps(result)

# 模擬與 agent 的對話
default_recipient = recipient_email or "payton.chou@microsoft.com"
USER_INPUTS = [
    f"請發送一封郵件到 {default_recipient}，主旨為 'Test from Logic App'，內容為 '歡迎來到我們的團隊！'"
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
    if not endpoint:
        raise ValueError("PROJECT_ENDPOINT 或 FOUNDRY_PROJECT_ENDPOINT 環境變數是必要的")
    
    print(f"使用端點: {endpoint}")
    if logic_app_manager and logic_app_manager.callback_url:
        print(f"Logic App 已設定並準備就緒")
    else:
        print("⚠️  Logic App 未設定，將使用模擬模式")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds, endpoint=endpoint) as client,
    ):
        # 1. 建立新的 agent 定義，包含 Logic App 函數工具的定義
        agent_definition = await client.agents.create_agent(
            model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
            name="LogicAppEmailAgent",
            description="專門使用 Logic App 發送電子郵件和提供時間資訊的代理程式。",
            instructions="您是一個助手，可以幫用戶發送電子郵件和提供時間資訊。當用戶需要發送郵件時，請使用 send_email_via_logic_app 函數。當用戶詢問時間時，請使用 fetch_current_datetime 函數。",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "LogicAppPlugin-fetch_current_datetime",
                        "description": "取得目前的日期和時間。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "string",
                                    "description": "可選的時間格式字串"
                                }
                            },
                            "required": [],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "LogicAppPlugin-send_email_via_logic_app",
                        "description": "透過 Azure Logic App 發送電子郵件。",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recipient": {
                                    "type": "string",
                                    "description": "收件人的電子郵件地址"
                                },
                                "subject": {
                                    "type": "string",
                                    "description": "電子郵件的主旨"
                                },
                                "body": {
                                    "type": "string",
                                    "description": "電子郵件的內容"
                                }
                            },
                            "required": ["recipient", "subject", "body"],
                        },
                    },
                }
            ],
        )
        print(f"Created agent definition, agent ID: {agent_definition.id}")
        
        # 2. 建立插件類別並註冊到 Semantic Kernel
        class LogicAppPlugin:
            @kernel_function(description="以指定格式取得目前時間", name="fetch_current_datetime")
            def fetch_current_datetime(self, time_format: Optional[str] = None) -> str:
                return fetch_current_datetime(time_format)
            
            @kernel_function(description="透過 Logic App 傳送電子郵件", name="send_email_via_logic_app")
            def send_email_via_logic_app(self, recipient: str, subject: str, body: str) -> str:
                return send_email_via_logic_app(recipient, subject, body)

        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
            plugins=[LogicAppPlugin()],
        )
        
        print("Registered Logic App functions to agent kernel")
        print(f"Agent kernel plugins: {list(agent.kernel.plugins.keys())}")
        
        # 驗證函數是否已註冊
        if agent.kernel.plugins:
            for plugin_name, plugin in agent.kernel.plugins.items():
                print(f"{plugin_name} functions: {list(plugin.functions.keys()) if hasattr(plugin, 'functions') else 'No functions attribute'}")

        # 3. 建立 agent 對話執行緒
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
            except Exception as e:  # noqa: BLE001
                print(f"Note: Could not delete agent {agent_definition.id}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
