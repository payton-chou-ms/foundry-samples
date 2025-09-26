# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Magentic Runtime module for the Magentic One team system.
Orchestrates 4 agents using Semantic Kernel's MagenticOrchestration framework.
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Semantic Kernel imports for Magentic orchestration
from semantic_kernel.agents import (
    Agent,
    AzureAIAgent, 
    AzureAIAgentSettings,
    MagenticOrchestration,
    StandardMagenticManager,
)
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.functions import kernel_function

from ..config.settings import MagenticTeamSettings
from ..agents import HotelAgent, TaxiFabricAgent, TaxiGenieAgent, EmailLogicAppsAgent
from .task_graph import TaskGraphBuilder, TaskGraph, TaskType, TaskStatus, ConflictResolutionStrategy


class MagenticTeamPlugin:
    """
    Plugin that provides tools for the Magentic manager to coordinate agents.
    """
    
    def __init__(self, team_runtime: 'MagenticTeamRuntime'):
        self.team_runtime = team_runtime
    
    @kernel_function
    def search_hotels(self, query: str, location: str = "", requirements: str = "") -> str:
        """Search for hotels based on user requirements."""
        try:
            result = asyncio.run(self.team_runtime.execute_hotel_task(query, location, requirements))
            return f"Hotel search completed: {result.get('summary', 'No results')}"
        except Exception as e:
            return f"Hotel search failed: {str(e)}"
    
    @kernel_function  
    def analyze_taxi_data_fabric(self, analysis_type: str, parameters: str = "") -> str:
        """Analyze taxi data using Microsoft Fabric lakehouse."""
        try:
            result = asyncio.run(self.team_runtime.execute_taxi_fabric_task(analysis_type, parameters))
            return f"Fabric taxi analysis completed: {result.get('summary', 'No results')}"
        except Exception as e:
            return f"Fabric taxi analysis failed: {str(e)}"
    
    @kernel_function
    def analyze_taxi_data_genie(self, query: str, context: str = "") -> str:
        """Analyze taxi data using Databricks Genie."""
        try:
            result = asyncio.run(self.team_runtime.execute_taxi_genie_task(query, context))
            return f"Genie taxi analysis completed: {result.get('summary', 'No results')}"
        except Exception as e:
            return f"Genie taxi analysis failed: {str(e)}"
    
    @kernel_function
    def send_email(self, recipient: str, subject: str, body: str) -> str:
        """Send email via Logic Apps."""
        try:
            result = asyncio.run(self.team_runtime.execute_email_task(recipient, subject, body))
            return f"Email sent successfully: {result.get('summary', 'No confirmation')}"
        except Exception as e:
            return f"Email sending failed: {str(e)}"
    
    @kernel_function
    def resolve_data_conflicts(self, fabric_data: str, genie_data: str) -> str:
        """Resolve conflicts between Fabric and Genie data."""
        try:
            result = self.team_runtime.resolve_conflicts(fabric_data, genie_data)
            return f"Data conflict resolution: {result.get('summary', 'No resolution')}"
        except Exception as e:
            return f"Conflict resolution failed: {str(e)}"


