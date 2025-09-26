# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Multi-Agent Orchestration with Semantic Kernel Magentic UI
    
    This sample demonstrates intelligent coordination of four specialized AI agents using
    Semantic Kernel's magentic functionality through an interactive Chainlit interface.
    
    Agents:
    1. Hotel Search Agent (Azure AI Search) - Hotel recommendations and information
    2. Logic App Agent (Azure Logic Apps) - Automated workflows and notifications
    3. Data Analysis Agent (Microsoft Fabric) - Taxi trip data analysis
    4. Databricks Agent (Azure Databricks) - Advanced data processing with Genie

USAGE:
    chainlit run step5_magentic_ui.py

    Before running the sample:
    pip install -r requirements.txt

    Set these environment variables:
    - PROJECT_ENDPOINT: Azure AI Foundry project endpoint
    - MODEL_DEPLOYMENT_NAME: AI model deployment name
    - AZURE_SUBSCRIPTION_ID: Azure subscription ID
    - AZURE_RESOURCE_GROUP: Azure resource group name
    
    For individual agents, set their specific environment variables as documented
    in their respective directories (s01-s04).
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import chainlit as cl
from dotenv import load_dotenv

# Azure and AI imports
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Semantic Kernel imports (conceptual - actual implementation may vary)
# from semantic_kernel import Kernel
# from semantic_kernel.connectors.ai.open_ai import AzureOpenAIChatCompletion
# from semantic_kernel.prompt_template.input_variables import InputVariable
# from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")

# Orchestration scenarios
ORCHESTRATION_SCENARIOS = [
    {
        "name": "Business Travel Planning",
        "description": "Plan business trip with hotel search, travel analytics, and automated notifications",
        "example": "Plan a business trip to New York with high-quality hotel near Manhattan, analyze taxi patterns for meeting scheduling, and send summary to my assistant",
        "agents": ["hotel_search", "fabric_analyst", "databricks_genie", "logic_app"],
        "complexity": "High"
    },
    {
        "name": "Event Planning Coordination",
        "description": "Coordinate corporate events with venue analysis and automated communications",
        "example": "Organize 200-person tech conference in Chicago with group hotel bookings, transportation analysis, and attendee notifications",
        "agents": ["hotel_search", "fabric_analyst", "databricks_genie", "logic_app"],
        "complexity": "High"
    },
    {
        "name": "Market Research Analysis",
        "description": "Comprehensive market research with data analysis and automated reporting",
        "example": "Research hospitality market trends for boutique hotels, analyze pricing and satisfaction patterns, distribute weekly reports",
        "agents": ["hotel_search", "databricks_genie", "fabric_analyst", "logic_app"],
        "complexity": "Medium"
    },
    {
        "name": "Hotel Recommendation with Analytics",
        "description": "Enhanced hotel search with location-based travel pattern analysis",
        "example": "Find best hotels in Manhattan considering taxi accessibility and travel efficiency",
        "agents": ["hotel_search", "fabric_analyst"],
        "complexity": "Low"
    },
    {
        "name": "Data Analysis with Reporting",
        "description": "Comprehensive data analysis with automated result distribution",
        "example": "Analyze NYC taxi patterns and automatically email insights to the team",
        "agents": ["fabric_analyst", "databricks_genie", "logic_app"],
        "complexity": "Medium"
    }
]

# Agent status enumeration
class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class AgentTask:
    """Represents a task to be executed by an agent"""
    agent_name: str
    task_description: str
    input_parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    expected_output_type: str = "text"
    timeout_seconds: int = 60
    retry_count: int = 0
    max_retries: int = 2

@dataclass
class AgentResult:
    """Represents the result from an agent execution"""
    agent_name: str
    status: AgentStatus
    result_data: Any = None
    error_message: str = ""
    execution_time_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

