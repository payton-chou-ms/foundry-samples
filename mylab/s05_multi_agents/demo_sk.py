# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    Semantic Kernel 多代理程式協作系統演示腳本
    展示如何使用基於 Semantic Kernel 的代理程式進行協作和移交
    
使用方式:
    python demo_sk.py

前置條件:
    pip install semantic-kernel azure-identity python-dotenv
    
    設定環境變數：
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_KEY (或使用 DefaultAzureCredential)
    - MODEL_DEPLOYMENT_NAME
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from multi_agent_system_sk import SemanticKernelMultiAgentSystem

class SemanticKernelDemo:
    """Semantic Kernel 多代理程式系統演示類"""
    
    def __init__(self):
        self.system = SemanticKernelMultiAgentSystem()
    
    async def run_full_demo(self):
        """執行完整演示"""
        print("🎭" + "=" * 80)
        print("🎭 歡迎使用 Semantic Kernel 多代理程式協作系統演示！")
        print("🎭" + "=" * 80)
        
        try:
            await self.system.initialize()
            
            # 運行各種演示場景
            await self._demo_basic_agent_functionality()
            await self._demo_handoff_scenarios() 
            await self._demo_cross_domain_collaboration()
            await self._demo_system_capabilities()
            
            print("\n" + "=" * 80)
            print("🎉 Semantic Kernel 多代理程式協作演示完成！")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ 演示過程中發生錯誤: {str(e)}")
        finally:
            await self.system.cleanup()
    
    async def _demo_basic_agent_functionality(self):
        """演示基本代理功能"""
        print("\n" + "🔧" * 60)
        print("🔧 第一部分：基本代理功能演示")
        print("🔧" * 60)
        
        scenarios = [
            {
                "name": "搜尋代理測試",
                "task": "搜尋紐約市中心的商務酒店，要有會議室和高速網路",
                "agent": "search",
                "description": "測試 SemanticKernelSearchAgent 的基本搜尋功能"
            },
            {
                "name": "自動化代理測試",
                "task": "發送一封感謝郵件給客戶，主題是'服務滿意度調查'",
                "agent": "logicapps",
                "description": "測試 SemanticKernelLogicAgent 的郵件發送功能"
            },
            {
                "name": "數據分析代理測試", 
                "task": "分析計程車在假日的使用模式，並與平日進行比較",
                "agent": "fabric",
                "description": "測試 SemanticKernelFabricAgent 的數據分析功能"
            },
            {
                "name": "複雜查詢代理測試",
                "task": "使用 Genie 查詢資料集中最常見的乘客數量分佈",
                "agent": "databricks", 
                "description": "測試 SemanticKernelDatabricksAgent 的複雜查詢功能"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📍 場景 {i}: {scenario['name']}")
            print(f"   描述: {scenario['description']}")
            print(f"   任務: {scenario['task']}")
            print(f"   代理: {scenario['agent']}")
            print("-" * 50)
            
            result = await self.system.execute_task(
                task=scenario["task"],
                initial_agent=scenario["agent"]
            )
            
            success_status = "✅ 成功" if result.get("success") else "❌ 失敗"
            print(f"   結果: {success_status}")
            
            if result.get("execution_history"):
                last_response = result["execution_history"][-1].get("result", {}).get("response", "")
                if last_response:
                    print(f"   回應: {last_response[:100]}...")
            
            await asyncio.sleep(1)  # 暫停一秒讓輸出更清晰
    
    async def _demo_handoff_scenarios(self):
        """演示移交場景"""
        print("\n" + "🔄" * 60)
        print("🔄 第二部分：代理間移交場景演示")
        print("🔄" * 60)
        
        handoff_scenarios = [
            {
                "name": "搜尋→自動化移交",
                "task": "搜尋台北的五星級酒店，然後發郵件把結果寄給經理",
                "initial_agent": "search",
                "description": "從搜尋代理開始，自動移交給自動化代理發送郵件"
            },
            {
                "name": "數據分析→複雜查詢移交",
                "task": "分析計程車數據後，使用機器學習預測未來一週的需求趨勢",
                "initial_agent": "fabric",
                "description": "從數據分析代理升級到複雜查詢代理進行機器學習分析"
            },
            {
                "name": "自動化→搜尋移交",
                "task": "設定自動化工作流程之前，先搜尋相關的 API 文檔和最佳實務",
                "initial_agent": "logicapps",
                "description": "自動化代理需要先搜尋資訊才能設定工作流程"
            }
        ]
        
        for i, scenario in enumerate(handoff_scenarios, 1):
            print(f"\n📍 移交場景 {i}: {scenario['name']}")
            print(f"   描述: {scenario['description']}")
            print(f"   任務: {scenario['task']}")
            print(f"   起始代理: {scenario['initial_agent']}")
            print("-" * 50)
            
            result = await self.system.execute_task(
                task=scenario["task"],
                initial_agent=scenario["initial_agent"]
            )
            
            success_status = "✅ 成功" if result.get("success") else "❌ 失敗"
            handoff_count = result.get("handoff_count", 0)
            final_agent = result.get("final_agent", "Unknown")
            
            print(f"   結果: {success_status}")
            print(f"   移交次數: {handoff_count}")
            print(f"   最終代理: {final_agent}")
            
            if result.get("execution_history"):
                print(f"   執行路徑: ", end="")
                agent_path = " → ".join([step["agent"] for step in result["execution_history"]])
                print(agent_path)
            
            await asyncio.sleep(1)
    
    async def _demo_cross_domain_collaboration(self):
        """演示跨領域協作"""
        print("\n" + "🤝" * 60)
        print("🤝 第三部分：跨領域協作演示") 
        print("🤝" * 60)
        
        collaboration_scenarios = [
            {
                "name": "全流程旅遊服務",
                "task": "我需要規劃一個商務行程：搜尋上海的商務酒店，分析當地的交通模式，然後發郵件給助手安排行程細節",
                "initial_agent": "search",
                "description": "涉及搜尋、數據分析和自動化的綜合協作"
            },
            {
                "name": "數據驅動的自動化決策",
                "task": "基於計程車使用高峰時段的分析結果，自動發送調度建議給車隊管理系統",
                "initial_agent": "fabric",
                "description": "數據分析結果驅動自動化操作"
            },
            {
                "name": "智慧客服完整流程",
                "task": "客戶詢問關於機器學習服務的問題，需要搜尋相關資訊、進行複雜分析、然後自動回覆客戶",
                "initial_agent": "search",
                "description": "客服場景的完整代理協作流程"
            }
        ]
        
        for i, scenario in enumerate(collaboration_scenarios, 1):
            print(f"\n📍 協作場景 {i}: {scenario['name']}")
            print(f"   描述: {scenario['description']}")
            print(f"   任務: {scenario['task']}")
            print("-" * 50)
            
            result = await self.system.execute_task(
                task=scenario["task"],
                initial_agent=scenario["initial_agent"]
            )
            
            success_status = "✅ 成功" if result.get("success") else "❌ 失敗"
            print(f"   結果: {success_status}")
            
            if result.get("execution_history"):
                print(f"   協作歷程:")
                for j, step in enumerate(result["execution_history"], 1):
                    agent_name = step["agent"]
                    step_success = "✅" if step["result"].get("success") else "❌"
                    print(f"      {j}. {step_success} {agent_name}")
            
            await asyncio.sleep(1)
    
    async def _demo_system_capabilities(self):
        """演示系統能力"""
        print("\n" + "⚙️" * 60)
        print("⚙️ 第四部分：系統能力展示")
        print("⚙️" * 60)
        
        # 顯示系統狀態
        self.system.show_system_status()
        
        # 顯示移交歷史
        history = self.system.orchestrator.get_handoff_history()
        print(f"\n📊 本次演示產生的移交記錄: {len(history)} 筆")
        
        if history:
            print("\n最近的移交記錄:")
            for i, record in enumerate(history[-5:], 1):  # 顯示最後5筆
                print(f"   {i}. {record['from_agent']} → {record['to_agent']}")
                print(f"      類型: {record['handoff_type']} | 優先級: {record['priority']}")
                print(f"      時間: {record['timestamp']}")
                print()
        
        # 統計信息
        agent_usage = {}
        for record in history:
            from_agent = record['from_agent']
            to_agent = record['to_agent']
            agent_usage[from_agent] = agent_usage.get(from_agent, 0) + 1
            if to_agent:
                agent_usage[to_agent] = agent_usage.get(to_agent, 0) + 1
        
        if agent_usage:
            print("📈 代理程式使用統計:")
            for agent, count in sorted(agent_usage.items(), key=lambda x: x[1], reverse=True):
                print(f"   {agent}: {count} 次")

async def main():
    """主函數"""
    demo = SemanticKernelDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    print("🚀 啟動 Semantic Kernel 多代理程式協作系統演示...")
    asyncio.run(main())