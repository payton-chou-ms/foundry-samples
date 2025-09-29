# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

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

"""
以下範例示範如何建立具有四個專業代理程式的 Magentic 編排：
- AI Search 搜尋代理程式 (從 step1_azure_ai_agent_retrieval_ai_search)
- Databricks 資料分析代理程式 (從 step1_azure_ai_agent_sk_databricks)  
- Microsoft Fabric 商業智慧代理程式 (從 step1_azure_ai_agent_sk_fabric)
- Logic App 工作流程自動化代理程式 (從 step1_azure_ai_agent_sk_logic_app)

這個整合範例展示了如何將多個單一代理程式的功能結合到一個協調的 Magentic 編排中，
提供全面的企業級 AI 解決方案。

在此處閱讀更多關於 Magentic 的資訊：
https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/

此範例示範建立和啟動運行時、建立具有四個 Azure AI 代理程式和 Magentic 管理員的編排、
呼叫編排，以及最後等待結果的完整企業級工作流程。
"""

# 載入環境變數
load_dotenv()
MY_AZURE_OPENAI_ENDPOINT = os.getenv("MY_AZURE_OPENAI_ENDPOINT")


# ==================== AI Search Plugin ====================
class AISearchPlugin:
    @kernel_function
    def search_documents(self, query: str) -> str:
        """搜尋和檢索相關文檔資訊"""
        search_results = {
            "產品資訊": "找到15筆相關產品文檔，包含技術規格、價格資訊和使用手冊",
            "政策文件": "檢索到8份相關政策文件，涵蓋合規要求和操作指南",
            "技術文檔": "搜尋結果包含12篇技術文件，提供實作細節和最佳實務",
            "客戶案例": "找到6個相關客戶案例研究，展示成功實施經驗"
        }
        
        for key in search_results:
            if any(keyword in query for keyword in ["產品", "商品", "物品"]):
                if key == "產品資訊":
                    return search_results[key]
            elif any(keyword in query for keyword in ["政策", "規定", "規範"]):
                if key == "政策文件":
                    return search_results[key]
            elif any(keyword in query for keyword in ["技術", "實作", "開發"]):
                if key == "技術文檔":
                    return search_results[key]
            elif any(keyword in query for keyword in ["案例", "客戶", "實例"]):
                if key == "客戶案例":
                    return search_results[key]
        
        return f"已搜尋查詢: {query}，找到多筆相關文檔和資料"

    @kernel_function
    def analyze_search_trends(self, topic: str) -> str:
        """分析搜尋趨勢和模式"""
        return f"分析 {topic} 的搜尋趨勢：搜尋量增長25%，相關查詢多集中在實務應用和故障排除"


# ==================== Databricks Plugin ====================
class DatabricksPlugin:
    @kernel_function
    def query_data_warehouse(self, query: str) -> str:
        """查詢資料倉庫中的資料"""
        simulated_results = {
            "使用者行為": "過去一周活躍使用者增長15%，平均會話時間增加23分鐘",
            "銷售績效": "電子產品類別領先，較上月成長18%；服裝類別穩定成長8%",
            "系統性能": "資料庫查詢平均響應時間：0.8秒，99%的查詢在2秒內完成",
            "預設": f"已執行資料倉庫查詢: {query}，返回詳細分析結果"
        }
        
        for key in simulated_results:
            if any(keyword in query for keyword in ["使用者", "用戶", "行為", "活動"]):
                if key == "使用者行為":
                    return simulated_results[key]
            elif any(keyword in query for keyword in ["銷售", "營收", "業績", "成長"]):
                if key == "銷售績效":
                    return simulated_results[key]
            elif any(keyword in query for keyword in ["性能", "效能", "系統", "回應"]):
                if key == "系統性能":
                    return simulated_results[key]
        
        return simulated_results["預設"]

    @kernel_function
    def run_analytics_job(self, job_type: str) -> str:
        """執行資料分析作業"""
        return f"已啟動 {job_type} 分析作業，預估執行時間15分鐘，將產生詳細報告和視覺化圖表"


