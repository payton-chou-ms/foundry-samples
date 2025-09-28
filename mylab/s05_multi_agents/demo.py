#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Demo script for the Multi-Agent Handoff System

This script demonstrates key features without requiring full Azure setup.
Perfect for understanding how agent handoffs work.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set mock environment 
os.environ['PROJECT_ENDPOINT'] = 'https://mock-endpoint.example.com'
os.environ['MODEL_DEPLOYMENT_NAME'] = 'mock-model-gpt-4'

from step4_handoff import HandoffOrchestrator, HandoffType
from specialized_agents import AzureAISearchAgent, LogicAppsAgent, FabricAgent, DatabricksAgent

# Mock AIProjectClient for demo
class MockAIProjectClient:
    def __init__(self, endpoint, credential):
        self.endpoint = endpoint
        self.credential = credential
        print(f"🔗 Mock connection to {endpoint}")

async def demo_agent_handoffs():
    """Demonstrate agent handoff functionality"""
    
    print("🎭 多代理程式移交系統演示")
    print("=" * 60)
    print("📝 注意：此演示使用 mock 模式，不需要實際的 Azure 連接")
    print()
    
    # Create mock project client
    mock_client = MockAIProjectClient("https://mock-endpoint.example.com", None)
    
    # Create orchestrator
    orchestrator = HandoffOrchestrator(mock_client)
    
    # Create and register agents
    agents = {
        "search": AzureAISearchAgent(),
        "logic": LogicAppsAgent(),
        "fabric": FabricAgent(), 
        "databricks": DatabricksAgent()
    }
    
    for agent in agents.values():
        orchestrator.register_agent(agent)
    
    print("📋 已註冊的代理程式:")
    for name, agent in agents.items():
        print(f"   • {agent.name}: {agent.description}")
    
    print("\n" + "="*60)
    print("🔄 測試移交邏輯")
    print("="*60)
    
    # Test scenarios
    scenarios = [
        {
            "name": "搜尋轉郵件移交",
            "task": "幫我搜尋一家紐約酒店，然後發郵件通知客戶",
            "starting_agent": "search",
            "expected_handoff": "LogicAppsAgent"
        },
        {
            "name": "數據分析升級移交", 
            "task": "我需要使用 Genie 進行複雜的機器學習分析",
            "starting_agent": "fabric",
            "expected_handoff": "DatabricksAgent"
        },
        {
            "name": "自動化轉搜尋移交",
            "task": "先搜尋最好的酒店，然後建立自動化工作流程",
            "starting_agent": "logic",
            "expected_handoff": "AzureAISearchAgent"
        },
        {
            "name": "無需移交案例",
            "task": "分析計程車數據的基本統計",
            "starting_agent": "fabric", 
            "expected_handoff": None
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 測試場景 {i}: {scenario['name']}")
        print(f"   任務: {scenario['task']}")
        print(f"   起始代理: {scenario['starting_agent']}")
        
        # Get the agent
        agent = agents[scenario['starting_agent']]
        
        # Test handoff logic
        handoff_req = agent.should_handoff(scenario['task'])
        
        if handoff_req:
            print(f"   ✅ 移交檢測: {handoff_req.from_agent} → {handoff_req.to_agent}")
            print(f"   🔄 移交類型: {handoff_req.handoff_type.value}")
            print(f"   📋 移交任務: {handoff_req.task_description[:50]}...")
            
            # Verify expected handoff
            if scenario["expected_handoff"] and handoff_req.to_agent == scenario["expected_handoff"]:
                print("   🎯 符合預期的移交目標!")
            elif scenario["expected_handoff"]:
                print(f"   ⚠️  預期移交到 {scenario['expected_handoff']}, 但實際移交到 {handoff_req.to_agent}")
        else:
            if scenario["expected_handoff"] is None:
                print("   ✅ 無需移交 (符合預期)")
            else:
                print(f"   ❌ 預期移交到 {scenario['expected_handoff']}, 但無移交發生")
    
    print("\n" + "="*60)
    print("🏗️ 移交類型說明")
    print("="*60)
    
    handoff_types = {
        HandoffType.FORWARD: "轉發 - 將任務轉發給更適合的代理",
        HandoffType.ESCALATE: "升級 - 升級給更專業的代理處理", 
        HandoffType.COLLABORATE: "協作 - 多個代理共同完成任務",
        HandoffType.COMPLETE: "完成 - 任務已完成，無需進一步處理"
    }
    
    for handoff_type, description in handoff_types.items():
        print(f"   • {handoff_type.value.upper()}: {description}")
    
    print("\n" + "="*60)
    print("🎯 系統特色")  
    print("="*60)
    
    features = [
        "智慧移交 - 自動檢測任務類型並移交給最適合的代理",
        "循環防護 - 防止代理間無限循環移交 (最多10次)",
        "上下文保持 - 移交時保留任務上下文和執行歷史",
        "彈性部署 - 支援 mock 模式，無需完整 Azure 環境",
        "錯誤處理 - 完整的錯誤處理和資源清理機制",
        "監控記錄 - 詳細的執行歷史和移交記錄"
    ]
    
    for feature in features:
        print(f"   ✅ {feature}")
    
    print("\n" + "="*60)
    print("🚀 下一步")
    print("="*60)
    print("1. 設定真實的 Azure 環境變數 (.env 檔案)")
    print("2. 安裝完整依賴: pip install -r requirements.txt")
    print("3. 執行完整系統: python multi_agent_system.py")
    print("4. 或直接使用互動模式體驗完整功能")
    
    print(f"\n🎉 演示完成！時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(demo_agent_handoffs())