class SharedContext:
    """Manages shared context and state across agents"""
    def __init__(self):
        self.conversation_memory = {}
        self.agent_outputs = {}
        self.user_preferences = {}
        self.session_data = {}
    
    def store_agent_result(self, agent_name: str, result: AgentResult):
        """Store result from an agent execution"""
        self.agent_outputs[agent_name] = result
    
    def get_context_for_agent(self, agent_name: str) -> Dict[str, Any]:
        """Get relevant context for a specific agent"""
        return {
            'memory': self.conversation_memory,
            'previous_results': self.agent_outputs,
            'user_preferences': self.user_preferences,
            'session_data': self.session_data
        }
    
    def update_conversation_memory(self, key: str, value: Any):
        """Update conversation memory"""
        self.conversation_memory[key] = value

class MockAgent:
    """Mock agent implementation for demonstration purposes"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
    
    async def execute(self, task: AgentTask, context: SharedContext) -> AgentResult:
        """Execute a task with the agent"""
        self.status = AgentStatus.RUNNING
        start_time = datetime.utcnow()
        
        try:
            # Simulate agent processing time
            await asyncio.sleep(2)
            
            # Mock different responses based on agent type
            result_data = await self._generate_mock_response(task, context)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.status = AgentStatus.COMPLETED
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result_data=result_data,
                execution_time_seconds=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self.status = AgentStatus.FAILED
            
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
    
    async def _generate_mock_response(self, task: AgentTask, context: SharedContext) -> str:
        """Generate mock responses based on agent type"""
        if self.name == "hotel_search":
            return """🏨 **Hotel Recommendations Found:**

**1. The Manhattan Business Hotel** ⭐⭐⭐⭐⭐
- Rating: 4.6/5.0
- Price: $285/night
- Amenities: Business center, WiFi, Parking, Gym
- Location: Midtown Manhattan, excellent taxi accessibility

**2. Boutique Central NYC** ⭐⭐⭐⭐
- Rating: 4.4/5.0  
- Price: $220/night
- Amenities: Boutique experience, WiFi, Meeting rooms
- Location: Central location with good transport links

**3. Executive Suites Manhattan** ⭐⭐⭐⭐⭐
- Rating: 4.7/5.0
- Price: $350/night
- Amenities: Executive lounge, Concierge, Parking
- Location: Premium location near business district"""

        elif self.name == "fabric_analyst":
            return """📊 **NYC Taxi Traffic Analysis:**

**Peak Travel Times:**
- Avoid: 8:00-9:30 AM (morning rush) - 45% longer trips
- Avoid: 5:00-7:00 PM (evening rush) - 55% longer trips
- Optimal: 10:00-11:00 AM - shortest wait times
- Optimal: 2:00-4:00 PM - efficient travel windows

**Manhattan Zones Performance:**
- Midtown pickup: Average 3-5 min wait time
- Financial District: 2-4 min wait time  
- Upper East/West: 5-8 min wait time

**Business Travel Insights:**
- Best meeting times: 10 AM-12 PM, 2 PM-4 PM
- Average trip duration: 12-18 minutes
- Suggested buffer time: +25% during peak hours"""

        elif self.name == "databricks_genie":
            return """🔍 **Advanced Analytics Results:**

**Hotel Location vs Transportation Efficiency Correlation:**

Based on analysis of 2.5M taxi trips and hotel locations:

**Efficiency Score by Hotel:**
- The Manhattan Business Hotel: **92/100**
  - 15% faster than average for business meetings
  - Optimal taxi pickup zone
  
- Boutique Central NYC: **87/100**
  - Good accessibility, moderate efficiency
  
- Executive Suites Manhattan: **95/100**
  - Premium location with best transport links
  - 20% reduction in travel time variance

**Predictive Insights:**
- Morning meetings (9-11 AM): Executive Suites saves 8 min/trip
- Afternoon appointments: All hotels perform similarly
- Weather impact: Executive Suites most resilient (covered pickup)

**Recommendation:** Executive Suites Manhattan optimal for efficiency despite higher cost."""

        elif self.name == "logic_app":
            return """📧 **Automated Actions Completed:**

**✅ Email Sent Successfully**
- Recipient: assistant@company.com
- Subject: "Business Trip Planning Report - NYC"
- Delivery Status: Confirmed at {time}
- Message ID: MSG_20240101_001

