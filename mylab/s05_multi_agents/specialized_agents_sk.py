# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    基於 Semantic Kernel 的專門代理程式實現，將單一功能的腳本轉換為可協作的代理程式類別。
    
包含以下代理程式：
- SemanticKernelSearchAgent: Azure AI Search 搜尋代理
- SemanticKernelLogicAgent: Logic Apps 自動化代理  
- SemanticKernelFabricAgent: Microsoft Fabric 數據分析代理
- SemanticKernelDatabricksAgent: Azure Databricks Genie 代理
"""

import os
import json
import random
from typing import Dict, Any, Optional, List, Set, Callable
from datetime import datetime
from dotenv import load_dotenv

# Import from our semantic kernel handoff system
from step4_handoff_semantic_kernel import SemanticKernelBaseAgent, HandoffRequest, HandoffType, create_handoff_request

# Semantic Kernel imports
try:
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.functions.kernel_arguments import KernelArguments
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    print("Warning: Semantic Kernel packages not available")
    SEMANTIC_KERNEL_AVAILABLE = False
    def kernel_function(name=None, description=None):
        """Mock kernel_function decorator"""
        def decorator(func):
            func._sk_function_name = name
            func._sk_function_description = description
            return func
        return decorator

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

# Semantic Kernel Plugin Classes
class AzureSearchPlugin:
    """Azure AI Search plugin for Semantic Kernel"""
    
    def __init__(self):
        self.search_client = None
        self.search_config = None
        self._initialize_search()
    
    def _initialize_search(self):
        """Initialize search configuration"""
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
        else:
            print("⚠️ Azure AI Search configuration not complete. Using mock search.")
    
    @kernel_function(name="search_hotels", description="搜尋酒店資訊並回傳結果")
    def search_hotels(self, query: str, filters: str = None) -> str:
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
                
                return json.dumps({
                    "success": True,
                    "query": query,
                    "results": hotel_results,
                    "total_found": len(hotel_results)
                }, ensure_ascii=False)
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
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
            return json.dumps({
                "success": True,
                "query": query,
                "results": mock_hotels,
                "total_found": len(mock_hotels)
            }, ensure_ascii=False)

class LogicAppsPlugin:
    """Logic Apps plugin for Semantic Kernel"""
    
    def __init__(self):
        self.logic_app_tool = None
        self._initialize_logic_apps()
    
    def _initialize_logic_apps(self):
        """Initialize Logic Apps configuration"""
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        logic_app_name = os.getenv("LOGIC_APP_NAME")
        trigger_name = os.getenv("TRIGGER_NAME")
        
        if all([subscription_id, resource_group, logic_app_name, trigger_name]):
            try:
                # Mock initialization since we don't have the actual AzureLogicAppTool
                print(f"✅ Logic Apps initialized: {logic_app_name}")
            except Exception as e:
                print(f"⚠️ Logic Apps initialization failed: {str(e)}")
        else:
            print("⚠️ Logic Apps configuration not complete. Using mock functions.")
    
    @kernel_function(name="send_email", description="發送電子郵件到指定收件人")
    def send_email(self, recipient: str, subject: str, body: str) -> str:
        """發送電子郵件"""
        try:
            # Mock email sending
            result = {
                "success": True,
                "message": f"Email sent successfully to {recipient}",
                "subject": subject,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @kernel_function(name="trigger_workflow", description="觸發邏輯應用程式工作流程")
    def trigger_workflow(self, workflow_name: str, parameters: str = "{}") -> str:
        """觸發 Logic App 工作流程"""
        try:
            params = json.loads(parameters) if parameters else {}
            result = {
                "success": True,
                "workflow": workflow_name,
                "parameters": params,
                "message": f"Workflow {workflow_name} triggered successfully",
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

class FabricPlugin:
    """Microsoft Fabric plugin for Semantic Kernel"""
    
    @kernel_function(name="query_holiday_comparison", description="查詢計程車行程的假日與平日比較數據")
    def query_holiday_comparison(self) -> str:
        """查詢假日與平日的計程車行程比較"""
        # Mock data analysis
        result = {
            "success": True,
            "analysis": "假日與平日計程車行程比較",
            "holiday_trips": 125000,
            "weekday_trips": 180000,
            "difference_percentage": -30.6,
            "average_fare_holiday": 25.80,
            "average_fare_weekday": 18.90,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result, ensure_ascii=False)
    
    @kernel_function(name="query_day_night_comparison", description="分析日間與夜間的計程車行程數據")
    def query_day_night_comparison(self) -> str:
        """分析日間（7:00-19:00）與夜間（19:00-7:00）的行程差異"""
        result = {
            "success": True,
            "analysis": "日間與夜間計程車行程比較",
            "day_trips": 220000,
            "night_trips": 85000,
            "day_average_fare": 19.50,
            "night_average_fare": 28.30,
            "peak_hours": "17:00-19:00",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result, ensure_ascii=False)
    
    @kernel_function(name="query_high_fare_trips", description="查詢高費用行程（>$70）的統計數據")
    def query_high_fare_trips(self) -> str:
        """查詢車資金額大於 70 的行程統計"""
        result = {
            "success": True,
            "analysis": "高費用行程統計分析",
            "high_fare_count": 2450,
            "total_trips": 305000,
            "percentage": 0.80,
            "average_high_fare": 87.50,
            "max_fare": 245.80,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(result, ensure_ascii=False)

class DatabricksPlugin:
    """Databricks plugin for Semantic Kernel"""
    
    def __init__(self):
        self.databricks_client = None
        self.genie_api = None
        self.genie_space_id = None
        self._initialize_databricks()
        
    def _initialize_databricks(self):
        """Initialize Databricks configuration"""
        # Mock initialization for now
        print("⚠️ Databricks configuration using mock functions.")
    
    @kernel_function(name="ask_genie", description="使用 Databricks Genie 查詢數據")
    def ask_genie(self, question: str, conversation_id: str = None) -> str:
        """向 Genie 提問並回傳回應"""
        try:
            # Mock Genie response
            if not conversation_id:
                conversation_id = f"mock_{random.randint(1000, 9999)}"
            
            mock_responses = {
                "乘客數量": {
                    "conversation_id": conversation_id,
                    "table": {
                        "columns": ["passenger_count", "trip_count", "percentage"],
                        "rows": [
                            ["1", "185,420", "60.8%"],
                            ["2", "67,890", "22.3%"],
                            ["3", "28,540", "9.4%"],
                            ["4", "15,230", "5.0%"],
                            ["5", "4,680", "1.5%"],
                            ["6", "3,240", "1.0%"]
                        ]
                    }
                },
                "default": {
                    "conversation_id": conversation_id,
                    "message": f"Mock Genie response for question: {question}. This would normally connect to your Databricks workspace and provide detailed data analysis results."
                }
            }
            
            # Return appropriate mock response based on question content
            if "乘客" in question or "passenger" in question.lower():
                return json.dumps(mock_responses["乘客數量"], ensure_ascii=False)
            else:
                return json.dumps(mock_responses["default"], ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "error": "An error occurred while talking to Genie.",
                "details": str(e)
            })

# Specialized Agent Classes using Semantic Kernel
class SemanticKernelSearchAgent(SemanticKernelBaseAgent):
    """基於 Semantic Kernel 的 Azure AI Search 搜尋代理程式"""
    
    def __init__(self):
        search_plugin = AzureSearchPlugin()
        super().__init__(
            name="SemanticKernelSearchAgent",
            description="專門處理搜尋相關的查詢和資訊檢索",
            instructions="""你是一個專業的搜尋助手，專門使用 Azure AI Search 來幫助用戶找到相關資訊。

