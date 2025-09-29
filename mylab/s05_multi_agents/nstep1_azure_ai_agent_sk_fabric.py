# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
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
以下範例示範如何在 Semantic Kernel 中使用 Azure AI Agent 結合 Microsoft Fabric。
本範例整合了 Fabric lakehouse 功能，提供計程車行程資料分析和商業智慧洞察。
"""

# 載入環境變數
load_dotenv()

# 從環境變數取得設定
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")

# 模擬與 agent 的對話
USER_INPUTS = [
    "分析計程車行程的平均距離和車資趨勢",
    "比較國定假日與平日的計程車使用模式",
    "找出最繁忙的計程車路線和時間段",
]


class FabricPlugin:
    def __init__(self):
        self.lakehouse_connected = False
        
    async def initialize_fabric_connection(self):
        """初始化 Microsoft Fabric 連接"""
        try:
            print("正在初始化 Microsoft Fabric lakehouse 連接...")
            # 模擬 Fabric 連接初始化
            self.lakehouse_connected = True
            print("Microsoft Fabric lakehouse 連接已初始化")
        except Exception as e:
            print(f"Fabric 初始化失敗: {e}")

    @kernel_function
    def query_taxi_trips(self, query_type: str) -> str:
        """查詢計程車行程資料"""
        if not self.lakehouse_connected:
            return "錯誤: Fabric lakehouse 未連接"
            
        # 模擬計程車資料查詢結果
        trip_data = {
            "平均距離": "平均行程距離: 5.2公里，平均車資: NT$180，過去一個月車資平均上漲3%",
            "假日模式": "國定假日行程數比平日少35%，但平均距離長40%，車資高出25%，顯示假日多為長程旅行",
            "繁忙路線": "最繁忙路線: 台北車站-松山機場 (日均326趟)，尖峰時段: 7-9AM (43%), 5-7PM (38%)",
            "一般查詢": f"已查詢計程車行程資料: {query_type}。返回相關統計分析結果。"
        }
        
        for key in trip_data:
            if any(keyword in query_type for keyword in ["距離", "車資", "趨勢", "平均"]):
                if key == "平均距離":
                    return trip_data[key]
            elif any(keyword in query_type for keyword in ["假日", "平日", "國定", "模式"]):
                if key == "假日模式":
                    return trip_data[key]
            elif any(keyword in query_type for keyword in ["繁忙", "路線", "時間"]):
                if key == "繁忙路線":
                    return trip_data[key]
        
        return trip_data["一般查詢"]

    @kernel_function
    def analyze_trip_patterns(self, pattern_type: str) -> str:
        """分析行程模式和異常"""
        pattern_analysis = {
            "時間模式": "週間通勤高峰明顯，週末分布較平均；雨天行程數增加60%",
            "地理模式": "市中心出發行程占65%，機場路線在週五、週日流量最高",
            "價格模式": "動態定價在尖峰時段啟動，平均增幅15-25%",
            "異常檢測": "檢測到3起異常長程行程 (>50公里)，2起異常高額車資 (>NT$1500)"
        }
        
        return pattern_analysis.get(pattern_type, f"已分析 {pattern_type} 模式，發現多項有趣趨勢")

    @kernel_function
    def generate_business_insights(self, focus_area: str) -> str:
        """生成商業洞察和建議"""
        business_insights = {
            "營收優化": "建議在尖峰時段增派車輛，預估可提升營收12%；考慮推出會員制度",
            "客戶體驗": "等待時間過長地區需要優化，建議在熱點區域增加車輛密度",
            "運營效率": "空車率在某些時段高達30%，建議優化調度算法和司機激勵政策",
            "市場趨勢": "電動車接受度提高，綠色出行需求成長25%，建議投資環保車隊"
        }
        
        return business_insights.get(focus_area, f"針對 {focus_area} 提供策略建議和市場洞察")

    @kernel_function
    def create_fabric_dashboard(self, dashboard_type: str) -> str:
        """在 Fabric 中建立分析儀表板"""
        return f"已在 Microsoft Fabric 中建立 {dashboard_type} 儀表板，包含即時資料視覺化和互動式篩選功能"


async def handle_streaming_intermediate_steps(message: ChatMessageContent) -> None:
    for item in message.items or []:
        if isinstance(item, FunctionResultContent):
            print(f"Function Result:> {item.result} for function: {item.name}")
        elif isinstance(item, FunctionCallContent):
            print(f"Function Call:> {item.name} with arguments: {item.arguments}")
        else:
            print(f"{item}")


async def create_fabric_agent(client) -> AzureAIAgent:
    """建立具有 Microsoft Fabric 功能的 Azure AI Agent"""
    
    # 建立 Fabric 插件
    fabric_plugin = FabricPlugin()
    await fabric_plugin.initialize_fabric_connection()
    
    # 建立 agent 定義
    agent_definition = await client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME or "gpt-4o",
        name="FabricAnalyst",
        description="專精於使用 Microsoft Fabric 進行資料分析和商業智慧的助手",
        instructions="""
        您是一位商業資料分析專家，專門使用 Microsoft Fabric lakehouse。
        您擅長:
        1. 分析計程車行程和交通資料
        2. 識別商業模式和市場趨勢
        3. 提供資料驅動的商業洞察
        4. 建立互動式分析儀表板
        
        請提供深入的分析，包含統計數據和可行的建議。
        使用專業的商業分析語言，並確保洞察具有實際應用價值。
        """,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-query_taxi_trips",
                    "description": "查詢計程車行程資料",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query_type": {"type": "string", "description": "查詢的資料類型或焦點"}
                        },
                        "required": ["query_type"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-analyze_trip_patterns",
                    "description": "分析行程模式和異常",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern_type": {"type": "string", "description": "要分析的模式類型"}
                        },
                        "required": ["pattern_type"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-generate_business_insights",
                    "description": "生成商業洞察和建議",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "focus_area": {"type": "string", "description": "商業分析的焦點領域"}
                        },
                        "required": ["focus_area"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "FabricPlugin-create_fabric_dashboard",
                    "description": "在 Fabric 中建立分析儀表板",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dashboard_type": {"type": "string", "description": "儀表板類型或焦點"}
                        },
                        "required": ["dashboard_type"],
                    },
                },
            },
        ],
    )
    
    # 建立 Semantic Kernel 對應的 Azure AI Agent
    agent = AzureAIAgent(
        client=client,
        definition=agent_definition,
        plugins=[fabric_plugin],
    )
    
    return agent


async def main() -> None:
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 建立 Fabric agent
        agent = await create_fabric_agent(client)
        
        print(f"已建立 Microsoft Fabric Agent，ID: {agent.id}")
        
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
            print(f"\n已清理 Microsoft Fabric Agent 資源")

        """
        範例輸出：
        # User: '分析計程車行程的平均距離和車資趨勢'
        Function Call:> FabricPlugin-query_taxi_trips with arguments: {"query_type": "平均距離和車資趨勢"}
        Function Result:> 平均行程距離: 5.2公里，平均車資: NT$180，過去一個月車資平均上漲3% for function: FabricPlugin-query_taxi_trips
        
        🚖 **計程車行程分析報告**
        
        根據 Microsoft Fabric lakehouse 的資料分析：
        
        📊 **基本統計**
        - 平均行程距離：5.2 公里
        - 平均車資：NT$180
        - 月成長趨勢：車資上漲 3%
        
        💡 **趨勢洞察**
        車資的溫和上漲反映了燃油成本和通膨壓力，建議監控客戶滿意度以確保價格競爭力。
        """


if __name__ == "__main__":
    asyncio.run(main())