# ==================== Microsoft Fabric Plugin ====================  
class FabricPlugin:
    @kernel_function
    def query_lakehouse_data(self, data_category: str) -> str:
        """查詢 Fabric lakehouse 中的資料"""
        lakehouse_data = {
            "交通資料": "計程車行程分析：平均距離5.2公里，尖峰時段集中在7-9AM和5-7PM",
            "商業資料": "零售銷售資料顯示：線上銷售佔比65%，行動裝置購買增長30%",
            "客戶資料": "客戶滿意度平均4.2/5，回購率提升12%，新客戶獲取成本下降8%",
            "財務資料": "季度營收成長15%，毛利率維持42%，營運效率指標持續改善"
        }
        
        for key in lakehouse_data:
            if any(keyword in data_category for keyword in ["交通", "運輸", "計程車", "行程"]):
                if key == "交通資料":
                    return lakehouse_data[key]
            elif any(keyword in data_category for keyword in ["商業", "零售", "銷售", "業務"]):
                if key == "商業資料":
                    return lakehouse_data[key]
            elif any(keyword in data_category for keyword in ["客戶", "顧客", "滿意度"]):
                if key == "客戶資料":
                    return lakehouse_data[key]
            elif any(keyword in data_category for keyword in ["財務", "營收", "獲利"]):
                if key == "財務資料":
                    return lakehouse_data[key]
        
        return f"已查詢 {data_category} 相關的 lakehouse 資料，提供綜合分析結果"

    @kernel_function
    def generate_business_report(self, report_type: str) -> str:
        """生成商業智慧報告"""
        return f"已生成 {report_type} 商業報告，包含KPI儀表板、趨勢分析和策略建議"


# ==================== Logic App Plugin ====================
class LogicAppPlugin:
    @kernel_function
    def send_notification(self, recipient: str, message_type: str, content: str) -> str:
        """透過 Logic App 發送通知"""
        return f"✅ 已透過 Logic App 發送 {message_type} 通知給 {recipient}：{content[:50]}..."

    @kernel_function
    def execute_workflow(self, workflow_name: str, parameters: str = "") -> str:
        """執行自動化工作流程"""
        workflow_details = {
            "資料處理": "資料處理工作流程已啟動，將自動清理、轉換並載入到目標系統",
            "報告生成": "報告生成工作流程執行中，將自動產生並分發給相關利害關係人",
            "客戶服務": "客戶服務工作流程已觸發，將自動分類並路由客戶查詢",
            "通知發送": "通知發送工作流程啟動，將向指定群組發送更新訊息"
        }
        
        for key in workflow_details:
            if key in workflow_name:
                return f"🚀 {workflow_details[key]} (參數: {parameters})"
        
        return f"🚀 工作流程 '{workflow_name}' 已成功執行，參數: {parameters or '無'}"

    @kernel_function
    def monitor_system_health(self, system_component: str) -> str:
        """監控系統健康狀態"""
        health_status = {
            "API服務": "✅ API服務正常，回應時間 < 100ms，可用性 99.9%",
            "資料庫": "✅ 資料庫連線穩定，查詢效能良好，儲存空間使用率 65%",
            "網路": "✅ 網路連線正常，延遲 < 50ms，頻寬使用率 45%",
            "儲存": "⚠️ 儲存空間使用率達85%，建議清理舊資料或擴充容量"
        }
        
        return health_status.get(system_component, f"監控 {system_component}：系統狀態良好，無異常警示")