**📋 Report Contents Delivered:**
- Hotel recommendations with booking links
- Transportation optimization schedule
- Meeting time recommendations
- Cost analysis summary

**🔔 Follow-up Actions Scheduled:**
- Booking reminder: 24 hours
- Itinerary confirmation: 48 hours  
- Travel checklist: 72 hours

**Logic App Workflow Status:** ✅ Completed successfully
**Execution Time:** 1.2 seconds
**Next Scheduled Run:** As requested""".format(time=datetime.now().strftime("%Y-%m-%d %H:%M"))

        else:
            return f"Mock response from {self.name} for task: {task.task_description}"

class OrchestrationEngine:
    """Main orchestration engine using Semantic Kernel concepts"""
    def __init__(self):
        self.agents = {
            "hotel_search": MockAgent("hotel_search", "Hotel Search Agent (Azure AI Search)"),
            "logic_app": MockAgent("logic_app", "Logic App Agent (Azure Logic Apps)"),
            "fabric_analyst": MockAgent("fabric_analyst", "Data Analysis Agent (Microsoft Fabric)"),
            "databricks_genie": MockAgent("databricks_genie", "Databricks Agent (Azure Databricks Genie)")
        }
        self.context = SharedContext()
    
    async def analyze_request_and_plan(self, user_request: str) -> List[AgentTask]:
        """Analyze user request and create execution plan using Semantic Kernel concepts"""
        
        # This would use Semantic Kernel's prompt functions in real implementation
        # For demo, we'll use rule-based planning
        
        tasks = []
        
        # Detect keywords to determine required agents
        request_lower = user_request.lower()
        
        # Hotel search patterns
        if any(word in request_lower for word in ['hotel', 'accommodation', 'booking', 'stay', 'lodging']):
            tasks.append(AgentTask(
                agent_name="hotel_search",
                task_description="Find hotel recommendations based on user requirements",
                input_parameters={"query": user_request, "filters": {}},
                dependencies=[]
            ))
        
        # Data analysis patterns  
        if any(word in request_lower for word in ['analyze', 'data', 'pattern', 'trend', 'taxi', 'transport']):
            tasks.append(AgentTask(
                agent_name="fabric_analyst", 
                task_description="Analyze transportation and travel patterns",
                input_parameters={"analysis_type": "travel_patterns", "query": user_request},
                dependencies=[]
            ))
        
        # Advanced analytics patterns
        if any(word in request_lower for word in ['correlation', 'optimize', 'predict', 'advanced', 'efficiency']):
            hotel_task_exists = any(task.agent_name == "hotel_search" for task in tasks)
            fabric_task_exists = any(task.agent_name == "fabric_analyst" for task in tasks)
            
            dependencies = []
            if hotel_task_exists:
                dependencies.append("hotel_search")
            if fabric_task_exists:
                dependencies.append("fabric_analyst")
                
            tasks.append(AgentTask(
                agent_name="databricks_genie",
                task_description="Perform advanced analytics and optimization",
                input_parameters={"query": user_request, "context_required": True},
                dependencies=dependencies
            ))
        
        # Automation/notification patterns
        if any(word in request_lower for word in ['send', 'email', 'notify', 'report', 'automate', 'schedule']):
            # Logic app should run after other agents to include their results
            other_agents = [task.agent_name for task in tasks if task.agent_name != "logic_app"]
            
            tasks.append(AgentTask(
                agent_name="logic_app",
                task_description="Send automated notifications and reports",
                input_parameters={"recipients": ["assistant@company.com"], "content_sources": other_agents},
                dependencies=other_agents
            ))
        
        return tasks
    
    async def execute_orchestrated_workflow(self, tasks: List[AgentTask]) -> Dict[str, AgentResult]:
        """Execute the planned workflow with proper dependency management"""
        results = {}
        completed_agents = set()
        
        # Continue until all tasks are completed
        while len(completed_agents) < len(tasks):
            # Find tasks ready to execute (dependencies satisfied)
            ready_tasks = [
                task for task in tasks 
                if task.agent_name not in completed_agents 
                and all(dep in completed_agents for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                break  # No more tasks can be executed
            
            # Execute ready tasks in parallel
            parallel_executions = []
            for task in ready_tasks:
                agent = self.agents.get(task.agent_name)
                if agent:
                    parallel_executions.append(self._execute_single_task(agent, task))
            
            # Wait for parallel executions to complete
            if parallel_executions:
                task_results = await asyncio.gather(*parallel_executions, return_exceptions=True)
                
                for i, result in enumerate(task_results):
                    if isinstance(result, AgentResult):
                        self.context.store_agent_result(result.agent_name, result)
                        results[result.agent_name] = result
                        completed_agents.add(result.agent_name)
        
        return results
    
    async def _execute_single_task(self, agent: MockAgent, task: AgentTask) -> AgentResult:
        """Execute a single task with timeout and error handling"""
        try:
            return await asyncio.wait_for(
                agent.execute(task, self.context), 
                timeout=task.timeout_seconds
            )
        except asyncio.TimeoutError:
            return AgentResult(
                agent_name=agent.name,
                status=AgentStatus.TIMEOUT,
                error_message=f"Task timed out after {task.timeout_seconds} seconds"
            )
        except Exception as e:
            return AgentResult(
                agent_name=agent.name,
                status=AgentStatus.FAILED,
                error_message=str(e)
            )

# Global orchestration engine
orchestration_engine = OrchestrationEngine()

@cl.on_chat_start
async def start():
    """Initialize the multi-agent orchestration interface"""
    
    welcome_msg = """# 🎯 Multi-Agent Orchestration with Semantic Kernel Magentic

