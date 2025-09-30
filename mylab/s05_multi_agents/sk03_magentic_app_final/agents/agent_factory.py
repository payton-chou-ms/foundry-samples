# Copyright (c) Microsoft. All rights reserved.

from semantic_kernel.agents import Agent, AzureAIAgent
from config.settings import settings
from plugins import AISearchPlugin, DatabricksPlugin, FabricPlugin, LogicAppPlugin


class AgentFactory:
    """代理程式工廠 - 負責創建和配置各種專業代理程式"""
    
    def __init__(self, connection_manager, logic_app_manager):
        self.connection_manager = connection_manager
        self.logic_app_manager = logic_app_manager
    
    async def create_ai_search_agent(self, client) -> Agent:
        """創建 AI Search 代理程式"""
        # 嘗試使用已存在的 agent ID
        search_agent_id = "asst_vnVvS09TGw3zOC6Z0vxiviN0"
        
        try:
            search_agent_definition = await client.agents.get_agent(agent_id=search_agent_id)
            
            # 檢查並修復 description 如果為空
            if not search_agent_definition.description:
                print(f"⚠️ AI Search Agent 缺少 description，正在更新...")
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
            print(f"✅ 已載入 AI Search Agent (ID: {search_agent_id})")
            return search_agent
            
        except Exception as e:
            print(f"⚠️ 無法載入 AI Search Agent: {e}")
            # 如果無法載入，建立新的 agent
            return await self._create_new_ai_search_agent(client)
    
    async def _create_new_ai_search_agent(self, client) -> Agent:
        """創建新的 AI Search 代理程式"""
        search_agent_definition = await client.agents.create_agent(
            model=settings.MODEL_DEPLOYMENT_NAME,
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
        return search_agent
    
    async def create_databricks_agent(self, client) -> Agent:
        """創建 Databricks 代理程式"""
        databricks_agent_definition = await client.agents.create_agent(
            model=settings.MODEL_DEPLOYMENT_NAME,
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
        
        # 配置插件連接
        databricks_plugin = DatabricksPlugin()
        databricks_connections = self.connection_manager.get_databricks_connections()
        databricks_plugin.set_connections(*databricks_connections)
        
        databricks_agent = AzureAIAgent(
            client=client,
            definition=databricks_agent_definition,
            plugins=[databricks_plugin],
        )
        return databricks_agent
    
    async def create_fabric_agent(self, client) -> Agent:
        """創建 Microsoft Fabric 代理程式"""
        fabric_agent_definition = await client.agents.create_agent(
            model=settings.MODEL_DEPLOYMENT_NAME,
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
        
        # 配置插件連接
        fabric_plugin = FabricPlugin()
        fabric_connection = self.connection_manager.get_fabric_connection()
        fabric_plugin.set_connection(fabric_connection)
        
        fabric_agent = AzureAIAgent(
            client=client,
            definition=fabric_agent_definition,
            plugins=[fabric_plugin],
        )
        return fabric_agent
    
    async def create_logic_app_agent(self, client) -> Agent:
        """創建 Logic App 代理程式"""
        logic_app_agent_definition = await client.agents.create_agent(
            model=settings.MODEL_DEPLOYMENT_NAME,
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
        
        # 配置插件管理器
        logic_app_plugin = LogicAppPlugin()
        logic_app_plugin.set_manager(self.logic_app_manager)
        
        logic_app_agent = AzureAIAgent(
            client=client,
            definition=logic_app_agent_definition,
            plugins=[logic_app_plugin],
        )
        return logic_app_agent
    
    async def create_all_agents(self, client) -> list[Agent]:
        """創建所有代理程式"""
        agents = []
        
        # 創建各個代理程式
        search_agent = await self.create_ai_search_agent(client)
        agents.append(search_agent)
        
        databricks_agent = await self.create_databricks_agent(client)
        agents.append(databricks_agent)
        
        fabric_agent = await self.create_fabric_agent(client)
        agents.append(fabric_agent)
        
        logic_app_agent = await self.create_logic_app_agent(client)
        agents.append(logic_app_agent)
        
        return agents