你的專業領域包括：
- 酒店資訊搜尋和推薦
- 向量搜尋和語意搜尋
- 文檔檢索和內容分析
- 搜尋結果排名和過濾

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求發送電子郵件 → SemanticKernelLogicAgent
- 用戶要求進行數據分析或統計 → SemanticKernelFabricAgent  
- 用戶要求查詢資料庫或進行複雜的資料處理 → SemanticKernelDatabricksAgent

請始終提供準確、相關且有用的搜尋結果。""",
            plugins=[search_plugin]
        )
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要發送郵件
        if any(word in task_lower for word in ["send email", "發送郵件", "寄信", "email", "郵件", "通知客戶", "notify", "發郵件", "郵件通知", "然後發郵件", "然後發送郵件"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelLogicAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with email sending request: {task}",
                context=context or {},
                priority=7
            )
        
        # 檢查是否需要數據分析
        if any(word in task_lower for word in ["analyze", "analysis", "statistics", "data", "分析", "統計", "數據"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelFabricAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with data analysis request: {task}",
                context=context or {},
                priority=6
            )
        
        return None

class SemanticKernelLogicAgent(SemanticKernelBaseAgent):
    """基於 Semantic Kernel 的 Logic Apps 自動化代理程式"""
    
    def __init__(self):
        logic_plugin = LogicAppsPlugin()
        super().__init__(
            name="SemanticKernelLogicAgent",
            description="專門處理自動化工作流程和郵件發送",
            instructions="""你是一個專業的自動化助手，專門使用 Azure Logic Apps 來執行自動化任務。

你的專業領域包括：
- 電子郵件發送和通知
- 工作流程自動化
- API 整合和調用
- 定時任務和觸發器管理

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求搜尋資訊 → SemanticKernelSearchAgent
- 用戶要求進行數據分析 → SemanticKernelFabricAgent
- 用戶要求查詢資料庫 → SemanticKernelDatabricksAgent

你可以協助用戶發送郵件、設定自動化工作流程等任務。""",
            plugins=[logic_plugin]
        )
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要搜尋 - 只有在明確的搜尋請求時才移交
        if any(word in task_lower for word in ["search hotel", "find hotel", "搜尋酒店", "查找酒店", "hotel search"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelSearchAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with search request: {task}",
                context=context or {},
                priority=6
            )
        
        # 檢查是否需要數據分析 - 只有在明確的分析請求時才移交
        if any(word in task_lower for word in ["analyze data", "analysis", "statistics", "分析數據", "統計分析", "taxi data", "計程車數據"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelFabricAgent", 
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with data analysis request: {task}",
                context=context or {},
                priority=6
            )
        
        return None

class SemanticKernelFabricAgent(SemanticKernelBaseAgent):
    """基於 Semantic Kernel 的 Microsoft Fabric 數據分析代理程式"""
    
    def __init__(self):
        fabric_plugin = FabricPlugin()
        super().__init__(
            name="SemanticKernelFabricAgent",
            description="專門處理數據分析和統計查詢",
            instructions="""你是專業的計程車數據分析助手，專門分析 Microsoft Fabric lakehouse 中的計程車行程數據。