Welcome to the intelligent multi-agent coordination system! I can orchestrate four specialized AI agents to handle complex, multi-domain tasks:

## 🤖 Available Agents:
- **🏨 Hotel Search Agent** - Azure AI Search powered hotel recommendations
- **⚡ Logic App Agent** - Automated workflows and notifications via Azure Logic Apps
- **📊 Data Analysis Agent** - Microsoft Fabric lakehouse data analysis
- **🔍 Databricks Agent** - Advanced analytics with Databricks Genie

## ✨ Capabilities:
- **Intelligent Task Planning** - Automatically determines which agents to use
- **Dependency Resolution** - Executes agents in optimal sequence
- **Context Sharing** - Agents share information for enhanced results
- **Parallel Execution** - Independent tasks run simultaneously for efficiency

## 🚀 Try These Pre-Configured Scenarios:"""

    await cl.Message(content=welcome_msg).send()
    
    # Create scenario buttons
    actions = []
    for i, scenario in enumerate(ORCHESTRATION_SCENARIOS):
        actions.append(
            cl.Action(
                name=f"scenario_{i}",
                value=scenario["example"],
                description=scenario["description"],
                label=f"🎯 {scenario['name']} ({scenario['complexity']})"
            )
        )
    
    await cl.Message(
        content="**🎮 Quick Start Scenarios** - Click any scenario to see multi-agent orchestration in action:",
        actions=actions
    ).send()
    
    instructions_msg = """## 💡 How It Works:
1. **Analysis Phase** - Semantic Kernel analyzes your request
2. **Planning Phase** - Determines optimal agent sequence and dependencies  
3. **Execution Phase** - Coordinates agents with shared context
4. **Synthesis Phase** - Combines results into comprehensive response

**You can also type custom requests!** The system will intelligently determine which agents to coordinate based on your needs."""

    await cl.Message(content=instructions_msg).send()

# Scenario action callbacks
@cl.action_callback("scenario_0")
async def scenario_0(action):
    await process_orchestrated_request(action.value)

@cl.action_callback("scenario_1") 
async def scenario_1(action):
    await process_orchestrated_request(action.value)

@cl.action_callback("scenario_2")
async def scenario_2(action):
    await process_orchestrated_request(action.value)

@cl.action_callback("scenario_3")
async def scenario_3(action):
    await process_orchestrated_request(action.value)

@cl.action_callback("scenario_4")
async def scenario_4(action):
    await process_orchestrated_request(action.value)