class MagenticTeamRuntime:
    """
    Main runtime for the Magentic One team system.
    Orchestrates Hotel, Taxi (Fabric & Genie), and Email agents using Semantic Kernel.
    """
    
    def __init__(self, settings: MagenticTeamSettings):
        """Initialize the Magentic team runtime."""
        self.settings = settings
        self.agents = {}
        self.runtime: Optional[InProcessRuntime] = None
        self.magentic_orchestration: Optional[MagenticOrchestration] = None
        self.project_client: Optional[AIProjectClient] = None
        self.agent_response_callback = self._default_response_callback
        
        # Individual agent instances
        self.hotel_agent = HotelAgent(settings.hotel)
        self.taxi_fabric_agent = TaxiFabricAgent(settings.taxi_fabric)
        self.taxi_genie_agent = TaxiGenieAgent(settings.taxi_genie)
        self.email_agent = EmailLogicAppsAgent(settings.email)
        
    def _default_response_callback(self, message: ChatMessageContent) -> None:
        """Default callback to observe agent messages."""
        print(f"**{message.name}**\n{message.content}")
    
    def set_response_callback(self, callback):
        """Set custom response callback for agent messages."""
        self.agent_response_callback = callback
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize all agents and the Magentic orchestration system.
        
        Returns:
            Dict with initialization status and agent information
        """
        try:
            # Initialize individual agents
            agents_status = {}
            
            # Hotel Agent
            hotel_result = self.hotel_agent.create()
            agents_status['hotel'] = hotel_result
            
            # Taxi Fabric Agent  
            fabric_result = self.taxi_fabric_agent.create()
            agents_status['taxi_fabric'] = fabric_result
            
            # Taxi Genie Agent
            genie_result = self.taxi_genie_agent.create()
            agents_status['taxi_genie'] = genie_result
            
            # Email Agent
            email_result = self.email_agent.create()
            agents_status['email'] = email_result
            
            # Check if all critical agents initialized successfully
            failed_agents = [name for name, status in agents_status.items() if not status.get('success', False)]
            
            if failed_agents:
                return {
                    "success": False,
                    "error": f"Failed to initialize agents: {', '.join(failed_agents)}",
                    "agents_status": agents_status
                }
            
            # Create Semantic Kernel agents for orchestration
            async with DefaultAzureCredential() as creds:
                # Create Azure AI client for Semantic Kernel integration
                async with AzureAIAgent.create_client(credential=creds) as sk_client:
                    self.project_client = sk_client
                    
                    # Create Semantic Kernel agent wrappers
                    sk_agents = await self._create_semantic_kernel_agents(sk_client)
                    
                    # Create Magentic orchestration
                    self.magentic_orchestration = MagenticOrchestration(
                        members=sk_agents,
                        manager=StandardMagenticManager(
                            chat_completion_service=AzureChatCompletion(
                                endpoint=self.settings.orchestrator.azure_openai_endpoint,
                            )
                        ),
                        agent_response_callback=self.agent_response_callback,
                    )
                    
                    # Create and start runtime
                    self.runtime = InProcessRuntime()
                    self.runtime.start()
                    
                    return {
                        "success": True,
                        "agents_status": agents_status,
                        "orchestration_ready": True,
                        "runtime_started": True
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to initialize Magentic team: {str(e)}",
                "agents_status": agents_status if 'agents_status' in locals() else {}
            }
    
    async def _create_semantic_kernel_agents(self, client) -> List[Agent]:
        """Create Semantic Kernel agent wrappers for orchestration."""
        sk_agents = []
        
        # Hotel Agent wrapper
        hotel_sk_agent_definition = await client.agents.create_agent(
            model=AzureAIAgentSettings().model_deployment_name,
            name="HotelSearchAgent",
            description="專業酒店搜索助理，提供酒店推薦和設施資訊 / Professional hotel search assistant for recommendations",
            instructions="""You are the hotel search specialist in a travel planning team.
Your role is to find and recommend hotels based on user requirements including:
- Location and proximity preferences
- Amenities (parking, wifi, gym, etc.)
- Rating and price considerations
- Special requirements (pet-friendly, accessibility, etc.)

When asked about hotels, provide specific recommendations with reasoning.
Always consider practical factors like parking availability and location convenience.""",
            tools=[
                {
                    "type": "function", 
                    "function": {
                        "name": "MagenticTeamPlugin-search_hotels",
                        "description": "Search for hotels based on user requirements",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Hotel search query"},
                                "location": {"type": "string", "description": "Desired location"},
                                "requirements": {"type": "string", "description": "Special requirements"}
                            },
                            "required": ["query"],
                        },
                    },
                }
            ],
        )
        
        hotel_sk_agent = AzureAIAgent(
            client=client,
            definition=hotel_sk_agent_definition,
            plugins=[MagenticTeamPlugin(self)],
        )
        sk_agents.append(hotel_sk_agent)
        
        # Taxi Fabric Agent wrapper
        taxi_fabric_sk_agent_definition = await client.agents.create_agent(
            model=AzureAIAgentSettings().model_deployment_name,
            name="TaxiFabricAnalyst",
            description="計程車數據分析專家 (Microsoft Fabric) / Taxi data analysis expert (Microsoft Fabric)",
            instructions="""You are the taxi data analysis specialist using Microsoft Fabric lakehouse.
Your expertise includes:
- Holiday vs weekday trip pattern analysis
- Day/night time comparison and fare analysis  
- Geographic pickup/dropoff area statistics
- Passenger count distributions
- High fare anomaly detection

