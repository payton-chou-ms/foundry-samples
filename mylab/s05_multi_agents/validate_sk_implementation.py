#!/usr/bin/env python3
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    驗證 Semantic Kernel 多代理程式系統實現的完整性和正確性
    
使用方式:
    python validate_sk_implementation.py
"""

import asyncio
import sys
import traceback
from typing import List, Dict, Any

def test_imports() -> bool:
    """測試所有模組是否可以正確導入"""
    print("🔍 測試模組導入...")
    
    try:
        # Test Semantic Kernel base modules
        from step4_handoff_semantic_kernel import (
            SemanticKernelBaseAgent, 
            SemanticKernelOrchestrator,
            HandoffType,
            HandoffRequest,
            create_handoff_request
        )
        print("  ✅ step4_handoff_semantic_kernel.py")
        
        # Test specialized agents
        from specialized_agents_sk import (
            SemanticKernelSearchAgent,
            SemanticKernelLogicAgent, 
            SemanticKernelFabricAgent,
            SemanticKernelDatabricksAgent,
            create_semantic_kernel_agent,
            AVAILABLE_SK_AGENTS
        )
        print("  ✅ specialized_agents_sk.py")
        
        # Test main system
        from multi_agent_system_sk import SemanticKernelMultiAgentSystem
        print("  ✅ multi_agent_system_sk.py")
        
        # Test demo
        from demo_sk import SemanticKernelDemo
        print("  ✅ demo_sk.py")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 導入失敗: {str(e)}")
        traceback.print_exc()
        return False

def test_agent_creation() -> bool:
    """測試代理程式創建"""
    print("\n🤖 測試代理程式創建...")
    
    try:
        from specialized_agents_sk import create_semantic_kernel_agent, AVAILABLE_SK_AGENTS
        
        created_agents = []
        for agent_type in AVAILABLE_SK_AGENTS:
            agent = create_semantic_kernel_agent(agent_type)
            created_agents.append(agent)
            print(f"  ✅ {agent.name} ({agent_type})")
        
        print(f"  📊 成功創建 {len(created_agents)} 個代理程式")
        return True
        
    except Exception as e:
        print(f"  ❌ 代理程式創建失敗: {str(e)}")
        traceback.print_exc()
        return False

async def test_system_initialization() -> bool:
    """測試系統初始化"""
    print("\n🚀 測試系統初始化...")
    
    try:
        from multi_agent_system_sk import SemanticKernelMultiAgentSystem
        
        system = SemanticKernelMultiAgentSystem()
        await system.initialize()
        
        print(f"  ✅ 系統初始化成功")
        print(f"  📊 已註冊代理程式: {len(system.agents)}")
        
        # Test cleanup
        await system.cleanup()
        print(f"  ✅ 系統清理成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 系統初始化失敗: {str(e)}")
        traceback.print_exc()
        return False

async def test_basic_task_execution() -> bool:
    """測試基本任務執行"""
    print("\n⚡ 測試基本任務執行...")
    
    try:
        from multi_agent_system_sk import SemanticKernelMultiAgentSystem
        
        system = SemanticKernelMultiAgentSystem()
        await system.initialize()
        
        # Test each agent type
        test_tasks = [
            ("search", "測試搜尋功能"),
            ("logicapps", "測試自動化功能"), 
            ("fabric", "測試數據分析功能"),
            ("databricks", "測試複雜查詢功能")
        ]
        
        successful_tasks = 0
        for agent_type, task in test_tasks:
            result = await system.execute_task(task, agent_type)
            if result.get("success"):
                successful_tasks += 1
                print(f"  ✅ {agent_type}: {task}")
            else:
                print(f"  ❌ {agent_type}: {task} - {result.get('error', 'Unknown error')}")
        
        await system.cleanup()
        
        print(f"  📊 成功執行 {successful_tasks}/{len(test_tasks)} 個任務")
        return successful_tasks == len(test_tasks)
        
    except Exception as e:
        print(f"  ❌ 任務執行測試失敗: {str(e)}")
        traceback.print_exc()
        return False

async def test_handoff_logic() -> bool:
    """測試移交邏輯"""
    print("\n🔄 測試移交邏輯...")
    
    try:
        from multi_agent_system_sk import SemanticKernelMultiAgentSystem
        
        system = SemanticKernelMultiAgentSystem()
        await system.initialize()
        
        # Test handoff scenarios
        handoff_tests = [
            {
                "initial_agent": "search",
                "task": "搜尋酒店然後發送郵件通知",
                "expected_handoff": True,
                "description": "搜尋→自動化移交"
            },
            {
                "initial_agent": "fabric", 
                "task": "進行機器學習分析",
                "expected_handoff": True,
                "description": "數據分析→複雜查詢移交"
            },
            {
                "initial_agent": "search",
                "task": "搜尋紐約的酒店",
                "expected_handoff": False,
                "description": "單一代理處理"
            }
        ]
        
        handoff_tests_passed = 0
        for test in handoff_tests:
            result = await system.execute_task(
                test["task"], 
                test["initial_agent"]
            )
            
            handoff_occurred = result.get("handoff_count", 0) > 0
            
            if handoff_occurred == test["expected_handoff"]:
                handoff_tests_passed += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"  {status} {test['description']}: 移交{'發生' if handoff_occurred else '未發生'}")
        
        await system.cleanup()
        
        print(f"  📊 移交邏輯測試: {handoff_tests_passed}/{len(handoff_tests)} 通過")
        return handoff_tests_passed == len(handoff_tests)
        
    except Exception as e:
        print(f"  ❌ 移交邏輯測試失敗: {str(e)}")
        traceback.print_exc()
        return False

async def test_demo_functionality() -> bool:
    """測試演示功能"""
    print("\n🎭 測試演示功能...")
    
    try:
        from demo_sk import SemanticKernelDemo
        
        demo = SemanticKernelDemo()
        await demo.system.initialize()
        
        # Test a simple demo scenario
        result = await demo.system.execute_task(
            "測試演示系統功能", 
            "search"
        )
        
        await demo.system.cleanup()
        
        if result.get("success"):
            print("  ✅ 演示系統功能正常")
            return True
        else:
            print(f"  ❌ 演示系統功能異常: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"  ❌ 演示功能測試失敗: {str(e)}")
        traceback.print_exc()
        return False

def test_plugin_system() -> bool:
    """測試 Plugin 系統"""
    print("\n🔌 測試 Plugin 系統...")
    
    try:
        from specialized_agents_sk import (
            AzureSearchPlugin,
            LogicAppsPlugin, 
            FabricPlugin,
            DatabricksPlugin
        )
        
        plugins = [
            AzureSearchPlugin(),
            LogicAppsPlugin(),
            FabricPlugin(), 
            DatabricksPlugin()
        ]
        
        plugin_functions_count = 0
        for plugin in plugins:
            # Count functions with SK attributes
            for attr_name in dir(plugin):
                attr = getattr(plugin, attr_name)
                if hasattr(attr, '_sk_function_name') or callable(attr) and not attr_name.startswith('_'):
                    if not attr_name.startswith('_'):
                        plugin_functions_count += 1
        
        print(f"  ✅ 成功載入 {len(plugins)} 個 plugins")
        print(f"  📊 總計 plugin 函數: {plugin_functions_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Plugin 系統測試失敗: {str(e)}")
        traceback.print_exc()
        return False

async def run_comprehensive_validation():
    """執行完整驗證"""
    print("🧪" + "=" * 80)
    print("🧪 Semantic Kernel 多代理程式系統 - 完整驗證")
    print("🧪" + "=" * 80)
    
    tests = [
        ("模組導入", test_imports),
        ("代理程式創建", test_agent_creation),
        ("Plugin 系統", test_plugin_system),
        ("系統初始化", test_system_initialization),
        ("基本任務執行", test_basic_task_execution),
        ("移交邏輯", test_handoff_logic),
        ("演示功能", test_demo_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試過程中發生錯誤: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "🏆" * 80)
    print("🏆 驗證結果總結")
    print("🏆" + "=" * 80)
    
    passed_tests = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗" 
        print(f"  {status} {test_name}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / len(results)) * 100
    print(f"\n📊 總體結果: {passed_tests}/{len(results)} 測試통過 ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 所有測試通過！Semantic Kernel 多代理程式系統實現完整且正確。")
        return True
    elif success_rate >= 80:
        print("⚠️ 大部分測試通過，系統基本可用，但可能需要修復一些問題。")
        return True
    else:
        print("❌ 多個測試失敗，系統可能存在重大問題需要修復。")
        return False

async def main():
    """主函數"""
    success = await run_comprehensive_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())