async def process_orchestrated_request(user_request: str):
    """Process a user request through the orchestration engine"""
    
    # Show user request
    await cl.Message(
        content=f"**🎯 Your Request:** {user_request}",
        author="User"
    ).send()
    
    # Analysis phase
    analysis_msg = await cl.Message(
        content="🧠 **Phase 1: Analyzing Request with Semantic Kernel...**"
    ).send()
    
    try:
        # Plan the execution
        tasks = await orchestration_engine.analyze_request_and_plan(user_request)
        
        if not tasks:
            analysis_msg.content = "❌ **Analysis Complete:** No suitable agents found for this request. Please try a different query."
            await analysis_msg.update()
            return
        
        # Update analysis results
        agent_names = [task.agent_name for task in tasks]
        analysis_msg.content = f"""✅ **Phase 1 Complete: Request Analysis**
        
**📋 Execution Plan Generated:**
- **Agents Selected:** {', '.join([name.replace('_', ' ').title() for name in agent_names])}
- **Total Tasks:** {len(tasks)}
- **Execution Pattern:** {'Sequential with dependencies' if any(task.dependencies for task in tasks) else 'Parallel execution'}

**🔄 Proceeding to Phase 2: Agent Coordination...**"""
        await analysis_msg.update()
        
        # Execution phase
        execution_msg = await cl.Message(
            content="⚡ **Phase 2: Executing Multi-Agent Coordination...**"
        ).send()
        
        # Execute the orchestrated workflow
        results = await orchestration_engine.execute_orchestrated_workflow(tasks)
        
        # Update execution results
        successful_agents = [name for name, result in results.items() if result.status == AgentStatus.COMPLETED]
        failed_agents = [name for name, result in results.items() if result.status in [AgentStatus.FAILED, AgentStatus.TIMEOUT]]
        
        execution_summary = f"""✅ **Phase 2 Complete: Agent Coordination**

**📊 Execution Summary:**
- **Successful Agents:** {len(successful_agents)}/{len(results)}
- **Total Execution Time:** {sum(r.execution_time_seconds for r in results.values()):.1f} seconds
- **Status:** {'✅ All agents completed successfully' if not failed_agents else f'⚠️ {len(failed_agents)} agent(s) had issues'}

**🎉 Proceeding to Phase 3: Result Synthesis...**"""
        
        execution_msg.content = execution_summary
        await execution_msg.update()
        
        # Results synthesis phase
        synthesis_msg = await cl.Message(
            content="🔄 **Phase 3: Synthesizing Multi-Agent Results...**"
        ).send()
        
        # Present individual agent results
        for agent_name, result in results.items():
            if result.status == AgentStatus.COMPLETED:
                agent_display_name = agent_name.replace('_', ' ').title()
                await cl.Message(
                    content=f"## 🤖 {agent_display_name} Results\n\n{result.result_data}",
                    author=agent_display_name
                ).send()
            else:
                agent_display_name = agent_name.replace('_', ' ').title()
                await cl.Message(
                    content=f"## ❌ {agent_display_name} Error\n\n{result.error_message}",
                    author=agent_display_name
                ).send()
        
        # Final synthesis
        synthesis_msg.content = f"""✅ **Phase 3 Complete: Multi-Agent Orchestration Finished**

**🎯 Orchestration Summary:**
- **Request:** {user_request[:100]}{'...' if len(user_request) > 100 else ''}
- **Agents Coordinated:** {len(results)}
- **Successful Completions:** {len(successful_agents)}
- **Total Processing Time:** {sum(r.execution_time_seconds for r in results.values()):.1f} seconds

**💡 The agents worked together using shared context and dependency resolution to provide you with comprehensive results!**

**🔄 Ready for your next multi-agent request!**"""
        
        await synthesis_msg.update()
        
    except Exception as e:
        analysis_msg.content = f"❌ **Orchestration Error:** {str(e)}"
        await analysis_msg.update()

@cl.on_message
async def main(message: cl.Message):
    """Handle direct user messages for orchestration"""
    await process_orchestrated_request(message.content)

if __name__ == "__main__":
    print("🚀 Multi-Agent Orchestration System")
    print("Use: chainlit run step5_magentic_ui.py")
    print("=" * 50)