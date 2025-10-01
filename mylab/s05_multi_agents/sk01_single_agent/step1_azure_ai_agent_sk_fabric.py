# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)

"""
以下範例示範如何在 Semantic Kernel 中使用真實的 Microsoft Fabric 連接
來查詢計程車數據。本範例使用 Azure AI Agent 與 FabricTool 進行實際的數據分析。

必要條件:
    1) 設定包含計程車行程數據的 Microsoft Fabric lakehouse
    2) 配置具有適當模型部署的 Azure AI Foundry 專案
    3) 在 Azure AI Foundry 中建立 Fabric 連接
"""

# 載入環境變數
load_dotenv()

# 從環境變數取得設定
FOUNDRY_PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT") or os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FABRIC_CONNECTION_NAME = os.getenv("FABRIC_CONNECTION_NAME")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o-mini")

# 測試查詢
USER_INPUTS = [
    "比較國定假日與一般平日的計程車總行程數。此外，分析假日與平日之間的平均行程距離和平均車資是否有顯著差異。",
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
    if not FOUNDRY_PROJECT_ENDPOINT:
        raise ValueError("PROJECT_ENDPOINT or FOUNDRY_PROJECT_ENDPOINT environment variable is required")
    if not FABRIC_CONNECTION_NAME:
        raise ValueError("FABRIC_CONNECTION_NAME environment variable is required")
    
    print(f"🔗 正在連接到 Azure AI Foundry Project...")
    print(f"   Endpoint: {FOUNDRY_PROJECT_ENDPOINT}")
    print(f"   Fabric Connection: {FABRIC_CONNECTION_NAME}")
    print(f"   Model: {MODEL_DEPLOYMENT_NAME}\n")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds, endpoint=FOUNDRY_PROJECT_ENDPOINT) as client,
    ):
        # 取得 Fabric 連接 ID
        try:
            print("🔗 正在取得 Fabric 連接...")
            connection = await client.connections.get(name=FABRIC_CONNECTION_NAME)
            fabric_connection_id = connection.id
            print(f"✅ 成功取得 Fabric 連接 ID: {fabric_connection_id}\n")
        except Exception as e:
            print(f"❌ 無法取得 Fabric 連接: {e}")
            print("   請確認:")
            print("   1. FABRIC_CONNECTION_NAME 環境變數設定正確")
            print("   2. Azure AI Foundry 中已建立 Fabric 連接")
            print("   3. 您有適當的權限存取該連接\n")
            raise

        # 1. 建立 agent 定義，使用真實的 FabricTool
        # 重要：使用 Azure AI 原生的 FabricTool 而非自定義函數
        print("🤖 正在建立 Fabric Agent...")
        
        # 從 azure.ai.agents.models 導入 FabricTool（注意：需要同步版本的 client）
        # 因為 Semantic Kernel 使用 async client，我們需要先用同步 client 建立 agent
        from azure.ai.projects import AIProjectClient
        from azure.ai.agents.models import FabricTool
        from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
        
        # 建立同步 client 用於 agent 創建
        with AIProjectClient(
            credential=SyncDefaultAzureCredential(),
            endpoint=FOUNDRY_PROJECT_ENDPOINT
        ) as sync_client:
            # 使用 FabricTool - 這會進行真實的 Fabric 查詢
            fabric_tool = FabricTool(connection_id=fabric_connection_id)
            
            agent_definition = sync_client.agents.create_agent(
                model=MODEL_DEPLOYMENT_NAME,
                name="FabricLakehouseAgent",
                description="專門使用 Microsoft Fabric lakehouse 分析計程車數據的代理程式。",
                instructions="""您是一個專業的數據分析助手，專門使用 Microsoft Fabric lakehouse 來分析計程車行程數據。

當用戶提出關於計程車數據的問題時：
1. 使用 Fabric 工具查詢實際的 lakehouse 數據
2. 根據查詢結果提供清晰、專業的分析
3. 使用繁體中文回應，但保留技術術語的英文
4. 提供具體的數字和洞察

您可以分析的數據類型包括：
- 行程統計（總數、平均值等）
- 時間趨勢（假日vs平日、日間vs夜間）
- 車資分析（平均車資、高費用行程等）
- 地理分布（熱門上車地點等）
- 乘客模式（乘客數量分布等）

請基於實際數據提供準確的分析結果。""",
                tools=fabric_tool.definitions,
                tool_resources=fabric_tool.resources,
            )
            
            agent_id = agent_definition.id
            print(f"✅ Agent 創建成功，Agent ID: {agent_id}")
            print(f"   使用真實的 Microsoft Fabric 連接進行數據查詢\n")
        
        # 2. 使用 Semantic Kernel 的 AzureAIAgent 連接到已建立的 agent
        # 注意：當使用 Azure AI 原生工具（如 FabricTool）時，不需要註冊 plugins
        # 因為工具調用由 Azure AI 服務直接處理
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
            # 不需要 plugins - FabricTool 由 Azure AI 服務處理
        )
        
        print("✅ Semantic Kernel Agent 初始化完成")
        print(f"✅ Agent 已配置使用 FabricTool 進行真實數據查詢\n")

        # 3. 建立 agent 對話執行緒並執行查詢
        thread: AzureAIAgentThread = None

        try:
            print("="*80)
            print("🚕 開始計程車數據分析")
            print("="*80 + "\n")
            
            for i, user_input in enumerate(USER_INPUTS, 1):
                print(f"📝 查詢 {i}/{len(USER_INPUTS)}:")
                print(f"   {user_input}\n")
                print("-"*80)
                print("🤔 Agent 正在分析（使用真實的 Fabric lakehouse 數據）...\n")
                
                # 4. 以指定執行緒呼叫 agent 並串流回應
                response_count = 0
                async for response in agent.invoke_stream(
                    messages=user_input,
                    thread=thread,
                    on_intermediate_message=handle_streaming_intermediate_steps,
                ):
                    # Print the agent's response
                    if response_count == 0:
                        print("💬 Agent 回應:")
                    print(f"{response}", end="", flush=True)
                    response_count += 1
                    # Update the thread for subsequent messages
                    thread = response.thread
                
                print("\n" + "="*80 + "\n")
                
        finally:
            # 5. 清理資源：刪除執行緒和 agent
            print("🧹 正在清理資源...")
            
            # 刪除執行緒
            if thread:
                try:
                    await thread.delete()
                    print("✅ Thread 已刪除")
                except Exception as e:
                    print(f"⚠️  無法刪除 thread: {e}")
                
            # 刪除 agent 定義以釋放資源
            try:
                await client.agents.delete_agent(agent_definition.id)
                print(f"✅ Agent 已刪除 (ID: {agent_definition.id})")
            except Exception as e:
                print(f"⚠️  無法刪除 agent: {e}")
            
            print("\n✨ 程式執行完畢")

        """
        範例輸出：
        🔗 正在取得 Fabric 連接...
        ✅ 成功取得 Fabric 連接 ID: <connection-id>
        
        🤖 正在建立 Fabric Agent...
        ✅ Agent 創建成功，Agent ID: asst_xxxxx
        
        📝 查詢 1/1:
           比較國定假日與一般平日的計程車總行程數...
        
        💬 Agent 回應:
        根據 Microsoft Fabric lakehouse 的實際數據分析：
        
        1. 平日總行程數：68,452 趟
        2. 國定假日總行程數：48,731 趟
        3. 差異：平日比假日多 19,721 趟（約 40.5%）
        
        [基於真實的 Fabric lakehouse 查詢結果]
        """


if __name__ == "__main__":
    asyncio.run(main())
