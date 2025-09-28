# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    專門的代理程式實現，將單一功能的腳本轉換為可協作的代理程式類別。
    
包含以下代理程式：
- AzureAISearchAgent: Azure AI Search 搜尋代理
- LogicAppsAgent: Logic Apps 自動化代理  
- FabricAgent: Microsoft Fabric 數據分析代理
- DatabricksAgent: Azure Databricks Genie 代理
"""

import os
import json
import random
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime
from dotenv import load_dotenv

# Import from our handoff system
from step4_handoff import BaseAgent, HandoffRequest, HandoffType, create_handoff_request

# Import necessary libraries for each agent - all conditional for testing
try:
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    print("Warning: Azure Search packages not available")
    AZURE_SEARCH_AVAILABLE = False
    class AzureKeyCredential: pass
    class SearchClient: pass

# Logic Apps dependencies
try:
    from azure.mgmt.logic import LogicManagementClient
    import requests
    LOGIC_APPS_AVAILABLE = True
except ImportError:
    print("Warning: Logic Apps packages not available")
    LOGIC_APPS_AVAILABLE = False
    class LogicManagementClient: pass

# Databricks dependencies
try:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.dashboards import GenieAPI
    DATABRICKS_AVAILABLE = True
except ImportError:
    print("Warning: Databricks SDK not available. Using mock functions.")
    DATABRICKS_AVAILABLE = False
    class WorkspaceClient: pass
    class GenieAPI: pass

# Import user functions from existing modules - conditional
try:
    import sys
    sys.path.append('../s02_azure_logic_app')
    from user_functions import user_functions as logic_app_functions
    from user_logic_apps import AzureLogicAppTool, create_send_email_function
    LOGIC_APP_FUNCTIONS_AVAILABLE = True
except ImportError:
    print("Warning: Logic App functions not available. Using mock functions.")
    logic_app_functions = set()
    LOGIC_APP_FUNCTIONS_AVAILABLE = False
    class AzureLogicAppTool: pass
    def create_send_email_function(*args): return lambda *a: "mock email function"

try:
    import sys
    sys.path.append('../s03_microsoft_fabric')
    from taxi_query_functions import taxi_query_functions
    TAXI_FUNCTIONS_AVAILABLE = True
except ImportError:
    print("Warning: Fabric functions not available. Using mock functions.")
    taxi_query_functions = set()
    TAXI_FUNCTIONS_AVAILABLE = False

class AzureAISearchAgent(BaseAgent):
    """Azure AI Search 搜尋代理程式"""
    
    def __init__(self):
        super().__init__(
            name="AzureAISearchAgent",
            description="專門處理搜尋相關的查詢和資訊檢索",
            instructions="""你是一個專業的搜尋助手，專門使用 Azure AI Search 來幫助用戶找到相關資訊。

你的專業領域包括：
- 酒店資訊搜尋和推薦
- 向量搜尋和語意搜尋
- 文檔檢索和內容分析
- 搜尋結果排名和過濾

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求發送電子郵件 → LogicAppsAgent
- 用戶要求進行數據分析或統計 → FabricAgent  
- 用戶要求查詢資料庫或進行複雜的資料處理 → DatabricksAgent

請始終提供準確、相關且有用的搜尋結果。"""
        )
        self.search_client = None
        self.search_config = None
        
    async def initialize(self, project_client):
        """初始化搜尋客戶端"""
        await super().initialize(project_client)
        
        # Initialize search configuration
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_api_key = os.getenv("AZURE_SEARCH_API_KEY")
        index_name = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")
        
        if search_endpoint and search_api_key:
            self.search_config = {
                "endpoint": search_endpoint,
                "index_name": index_name
            }
            self.search_client = SearchClient(
                endpoint=search_endpoint,
                index_name=index_name,
                credential=AzureKeyCredential(search_api_key)
            )
            print(f"✅ Azure AI Search initialized for index: {index_name}")
        else:
            print("⚠️ Azure AI Search configuration not complete. Using mock search.")
    
    def search_hotels(self, query: str, filters: str = None) -> Dict[str, Any]:
        """搜尋酒店信息"""
        if self.search_client:
            try:
                if filters:
                    results = self.search_client.search(
                        search_text=query,
                        filter=filters,
                        top=5
                    )
                else:
                    results = self.search_client.search(search_text=query, top=5)
                
                hotel_results = []
                for result in results:
                    hotel_results.append({
                        "name": result.get("HotelName", "Unknown"),
                        "description": result.get("Description", ""),
                        "rating": result.get("Rating", 0),
                        "address": result.get("Address", ""),
                        "tags": result.get("Tags", [])
                    })
                
                return {
                    "success": True,
                    "query": query,
                    "results": hotel_results,
                    "total_found": len(hotel_results)
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            # Mock search results
            mock_hotels = [
                {
                    "name": "Grand Plaza Hotel",
                    "description": "Luxury hotel in downtown area with excellent amenities",
                    "rating": 4.5,
                    "address": "123 Main Street, Downtown",
                    "tags": ["luxury", "business", "spa"]
                },
                {
                    "name": "Boutique Garden Hotel",
                    "description": "Charming boutique hotel with garden views",
                    "rating": 4.2,
                    "address": "456 Garden Ave, Midtown",
                    "tags": ["boutique", "garden", "romantic"]
                }
            ]
            return {
                "success": True,
                "query": query,
                "results": mock_hotels,
                "total_found": len(mock_hotels)
            }
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要發送郵件 - 更全面的關鍵詞檢測
        if any(word in task_lower for word in ["send email", "發送郵件", "寄信", "email", "郵件", "通知客戶", "notify"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="LogicAppsAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with email sending request: {task}",
                context=context or {},
                priority=7
            )
        
        # 檢查是否需要數據分析
        if any(word in task_lower for word in ["analyze", "analysis", "statistics", "data", "分析", "統計", "數據"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="FabricAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with data analysis request: {task}",
                context=context or {},
                priority=6
            )
        
        return None

class LogicAppsAgent(BaseAgent):
    """Logic Apps 自動化代理程式"""
    
    def __init__(self):
        # Get available functions
        available_functions = set()
        if logic_app_functions:
            available_functions.update(logic_app_functions)
        
        super().__init__(
            name="LogicAppsAgent",
            description="專門處理自動化工作流程和郵件發送",
            instructions="""你是一個專業的自動化助手，專門使用 Azure Logic Apps 來執行自動化任務。

