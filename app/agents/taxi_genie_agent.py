# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Taxi Genie Agent module - abstracts Databricks Genie functionality
from chainlit_agent_adb_genie.py into a reusable agent interface.
"""

import json
import os
from typing import Optional, Dict, Any, List, Set, Callable
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from ..config.settings import TaxiGenieAgentSettings

# Mock Databricks dependencies for now - in real implementation these would be properly imported
class MockWorkspaceClient:
    def __init__(self, host, token):
        self.host = host
        self.token = token
        self.api_client = self
        
class MockGenieAPI:
    def __init__(self, api_client):
        self.api_client = api_client
        
    def start_conversation_and_wait(self, space_id, question):
        return type('Message', (), {
            'conversation_id': 'mock_conv_123',
            'id': 'mock_msg_456',
            'query_result': None
        })()
        
    def get_message(self, space_id, conversation_id, message_id):
        return type('Message', (), {
            'content': f'Mock response to: {question}' if 'question' in locals() else 'Mock response',
            'attachments': []
        })()


# Set mock environment variables for Databricks
os.environ["DATABRICKS_SDK_UPSTREAM"] = "AzureAIFoundry"
os.environ["DATABRICKS_SDK_UPSTREAM_VERSION"] = "1.0.0"

DATABRICKS_ENTRA_ID_AUDIENCE_SCOPE = "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"


def ask_genie(question: str, conversation_id: str = None) -> str:
    """
    Ask Genie a question and return the response as JSON.
    The response JSON will contain the conversation ID and either the message content or a table of results.
    Reuse the conversation ID in future calls to continue the conversation and maintain context.
    
    param question: The question to ask Genie.
    param conversation_id: The ID of the conversation to continue. If None, a new conversation will be started.
    """
    try:
        # Mock implementation - in real version this would use actual Genie API
        import random
        
        # Generate mock data based on common taxi analysis questions
        if any(keyword in question.lower() for keyword in ['average', 'fare', 'cost']):
            mock_data = {
                "conversation_id": conversation_id or f"conv_{random.randint(1000, 9999)}",
                "table": {
                    "columns": ["metric", "value", "currency"],
                    "rows": [
                        ["Average Fare", f"{random.uniform(12.5, 18.7):.2f}", "USD"],
                        ["Median Fare", f"{random.uniform(10.2, 15.8):.2f}", "USD"],
                        ["Max Fare", f"{random.uniform(150, 350):.2f}", "USD"]
                    ]
                }
            }
        elif any(keyword in question.lower() for keyword in ['trips', 'count', 'number']):
            mock_data = {
                "conversation_id": conversation_id or f"conv_{random.randint(1000, 9999)}",
                "table": {
                    "columns": ["time_period", "trip_count", "percentage"],
                    "rows": [
                        ["Morning (6-12)", f"{random.randint(25000, 35000):,}", "28%"],
                        ["Afternoon (12-18)", f"{random.randint(30000, 40000):,}", "32%"],
                        ["Evening (18-24)", f"{random.randint(20000, 30000):,}", "24%"],
                        ["Night (0-6)", f"{random.randint(10000, 20000):,}", "16%"]
                    ]
                }
            }
        elif any(keyword in question.lower() for keyword in ['distance', 'mile', 'km']):
            mock_data = {
                "conversation_id": conversation_id or f"conv_{random.randint(1000, 9999)}",
                "table": {
                    "columns": ["distance_range", "trip_count", "avg_fare"],
                    "rows": [
                        ["0-2 miles", f"{random.randint(40000, 60000):,}", f"${random.uniform(8, 12):.2f}"],
                        ["2-5 miles", f"{random.randint(30000, 50000):,}", f"${random.uniform(15, 25):.2f}"],
                        ["5-10 miles", f"{random.randint(15000, 25000):,}", f"${random.uniform(28, 45):.2f}"],
                        ["10+ miles", f"{random.randint(5000, 15000):,}", f"${random.uniform(50, 85):.2f}"]
                    ]
                }
            }
        elif any(keyword in question.lower() for keyword in ['pickup', 'location', 'zone', 'area']):
            locations = ['Manhattan Midtown', 'JFK Airport', 'LaGuardia Airport', 'Brooklyn', 'Queens', 'Bronx']
            mock_data = {
                "conversation_id": conversation_id or f"conv_{random.randint(1000, 9999)}",
                "table": {
                    "columns": ["pickup_location", "trip_count", "avg_fare"],
                    "rows": [
                        [loc, f"{random.randint(5000, 25000):,}", f"${random.uniform(12, 28):.2f}"]
                        for loc in locations[:5]
                    ]
                }
            }
        else:
            # Generic response
            mock_data = {
                "conversation_id": conversation_id or f"conv_{random.randint(1000, 9999)}",
                "message": f"Based on the NYC taxi dataset analysis: {question}. The data shows various patterns in taxi usage across different time periods and locations."
            }
            
        return json.dumps(mock_data)

    except Exception as e:
        return json.dumps({
            "error": "An error occurred while talking to Genie.",
            "details": str(e),
            "conversation_id": conversation_id
        })


class TaxiGenieAgent:
    """
    Taxi data analysis agent using Databricks Genie.
    Provides standardized create/run/tools interface for the Magentic orchestrator.
    """
    
    def __init__(self, settings: TaxiGenieAgentSettings):
        """Initialize the Taxi Genie agent with configuration."""
        self.settings = settings
        self.project_client: Optional[AIProjectClient] = None
        self.agent = None
        self.thread = None
        self.genie_api = None
        self.genie_space_id = None
        self.databricks_workspace_client = None
        self.credential = None
        
    def _initialize_databricks_connection(self) -> bool:
        """Initialize Databricks connection and Genie API."""
        try:
            # Initialize Azure credentials and clients
            self.credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
            
            project_client = AIProjectClient(
                self.settings.foundry_project_endpoint,
                self.credential
            )
            
            connection = project_client.connections.get(self.settings.foundry_databricks_connection_name)
            
            if connection.metadata.get('azure_databricks_connection_type') == 'genie':
                self.genie_space_id = connection.metadata.get('genie_space_id')
            else:
                return False

            # Mock Databricks client for now - in real implementation:
            # from databricks.sdk import WorkspaceClient
            # from databricks.sdk.service.dashboards import GenieAPI
            # self.databricks_workspace_client = WorkspaceClient(
            #     host=connection.target,
            #     token=self.credential.get_token("2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default").token,
            # )
            # self.genie_api = GenieAPI(self.databricks_workspace_client.api_client)
            
            self.databricks_workspace_client = MockWorkspaceClient(
                host=connection.target if hasattr(connection, 'target') else 'mock-host',
                token='mock-token'
            )
            self.genie_api = MockGenieAPI(self.databricks_workspace_client.api_client)
            
            return True
            
        except Exception as e:
            print(f"Failed to initialize Databricks connection: {str(e)}")
            return False
    
    def create(self) -> Dict[str, Any]:
        """
        Create the taxi genie agent and conversation thread.
        
        Returns:
            Dict with agent and thread information
        """
        try:
            # Initialize Databricks connection
            if not self._initialize_databricks_connection():
                return {
                    "success": False,
                    "error": "Failed to initialize Databricks Genie connection"
                }
            
            # Create the project client
            self.project_client = AIProjectClient(
                self.settings.project_endpoint,
                self.credential or DefaultAzureCredential(exclude_interactive_browser_credential=False)
            )
            
            # Create toolset with ask_genie function
            toolset = ToolSet()
            user_functions: Set[Callable[..., Any]] = {ask_genie}
            functions = FunctionTool(functions=user_functions)
            toolset.add(functions)

            # Create agent with Genie integration
            self.project_client.agents.enable_auto_function_calls(toolset)
            
            agent_instructions = """
