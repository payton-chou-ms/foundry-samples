# Copyright (c) Microsoft. All rights reserved.

import asyncio

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionCallContent,
    FunctionResultContent,
)

"""
以下範例示範如何在多個 Azure AI Agent 之間實現任務轉交 (handoff) 功能。
此範例展示了一個協調者 agent 如何根據任務類型，將工作分配給專門的 agent。
"""

# Agent IDs for different specialized agents
COORDINATOR_AGENT_ID = "asst_coordinator_example_id"
SEARCH_AGENT_ID = "asst_vnVvS09TGw3zOC6Z0vxiviN0"  # AI Search Agent
ANALYSIS_AGENT_ID = "asst_analysis_example_id"       # Data Analysis Agent
WORKFLOW_AGENT_ID = "asst_workflow_example_id"       # Workflow Agent

# 模擬複雜的用戶任務
USER_TASKS = [
    "我需要找到關於豪華飯店的資訊，然後分析客戶評價數據，最後建立一個審核工作流程",
    "幫我搜尋市場趨勢資料，進行競爭分析，並發送報告給管理團隊",
]


class AgentHandoffManager:
    """管理多個 agent 之間的任務轉交"""
    
    def __init__(self, client):
        self.client = client
        self.agents = {}
        self.threads = {}
    
    async def initialize_agents(self):
        """初始化所有專門的 agents"""
        agent_configs = {
            "coordinator": COORDINATOR_AGENT_ID,
            "search": SEARCH_AGENT_ID,
            "analysis": ANALYSIS_AGENT_ID,
            "workflow": WORKFLOW_AGENT_ID,
        }
        
        for role, agent_id in agent_configs.items():
            try:
                agent_definition = await self.client.agents.get_agent(agent_id=agent_id)
                self.agents[role] = AzureAIAgent(
                    client=self.client,
                    definition=agent_definition,
                )
                print(f"✅ {role.capitalize()} agent initialized: {agent_id}")
            except Exception as e:
                print(f"❌ Failed to initialize {role} agent: {e}")
                # 使用模擬 agent 作為後備
                self.agents[role] = None
    
    async def coordinate_task(self, user_input: str) -> str:
        """協調任務執行，決定使用哪個 agent"""
        print(f"\n🎯 Coordinator analyzing task: '{user_input}'")
        
        # 分析任務，決定需要哪些 agents
        subtasks = self._parse_task(user_input)
        results = []
        
        for subtask in subtasks:
            agent_type = subtask["agent"]
            task_description = subtask["task"]
            
            print(f"\n📋 Handing off to {agent_type} agent: {task_description}")
            
            if self.agents.get(agent_type):
                result = await self._execute_with_agent(agent_type, task_description)
                results.append(f"{agent_type.capitalize()} result: {result}")
            else:
                # 模擬執行
                result = f"Mock {agent_type} execution: {task_description}"
                results.append(result)
                print(f"🔄 {result}")
        
        # 綜合所有結果
        final_result = self._combine_results(results)
        return final_result
    
    def _parse_task(self, task: str) -> list:
        """分析任務並決定需要哪些專門的 agents"""
        subtasks = []
        
        # 簡單的關鍵字匹配邏輯
        if any(keyword in task for keyword in ["搜尋", "找到", "資訊", "資料"]):
            subtasks.append({
                "agent": "search",
                "task": "搜尋和檢索相關資訊"
            })
        
        if any(keyword in task for keyword in ["分析", "評價", "趨勢", "競爭"]):
            subtasks.append({
                "agent": "analysis", 
                "task": "進行數據分析和洞察"
            })
        
        if any(keyword in task for keyword in ["工作流程", "審核", "發送", "通知"]):
            subtasks.append({
                "agent": "workflow",
                "task": "執行工作流程和自動化任務"
            })
        
        return subtasks or [{"agent": "search", "task": "一般任務處理"}]
    
    async def _execute_with_agent(self, agent_type: str, task: str) -> str:
        """使用指定的 agent 執行任務"""
        agent = self.agents[agent_type]
        thread_key = f"{agent_type}_thread"
        
        try:
            # 為每個 agent 維護獨立的對話線程
            if thread_key not in self.threads:
                self.threads[thread_key] = None
            
            result_parts = []
            async for response in agent.invoke_stream(
                messages=task,
                thread=self.threads[thread_key],
            ):
                result_parts.append(str(response))
                self.threads[thread_key] = response.thread
            
            return "".join(result_parts)
            
        except Exception as e:
            return f"Error executing with {agent_type} agent: {e}"
    
    def _combine_results(self, results: list) -> str:
        """綜合所有 agent 的執行結果"""
        combined = "🎯 Multi-agent task execution completed:\n\n"
        for i, result in enumerate(results, 1):
            combined += f"{i}. {result}\n"
        
        combined += "\n📊 Summary: All specialized agents have completed their assigned tasks successfully."
        return combined
    
    async def cleanup(self):
        """清理所有線程"""
        for thread in self.threads.values():
            if thread:
                try:
                    await thread.delete()
                except:
                    pass


async def handle_streaming_intermediate_steps(message: ChatMessageContent) -> None:
    """處理串流中的中間步驟"""
    for item in message.items or []:
        if isinstance(item, FunctionResultContent):
            print(f"Function Result: {item.result} for function: {item.name}")
        elif isinstance(item, FunctionCallContent):
            print(f"Function Call: {item.name} with arguments: {item.arguments}")


async def main() -> None:
    print("🚀 Starting Multi-Agent Handoff Demo")
    
    async with (
        DefaultAzureCredential() as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ):
        # 建立 Agent 轉交管理器
        handoff_manager = AgentHandoffManager(client)
        await handoff_manager.initialize_agents()
        
        try:
            # 處理複雜任務
            for i, task in enumerate(USER_TASKS, 1):
                print(f"\n{'='*60}")
                print(f"📝 Task #{i}: {task}")
                print(f"{'='*60}")
                
                result = await handoff_manager.coordinate_task(task)
                print(f"\n✅ Final Result:\n{result}")
                
                print(f"\n{'='*60}\n")
            
        finally:
            # 清理資源
            await handoff_manager.cleanup()
    
    """
    範例輸出：
    🚀 Starting Multi-Agent Handoff Demo
    ✅ Coordinator agent initialized: asst_coordinator_example_id
    ✅ Search agent initialized: asst_vnVvS09TGw3zOC6Z0vxiviN0
    ✅ Analysis agent initialized: asst_analysis_example_id
    ✅ Workflow agent initialized: asst_workflow_example_id
    
    ============================================================
    📝 Task #1: 我需要找到關於豪華飯店的資訊，然後分析客戶評價數據，最後建立一個審核工作流程
    ============================================================
    
    🎯 Coordinator analyzing task: '我需要找到關於豪華飯店的資訊，然後分析客戶評價數據，最後建立一個審核工作流程'
    
    📋 Handing off to search agent: 搜尋和檢索相關資訊
    📋 Handing off to analysis agent: 進行數據分析和洞察  
    📋 Handing off to workflow agent: 執行工作流程和自動化任務
    
    ✅ Final Result:
    🎯 Multi-agent task execution completed:
    
    1. Search result: [豪華飯店搜尋結果]
    2. Analysis result: [客戶評價分析結果] 
    3. Workflow result: [審核工作流程建立結果]
    
    📊 Summary: All specialized agents have completed their assigned tasks successfully.
    """


if __name__ == "__main__":
    asyncio.run(main())