async def get_integrated_agents(client) -> list[Agent]:
    """回傳將參與 Magentic 編排的整合代理程式清單"""
    agents = []
    
    # 1. AI Search 檢索代理程式
    search_agent_definition = await client.agents.create_agent(
        model=AzureAIAgentSettings().model_deployment_name,
        name="AISearchAgent", 
        description="專精於文檔搜尋和資訊檢索的助手，具備 Azure AI Search 整合功能",
        instructions="""
        您是資訊檢索專家。您專門:
        1. 搜尋和分析大量文檔資料
        2. 提供精確的資訊檢索結果
        3. 識別相關內容和趨勢模式
        4. 確保資訊的準確性和相關性
        
        請提供清晰、結構化的搜尋結果，並標明資料來源的可信度。
        """,
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
            {
                "type": "function", 
                "function": {
                    "name": "AISearchPlugin-analyze_search_trends",
                    "description": "分析搜尋趨勢和模式",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "要分析的主題"}
                        },
                        "required": ["topic"],
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
        model=AzureAIAgentSettings().model_deployment_name,
        name="DatabricksAnalyst",
        description="專精於大數據分析和機器學習的助手，具備 Databricks 平台整合功能",
        instructions="""
        您是資料科學專家。您專長:
        1. 大規模資料分析和處理
        2. 機器學習模型開發和部署
        3. 資料視覺化和洞察提取
        4. 效能優化和資料品質管理
        
        請提供基於資料的洞察和可執行的建議，並確保分析結果的統計顯著性。
        """,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "DatabricksPlugin-query_data_warehouse",
                    "description": "查詢資料倉庫中的資料",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "資料查詢內容"}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "DatabricksPlugin-run_analytics_job",
                    "description": "執行資料分析作業",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "job_type": {"type": "string", "description": "分析作業類型"}
                        },
                        "required": ["job_type"],
                    },
                },
            },
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
        model=AzureAIAgentSettings().model_deployment_name,
        name="FabricBusinessAnalyst",
        description="專精於商業智慧和資料視覺化的助手，具備 Microsoft Fabric 平台整合功能",
        instructions="""
        您是商業分析專家。您擅長:
        1. 商業資料分析和 KPI 追蹤
        2. 建立互動式儀表板和報告
        3. 識別商業機會和風險
        4. 提供策略性商業洞察
        
        請提供具有商業價值的分析結果，包含明確的行動建議和投資回報評估。
        """,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-query_lakehouse_data",
                    "description": "查詢 Fabric lakehouse 中的資料",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_category": {"type": "string", "description": "資料類別"}
                        },
                        "required": ["data_category"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-generate_business_report",
                    "description": "生成商業智慧報告",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "report_type": {"type": "string", "description": "報告類型"}
                        },
                        "required": ["report_type"],
                    },
                },
            },
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
        model=AzureAIAgentSettings().model_deployment_name,
        name="LogicAppOrchestrator",
        description="專精於業務流程自動化和系統整合的助手，具備 Azure Logic Apps 整合功能",
        instructions="""
        您是業務流程自動化專家。您能夠:
        1. 設計和執行自動化工作流程
        2. 整合多個系統和服務
        3. 監控和管理業務流程
        4. 優化營運效率和降低成本
        
        請提供實務可行的自動化解決方案，並確保流程的可靠性和可擴展性。
        """,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-send_notification",
                    "description": "透過 Logic App 發送通知",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient": {"type": "string", "description": "收件人"},
                            "message_type": {"type": "string", "description": "訊息類型"},
                            "content": {"type": "string", "description": "訊息內容"}
                        },
                        "required": ["recipient", "message_type", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-execute_workflow",
                    "description": "執行自動化工作流程",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workflow_name": {"type": "string", "description": "工作流程名稱"},
                            "parameters": {"type": "string", "description": "執行參數"}
                        },
                        "required": ["workflow_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "LogicAppPlugin-monitor_system_health",
                    "description": "監控系統健康狀態",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "system_component": {"type": "string", "description": "系統組件名稱"}
                        },
                        "required": ["system_component"],
                    },
                },
            },
        ],
    )
    logic_app_agent = AzureAIAgent(
        client=client,
        definition=logic_app_agent_definition,
        plugins=[LogicAppPlugin()],
    )
    agents.append(logic_app_agent)
    
    return agents