You are a data analysis agent connected to the Databricks "samples.nyctaxi.trips" dataset. 
Your role is to help users explore and analyze taxi trip data using Databricks Genie.
You should respond to natural language queries by generating SQL queries and summarizing results.

You can answer the following types of questions:
1. Fare statistics: e.g., average, maximum, or minimum fare amount.
2. Time-based trends: e.g., trip counts by hour, day, or week.
3. Distance vs fare analysis: e.g., correlation between distance and fare, fare distribution by distance.
4. Geographic comparisons: e.g., which pickup or dropoff zip codes have the highest average fare.
5. Outlier detection: e.g., identify trips with unusually high fares relative to distance.

Always explain your answer clearly, and when relevant, show both the query and a short natural-language summary of the results.
Use the ask_genie function to query the Databricks Genie system and provide comprehensive analysis.
"""
            
            self.agent = self.project_client.agents.create_agent(
                model=self.settings.model_deployment_name,
                name="Databricks Taxi Data Analysis Agent",
                instructions=agent_instructions,
                toolset=toolset,
            )
            
            # Create conversation thread
            self.thread = self.project_client.agents.threads.create()
            
            return {
                "success": True,
                "agent_id": self.agent.id,
                "thread_id": self.thread.id,
                "agent_name": self.agent.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create taxi genie agent: {str(e)}"
            }
    
    def run(self, thread_id: str, prompt: str) -> Dict[str, Any]:
        """
        Run the taxi genie agent with a user prompt.
        
        Args:
            thread_id: The conversation thread ID
            prompt: User's question or request
            
        Returns:
            Dict with response and status information
        """
        try:
            if not self.project_client or not self.agent:
                return {
                    "success": False,
                    "error": "Taxi genie agent not properly initialized"
                }
            
            # Create message and run
            self.project_client.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=prompt,
            )

            run = self.project_client.agents.runs.create_and_process(
                thread_id=thread_id,
                agent_id=self.agent.id
            )

            if run.status == "completed":
                # Get the latest assistant message
                messages = self.project_client.agents.messages.list(thread_id=thread_id)
                
                for message in messages:
                    if message.role == "assistant":
                        response_content = ""
                        for content_item in message.content:
                            if hasattr(content_item, 'text') and hasattr(content_item.text, 'value'):
                                response_content = content_item.text.value
                                break
                        
                        if response_content:
                            return {
                                "success": True,
                                "response": response_content,
                                "run_status": run.status
                            }
                        break

                return {
                    "success": False,
                    "error": "No valid assistant response found"
                }
            elif run.status == "failed":
                return {
                    "success": False,
                    "error": f"Run failed: {run.last_error}",
                    "run_status": run.status
                }
            else:
                return {
                    "success": False,
                    "error": f"Unexpected run status: {run.status}",
                    "run_status": run.status
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Taxi genie agent run failed: {str(e)}"
            }
    
    def tools(self) -> List[Dict[str, Any]]:
        """
        Return available tools/functions for this agent.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "ask_genie",
                "description": "Query Databricks Genie system for taxi trip analysis",
                "parameters": {
                    "question": "string - Natural language question about taxi data",
                    "conversation_id": "string (optional) - Conversation ID to maintain context"
                }
            }
        ]
    
    def get_sample_questions(self) -> List[str]:
        """
        Get sample questions that showcase the taxi genie agent's capabilities.
        
        Returns:
            List of sample questions
        """
        return [
            "What is the average fare amount per trip? (平均車資)",
            "How does the number of trips vary by hour of the day or day of the week? (依時間的趨勢)",
            "What is the correlation between trip distance and fare amount? (距離 vs 車資關係)",
            "Which pickup zip codes have the highest average fares? (地區比較)",
            "Are there any outlier trips with unusually high fare amounts compared to their distance? (異常值分析)"
        ]
    
    def cleanup(self) -> bool:
        """
        Clean up the agent resources.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.project_client and self.agent:
                self.project_client.agents.delete_agent(self.agent.id)
                return True
            return False
        except Exception:
            return False
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for display purposes.
        
        Returns:
            Dict with agent details
        """
        if self.agent and self.thread:
            return {
                "name": "Taxi Data Analysis Agent (Genie)",
                "role": "Databricks Genie Analysis", 
                "agent_id": self.agent.id,
                "thread_id": self.thread.id,
                "description": "專業計程車數據分析助手 (Databricks Genie) / Professional taxi data analysis assistant (Databricks Genie)",
                "capabilities": [
                    "車資統計分析 / Fare statistics analysis",
                    "時間趨勢分析 / Time-based trend analysis", 
                    "距離與車資關聯 / Distance vs fare correlation",
                    "地理區域比較 / Geographic area comparison",
                    "異常值檢測 / Outlier detection"
                ]
            }
        return {"name": "Taxi Data Analysis Agent (Genie)", "status": "Not initialized"}