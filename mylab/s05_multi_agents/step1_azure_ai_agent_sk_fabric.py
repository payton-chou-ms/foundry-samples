# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import os
from typing import Optional
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)
from semantic_kernel.functions.kernel_function_decorator import kernel_function

"""
以下範例示範如何在 Semantic Kernel 中使用已存在的
Azure AI Agent。本範例假設您已先前建立好 agent（透過程式、Portal 或 CLI）。
"""

# 載入環境變數
load_dotenv()

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_FABRIC_CONNECTION_NAME = os.getenv("FABRIC_CONNECTION_NAME")

# 新增 agent_id 變數
# agent_id = "<your-agent-id>"
agent_id = "asst_WQGJrTdKZcrBqtyQEnStVKHn"

# 全域變數儲存 Fabric 連接資訊
fabric_connection = None

# 定義 query_fabric 函數作為 Kernel Function
@kernel_function(description="向 Microsoft Fabric lakehouse 查詢計程車數據並取得回應", name="query_fabric")
def query_fabric(question: str, query_type: str = "general") -> str:
    """
    向 Microsoft Fabric lakehouse 提問並以 JSON 格式回傳回應。
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

# 模擬與 agent 的對話
USER_INPUTS = [
    "比較國定假日與一般平日的計程車總行程數",
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
    global fabric_connection
    
    if not FOUNDRY_PROJECT_ENDPOINT:
        raise ValueError("FOUNDRY_PROJECT_ENDPOINT environment variable is required")
    if not FOUNDRY_FABRIC_CONNECTION_NAME:
        raise ValueError("FOUNDRY_FABRIC_CONNECTION_NAME environment variable is required")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds, endpoint=FOUNDRY_PROJECT_ENDPOINT) as client,
    ):
        # 設置 Microsoft Fabric 連接
        try:
            # 取得 Fabric 連接資訊
            connection = await client.connections.get(name=FOUNDRY_FABRIC_CONNECTION_NAME)
            print(f"Retrieved connection '{FOUNDRY_FABRIC_CONNECTION_NAME}' from AI project")
            
            # 模擬 Fabric 連接設置（在實際實作中會設置真實的 Fabric 連接）
            fabric_connection = {
                "name": connection.name,
                "target": connection.target if hasattr(connection, 'target') else 'mock-fabric-endpoint',
                "connection_type": "fabric_lakehouse"
            }
            print(f"Microsoft Fabric connection initialized successfully")
            
        except Exception as e:
            print(f"Warning: Could not retrieve Fabric connection, using mock connection: {e}")
            # 使用模擬連接以便範例可以執行
            fabric_connection = {
                "name": "mock-fabric-connection",
                "target": "mock-fabric-endpoint", 
                "connection_type": "fabric_lakehouse"
            }
            print("Using mock Fabric connection for demonstration")

        # 1. 建立新的 agent 定義，包含 query_fabric 函數工具的定義
        # 這是關鍵：我們需要在 Azure AI 服務層面定義函數工具
        agent_definition = await client.agents.create_agent(
            model=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
            name="FabricLakehouseAgent",
            description="專門使用 Microsoft Fabric lakehouse 分析計程車數據的代理程式。",
            instructions="您是一個數據分析助手，專門使用 Microsoft Fabric lakehouse 來回答關於計程車數據的問題。當用戶詢問數據相關問題時，請使用 query_fabric 函數來獲取準確的分析結果。",
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
        print(f"Created agent definition, agent ID: {agent_definition.id}")
        
        # 2. 使用定義建立 Semantic Kernel AzureAIAgent 實例
        # 建立一個簡單的插件類別
        class FabricPlugin:
            @kernel_function(description="向 Microsoft Fabric lakehouse 查詢計程車數據並取得回應", name="query_fabric")
            def query_fabric(self, question: str, query_type: Optional[str] = "general") -> str:
                return query_fabric(question, query_type or "general")

        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
            plugins=[FabricPlugin()],  # 註冊包含實際函數實現的插件
        )
        
        print("Registered query_fabric function to agent kernel")
        print(f"Agent kernel plugins: {list(agent.kernel.plugins.keys())}")
        
        # 驗證函數是否已註冊
        if agent.kernel.plugins:
            for plugin_name, plugin in agent.kernel.plugins.items():
                print(f"{plugin_name} functions: {list(plugin.functions.keys()) if hasattr(plugin, 'functions') else 'No functions attribute'}")

        # 3. 建立 agent 對話執行緒
        # 若未提供執行緒，系統將建立並回傳含初始回應的新執行緒
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
            except Exception as e:
                print(f"Note: Could not delete agent {agent_definition.id}: {e}")

        """
        範例輸出：
        # User: '比較國定假日與一般平日的計程車總行程數'
        # Agent: 根據 Microsoft Fabric lakehouse 的計程車數據分析，平日行程數 (70,000) 比國定假日 (50,000) 多 20,000 趟。
        """


if __name__ == "__main__":
    asyncio.run(main())
