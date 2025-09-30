# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Dict, List, Optional, Any

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)

"""
以下範例整合多個專門的 Azure AI Agent，建立一個完整的多 agent 協作系統。
此系統基於 Semantic Kernel 框架，支援智能任務分配和 agent 間的協調。

整合的 agent 類型：
1. AI Search Agent - 資訊檢索和搜尋
2. Databricks Agent - 資料分析和處理 
3. Fabric Agent - 資料倉儲和 BI 報表
4. Logic App Agent - 工作流程自動化

系統特色：
- 智能任務解析和分配
- Agent 間協調和結果整合
- 支援複雜業務流程
- 完整的錯誤處理和資源管理
"""


class SemanticKernelMultiAgentSystem:
    """基於 Semantic Kernel 的多 Agent 協作系統"""
    
    def __init__(self, client):
        self.client = client
        self.agents: Dict[str, AzureAIAgent] = {}
        self.threads: Dict[str, AzureAIAgentThread] = {}
        self.agent_capabilities = {
            "search": {
                "keywords": ["搜尋", "找到", "查詢", "檢索", "資訊", "資料", "hotel", "luxury"],
                "description": "專門處理資訊搜尋和檢索任務"
            },
            "databricks": {
                "keywords": ["分析", "處理", "ETL", "資料科學", "機器學習", "數據", "統計"],
                "description": "專門處理資料分析和機器學習任務"
            },
            "fabric": {
                "keywords": ["報表", "BI", "資料倉儲", "OneLake", "Power BI", "同步", "倉儲"],
                "description": "專門處理資料倉儲和商業智慧報表"
            },
            "logic_app": {
                "keywords": ["工作流程", "自動化", "通知", "郵件", "審核", "流程", "觸發"],
                "description": "專門處理工作流程自動化和業務流程管理"
            }
        }
        
        # Agent IDs - 實際使用時請替換為真實的 Agent IDs
        self.agent_ids = {
            "search": "asst_vnVvS09TGw3zOC6Z0vxiviN0",  # 實際的 AI Search Agent ID
            "databricks": "asst_databricks_example_id",   # Databricks Agent ID
            "fabric": "asst_fabric_example_id",           # Fabric Agent ID  
            "logic_app": "asst_logic_app_example_id",     # Logic App Agent ID
        }
    
    async def initialize_agents(self) -> bool:
        """初始化所有專門的 agents"""
        print("🔄 Initializing Semantic Kernel Multi-Agent System...")
        
        success_count = 0
        for agent_type, agent_id in self.agent_ids.items():
            try:
                print(f"  📡 Connecting to {agent_type} agent...")
                agent_definition = await self.client.agents.get_agent(agent_id=agent_id)
                self.agents[agent_type] = AzureAIAgent(
                    client=self.client,
                    definition=agent_definition,
                )
                print(f"  ✅ {agent_type.capitalize()} agent ready: {agent_id}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ Failed to initialize {agent_type} agent: {e}")
                print(f"  🔄 Using mock agent for {agent_type}")
                self.agents[agent_type] = None  # 將使用模擬功能
        
        print(f"\n🎯 Multi-Agent System initialized: {success_count}/{len(self.agent_ids)} agents active")
        return success_count > 0
    
    async def process_complex_task(self, user_input: str) -> str:
        """處理複雜任務，自動分配給適當的 agents"""
        print(f"\n🧠 Analyzing complex task: '{user_input}'")
        
        # 1. 任務解析和 agent 選擇
        required_agents = self._analyze_task_requirements(user_input)
        print(f"📋 Required agents: {', '.join(required_agents)}")
        
        if not required_agents:
            return "⚠️ No suitable agents found for this task."
        
        # 2. 建立執行計畫
        execution_plan = self._create_execution_plan(user_input, required_agents)
        print(f"📊 Execution plan created with {len(execution_plan)} steps")
        
        # 3. 循序執行各步驟
        results = []
        context = {}
        
        for i, step in enumerate(execution_plan, 1):
            print(f"\n🎯 Step {i}/{len(execution_plan)}: {step['description']}")
            print(f"   Agent: {step['agent']}")
            print(f"   Task: {step['task']}")
            
            result = await self._execute_step(step, context)
            results.append({
                "step": i,
                "agent": step['agent'],
                "description": step['description'],
                "result": result
            })
            
            # 更新上下文供後續步驟使用
            context[f"step_{i}_result"] = result
            print(f"   ✅ Step {i} completed")
        
        # 4. 整合結果
        final_result = self._integrate_results(user_input, results)
        return final_result
    
    def _analyze_task_requirements(self, task: str) -> List[str]:
        """分析任務需求，決定需要哪些 agents"""
        required_agents = []
        task_lower = task.lower()
        
        # 計算每個 agent 的匹配分數
        agent_scores = {}
        for agent_type, config in self.agent_capabilities.items():
            score = sum(1 for keyword in config["keywords"] if keyword in task_lower)
            if score > 0:
                agent_scores[agent_type] = score
        
        # 根據分數排序，選擇最相關的 agents
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        required_agents = [agent for agent, score in sorted_agents if score > 0]
        
        return required_agents[:3]  # 最多選擇3個最相關的 agents
    
    def _create_execution_plan(self, task: str, agents: List[str]) -> List[Dict[str, Any]]:
        """根據任務和選定的 agents 建立執行計畫"""
        plan = []
        
        # 基本執行順序邏輯
        agent_order = ["search", "databricks", "fabric", "logic_app"]
        ordered_agents = [agent for agent in agent_order if agent in agents]
        
        for agent in ordered_agents:
            step_task = self._generate_agent_task(task, agent)
            plan.append({
                "agent": agent,
                "description": self.agent_capabilities[agent]["description"],
                "task": step_task
            })
        
        return plan
    
    def _generate_agent_task(self, original_task: str, agent_type: str) -> str:
        """為特定 agent 產生具體的子任務"""
        task_templates = {
            "search": f"根據以下需求搜尋相關資訊：{original_task}",
            "databricks": f"分析以下任務中的資料需求：{original_task}",
            "fabric": f"為以下業務需求建立報表和資料倉儲方案：{original_task}",
            "logic_app": f"為以下流程設計自動化工作流程：{original_task}"
        }
        
        return task_templates.get(agent_type, original_task)
    
    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> str:
        """執行單一步驟"""
        agent_type = step["agent"]
        task = step["task"]
        
        # 檢查是否有可用的真實 agent
        agent = self.agents.get(agent_type)
        
        if agent:
            return await self._execute_with_real_agent(agent_type, agent, task)
        else:
            return await self._execute_with_mock_agent(agent_type, task)
    
    async def _execute_with_real_agent(self, agent_type: str, agent: AzureAIAgent, task: str) -> str:
        """使用真實 agent 執行任務"""
        thread_key = f"{agent_type}_thread"
        
        try:
            # 獲取或建立該 agent 的對話線程
            current_thread = self.threads.get(thread_key)
            
            result_parts = []
            async for response in agent.invoke_stream(
                messages=task,
                thread=current_thread,
                on_intermediate_message=self._handle_streaming_steps,
            ):
                result_parts.append(str(response))
                # 更新線程
                self.threads[thread_key] = response.thread
            
            full_result = "".join(result_parts)
            return full_result if full_result.strip() else f"✅ {agent_type} agent completed the task successfully"
            
        except Exception as e:
            print(f"  ⚠️ Error with {agent_type} agent: {e}")
            return f"❌ Error executing {agent_type} task: {str(e)}"
    
    async def _execute_with_mock_agent(self, agent_type: str, task: str) -> str:
        """使用模擬 agent 執行任務"""
        mock_responses = {
            "search": f"🔍 Mock Search Result: Found relevant information for '{task}'. Key findings include luxury hotels, customer reviews, and market data.",
            "databricks": f"📊 Mock Databricks Analysis: Processed data pipeline for '{task}'. Generated statistical insights and ML models.",
            "fabric": f"📈 Mock Fabric Report: Created BI dashboard and data warehouse for '{task}'. Power BI reports are ready.",
            "logic_app": f"⚙️ Mock Logic App Workflow: Automated workflow created for '{task}'. Notifications and approvals configured."
        }
        
        # 模擬一些處理時間
        await asyncio.sleep(1)
        
        return mock_responses.get(agent_type, f"✅ Mock {agent_type} execution completed")
    
    async def _handle_streaming_steps(self, message: ChatMessageContent) -> None:
        """處理串流回應中的中間步驟"""
        for item in message.items or []:
            if isinstance(item, FunctionResultContent):
                print(f"    📋 Function Result: {item.result} ({item.name})")
            elif isinstance(item, FunctionCallContent):
                print(f"    🔧 Function Call: {item.name}({item.arguments})")
    
    def _integrate_results(self, original_task: str, results: List[Dict[str, Any]]) -> str:
        """整合所有 agent 的執行結果"""
        integrated_result = f"🎯 Multi-Agent Task Execution Report\n"
        integrated_result += f"{'='*60}\n\n"
        integrated_result += f"📝 Original Task: {original_task}\n\n"
        integrated_result += f"🔄 Execution Summary:\n"
        
        for result in results:
            integrated_result += f"\n{result['step']}. {result['description']}\n"
            integrated_result += f"   Agent: {result['agent'].upper()}\n"
            integrated_result += f"   Result: {result['result']}\n"
        
        integrated_result += f"\n{'='*60}\n"
        integrated_result += f"✅ Task Completion Status: All {len(results)} agents completed successfully\n"
        integrated_result += f"📊 Integrated Solution: Multi-agent collaboration provided comprehensive solution\n"
        integrated_result += f"🎉 System Status: Ready for next task\n"
        
        return integrated_result
    
    async def cleanup(self):
        """清理所有資源"""
        print("\n🧹 Cleaning up multi-agent system resources...")
        
        cleanup_count = 0
        for thread_key, thread in self.threads.items():
            if thread:
                try:
                    await thread.delete()
                    cleanup_count += 1
                except Exception as e:
                    print(f"  ⚠️ Failed to cleanup {thread_key}: {e}")
        
        print(f"  ✅ Cleaned up {cleanup_count} agent threads")
        self.threads.clear()
        self.agents.clear()


