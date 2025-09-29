# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from typing import Any, Callable, Set
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import GenieAPI

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)
from semantic_kernel.functions import kernel_function

"""
以下範例示範如何在 Semantic Kernel 中使用 Azure AI Agent 結合 Databricks Genie。
本範例整合了 Databricks 工作區存取功能，提供資料分析和查詢能力。
"""

# 載入環境變數
load_dotenv()

# Databricks 設定
os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"
DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_DATABRICKS_CONNECTION_NAME = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")

# 模擬與 agent 的對話
USER_INPUTS = [
    "分析我們資料倉庫中最近一周的使用者行為趨勢",
    "比較不同產品類別的銷售績效",
]


class DatabricksPlugin:
    def __init__(self):
        self.workspace_client = None
        self.genie_api = None
        
    async def initialize_databricks(self):
        """初始化 Databricks 連接"""
        try:
            # 模擬 Databricks 連接初始化
            print("正在初始化 Databricks 連接...")
            # 實際實作時需要設定真實的 Databricks 工作區客戶端
            # self.workspace_client = WorkspaceClient()
            # self.genie_api = GenieAPI(self.workspace_client.api_client)
            print("Databricks 連接已初始化")
        except Exception as e:
            print(f"Databricks 初始化失敗: {e}")

    @kernel_function
    def query_data_warehouse(self, query: str) -> str:
        """查詢資料倉庫中的資料"""
        # 模擬資料查詢功能
        simulated_results = {
            "使用者行為": "過去一周活躍使用者增長15%，平均會話時間增加23分鐘",
            "銷售績效": "電子產品類別領先，較上月成長18%；服裝類別穩定成長8%",
            "預設": f"已執行查詢: {query}。返回模擬資料分析結果。"
        }
        
        for key in simulated_results:
            if key in query or any(keyword in query for keyword in ["行為", "趨勢", "使用者"]):
                if key == "使用者行為":
                    return simulated_results[key]
            elif "銷售" in query or "產品" in query or "績效" in query:
                if key == "銷售績效":
                    return simulated_results[key]
        
        return simulated_results["預設"]

    @kernel_function
    def analyze_data_patterns(self, data_type: str) -> str:
        """分析資料模式和趨勢"""
        analysis_results = {
            "使用者行為": "檢測到週末使用率提高40%，移動端存取比例達65%",
            "銷售數據": "發現季節性購買模式，Q4季度銷售額通常比Q1高出30%",
            "系統性能": "資料庫查詢效能穩定，平均響應時間小於2秒"
        }
        
        return analysis_results.get(data_type, f"已分析 {data_type} 資料模式，生成詳細報告")

    @kernel_function
    def create_data_visualization(self, chart_type: str, data_source: str) -> str:
        """建立資料視覺化圖表"""
        return f"已建立 {chart_type} 圖表，資料來源: {data_source}。圖表包含互動式功能和即時更新。"


async def handle_streaming_intermediate_steps(message: ChatMessageContent) -> None:
    for item in message.items or []:
        if isinstance(item, FunctionResultContent):
            print(f"Function Result:> {item.result} for function: {item.name}")
        elif isinstance(item, FunctionCallContent):
            print(f"Function Call:> {item.name} with arguments: {item.arguments}")
        else:
            print(f"{item}")


async def create_databricks_agent(client) -> AzureAIAgent:
    """建立具有 Databricks 功能的 Azure AI Agent"""
    
    # 建立 Databricks 插件
    databricks_plugin = DatabricksPlugin()
    await databricks_plugin.initialize_databricks()
    
    # 建立 agent 定義
    agent_definition = await client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME or "gpt-4o",
        name="DatabricksDataAnalyst",
        description="專精於使用 Databricks 進行資料分析和查詢的助手",
        instructions="""
        您是一位資料分析專家，專門使用 Databricks 平台。
        您能夠:
        1. 查詢和分析大型資料集
        2. 識別資料中的模式和趨勢
        3. 建立資料視覺化圖表
        4. 提供資料驅動的洞察和建議
        
        請用專業但易懂的方式回答問題，並提供具體的數據支持。
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
                            "query": {"type": "string", "description": "要執行的查詢描述"}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "DatabricksPlugin-analyze_data_patterns",
                    "description": "分析資料模式和趨勢",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_type": {"type": "string", "description": "要分析的資料類型"}
                        },
                        "required": ["data_type"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "DatabricksPlugin-create_data_visualization",
                    "description": "建立資料視覺化圖表",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chart_type": {"type": "string", "description": "圖表類型 (如: 長條圖, 折線圖, 圓餅圖)"},
                            "data_source": {"type": "string", "description": "資料來源描述"}
                        },
                        "required": ["chart_type", "data_source"],
                    },
                },
            },
        ],
    )
    
    # 建立 Semantic Kernel 對應的 Azure AI Agent
    agent = AzureAIAgent(
        client=client,
        definition=agent_definition,
        plugins=[databricks_plugin],
    )
    
    return agent


async def main() -> None:
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 建立 Databricks agent
        agent = await create_databricks_agent(client)
        
        print(f"已建立 Databricks Agent，ID: {agent.id}")
        
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
            print(f"\n已清理 Databricks Agent 資源")

        """
        範例輸出：
        # User: '分析我們資料倉庫中最近一周的使用者行為趨勢'
        Function Call:> DatabricksPlugin-query_data_warehouse with arguments: {"query": "最近一周的使用者行為趨勢"}
        Function Result:> 過去一周活躍使用者增長15%，平均會話時間增加23分鐘 for function: DatabricksPlugin-query_data_warehouse
        
        根據資料倉庫的分析結果，我發現了以下使用者行為趨勢：
        
        📊 **使用者活躍度成長**
        - 活躍使用者數量增長了 15%
        - 平均會話時間增加了 23 分鐘
        
        這表示使用者對平台的參與度顯著提升，建議繼續優化使用者體驗以維持這個正向趨勢。
        """


if __name__ == "__main__":
    asyncio.run(main())