def agent_response_callback(message: ChatMessageContent) -> None:
    """觀察函數，用於列印來自代理程式的訊息"""
    print(f"\n**{message.name}**")
    print(f"{message.content}")
    print("-" * 60)


async def main():
    """執行整合多代理程式編排的主要函數"""
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        print("🚀 正在初始化企業級多代理程式系統...")
        print("=" * 60)
        
        # 1. 建立整合的 Magentic 編排
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
        print("=" * 60)

        try:
            # 3. 執行複合型企業任務
            complex_task = """
            我們公司正在進行數位轉型，需要一個全面的分析和行動計劃。請協助我們：

            1. **資訊收集**: 搜尋我們現有的技術文檔和最佳實務案例
            2. **資料分析**: 分析當前的使用者行為和系統性能資料
            3. **商業洞察**: 評估我們的財務和客戶資料，識別改善機會
            4. **流程自動化**: 建議並實施自動化工作流程來提升營運效率

            請各個代理程式根據專長貢獻分析和建議，最終提供一個整合的數位轉型策略。
            """
            
            print("📋 **執行任務**: 企業數位轉型全面分析")
            print("🎯 **目標**: 整合四個專業領域的洞察，制定轉型策略")
            print("=" * 60)
            
            # 呼叫編排
            orchestration_result = await magentic_orchestration.invoke(
                task=complex_task,
                runtime=runtime,
            )

            # 4. 等待並展示結果
            final_result = await orchestration_result.get()

            print("\n" + "=" * 60)
            print("🎯 **最終整合策略**")
            print("=" * 60)
            print(f"{final_result}")
            print("=" * 60)

        finally:
            # 5. 清理資源
            print("\n🧹 正在清理系統資源...")
            await runtime.stop_when_idle()
            
            # 刪除所有代理程式
            for agent in agents_list:
                await client.agents.delete_agent(agent.id)
                print(f"   ✅ 已刪除 {agent.name}")
            
            print("✅ 系統清理完成")

    """
    範例輸出結構：
    
    🚀 正在初始化企業級多代理程式系統...
    ============================================================
    ✅ 已建立 4 個專業代理程式:
       1. AISearchAgent - 專精於文檔搜尋和資訊檢索的助手
       2. DatabricksAnalyst - 專精於大數據分析和機器學習的助手
       3. FabricBusinessAnalyst - 專精於商業智慧和資料視覺化的助手
       4. LogicAppOrchestrator - 專精於業務流程自動化和系統整合的助手
    ✅ 多代理程式運行時已啟動
    ============================================================
    
    **AISearchAgent**
    找到15筆相關產品文檔，包含技術規格、價格資訊和使用手冊
    ------------------------------------------------------------
    
    **DatabricksAnalyst** 
    過去一周活躍使用者增長15%，平均會話時間增加23分鐘
    ------------------------------------------------------------
    
    **FabricBusinessAnalyst**
    季度營收成長15%，毛利率維持42%，營運效率指標持續改善
    ------------------------------------------------------------
    
    **LogicAppOrchestrator**
    🚀 資料處理工作流程已啟動，將自動清理、轉換並載入到目標系統
    ------------------------------------------------------------
    
    ============================================================
    🎯 **最終整合策略**
    ============================================================
    基於四個專業代理程式的分析，我們的數位轉型策略建議如下：
    
    1. **技術基礎設施升級**: 根據搜尋到的最佳實務，優先投資雲端原生架構
    2. **資料驅動決策**: 利用使用者行為成長趨勢，擴大資料分析能力
    3. **商業價值最大化**: 營收成長趨勢良好，建議投資客戶體驗提升
    4. **流程自動化加速**: 透過工作流程自動化，預估可節省30%營運成本
    
    建議實施時程：6個月，預估投資回報率：250%
    ============================================================
    """


if __name__ == "__main__":
    asyncio.run(main())