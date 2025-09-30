# Copyright (c) Microsoft. All rights reserved.

import asyncio
import datetime
import json
import os
import requests
from typing import Optional
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential

# Databricks imports
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI

from semantic_kernel.agents import (
    Agent,
    AzureAIAgent,
    AzureAIAgentSettings,
    MagenticOrchestration,
    StandardMagenticManager,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.functions import kernel_function

# Logic App imports
try:
    from azure.mgmt.logic import LogicManagementClient
    LOGIC_MGMT_AVAILABLE = True
except ImportError:
    LOGIC_MGMT_AVAILABLE = False

"""
互動式多代理程式系統 - Magentic 編排
================================================

這是一個互動式的企業級多代理程式系統，整合了四個專業代理程式：

1. **AI Search Agent**: 飯店和文檔搜尋專家
   - 使用 Azure AI Search 進行語義搜尋
   - 可搜尋飯店資訊、技術文檔等

2. **Databricks Agent**: 資料分析專家  
   - 使用 Databricks Genie API 進行數據查詢
   - 可分析交易數據、使用者行為等

3. **Fabric Agent**: 商業智慧專家
   - 使用 Microsoft Fabric lakehouse 分析計程車數據
   - 提供商業洞察和 KPI 分析

4. **Logic App Agent**: 工作流程自動化專家
   - 使用 Azure Logic Apps 發送電子郵件
   - 提供時間資訊和自動化流程

使用方式:
    python step2_sk_multi_agent_magentic.py

範例問題:
    1. "幫我找一些豪華飯店，然後分析一下預訂數據趨勢"
    2. "查詢交易數據中的異常模式，並發送報告到我的郵箱"
    3. "搜尋技術文檔中的最佳實務，並生成摘要郵件"
    4. "分析計程車數據的高峰時段，然後推薦相關的商務飯店"
"""

# 載入環境變數
load_dotenv()

# 設定 Databricks SDK
os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"

DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"

# 環境變數設定
MY_AZURE_OPENAI_ENDPOINT = os.getenv("MY_AZURE_OPENAI_ENDPOINT")
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

# Databricks 連接設定
FOUNDRY_DATABRICKS_CONNECTION_NAME = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")

# Fabric 連接設定  
FOUNDRY_FABRIC_CONNECTION_NAME = os.getenv("FABRIC_CONNECTION_NAME")

# Logic App 設定
subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
resource_group = os.environ.get("AZURE_RESOURCE_GROUP") 
logic_app_name = os.environ.get("LOGIC_APP_NAME")
trigger_name = os.environ.get("TRIGGER_NAME")
recipient_email = os.environ.get("RECIPIENT_EMAIL")
LOGIC_APP_EMAIL_TRIGGER_URL = os.getenv("LOGIC_APP_EMAIL_TRIGGER_URL")

# 全域變數儲存連接資訊
genie_api = None
genie_space_id = None
databricks_workspace_client = None
fabric_connection = None
logic_app_manager = None

# 預定義問題範例
SAMPLE_QUESTIONS = [
    # 單一代理程式問題
    "推薦一些豪華飯店給商務旅客",
    "查詢最近一周的交易數據平均值",
    "比較國定假日與平日的計程車行程數",
    "發送測試郵件到我的信箱",
    "查詢當前時間並格式化",
    "搜尋關於數位轉型的最佳實務文檔",
    
    # 多代理程式合作問題
    "幫我找豪華飯店，然後分析預訂趨勢數據，最後發送分析報告到我的郵箱",
    "搜尋技術文檔中的 API 最佳實務，查詢系統性能數據，並將結果整合後寄送給團隊",
    "分析計程車數據找出高峰時段，推薦該時段附近的商務飯店，並預約確認郵件",
    "查詢異常交易數據，搜尋相關安全政策文檔，制定處理流程並通知管理層",
]

SAMPLE_DESCRIPTIONS = [
    "豪華飯店推薦 (AI Search)",
    "交易數據查詢 (Databricks)", 
    "計程車行程分析 (Fabric)",
    "發送測試郵件 (Logic App)",
    "取得當前時間 (Logic App)",
    "搜尋技術文檔 (AI Search)",
    "🔗 飯店推薦 + 數據分析 + 郵件報告",
    "🔗 文檔搜尋 + 數據查詢 + 結果整合",
    "🔗 數據分析 + 飯店推薦 + 預約通知", 
    "🔗 異常偵測 + 政策搜尋 + 流程通知",
]
logic_app_manager = None

# Logic App 管理類別
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


# ==================== AI Search Plugin ====================
class AISearchPlugin:
    @kernel_function
    def search_documents(self, query: str) -> str:
        """搜尋和檢索相關文檔資訊 - 這會使用 Azure AI Search 提供的檢索功能"""
        # 注意：這個是使用 retrieval 工具的 agent，實際搜尋由 Azure AI Search 處理
        # 在 multi-agent 場景中，這個 plugin 主要是作為代理程式的工具介面
        return f"已搜尋查詢: '{query}'。Azure AI Search 檢索功能已啟動，將返回相關文檔。"

    @kernel_function
    def analyze_search_trends(self, topic: str) -> str:
        """分析搜尋趨勢和模式"""
        return f"正在分析 '{topic}' 的搜尋趨勢。將透過 Azure AI Search 分析歷史查詢模式和結果相關性。"


# ==================== Databricks Plugin ====================
class DatabricksPlugin:
    @kernel_function
    def ask_genie(self, question: str, conversation_id: Optional[str] = None) -> str:
        """
        向 Databricks Genie 提問並以 JSON 格式回傳回應。
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
            # 如果 conversation_id 是字串 "null"，將其設為 None
            if conversation_id == "null":
                conversation_id = None
                
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


# ==================== Microsoft Fabric Plugin ====================  
class FabricPlugin:
    @kernel_function
    def query_fabric(self, question: str, query_type: str = "general") -> str:
        """
        向 Microsoft Fabric lakehouse 查詢計程車數據並取得回應。
        這是一個模擬函數，在實際實作中會連接到真實的 Fabric lakehouse。
        
        Args:
            question: 要查詢的問題
            query_type: 查詢類型 (general, stats, trends, anomaly, geography)
            
        Returns:
            str: JSON 格式的回應，包含查詢結果
        """
        global fabric_connection
        
        if not fabric_connection:
            return json.dumps({
                "error": "Microsoft Fabric connection not initialized",
                "details": "Please ensure FOUNDRY_FABRIC_CONNECTION_NAME is set correctly"
            })
        
        try:
            # 這裡模擬 Fabric lakehouse 查詢
            # 在實際實作中，這會執行 SQL 查詢到 Fabric lakehouse
            
            import random
            
            if "總行程數" in question or "trip count" in question.lower():
                # 模擬行程統計查詢
                holiday_trips = random.randint(45000, 55000)
                weekday_trips = random.randint(65000, 75000)
                return json.dumps({
                    "query": question,
                    "result": {
                        "holiday_trips": holiday_trips,
                        "weekday_trips": weekday_trips,
                        "difference": weekday_trips - holiday_trips,
                        "analysis": f"平日行程數 ({weekday_trips}) 比國定假日 ({holiday_trips}) 多 {weekday_trips - holiday_trips} 趟"
                    }
                })
            elif "車資" in question or "fare" in question.lower():
                # 模擬車資分析查詢
                avg_fare = round(random.uniform(12.5, 15.8), 2)
                high_fare_count = random.randint(8000, 12000)
                total_trips = random.randint(500000, 600000)
                percentage = round((high_fare_count / total_trips) * 100, 2)
                return json.dumps({
                    "query": question,
                    "result": {
                        "average_fare": avg_fare,
                        "high_fare_trips": high_fare_count,
                        "total_trips": total_trips,
                        "percentage": percentage,
                        "analysis": f"平均車資為 ${avg_fare}，高車資行程 (>$70) 佔 {percentage}%"
                    }
                })
            elif "日間" in question and "夜間" in question:
                # 模擬日夜對比查詢
                day_trips = random.randint(380000, 420000)
                night_trips = random.randint(180000, 220000)
                day_avg_fare = round(random.uniform(13.2, 15.5), 2)
                night_avg_fare = round(random.uniform(14.8, 17.2), 2)
                return json.dumps({
                    "query": question,
                    "result": {
                        "day_trips": day_trips,
                        "night_trips": night_trips,
                        "day_avg_fare": day_avg_fare,
                        "night_avg_fare": night_avg_fare,
                        "analysis": f"日間行程: {day_trips} 趟 (平均 ${day_avg_fare})，夜間行程: {night_trips} 趟 (平均 ${night_avg_fare})"
                    }
                })
            else:
                # 一般查詢回應
                return json.dumps({
                    "query": question,
                    "result": {
                        "message": "這是一個關於計程車數據的模擬分析結果",
                        "data_source": "Microsoft Fabric lakehouse (模擬)",
                        "note": "實際實作中會執行真實的 SQL 查詢"
                    }
                })

        except Exception as e:
            return json.dumps({
                "error": "查詢 Microsoft Fabric lakehouse 時發生錯誤",
                "details": str(e)
            })


# ==================== Logic App Plugin ====================
class LogicAppPlugin:
    @kernel_function
    def fetch_current_datetime(self, time_format: Optional[str] = None) -> str:
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

    @kernel_function
    def send_email_via_logic_app(self, recipient: str, subject: str, body: str) -> str:
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


async def get_integrated_agents(client) -> list[Agent]:
    """回傳將參與 Magentic 編排的整合代理程式清單"""
    agents = []
    
    # 1. AI Search 檢索代理程式 (使用已存在的 agent ID)
    search_agent_id = "asst_vnVvS09TGw3zOC6Z0vxiviN0"
    try:
        search_agent_definition = await client.agents.get_agent(agent_id=search_agent_id)
        
        # 檢查並修復 description 如果為空
        if not search_agent_definition.description:
            print(f"⚠️ AI Search Agent 缺少 description，正在更新...")
            # 更新 agent 的 description
            search_agent_definition = await client.agents.update_agent(
                agent_id=search_agent_id,
                name=search_agent_definition.name or "AISearchAgent",
                description="專精於文檔搜尋和資訊檢索的助手，具備 Azure AI Search 整合功能",
                instructions=search_agent_definition.instructions or "您是資訊檢索專家。使用搜尋工具來獲取準確的結果。",
                model=search_agent_definition.model,
                tools=search_agent_definition.tools,
            )
        
        search_agent = AzureAIAgent(
            client=client,
            definition=search_agent_definition,
            plugins=[AISearchPlugin()],
        )
        agents.append(search_agent)
        print(f"✅ 已載入 AI Search Agent (ID: {search_agent_id})")
    except Exception as e:
        print(f"⚠️ 無法載入 AI Search Agent: {e}")
        # 如果無法載入，建立新的 agent
        search_agent_definition = await client.agents.create_agent(
            model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
            name="AISearchAgent", 
            description="專精於飯店搜尋和文檔檢索的助手，具備 Azure AI Search 整合功能",
            instructions="""您是一個專業的飯店推薦和文檔檢索助手。您可以根據用戶的需求，使用 Azure AI Search 來搜索和推薦合適的飯店或相關文檔。

您的專長包括:
1. 飯店推薦: 根據用戶需求（豪華、經濟、商務等）搜尋合適的飯店
2. 文檔檢索: 搜尋技術文檔、最佳實務、政策文件等企業資料
3. 資訊分析: 提供詳細的搜尋結果分析和建議

當用戶詢問飯店推薦或文檔搜尋相關問題時，請:
- 使用搜尋工具來查找相關資訊
- 提供詳細的推薦與說明
- 包含具體的資訊如位置、價格、特色等
- 以繁體中文回應，保持專業和有幫助的語調""",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "AISearchPlugin-search_documents",
                        "description": "搜尋和檢索相關文檔資訊",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "搜尋查詢內容"}
                            },
                            "required": ["query"],
                        },
                    },
                },
            ],
        )
        search_agent = AzureAIAgent(
            client=client,
            definition=search_agent_definition,
            plugins=[AISearchPlugin()],
        )
        agents.append(search_agent)
    
    # 2. Databricks 資料分析代理程式
    databricks_agent_definition = await client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
        name="DatabricksAnalyst",
        description="專精於大數據分析和機器學習的助手，具備 Databricks 平台整合功能",
        instructions="""您是一個專業的資料科學分析助手，使用 Databricks Genie API 來分析和查詢數據。

您的專長包括:
1. 交易數據分析: 計算平均值、趨勢分析、異常檢測
2. 使用者行為分析: 活躍用戶、行為模式、參與度指標  
3. 系統性能分析: API 延遲、錯誤率、流量分析
4. 商業指標計算: 收入分析、成長率、KPI 追蹤

當用戶詢問數據相關問題時，請:
- 使用 ask_genie 函數從 Databricks 獲取真實數據
- 如果是後續問題，使用 conversation_id 維持對話上下文
- 提供清晰的數據洞察和趨勢分析
- 包含具體的統計數字和可視化建議
- 以繁體中文回應，保持專業和分析性的語調

請總是基於真實數據提供分析，而不是假設或估計。""",
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
    databricks_agent = AzureAIAgent(
        client=client,
        definition=databricks_agent_definition,
        plugins=[DatabricksPlugin()],
    )
    agents.append(databricks_agent)
    
    # 3. Microsoft Fabric 商業智慧代理程式
    fabric_agent_definition = await client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
        name="FabricBusinessAnalyst",
        description="專精於商業智慧和計程車數據分析的助手，具備 Microsoft Fabric 平台整合功能",
        instructions="""您是一個專業的商業分析助手，專門分析 Microsoft Fabric lakehouse 中的計程車行程數據。

您的專業領域包括分析：
- 國定假日與平日的行程模式和費用比較
- 高費用行程分析（行程 > $70）及其百分比分佈  
- 日間（7:00-19:00）與夜間（19:00-7:00）行程和費用模式
- 地理分析，包括熱門上車地點和郵遞區號
- 乘客數量分佈和統計分析
- 商業 KPI 如客戶終身價值、毛利率、客戶流失率

您應該：
1. 使用 query_fabric 函數從 Fabric lakehouse 檢索真實數據
2. 提供清晰、結構化的回應，包含具體數字和統計資料
3. 基於數據分析提供商業洞察和趋勢
4. 以繁體中文呈現資訊，同時保留技術術語和欄位名稱的英文
5. 始終保持專業和樂於助人的語調

當使用者詢問計程車行程數據或商業分析時，提供包含相關統計、趨勢和可行洞察的全面分析。""",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-query_fabric",
                    "description": "使用 Microsoft Fabric lakehouse 查詢和分析計程車數據。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string", 
                                "description": "要查詢的問題或分析請求"
                            },
                            "query_type": {
                                "type": "string", 
                                "description": "查詢類型：general, stats, trends, anomaly, geography",
                                "default": "general"
                            }
                        },
                        "required": ["question"],
                    },
                },
            }
        ],
    )
    fabric_agent = AzureAIAgent(
        client=client,
        definition=fabric_agent_definition,
        plugins=[FabricPlugin()],
    )
    agents.append(fabric_agent)
    
    # 4. Logic App 工作流程自動化代理程式
    logic_app_agent_definition = await client.agents.create_agent(
        model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
        name="LogicAppOrchestrator",
        description="專精於業務流程自動化和系統整合的助手，具備 Azure Logic Apps 整合功能",
        instructions="""您是一個專業的業務流程自動化助手，專精於使用 Azure Logic Apps 來執行發送電子郵件和時間相關的任務。

您的功能包括:
1. 電子郵件發送: 透過 Azure Logic App 發送專業的商業郵件
2. 時間管理: 提供當前時間資訊，支援多種格式
3. 工作流程自動化: 建議和協助設置自動化業務流程
4. 通知系統: 發送報告、提醒和狀態更新郵件

您應該：
1. 當用戶需要發送郵件時，使用 send_email_via_logic_app 函數
2. 當用戶詢問時間時，使用 fetch_current_datetime 函數
3. 提供專業的郵件內容建議和格式化
4. 確保郵件內容清晰、專業且符合商業標準
5. 以繁體中文回應，但保持郵件內容的適當語言

特別注意:
- 郵件主旨要簡潔明確
- 郵件內容要結構化且易讀
- 包含必要的聯絡資訊和後續行動
- 適當使用正式或半正式的語調""",
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
                }
            }
        ],
    )
    logic_app_agent = AzureAIAgent(
        client=client,
        definition=logic_app_agent_definition,
        plugins=[LogicAppPlugin()],
    )
    agents.append(logic_app_agent)
    
    return agents


def display_menu():
    """顯示互動選單"""
    print("\n" + "="*80)
    print("🤖 多代理程式企業智能助手 - Magentic 編排系統")
    print("="*80)
    print("\n可用的專業代理程式:")
    print("🔍 AI Search Agent    - 飯店搜尋和文檔檢索專家")
    print("📊 Databricks Agent  - 資料分析和機器學習專家") 
    print("📈 Fabric Agent      - 商業智慧和計程車數據專家")
    print("⚡ Logic App Agent   - 工作流程自動化和郵件專家")
    
    print(f"\n📋 預設問題範例:")
    for i, (question, desc) in enumerate(zip(SAMPLE_QUESTIONS, SAMPLE_DESCRIPTIONS), 1):
        print(f"   {i:2d}. {desc}")
    
    print("\n其他選項:")
    print("   0. 退出程式")
    print("   99. 自定義問題（直接輸入您的問題）")
    print("\n" + "="*80)

def get_query_by_selection(selection: str) -> str:
    """透過選擇編號取得範例查詢"""
    try:
        query_num = int(selection)
        if 1 <= query_num <= len(SAMPLE_QUESTIONS):
            return SAMPLE_QUESTIONS[query_num - 1]
    except ValueError:
        pass
    return None

def display_task_info(task: str):
    """顯示任務資訊"""
    print(f"\n📋 **執行任務**:")
    print("-" * 60)
    print(f"{task}")
    print("-" * 60)
    print("🤖 多代理程式正在協作處理您的請求...")
    print("=" * 60)

async def process_user_query(magentic_orchestration, runtime, query: str):
    """處理使用者查詢"""
    try:
        display_task_info(query)
        
        # 呼叫編排
        orchestration_result = await magentic_orchestration.invoke(
            task=query,
            runtime=runtime,
        )

        # 等待並展示結果  
        final_result = await orchestration_result.get()

        print("\n" + "=" * 60)
        print("🎯 **最終結果**")
        print("=" * 60)
        print(f"{final_result}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 處理查詢時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def agent_response_callback(message: ChatMessageContent) -> None:
    """觀察函數，用於列印來自代理程式的訊息"""
    print(f"\n**{message.name}**")
    print(f"{message.content}")
    print("-" * 60)


async def main():
    """執行整合多代理程式編排的主要函數"""
    global genie_api, genie_space_id, databricks_workspace_client, fabric_connection, logic_app_manager
    
    if not FOUNDRY_PROJECT_ENDPOINT:
        raise ValueError("FOUNDRY_PROJECT_ENDPOINT environment variable is required")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds, endpoint=FOUNDRY_PROJECT_ENDPOINT) as client,
    ):
        print("🚀 正在初始化企業級多代理程式系統...")
        print("=" * 60)
        
        # 初始化各種連接
        print("🔧 正在初始化系統連接...")
        
        # 1. 初始化 Databricks 連接
        try:
            if FOUNDRY_DATABRICKS_CONNECTION_NAME:
                connection = await client.connections.get(name=FOUNDRY_DATABRICKS_CONNECTION_NAME)
                print(f"✅ 取得 Databricks 連接 '{FOUNDRY_DATABRICKS_CONNECTION_NAME}'")
                
                if connection.metadata.get('azure_databricks_connection_type') == 'genie':
                    genie_space_id = connection.metadata.get('genie_space_id')
                    print(f"✅ 取得 Genie Space ID: {genie_space_id}")
                else:
                    print("⚠️ Databricks 連接不是 Genie 類型")

                # 初始化 Databricks 工作區客戶端
                token_result = await creds.get_token(DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE)
                databricks_workspace_client = WorkspaceClient(
                    host=connection.target,
                    token=token_result.token,
                )
                genie_api = GenieAPI(databricks_workspace_client.api_client)
                print("✅ Databricks Genie API 初始化成功")
        except Exception as e:
            print(f"⚠️ Databricks 連接失敗: {e}")
            
        # 2. 初始化 Microsoft Fabric 連接
        try:
            if FOUNDRY_FABRIC_CONNECTION_NAME:
                connection = await client.connections.get(name=FOUNDRY_FABRIC_CONNECTION_NAME)
                print(f"✅ 取得 Fabric 連接 '{FOUNDRY_FABRIC_CONNECTION_NAME}'")
                
                fabric_connection = {
                    "name": connection.name,
                    "target": connection.target if hasattr(connection, 'target') else 'mock-fabric-endpoint',
                    "connection_type": "fabric_lakehouse"
                }
                print("✅ Microsoft Fabric 連接初始化成功")
        except Exception as e:
            print(f"⚠️ Fabric 連接失敗，使用模擬模式: {e}")
            fabric_connection = {
                "name": "mock-fabric-connection",
                "target": "mock-fabric-endpoint", 
                "connection_type": "fabric_lakehouse"
            }
        
        # 3. 初始化 Logic App 連接
        if (LOGIC_APP_EMAIL_TRIGGER_URL or 
            (subscription_id and resource_group and logic_app_name and trigger_name)):
            try:
                logic_app_manager = LogicAppManager()
                print("✅ Logic App 管理器初始化成功")
            except Exception as e:
                print(f"⚠️ Logic App 連接失敗: {e}")
        else:
            print("⚠️ Logic App 設定未完整，將使用模擬模式")
            
        print("=" * 60)
        
        # 建立整合的 Magentic 編排
        agents_list = await get_integrated_agents(client)
        
        print(f"✅ 已建立 {len(agents_list)} 個專業代理程式:")
        for i, agent in enumerate(agents_list, 1):
            print(f"   {i}. {agent.name} - {agent.description}")
        
        magentic_orchestration = MagenticOrchestration(
            members=agents_list,
            manager=StandardMagenticManager(
                chat_completion_service=AzureChatCompletion(
                    endpoint=MY_AZURE_OPENAI_ENDPOINT,
                )
            ),
            agent_response_callback=agent_response_callback,
        )
        
        # 2. 建立運行時並啟動
        runtime = InProcessRuntime()
        runtime.start()
        print("✅ 多代理程式運行時已啟動")
        
        print("\n🎯 歡迎使用多代理程式企業智能助手！")
        print("您可以選擇預設查詢或輸入自定義問題。")

        try:
            # 3. 互動式查詢循環
            while True:
                try:
                    display_menu()
                    user_choice = input("\n請選擇 (例如: 1, 2, 99 或 0): ").strip()
                    
                    if user_choice == "0":
                        print("\n👋 謝謝使用，再見！")
                        break
                    elif user_choice == "99":
                        custom_query = input("\n請輸入您的問題: ").strip()
                        if not custom_query:
                            print("❌ 問題不能為空")
                            continue
                        user_query = custom_query
                    else:
                        sample_query = get_query_by_selection(user_choice)
                        if sample_query:
                            user_query = sample_query
                            print(f"\n📋 選擇的查詢: {sample_query[:100]}{'...' if len(sample_query) > 100 else ''}")
                        else:
                            print("❌ 無效的選擇，請重新選擇")
                            continue
                    
                    # 處理使用者查詢
                    print("\n🔄 啟動多代理程式協作...")
                    success = await process_user_query(magentic_orchestration, runtime, user_query)
                    
                    if success:
                        print("✅ 查詢處理完成")
                    else:
                        print("❌ 查詢處理失敗")
                    
                    # 詢問使用者是否要繼續
                    continue_choice = input("\n是否繼續查詢？(y/n): ").strip().lower()
                    if continue_choice not in ['y', 'yes', '是', '']:
                        print("\n👋 謝謝使用，再見！")
                        break
                        
                except KeyboardInterrupt:
                    print("\n\n👋 程式被中斷，再見！")
                    break
                except Exception as e:
                    print(f"❌ 處理過程中發生錯誤: {str(e)}")
                    continue

        finally:
            # 5. 清理資源
            print("\n🧹 正在清理系統資源...")
            await runtime.stop_when_idle()
            
            # 刪除所有代理程式 (除了預先存在的 AI Search agent)
            for agent in agents_list:
                if agent.id != "asst_vnVvS09TGw3zOC6Z0vxiviN0":  # 不刪除預先存在的 agent
                    try:
                        await client.agents.delete_agent(agent.id)
                        print(f"   ✅ 已刪除 {agent.name}")
                    except Exception as e:
                        print(f"   ⚠️ 無法刪除 {agent.name}: {e}")
                else:
                    print(f"   🔒 保留預先存在的 {agent.name}")
            
            print("✅ 系統清理完成")


if __name__ == "__main__":
    asyncio.run(main())