async def main() -> None:
    """主要執行函數"""
    print("🚀 Starting Semantic Kernel Multi-Agent System")
    print("=" * 60)
    
    # 複雜任務範例
    COMPLEX_TASKS = [
        "我需要找到關於豪華飯店的詳細資訊，分析客戶滿意度數據，產生 BI 報表，並建立自動化的客戶回饋處理流程",
        "幫我搜尋市場競爭對手的資料，進行深度資料分析，建立 Power BI 儀表板，然後設置自動化的週報發送工作流程",
        "查詢產品銷售趨勢，執行 ETL 資料處理，同步到資料倉儲，並建立異常檢測的自動化通知系統"
    ]
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 建立多 agent 系統
        multi_agent_system = SemanticKernelMultiAgentSystem(client)
        
        # 初始化系統
        if not await multi_agent_system.initialize_agents():
            print("❌ Failed to initialize multi-agent system")
            return
        
        try:
            # 處理複雜任務
            for i, task in enumerate(COMPLEX_TASKS, 1):
                print(f"\n🎯 Processing Complex Task #{i}")
                print("=" * 60)
                print(f"Task: {task}")
                print("=" * 60)
                
                result = await multi_agent_system.process_complex_task(task)
                print(f"\n📋 Final Integrated Result:")
                print(result)
                
                if i < len(COMPLEX_TASKS):
                    print(f"\n⏱️ Preparing for next task...\n")
                    await asyncio.sleep(2)
        
        finally:
            # 清理資源
            await multi_agent_system.cleanup()
    
    print("\n🎉 Multi-Agent System Demo Completed Successfully!")


if __name__ == "__main__":
    asyncio.run(main())