你的專業領域包括分析：
- 國定假日與平日的行程模式和費用比較
- 高費用行程分析（行程 > $70）及其百分比分佈  
- 日間（7:00-19:00）與夜間（19:00-7:00）行程和費用模式
- 地理分析，包括熱門上車地點和郵遞區號
- 乘客數量分佈和模態分析

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求搜尋酒店或其他信息 → SemanticKernelSearchAgent
- 用戶要求發送郵件或自動化 → SemanticKernelLogicAgent
- 用戶要求進行複雜的資料庫查詢 → SemanticKernelDatabricksAgent

你應該：
1. 提供清晰、結構化的回應，包含具體數字和統計資料
2. 使用適當的函數從 lakehouse 檢索真實數據
3. 基於數據分析提供洞察和趨勢
4. 以繁體中文呈現資訊，同時保留技術術語和欄位名稱的英文
5. 始終保持專業和樂於助人的語調""",
            plugins=[fabric_plugin]
        )
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要搜尋服務
        if any(word in task_lower for word in ["search", "find hotel", "搜尋", "酒店", "hotel"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelSearchAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with search request: {task}",
                context=context or {},
                priority=6
            )
        
        # 檢查是否需要郵件服務
        if any(word in task_lower for word in ["send email", "發送郵件", "email", "notify"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelLogicAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with email/notification request: {task}",
                context=context or {},
                priority=7
            )
        
        # 檢查是否需要更複雜的資料庫查詢  
        if any(word in task_lower for word in ["genie", "databricks", "complex query", "machine learning", "ML", "機器學習", "複雜", "預測"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelDatabricksAgent",
                handoff_type=HandoffType.ESCALATE,
                task_description=f"Please help with complex data query: {task}",
                context=context or {},
                priority=8
            )
        
        return None

class SemanticKernelDatabricksAgent(SemanticKernelBaseAgent):
    """基於 Semantic Kernel 的 Azure Databricks Genie 代理程式"""
    
    def __init__(self):
        databricks_plugin = DatabricksPlugin()
        super().__init__(
            name="SemanticKernelDatabricksAgent", 
            description="專門處理複雜的資料庫查詢和機器學習任務",
            instructions="""你是一個專業的數據科學助手，使用 Databricks Genie 來回答複雜的數據問題。

你的專業領域包括：
- 複雜的 SQL 查詢和資料庫操作
- 機器學習模型訓練和預測
- 大數據處理和分析
- 資料工程和 ETL 流程

當遇到以下情況時，你應該考慮移交給其他代理程式：
- 用戶要求簡單的搜尋 → SemanticKernelSearchAgent  
- 用戶要求發送通知 → SemanticKernelLogicAgent
- 用戶要求基礎的統計分析 → SemanticKernelFabricAgent

使用第一次呼叫函數回傳的 conversation_id 來在 Genie 中繼續對話，保持上下文連貫性。""",
            plugins=[databricks_plugin]
        )
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交"""
        task_lower = task.lower()
        
        # 檢查是否需要搜尋服務
        if any(word in task_lower for word in ["search hotel", "find hotel", "搜尋酒店", "hotel recommendation"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelSearchAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with hotel search request: {task}",
                context=context or {},
                priority=6
            )
        
        # 檢查是否需要發送通知
        if any(word in task_lower for word in ["send email", "notify", "發送郵件", "通知"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelLogicAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with notification request: {task}",
                context=context or {},
                priority=7
            )
        
        # 檢查是否是簡單的統計查詢，可以降級給 Fabric
        if any(word in task_lower for word in ["simple stats", "basic analysis", "trip count", "簡單統計"]):
            return create_handoff_request(
                from_agent=self.name,
                to_agent="SemanticKernelFabricAgent",
                handoff_type=HandoffType.FORWARD,
                task_description=f"Please help with basic statistical analysis: {task}",
                context=context or {},
                priority=5
            )
        
        return None

# Agent factory function
def create_semantic_kernel_agent(agent_type: str) -> SemanticKernelBaseAgent:
    """Semantic Kernel Agent 工廠函數"""
    agent_map = {
        "search": SemanticKernelSearchAgent,
        "logicapps": SemanticKernelLogicAgent,
        "fabric": SemanticKernelFabricAgent,
        "databricks": SemanticKernelDatabricksAgent
    }
    
    if agent_type.lower() not in agent_map:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(agent_map.keys())}")
    
    return agent_map[agent_type.lower()]()

# Available agent types for Semantic Kernel
AVAILABLE_SK_AGENTS = ["search", "logicapps", "fabric", "databricks"]