你的專業領域包括：
- 電子郵件發送和通知
- 工作流程自動化
- API 整合和調用
- 定時任務和觸發器管理

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求搜尋資訊 → AzureAISearchAgent
- 用戶要求進行數據分析 → FabricAgent
- 用戶要求查詢資料庫 → DatabricksAgent

你可以協助用戶發送郵件、設定自動化工作流程等任務。""",
            tools=list(available_functions) if available_functions else []
        )
        self.logic_app_tool = None
        
    async def initialize(self, project_client):
        """初始化 Logic Apps 工具"""
        await super().initialize(project_client)
        
        # Initialize Logic Apps configuration
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        logic_app_name = os.getenv("LOGIC_APP_NAME")
        trigger_name = os.getenv("TRIGGER_NAME")
        
        if all([subscription_id, resource_group, logic_app_name, trigger_name]):
            try:
                self.logic_app_tool = AzureLogicAppTool(subscription_id, resource_group)
                self.logic_app_tool.register_logic_app(logic_app_name, trigger_name)
                print(f"✅ Logic Apps initialized: {logic_app_name}")
            except Exception as e:
                print(f"⚠️ Logic Apps initialization failed: {str(e)}")
        else:
            print("⚠️ Logic Apps configuration not complete. Using mock functions.")
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要搜尋
        if any(word in task_lower for word in ["search", "find", "搜尋", "查找", "hotel", "酒店"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="AzureAISearchAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with search request: {task}",
                context=context or {},
                priority=6
            )
        
        # 檢查是否需要數據分析
        if any(word in task_lower for word in ["analyze", "analysis", "statistics", "分析", "統計", "taxi", "計程車"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="FabricAgent", 
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with data analysis request: {task}",
                context=context or {},
                priority=6
            )
        
        return None

class FabricAgent(BaseAgent):
    """Microsoft Fabric 數據分析代理程式"""
    
    def __init__(self):
        # Get available functions
        available_functions = set()
        if taxi_query_functions:
            available_functions.update(taxi_query_functions)
        
        super().__init__(
            name="FabricAgent",
            description="專門處理數據分析和統計查詢",
            instructions="""你是專業的計程車數據分析助手，專門分析 Microsoft Fabric lakehouse 中的計程車行程數據。

你的專業領域包括分析：
- 國定假日與平日的行程模式和費用比較
- 高費用行程分析（行程 > $70）及其百分比分佈  
- 日間（7:00-19:00）與夜間（19:00-7:00）行程和費用模式
- 地理分析，包括熱門上車地點和郵遞區號
- 乘客數量分佈和模態分析

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求搜尋酒店或其他信息 → AzureAISearchAgent
- 用戶要求發送郵件或自動化 → LogicAppsAgent
- 用戶要求進行複雜的資料庫查詢 → DatabricksAgent

