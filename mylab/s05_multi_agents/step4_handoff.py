# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此檔案實現了多代理程式協作的移交（handoff）機制。
    允許不同專業的代理程式之間協作完成複雜任務。
    
使用方式:
    python step4_handoff.py

前置條件:
    pip install azure-ai-projects azure-identity python-dotenv azure-search-documents
    databricks-sdk azure-mgmt-logic requests
    
    設定環境變數：
    - PROJECT_ENDPOINT
    - MODEL_DEPLOYMENT_NAME
    - 各個代理程式所需的特定環境變數
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Azure imports - conditional to support testing without Azure dependencies
try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    from azure.ai.agents.models import ToolSet, FunctionTool
    AZURE_AVAILABLE = True
except ImportError:
    print("Warning: Azure AI packages not available. Running in mock mode.")
    AZURE_AVAILABLE = False
    # Mock classes for testing
    class AIProjectClient: pass
    class DefaultAzureCredential: pass
    class ToolSet: pass
    class FunctionTool: pass

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HandoffType(Enum):
    """移交類型定義"""
    FORWARD = "forward"  # 轉發給特定代理
    ESCALATE = "escalate"  # 升級給更專業的代理
    COLLABORATE = "collaborate"  # 多代理協作
    COMPLETE = "complete"  # 任務完成

@dataclass
class HandoffRequest:
    """移交請求的數據結構"""
    from_agent: str
    to_agent: Optional[str]
    handoff_type: HandoffType
    task_description: str
    context: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1-10, 10為最高優先級
    
