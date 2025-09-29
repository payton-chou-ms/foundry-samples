# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
說明:
    此檔案實現了基於 Semantic Kernel 的多代理程式協作移交（handoff）機制。
    使用 Semantic Kernel 的 ChatCompletionAgent 來替代原本的 Azure AI Projects agents。
    允許不同專業的代理程式之間協作完成複雜任務。
    
使用方式:
    python step4_handoff-semantic-kernel.py

前置條件:
    pip install semantic-kernel azure-identity python-dotenv
    
    設定環境變數：
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_KEY (或使用 DefaultAzureCredential)
    - MODEL_DEPLOYMENT_NAME
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

# Semantic Kernel imports
try:
    from semantic_kernel import Kernel
    from semantic_kernel.agents import ChatCompletionAgent
    from semantic_kernel.agents.runtime import InProcessRuntime
    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
    from semantic_kernel.contents import ChatMessageContent, ChatHistory
    from semantic_kernel.functions import kernel_function, KernelArguments
    from semantic_kernel.planners import FunctionCallingStepwisePlanner
    SEMANTIC_KERNEL_AVAILABLE = True
except ImportError:
    print("Warning: Semantic Kernel packages not available. Running in mock mode.")
    SEMANTIC_KERNEL_AVAILABLE = False
    # Mock classes for testing
    class Kernel: pass
    class ChatCompletionAgent: pass
    class InProcessRuntime: pass
    class AzureChatCompletion: pass
    class ChatMessageContent: pass
    class ChatHistory: pass
    class KernelArguments: pass

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

class SemanticKernelBaseAgent:
    """基於 Semantic Kernel 的基礎代理程式類別"""
    
    def __init__(self, name: str, description: str, instructions: str, plugins: List[Any] = None):
        self.name = name
        self.description = description
        self.instructions = instructions
        self.plugins = plugins or []
        self.agent = None
        self.kernel = None
        self.chat_history = None
        
    async def initialize(self, kernel: Kernel = None) -> None:
        """初始化代理程式"""
        if not SEMANTIC_KERNEL_AVAILABLE:
            logger.warning(f"Semantic Kernel not available, agent '{self.name}' running in mock mode")
            return
            
        # Create or use provided kernel
        if kernel is None:
            self.kernel = Kernel()
            
            # Add Azure OpenAI service
            azure_openai = AzureChatCompletion(
                deployment_name=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o"),
                endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                api_key=os.environ.get("AZURE_OPENAI_API_KEY")
            )
            self.kernel.add_service(azure_openai)
        else:
            self.kernel = kernel
        
        # Add plugins to kernel
        for plugin in self.plugins:
            self.kernel.add_plugin(plugin, plugin.__class__.__name__)
        
        # Create chat completion agent
        self.agent = ChatCompletionAgent(
            service_id="chat-gpt",
            kernel=self.kernel,
            name=self.name,
            instructions=self.instructions,
            description=self.description
        )
        
        # Initialize chat history
        self.chat_history = ChatHistory()
        
        logger.info(f"Semantic Kernel Agent '{self.name}' initialized")
        
    async def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """處理任務並返回結果"""
        if not SEMANTIC_KERNEL_AVAILABLE:
            return {
                "success": True,
                "response": f"Mock response from {self.name}: Task '{task[:50]}...' processed successfully",
                "agent": self.name,
                "conversation_id": "mock_conversation_id"
            }
            
        if not self.agent:
            raise RuntimeError(f"Agent '{self.name}' not initialized")
        
        try:
            # Add context to the task if provided
            full_task = task
            if context:
                context_str = json.dumps(context, indent=2, ensure_ascii=False)
                full_task = f"{task}\n\n相關上下文信息：\n{context_str}"
            
            # Add user message to chat history
            self.chat_history.add_user_message(full_task)
            
            # Get response from agent
            async for response in self.agent.invoke(self.chat_history):
                if response.role.label == "assistant":
                    # Add assistant response to history
                    self.chat_history.add_message(response)
                    
                    return {
                        "success": True,
                        "response": response.content,
                        "agent": self.name,
                        "conversation_id": f"sk_{self.name}_{len(self.chat_history)}"
                    }
            
            return {
                "success": False,
                "error": "No response received from agent",
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
        logger.info(f"Semantic Kernel Agent '{self.name}' cleanup completed")

class SemanticKernelOrchestrator:
    """基於 Semantic Kernel 的移交協調器，管理多代理程式之間的協作"""
    
    def __init__(self):
        self.agents: Dict[str, SemanticKernelBaseAgent] = {}
        self.handoff_history: List[HandoffRequest] = []
        self.kernel = None
        self.runtime = None
        
    async def initialize(self):
        """初始化協調器和運行時"""
        if not SEMANTIC_KERNEL_AVAILABLE:
            logger.warning("Semantic Kernel not available, orchestrator running in mock mode")
            return
            
        # Create shared kernel
        self.kernel = Kernel()
        
        # Add Azure OpenAI service
        azure_openai = AzureChatCompletion(
            deployment_name=os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o"),
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY")
        )
        self.kernel.add_service(azure_openai)
        
        # Create and start runtime
        self.runtime = InProcessRuntime()
        self.runtime.start()
        
        logger.info("Semantic Kernel Orchestrator initialized")
    
    def register_agent(self, agent: SemanticKernelBaseAgent):
        """註冊代理程式"""
        self.agents[agent.name] = agent
        logger.info(f"Registered Semantic Kernel agent: {agent.name}")
    
    async def initialize_all_agents(self):
        """初始化所有代理程式"""
        for agent in self.agents.values():
            await agent.initialize(self.kernel)
    
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
            logger.info(f"Processing task with Semantic Kernel agent: {current_agent.name}")
            
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
            
        # Stop runtime
        if self.runtime:
            await self.runtime.stop_when_idle()
    
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
    print("This module provides the Semantic Kernel handoff infrastructure for the multi-agent system.")
    print("Please use multi_agent_system_sk.py to run the complete Semantic Kernel-based system.")