你應該：
1. 提供清晰、結構化的回應，包含具體數字和統計資料
2. 使用適當的函數從 lakehouse 檢索真實數據
3. 基於數據分析提供洞察和趨勢
4. 以繁體中文呈現資訊，同時保留技術術語和欄位名稱的英文
5. 始終保持專業和樂於助人的語調""",
            tools=list(available_functions) if available_functions else []
        )
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要搜尋服務
        if any(word in task_lower for word in ["search", "find hotel", "搜尋", "酒店", "hotel"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="AzureAISearchAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with search request: {task}",
                context=context or {},
                priority=6
            )
        
        # 檢查是否需要郵件服務
        if any(word in task_lower for word in ["send email", "發送郵件", "email", "notify"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="LogicAppsAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with email/notification request: {task}",
                context=context or {},
                priority=7
            )
        
        # 檢查是否需要更複雜的資料庫查詢
        if any(word in task_lower for word in ["genie", "databricks", "complex query", "machine learning", "ML"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="DatabricksAgent",
                handoff_type=HandoffType.ESCALATE,
                task_description=f"Please help with complex data query: {task}",
                context=context or {},
                priority=8
            )
        
        return None

class DatabricksAgent(BaseAgent):
    """Azure Databricks Genie 代理程式"""
    
    def __init__(self):
        super().__init__(
            name="DatabricksAgent", 
            description="專門處理複雜的資料庫查詢和機器學習任務",
            instructions="""你是一個專業的數據科學助手，使用 Databricks Genie 來回答複雜的數據問題。

你的專業領域包括：
- 複雜的 SQL 查詢和資料庫操作
- 機器學習模型訓練和預測
- 大數據處理和分析
- 資料工程和 ETL 流程

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求簡單的搜尋 → AzureAISearchAgent  
- 用戶要求發送通知 → LogicAppsAgent
- 用戶要求基礎的統計分析 → FabricAgent

使用第一次呼叫函數回傳的 conversation_id 來在 Genie 中繼續對話，保持上下文連貫性。""",
            tools=[self.ask_genie] if DATABRICKS_AVAILABLE else []
        )
        self.databricks_client = None
        self.genie_api = None
        self.genie_space_id = None
        
    async def initialize(self, project_client):
        """初始化 Databricks 客戶端"""
        await super().initialize(project_client)
        
        # Initialize Databricks configuration
        project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT") 
        connection_name = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")
        
        if DATABRICKS_AVAILABLE and project_endpoint and connection_name:
            try:
                from azure.identity import DefaultAzureCredential
                
                # Get connection details
                connection = project_client.connections.get(connection_name)
                
                if connection.metadata.get('azure_databricks_connection_type') == 'genie':
                    self.genie_space_id = connection.metadata['genie_space_id']
                    
                    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
                    self.databricks_client = WorkspaceClient(
                        host=connection.target,
                        token=credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default").token,
                    )
                    
                    self.genie_api = GenieAPI(self.databricks_client.api_client)
                    print(f"✅ Databricks Genie initialized with space ID: {self.genie_space_id}")
                else:
                    print("⚠️ Connection is not of type 'genie'")
            except Exception as e:
                print(f"⚠️ Databricks initialization failed: {str(e)}")
        else:
            print("⚠️ Databricks configuration not complete or SDK not available. Using mock functions.")
    
    def ask_genie(self, question: str, conversation_id: str = None) -> str:
        """向 Genie 提問並回傳回應"""
        if self.genie_api and self.genie_space_id:
            try:
                if conversation_id is None:
                    message = self.genie_api.start_conversation_and_wait(self.genie_space_id, question)
                    conversation_id = message.conversation_id
                else:
                    message = self.genie_api.create_message_and_wait(self.genie_space_id, conversation_id, question)

                query_result = None
                if message.query_result:
                    query_result = self.genie_api.get_message_query_result(
                        self.genie_space_id, message.conversation_id, message.id
                    )

                message_content = self.genie_api.get_message(self.genie_space_id, message.conversation_id, message.id)

                # 處理結構化數據
                if query_result and query_result.statement_response:
                    statement_id = query_result.statement_response.statement_id
                    results = self.databricks_client.statement_execution.get_statement(statement_id)
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

                # 回退到文字訊息
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
        else:
            # Mock response
            return json.dumps({
                "conversation_id": f"mock_{random.randint(1000, 9999)}",
                "message": f"Mock Genie response for question: {question}. This would normally connect to your Databricks workspace."
            })
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要搜尋服務
        if any(word in task_lower for word in ["search hotel", "find hotel", "搜尋酒店", "hotel recommendation"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="AzureAISearchAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with hotel search request: {task}",
                context=context or {},
                priority=6
            )
        
        # 檢查是否需要發送通知
        if any(word in task_lower for word in ["send email", "notify", "發送郵件", "通知"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="LogicAppsAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with notification request: {task}",
                context=context or {},
                priority=7
            )
        
        # 檢查是否是簡單的統計查詢，可以降級給 Fabric
        if any(word in task_lower for word in ["simple stats", "basic analysis", "trip count", "簡單統計"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="FabricAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with basic statistical analysis: {task}",
                context=context or {},
                priority=5
            )
        
        return None

# Agent factory function
def create_agent(agent_type: str) -> BaseAgent:
    """Agent 工廠函數"""
    agent_map = {
        "search": AzureAISearchAgent,
        "logicapps": LogicAppsAgent,
        "fabric": FabricAgent,
        "databricks": DatabricksAgent
    }
    
    if agent_type.lower() not in agent_map:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(agent_map.keys())}")
    
    return agent_map[agent_type.lower()]()

# Available agent types
AVAILABLE_AGENTS = ["search", "logicapps", "fabric", "databricks"]