class BaseAgent:
    """基礎代理程式類別"""
    
    def __init__(self, name: str, description: str, instructions: str, tools: List[Any] = None):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.tools = tools or []
        self.agent = None
        self.thread = None
        self.project_client = None
        
    async def initialize(self, project_client: AIProjectClient) -> None:
        """初始化代理程式"""
        if not AZURE_AVAILABLE:
            logger.warning(f"Azure not available, agent '{self.name}' running in mock mode")
            return
            
        self.project_client = project_client
        
        # Create toolset if tools are provided
        toolset = None
        if self.tools:
            functions = FunctionTool(functions=set(self.tools))
            toolset = ToolSet()
            toolset.add(functions)
            project_client.agents.enable_auto_function_calls(toolset)
        
        # Create the agent
        self.agent = project_client.agents.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name=self.name,
            instructions=self.instructions,
            toolset=toolset
        )
        
        # Create a thread for conversation
        self.thread = project_client.agents.threads.create()
        
        logger.info(f"Agent '{self.name}' initialized with ID: {self.agent.id}")
        
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理任務並返回結果"""
        if not AZURE_AVAILABLE:
            return {
                "success": True,
                "response": f"Mock response from {self.name}: Task '{task[:50]}...' processed successfully",
                "agent": self.name,
                "run_id": "mock_run_id"
            }
            
        if not self.agent or not self.thread:
            raise RuntimeError(f"Agent '{self.name}' not initialized")
        
        try:
            # Add context to the task if provided
            full_task = task
            if context:
                context_str = json.dumps(context, indent=2, ensure_ascii=False)
                full_task = f"{task}\n\n相關上下文信息：\n{context_str}"
            
            # Create message
            message = self.project_client.agents.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=full_task
            )
            
            # Process the task
            run = self.project_client.agents.runs.create_and_process(
                thread_id=self.thread.id,
                agent_id=self.agent.id
            )
            
            if run.status == "completed":
                # Get the response
                messages = self.project_client.agents.messages.list(
                    thread_id=self.thread.id,
                    order="desc",
                    limit=1
                )
                
                message_list = list(messages)
                if message_list:
                    latest_message = message_list[0]
                    if latest_message.role == "assistant":
                        response_text = ""
                        if latest_message.content:
                            for content in latest_message.content:
                                if hasattr(content, 'text') and content.text:
                                    if hasattr(content.text, 'value'):
                                        response_text += content.text.value
                        
                        return {
                            "success": True,
                            "response": response_text,
                            "agent": self.name,
                            "run_id": run.id
                        }
            
            return {
                "success": False,
                "error": f"Task processing failed with status: {run.status}",
                "agent": self.name
            }
            
        except Exception as e:
            logger.error(f"Error processing task in agent '{self.name}': {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def should_handoff(self, task: str, context: Dict[str, Any] = None) -> Optional[HandoffRequest]:
        """判斷是否需要移交給其他代理程式"""
        # 基礎類別默認不移交，子類別可以重寫此方法
        return None
    
    async def cleanup(self):
        """清理資源"""
        if AZURE_AVAILABLE and self.agent and self.project_client:
            try:
                self.project_client.agents.delete_agent(self.agent.id)
                logger.info(f"Agent '{self.name}' cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up agent '{self.name}': {str(e)}")
        else:
            logger.info(f"Agent '{self.name}' cleanup skipped (mock mode)")

class HandoffOrchestrator:
    """移交協調器，管理多代理程式之間的協作"""
    
    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client
        self.agents: Dict[str, BaseAgent] = {}
        self.handoff_history: List[HandoffRequest] = []
        
    def register_agent(self, agent: BaseAgent):
        """註冊代理程式"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    async def initialize_all_agents(self):
        """初始化所有代理程式"""
        for agent in self.agents.values():
            await agent.initialize(self.project_client)
    
    async def execute_task(self, task: str, initial_agent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """執行任務，支援代理程式間移交"""
        if initial_agent not in self.agents:
            return {
                "success": False,
                "error": f"Agent '{initial_agent}' not found"
            }
        
        current_agent = self.agents[initial_agent]
        execution_history = []
        max_handoffs = 10  # 防止無限循環
        handoff_count = 0
        
        current_task = task
        current_context = context or {}
        
        while handoff_count < max_handoffs:
            logger.info(f"Processing task with agent: {current_agent.name}")
            
            # Process task with current agent
            result = await current_agent.process_task(current_task, current_context)
            execution_history.append({
                "agent": current_agent.name,
                "task": current_task,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            if not result.get("success"):
                break
            
            # Check if handoff is needed
            handoff_request = current_agent.should_handoff(current_task, current_context)
            if not handoff_request:
                # Task completed, no handoff needed
                break
            
            # Record handoff
            self.handoff_history.append(handoff_request)
            handoff_count += 1
            
            if handoff_request.handoff_type == HandoffType.COMPLETE:
                break
            elif handoff_request.handoff_type in [HandoffType.FORWARD, HandoffType.ESCALATE]:
                if handoff_request.to_agent not in self.agents:
                    logger.error(f"Target agent '{handoff_request.to_agent}' not found")
                    break
                
                current_agent = self.agents[handoff_request.to_agent]
                current_task = handoff_request.task_description
                current_context.update(handoff_request.context)
            elif handoff_request.handoff_type == HandoffType.COLLABORATE:
                # 協作模式，需要特殊處理
                collab_result = await self._handle_collaboration(handoff_request)
                execution_history.append(collab_result)
                break
        
        return {
            "success": len(execution_history) > 0 and execution_history[-1]["result"].get("success", False),
            "execution_history": execution_history,
            "handoff_count": handoff_count,
            "final_agent": current_agent.name if handoff_count < max_handoffs else None
        }
    
    async def _handle_collaboration(self, handoff_request: HandoffRequest) -> Dict[str, Any]:
        """處理協作請求"""
        # 這裡可以實現多代理協作邏輯
        # 簡化版本：依序執行多個代理
        collaboration_results = []
        
        # 假設 to_agent 包含多個代理名稱，用逗號分隔
        if handoff_request.to_agent:
            agent_names = handoff_request.to_agent.split(",")
            for agent_name in agent_names:
                agent_name = agent_name.strip()
                if agent_name in self.agents:
                    agent = self.agents[agent_name]
                    result = await agent.process_task(
                        handoff_request.task_description,
                        handoff_request.context
                    )
                    collaboration_results.append({
                        "agent": agent_name,
                        "result": result
                    })
        
        return {
            "agent": "Collaboration",
            "task": handoff_request.task_description,
            "result": {
                "success": True,
                "response": "Collaboration completed",
                "collaboration_results": collaboration_results
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def cleanup_all_agents(self):
        """清理所有代理程式"""
        for agent in self.agents.values():
            await agent.cleanup()
    
    def get_handoff_history(self) -> List[Dict[str, Any]]:
        """獲取移交歷史記錄"""
        return [
            {
                "from_agent": req.from_agent,
                "to_agent": req.to_agent,
                "handoff_type": req.handoff_type.value,
                "task_description": req.task_description,
                "timestamp": req.timestamp.isoformat(),
                "priority": req.priority
            }
            for req in self.handoff_history
        ]

# 輔助函數
def create_handoff_request(
    from_agent: str,
    to_agent: Optional[str],
    handoff_type: HandoffType,
    task_description: str,
    context: Dict[str, Any] = None,
    priority: int = 5
) -> HandoffRequest:
    """創建移交請求"""
    return HandoffRequest(
        from_agent=from_agent,
        to_agent=to_agent,
        handoff_type=handoff_type,
        task_description=task_description,
        context=context or {},
        timestamp=datetime.now(),
        priority=priority
    )

if __name__ == "__main__":
    print("This module provides the handoff infrastructure for the multi-agent system.")
    print("Please use multi_agent_system.py to run the complete system.")