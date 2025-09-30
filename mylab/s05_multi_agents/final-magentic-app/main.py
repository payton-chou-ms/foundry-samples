# Copyright (c) Microsoft. All rights reserved.

"""
互動式多代理程式系統 - Magentic 編排 (重構版本)
================================================

這是一個重構後的企業級多代理程式系統，整合了四個專業代理程式：

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

架構重構特點：
- 模組化設計，職責分離清晰
- 配置統一管理
- 插件可獨立維護和測試
- 代理程式工廠模式
- 編排邏輯封裝

使用方式:
    python main.py

範例問題:
    1. "幫我找一些豪華飯店，然後分析一下預訂數據趨勢"
    2. "查詢交易數據中的異常模式，並發送報告到我的郵箱"
    3. "搜尋技術文檔中的最佳實務，並生成摘要郵件"
    4. "分析計程車數據的高峰時段，然後推薦相關的商務飯店"
"""

import asyncio
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent

# 導入重構後的模組
from config import settings
from utils import ConnectionManager, LogicAppManager, display_menu, get_query_by_selection
from agents import AgentFactory
from orchestration import MagenticOrchestrator


async def initialize_system():
    """初始化系統"""
    print("🚀 正在初始化企業級多代理程式系統...")
    print("=" * 60)
    
    # 驗證配置
    settings.validate()
    settings.configure_databricks_sdk()
    
    # 建立 Azure AI 客戶端
    creds = DefaultAzureCredential()
    client = AzureAIAgent.create_client(credential=creds, endpoint=settings.FOUNDRY_PROJECT_ENDPOINT)
    
    return creds, client


async def initialize_connections(client):
    """初始化所有外部連接"""
    print("🔧 正在初始化系統連接...")
    
    # 初始化連接管理器
    connection_manager = ConnectionManager()
    
    # 初始化各種連接
    await connection_manager.initialize_databricks(client)
    await connection_manager.initialize_fabric(client)
    
    # 初始化 Logic App 管理器
    logic_app_manager = None
    if (settings.LOGIC_APP_EMAIL_TRIGGER_URL or 
        (settings.AZURE_SUBSCRIPTION_ID and settings.AZURE_RESOURCE_GROUP and 
         settings.LOGIC_APP_NAME and settings.TRIGGER_NAME)):
        try:
            logic_app_manager = LogicAppManager()
            print("✅ Logic App 管理器初始化成功")
        except Exception as e:
            print(f"⚠️ Logic App 連接失敗: {e}")
    else:
        print("⚠️ Logic App 設定未完整，將使用模擬模式")
    
    print("=" * 60)
    return connection_manager, logic_app_manager


async def create_agents(client, connection_manager, logic_app_manager):
    """創建所有代理程式"""
    # 創建代理程式工廠
    agent_factory = AgentFactory(connection_manager, logic_app_manager)
    
    # 創建所有代理程式
    agents_list = await agent_factory.create_all_agents(client)
    
    print(f"✅ 已建立 {len(agents_list)} 個專業代理程式:")
    for i, agent in enumerate(agents_list, 1):
        print(f"   {i}. {agent.name} - {agent.description}")
    
    return agents_list


async def run_interactive_session(orchestrator):
    """執行互動式會話"""
    print("\n🎯 歡迎使用多代理程式企業智能助手！")
    print("您可以選擇預設查詢或輸入自定義問題。")

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
                query_type = "multi_agent"  # 自訂查詢預設為多代理程式類型
            else:
                result = get_query_by_selection(user_choice)
                if result[0]:  # 如果有查詢結果
                    user_query, query_type = result
                    print(f"\n📋 選擇的查詢: {user_query[:100]}{'...' if len(user_query) > 100 else ''}")
                    print(f"📊 查詢類型: {query_type}")
                else:
                    print("❌ 無效的選擇，請重新選擇")
                    continue
            
            # 處理使用者查詢
            print("\n🔄 啟動多代理程式協作...")
            success = await orchestrator.process_query(user_query, query_type)
            
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


async def cleanup_agents(client, agents_list):
    """清理代理程式資源"""
    print("\n🧹 正在清理系統資源...")
    
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


async def main():
    """主函數 - 執行整合多代理程式編排"""
    
    try:
        # 1. 初始化系統
        creds, client = await initialize_system()
        
        async with creds, client:
            # 2. 初始化連接
            connection_manager, logic_app_manager = await initialize_connections(client)
            
            # 3. 創建代理程式
            agents_list = await create_agents(client, connection_manager, logic_app_manager)
            
            # 4. 創建編排器，使用配置的超時設定
            orchestrator = MagenticOrchestrator(
                agents_list, 
                response_timeout=settings.RESPONSE_TIMEOUT,
                max_iterations=settings.MAX_ITERATIONS
            )
            await orchestrator.start_runtime()
            
            print(f"⚙️ 系統設定:")
            print(f"   📊 響應超時: {settings.RESPONSE_TIMEOUT} 秒")
            print(f"   🔄 最大響應次數: {settings.MAX_ITERATIONS}")
            print("=" * 60)
            
            try:
                # 5. 執行互動式會話
                await run_interactive_session(orchestrator)
                
            finally:
                # 6. 清理資源
                await orchestrator.stop_runtime()
                await cleanup_agents(client, agents_list)
                
    except Exception as e:
        print(f"❌ 系統初始化失敗: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())