Provide detailed statistical analysis with clear insights and trends.
Always include relevant numbers and percentages in your responses.""",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "MagenticTeamPlugin-analyze_taxi_data_fabric",
                        "description": "Analyze taxi data using Microsoft Fabric",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "analysis_type": {"type": "string", "description": "Type of analysis to perform"},
                                "parameters": {"type": "string", "description": "Analysis parameters"}
                            },
                            "required": ["analysis_type"],
                        },
                    },
                }
            ],
        )
        
        taxi_fabric_sk_agent = AzureAIAgent(
            client=client,
            definition=taxi_fabric_sk_agent_definition,
            plugins=[MagenticTeamPlugin(self)],
        )
        sk_agents.append(taxi_fabric_sk_agent)
        
        # Taxi Genie Agent wrapper
        taxi_genie_sk_agent_definition = await client.agents.create_agent(
            model=AzureAIAgentSettings().model_deployment_name,
            name="TaxiGenieAnalyst",
            description="計程車數據分析專家 (Databricks Genie) / Taxi data analysis expert (Databricks Genie)",
            instructions="""You are the taxi data analysis specialist using Databricks Genie.
You can query the NYC taxi dataset to provide insights on:
- Fare statistics and distributions
- Time-based usage patterns
- Distance vs fare correlations
- Geographic comparisons
- Outlier trip detection

Use natural language queries to Genie and provide clear explanations of results.
Compare findings with other data sources when available.""",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "MagenticTeamPlugin-analyze_taxi_data_genie",
                        "description": "Analyze taxi data using Databricks Genie",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Natural language query for Genie"},
                                "context": {"type": "string", "description": "Additional context or conversation ID"}
                            },
                            "required": ["query"],
                        },
                    },
                }
            ],
        )
        
        taxi_genie_sk_agent = AzureAIAgent(
            client=client,
            definition=taxi_genie_sk_agent_definition,
            plugins=[MagenticTeamPlugin(self)],
        )
        sk_agents.append(taxi_genie_sk_agent)
        
        # Email Agent wrapper
        email_sk_agent_definition = await client.agents.create_agent(
            model=AzureAIAgentSettings().model_deployment_name,
            name="EmailAutomationAgent", 
            description="電子郵件自動化專家 / Email automation specialist",
            instructions="""You are the email automation specialist responsible for:
- Sending travel summaries and recommendations
- Delivering data analysis reports
- Creating decision packages with key insights
- Managing notifications and alerts

