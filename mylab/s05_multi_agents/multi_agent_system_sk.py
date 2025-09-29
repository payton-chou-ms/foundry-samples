# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    基於 Semantic Kernel 的多代理程式協作系統主程式，整合四個專門的代理程式：
    - SemanticKernelSearchAgent (搜尋代理)
    - SemanticKernelLogicAgent (自動化代理)
    - SemanticKernelFabricAgent (數據分析代理)  
    - SemanticKernelDatabricksAgent (資料科學代理)
    
    支援代理程式間的智慧移交和協作。

使用方式:
    python multi_agent_system_sk.py

前置條件:
    pip install semantic-kernel azure-identity python-dotenv azure-search-documents
    pip install databricks-sdk azure-mgmt-logic requests
    
    設定 .env 檔案包含所需的環境變數
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Import our semantic kernel handoff system and specialized agents
try:
    from step4_handoff_semantic_kernel import SemanticKernelOrchestrator
    from specialized_agents_sk import (
        SemanticKernelSearchAgent,
        SemanticKernelLogicAgent, 
        SemanticKernelFabricAgent,
        SemanticKernelDatabricksAgent,
        create_semantic_kernel_agent,
        AVAILABLE_SK_AGENTS
    )
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    print("Warning: Semantic Kernel modules not available. Running in mock mode.")
    SEMANTIC_KERNEL_AVAILABLE = False
    class SemanticKernelOrchestrator: pass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SemanticKernelMultiAgentSystem:
    """基於 Semantic Kernel 的多代理程式系統主類"""
    
    def __init__(self):
        self.orchestrator = None
        self.agents = {}
        self.initialized = False
        
    async def initialize(self):
        """初始化多代理程式系統"""
        print("🚀 初始化 Semantic Kernel 多代理程式協作系統...")
        print("=" * 70)
        
        # Check required environment variables
        required_vars = ["AZURE_OPENAI_ENDPOINT", "MODEL_DEPLOYMENT_NAME"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️ Missing required environment variables: {', '.join(missing_vars)}")
            print("⚠️ System will run in mock mode")
        
        # Create orchestrator
        self.orchestrator = SemanticKernelOrchestrator()
        await self.orchestrator.initialize()
        
        # Create and register specialized agents
        print("\n📋 創建基於 Semantic Kernel 的專門代理程式...")
        
        try:
            # Semantic Kernel Search Agent
            search_agent = SemanticKernelSearchAgent()
            self.orchestrator.register_agent(search_agent)
            self.agents["search"] = search_agent
            print("✅ SemanticKernelSearchAgent - 搜尋代理")
            
            # Semantic Kernel Logic Agent  
            logic_agent = SemanticKernelLogicAgent()
            self.orchestrator.register_agent(logic_agent)
            self.agents["logicapps"] = logic_agent
            print("✅ SemanticKernelLogicAgent - 自動化代理")
            
            # Semantic Kernel Fabric Agent
            fabric_agent = SemanticKernelFabricAgent()
            self.orchestrator.register_agent(fabric_agent)
            self.agents["fabric"] = fabric_agent
            print("✅ SemanticKernelFabricAgent - 數據分析代理")
            
            # Semantic Kernel Databricks Agent
            databricks_agent = SemanticKernelDatabricksAgent()
            self.orchestrator.register_agent(databricks_agent)
            self.agents["databricks"] = databricks_agent
            print("✅ SemanticKernelDatabricksAgent - 資料科學代理")
            
        except Exception as e:
            logger.error(f"Error creating agents: {str(e)}")
            raise
        
        # Initialize all agents
        print("\n🔧 初始化所有 Semantic Kernel 代理程式...")
        await self.orchestrator.initialize_all_agents()
        
        self.initialized = True
        print("\n✅ Semantic Kernel 多代理程式系統初始化完成！")
        
    async def execute_task(self, task: str, initial_agent: str = "search", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行任務並支援代理程式間協作"""
        if not self.initialized:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        print(f"\n🎯 執行任務 (Semantic Kernel): {task}")
        print(f"📍 起始代理: {initial_agent}")
        print("-" * 50)
        
        # Validate initial agent
        agent_name_map = {
            "search": "SemanticKernelSearchAgent",
            "logicapps": "SemanticKernelLogicAgent", 
            "fabric": "SemanticKernelFabricAgent",
            "databricks": "SemanticKernelDatabricksAgent"
        }
        
        if initial_agent not in agent_name_map:
            initial_agent = "search"  # Default to search agent
        
        agent_name = agent_name_map[initial_agent]
        
        try:
            # Execute task with orchestrator
            result = await self.orchestrator.execute_task(
                task=task,
                initial_agent=agent_name,
                context=context
            )
            
            # Log execution details
            print(f"\n📊 執行結果:")
            print(f"   成功: {'是' if result.get('success') else '否'}")
            print(f"   移交次數: {result.get('handoff_count', 0)}")
            print(f"   最終代理: {result.get('final_agent', 'N/A')}")
            
            # Show execution history
            if result.get('execution_history'):
                print(f"\n📚 執行歷史:")
                for i, step in enumerate(result['execution_history'], 1):
                    agent_name = step.get('agent', 'Unknown')
                    success = step.get('result', {}).get('success', False)
                    status = '✅' if success else '❌'
                    print(f"   {i}. {status} {agent_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_history": []
            }
    
    def get_agent_capabilities(self) -> Dict[str, str]:
        """獲取各代理程式的能力說明"""
        return {
            "SemanticKernelSearchAgent": "🔍 專門處理搜尋相關查詢，包括酒店搜尋、資訊檢索、向量搜尋等 (Semantic Kernel)",
            "SemanticKernelLogicAgent": "⚡ 專門處理自動化任務，包括郵件發送、工作流程、API 整合等 (Semantic Kernel)",
            "SemanticKernelFabricAgent": "📊 專門處理數據分析，包括計程車數據統計、趨勢分析、地理分析等 (Semantic Kernel)",
            "SemanticKernelDatabricksAgent": "🧠 專門處理複雜查詢，包括機器學習、大數據處理、高級分析等 (Semantic Kernel)"
        }
    
    def show_system_status(self):
        """顯示系統狀態"""
        print("\n" + "=" * 70)
        print("🏢 Semantic Kernel 多代理程式協作系統狀態")
        print("=" * 70)
        
        if not self.initialized:
            print("❌ 系統未初始化")
            return
        
        print("✅ Semantic Kernel 系統已初始化")
        print(f"\n📋 已註冊代理程式數量: {len(self.agents)}")
        
        capabilities = self.get_agent_capabilities()
        for agent_name, description in capabilities.items():
            print(f"\n{description}")
        
        print(f"\n📈 移交歷史記錄數: {len(self.orchestrator.get_handoff_history())}")
        print("=" * 70)
    
    async def cleanup(self):
        """清理系統資源"""
        if self.orchestrator:
            print("\n🧹 清理 Semantic Kernel 系統資源...")
            await self.orchestrator.cleanup_all_agents()
            print("✅ 清理完成")

def display_menu():
    """顯示互動選單"""
    print("\n" + "=" * 80)
    print("🤖 Semantic Kernel 多代理程式協作系統 - 選單")
    print("=" * 80)
    print("\n請選擇操作：")
    print("\n示例任務：")
    print("   1. 搜尋紐約的精品酒店")
    print("   2. 分析計程車行程數據的日夜差異") 
    print("   3. 發送包含當前時間的電子郵件")
    print("   4. 查詢最高費用的計程車行程")
    print("   5. 使用 Genie 進行複雜資料查詢")
    print("\n系統操作：")
    print("   6. 顯示系統狀態和代理能力")
    print("   7. 查看移交歷史記錄")
    print("   8. 自定義任務")
    print("   0. 退出")
    print("\n" + "=" * 80)

def get_sample_tasks() -> Dict[str, Dict[str, Any]]:
    """獲取示例任務"""
    return {
        "1": {
            "task": "我想找紐約的精品酒店，評分要高，最好有商務設施",
            "agent": "search",
            "description": "酒店搜尋任務 (SK)"
        },
        "2": {
            "task": "比較日間（7:00–19:00）與夜間（19:00–7:00）的計程車行程數量和平均車資金額",
            "agent": "fabric", 
            "description": "數據分析任務 (SK)"
        },
        "3": {
            "task": "發送一封電子郵件，包含當前時間和系統狀態信息",
            "agent": "logicapps",
            "description": "自動化任務 (SK)"
        },
        "4": {
            "task": "找出車資金額大於 70 的行程數量和這些高車資行程的百分比",
            "agent": "fabric",
            "description": "統計分析任務 (SK)"  
        },
        "5": {
            "task": "使用 Genie 查詢我們資料集中最常見的乘客數量值",
            "agent": "databricks",
            "description": "複雜資料查詢 (SK)"
        }
    }

async def interactive_mode():
    """互動模式"""
    system = SemanticKernelMultiAgentSystem()
    
    try:
        await system.initialize()
        
        sample_tasks = get_sample_tasks()
        
        while True:
            display_menu()
            choice = input("\n請選擇 (0-8): ").strip()
            
            if choice == "0":
                print("\n👋 感謝使用，再見！")
                break
            
            elif choice in sample_tasks:
                task_info = sample_tasks[choice]
                print(f"\n🚀 執行{task_info['description']}: {task_info['task']}")
                
                result = await system.execute_task(
                    task=task_info["task"],
                    initial_agent=task_info["agent"]
                )
                
                if result.get("success"):
                    print(f"\n✅ 任務執行成功！")
                    # Show final response if available
                    if result.get("execution_history"):
                        last_step = result["execution_history"][-1]
                        if last_step.get("result", {}).get("response"):
                            print(f"\n💬 最終回應：")
                            print(f"{last_step['result']['response'][:500]}...")
                else:
                    print(f"\n❌ 任務執行失敗: {result.get('error', 'Unknown error')}")
            
            elif choice == "6":
                system.show_system_status()
            
            elif choice == "7":
                history = system.orchestrator.get_handoff_history()
                print(f"\n📚 移交歷史記錄 ({len(history)} 筆):")
                if history:
                    for i, record in enumerate(history[-10:], 1):  # Show last 10
                        print(f"   {i}. {record['from_agent']} → {record['to_agent']}")
                        print(f"      類型: {record['handoff_type']} | 時間: {record['timestamp']}")
                else:
                    print("   目前無移交記錄")
            
            elif choice == "8":
                custom_task = input("\n請輸入自定義任務: ").strip()
                if custom_task:
                    agent_choice = input("選擇起始代理 (search/logicapps/fabric/databricks) [預設: search]: ").strip()
                    if not agent_choice:
                        agent_choice = "search"
                    
                    result = await system.execute_task(
                        task=custom_task,
                        initial_agent=agent_choice
                    )
                    
                    if result.get("success"):
                        print(f"\n✅ 自定義任務執行成功！")
                    else:
                        print(f"\n❌ 自定義任務執行失敗: {result.get('error', 'Unknown error')}")
                else:
                    print("❌ 任務不能為空")
            
            else:
                print("❌ 無效選擇，請重新輸入")
            
            input("\n按 Enter 繼續...")
    
    except KeyboardInterrupt:
        print("\n\n👋 程式被中斷，正在清理...")
    except Exception as e:
        print(f"\n❌ 系統錯誤: {str(e)}")
        logger.error(f"System error: {str(e)}")
    finally:
        await system.cleanup()

async def main():
    """主函數"""
    print("🤖 歡迎使用 Semantic Kernel 多代理程式協作系統！")
    print("=" * 60)
    
    await interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())