Format emails professionally with clear structure and relevant information.
Always confirm email delivery status and provide tracking information when available.""",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "MagenticTeamPlugin-send_email",
                        "description": "Send email via Logic Apps",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "recipient": {"type": "string", "description": "Email recipient address"},
                                "subject": {"type": "string", "description": "Email subject line"},
                                "body": {"type": "string", "description": "Email body content"}
                            },
                            "required": ["recipient", "subject", "body"],
                        },
                    },
                }
            ],
        )
        
        email_sk_agent = AzureAIAgent(
            client=client,
            definition=email_sk_agent_definition,
            plugins=[MagenticTeamPlugin(self)],
        )
        sk_agents.append(email_sk_agent)
        
        return sk_agents
    
    async def execute_scenario(self, user_query: str, scenario_type: str = "auto") -> Dict[str, Any]:
        """
        Execute a multi-agent scenario based on user query.
        
        Args:
            user_query: Natural language query from user
            scenario_type: Type of scenario ("travel_query", "data_consistency", "decision_package", "auto")
            
        Returns:
            Dict with scenario execution results
        """
        try:
            if not self.magentic_orchestration or not self.runtime:
                return {
                    "success": False,
                    "error": "Magentic orchestration not initialized"
                }
            
            # Auto-detect scenario type based on query keywords
            if scenario_type == "auto":
                scenario_type = self._detect_scenario_type(user_query)
            
            # Execute orchestrated workflow
            orchestration_result = await self.magentic_orchestration.invoke(
                task=user_query,
                runtime=self.runtime,
            )
            
            # Wait for results
            result_value = await orchestration_result.get()
            
            return {
                "success": True,
                "scenario_type": scenario_type,
                "result": result_value,
                "query": user_query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Scenario execution failed: {str(e)}",
                "scenario_type": scenario_type,
                "query": user_query
            }
    
    def _detect_scenario_type(self, user_query: str) -> str:
        """Auto-detect scenario type based on user query keywords."""
        query_lower = user_query.lower()
        
        # Travel query scenario keywords
        travel_keywords = ['hotel', 'travel', 'booking', 'accommodation', 'stay', 'taxi', 'transport', 'email', 'send', 'summary']
        
        # Data consistency scenario keywords  
        consistency_keywords = ['compare', 'consistency', 'difference', 'fabric', 'genie', 'data', 'check']
        
        # Decision package scenario keywords
        decision_keywords = ['recommend', 'decision', 'package', 'hotspot', 'insight', 'comprehensive']
        
        travel_score = sum(1 for keyword in travel_keywords if keyword in query_lower)
        consistency_score = sum(1 for keyword in consistency_keywords if keyword in query_lower)
        decision_score = sum(1 for keyword in decision_keywords if keyword in query_lower)
        
        if consistency_score >= 2:
            return "data_consistency"
        elif decision_score >= 2:
            return "decision_package"
        else:
            return "travel_query"  # Default scenario
    
    async def execute_hotel_task(self, query: str, location: str = "", requirements: str = "") -> Dict[str, Any]:
        """Execute hotel search task."""
        result = self.hotel_agent.run(
            self.hotel_agent.thread.id,
            f"Search for hotels: {query}. Location: {location}. Requirements: {requirements}"
        )
        return {"summary": result.get('response', 'No response'), "details": result}
    
    async def execute_taxi_fabric_task(self, analysis_type: str, parameters: str = "") -> Dict[str, Any]:
        """Execute taxi analysis task using Fabric."""
        result = self.taxi_fabric_agent.run(
            self.taxi_fabric_agent.thread.id,
            f"Analyze taxi data: {analysis_type}. Parameters: {parameters}"
        )
        return {"summary": result.get('response', 'No response'), "details": result}
    
    async def execute_taxi_genie_task(self, query: str, context: str = "") -> Dict[str, Any]:
        """Execute taxi analysis task using Genie."""
        result = self.taxi_genie_agent.run(
            self.taxi_genie_agent.thread.id,
            f"Query: {query}. Context: {context}"
        )
        return {"summary": result.get('response', 'No response'), "details": result}
    
    async def execute_email_task(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Execute email sending task."""
        result = self.email_agent.run(
            self.email_agent.thread.id,
            f"Send email to {recipient} with subject '{subject}' and body: {body}"
        )
        return {"summary": result.get('response', 'No response'), "details": result}
    
    def resolve_conflicts(self, fabric_data: str, genie_data: str) -> Dict[str, Any]:
        """Resolve conflicts between Fabric and Genie data."""
        try:
            # Parse data strings as needed
            fabric_parsed = eval(fabric_data) if isinstance(fabric_data, str) else fabric_data
            genie_parsed = eval(genie_data) if isinstance(genie_data, str) else genie_data
            
            result = ConflictResolutionStrategy.resolve_conflicts(
                fabric_parsed, genie_parsed, "newest_priority"
            )
            
            return {"summary": f"Resolved {result['conflict_count']} conflicts", "details": result}
            
        except Exception as e:
            return {"summary": f"Conflict resolution failed: {str(e)}", "details": {}}
    
    async def cleanup(self) -> Dict[str, Any]:
        """Clean up all resources."""
        cleanup_results = {}
        
        try:
            # Stop runtime
            if self.runtime:
                await self.runtime.stop_when_idle()
                cleanup_results['runtime'] = "stopped"
            
            # Cleanup individual agents
            cleanup_results['hotel'] = self.hotel_agent.cleanup()
            cleanup_results['taxi_fabric'] = self.taxi_fabric_agent.cleanup()
            cleanup_results['taxi_genie'] = self.taxi_genie_agent.cleanup()
            cleanup_results['email'] = self.email_agent.cleanup()
            
            return {
                "success": True,
                "cleanup_results": cleanup_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Cleanup failed: {str(e)}",
                "partial_cleanup": cleanup_results
            }
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get current status of all team members."""
        return {
            "hotel_agent": self.hotel_agent.get_agent_info(),
            "taxi_fabric_agent": self.taxi_fabric_agent.get_agent_info(),
            "taxi_genie_agent": self.taxi_genie_agent.get_agent_info(),
            "email_agent": self.email_agent.get_agent_info(),
            "orchestration_ready": self.magentic_orchestration is not None,
            "runtime_active": self.runtime is not None and hasattr(self.runtime, '_started')
        }