# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Taxi Fabric Agent module - abstracts Microsoft Fabric taxi data analysis functionality
from chainlit_app.py and taxi_query_functions.py into a reusable agent interface.
"""

import json
import asyncio
from typing import Optional, Dict, Any, List, Set, Callable
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ToolSet, FunctionTool
from ..config.settings import TaxiFabricAgentSettings

# Import taxi query functions - we'll copy them locally to avoid path dependencies
# In a real implementation, these would be properly imported or refactored
import random
from datetime import datetime


def mock_execute_query(query: str) -> Dict[str, Any]:
    """Mock function to simulate executing a SQL query against taxi trip data."""
    print(f"Executing query: {query[:100]}...")
    return {"result": "Mock query result", "query": query}


def get_daily_trip_stats(date: str) -> str:
    """Get total trip count and revenue for a specific date."""
    total_trips = random.randint(50000, 80000)
    total_revenue = random.randint(200000, 400000)
    avg_fare = total_revenue / total_trips
    
    result = {
        "date": date,
        "total_trips": total_trips,
        "total_revenue": round(total_revenue, 2),
        "average_fare": round(avg_fare, 2)
    }
    
    return json.dumps(result)


def get_day_night_comparison(days: int = 60) -> str:
    """Compare day (7:00-19:00) vs night (19:00-7:00) ride patterns."""
    day_rides = random.randint(400000, 600000)
    night_rides = random.randint(300000, 500000)
    day_avg_fare = random.uniform(15.0, 20.0)
    night_avg_fare = random.uniform(18.0, 25.0)
    
    result = {
        "period_days": days,
        "day_period": "7:00-19:00",
        "night_period": "19:00-7:00",
        "day_stats": {
            "ride_count": day_rides,
            "avg_fare": round(day_avg_fare, 2),
            "percentage": round(day_rides / (day_rides + night_rides) * 100, 2)
        },
        "night_stats": {
            "ride_count": night_rides,
            "avg_fare": round(night_avg_fare, 2),
            "percentage": round(night_rides / (day_rides + night_rides) * 100, 2)
        },
        "fare_difference": round(night_avg_fare - day_avg_fare, 2)
    }
    
    return json.dumps(result)


def get_top_pickup_areas(days: int = 30) -> str:
    """Get top 10 pickup areas by ride volume with percentages."""
    areas = [
        'Manhattan Midtown', 'JFK Airport', 'LGA Airport', 'Manhattan Financial District',
        'Brooklyn Heights', 'Queens Astoria', 'Bronx Yankee Stadium', 'Manhattan Chelsea',
        'Brooklyn DUMBO', 'Staten Island Ferry'
    ]
    
    top_areas = []
    total_rides = random.randint(800000, 1200000)
    remaining_percentage = 100.0
    
    for i, area in enumerate(areas):
        if i == len(areas) - 1:
            percentage = remaining_percentage
        else:
            percentage = random.uniform(5.0, 20.0)
            remaining_percentage -= percentage
        
        ride_count = int(total_rides * percentage / 100)
        
        top_areas.append({
            "rank": i + 1,
            "pickup_location": area,
            "ride_count": ride_count,
            "percentage": round(percentage, 2)
        })
    
    result = {
        "period_days": days,
        "total_rides": total_rides,
        "top_areas": top_areas
    }
    
    return json.dumps(result)


def get_passenger_count_distribution() -> str:
    """Get distribution of passenger counts by percentage."""
    passenger_data = [
        {"count": 1, "rides": random.randint(600000, 800000)},
        {"count": 2, "rides": random.randint(200000, 350000)},
        {"count": 3, "rides": random.randint(80000, 150000)},
        {"count": 4, "rides": random.randint(40000, 80000)},
        {"count": 5, "rides": random.randint(10000, 30000)},
        {"count": 6, "rides": random.randint(5000, 15000)}
    ]
    
    total_rides = sum(data["rides"] for data in passenger_data)
    
    distribution = []
    for data in passenger_data:
        percentage = (data["rides"] / total_rides) * 100
        distribution.append({
            "passenger_count": data["count"],
            "ride_count": data["rides"],
            "percentage": round(percentage, 2)
        })
    
    result = {
        "total_rides_analyzed": total_rides,
        "distribution": distribution
    }
    
    return json.dumps(result)


def get_highest_fares(start_date: str, limit: int = 10) -> str:
    """Get highest fare amounts since a given date with trip details."""
    high_fares = []
    locations = [
        ('JFK Airport', 'Manhattan Financial District'),
        ('Newark Airport', 'Brooklyn Heights'),
        ('LGA Airport', 'Queens Astoria'),
        ('Manhattan Midtown', 'Bronx Yankee Stadium'),
        ('Brooklyn DUMBO', 'Staten Island Ferry')
    ]
    
    for i in range(limit):
        pickup_loc, dropoff_loc = random.choice(locations)
        fare = random.uniform(150.0, 500.0)
        distance = random.uniform(25.0, 60.0)
        
        high_fares.append({
            "rank": i + 1,
            "trip_id": f"TRIP_{random.randint(100000, 999999)}",
            "pickup_datetime": f"2025-{random.randint(1,8):02d}-{random.randint(1,28):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:00",
            "pickup_location": pickup_loc,
            "dropoff_location": dropoff_loc,
            "fare_amount": round(fare, 2),
            "trip_distance": round(distance, 2),
            "passenger_count": random.randint(1, 4)
        })
    
    result = {
        "since_date": start_date,
        "top_fares": high_fares
    }
    
    return json.dumps(result)


# Taxi query functions set for FunctionTool
taxi_query_functions: Set[Callable[..., Any]] = {
    get_daily_trip_stats,
    get_day_night_comparison,
    get_top_pickup_areas,
    get_passenger_count_distribution,
    get_highest_fares
}


class TaxiFabricAgent:
    """
    Taxi data analysis agent for Microsoft Fabric lakehouse.
    Provides standardized create/run/tools interface for the Magentic orchestrator.
    """
    
    def __init__(self, settings: TaxiFabricAgentSettings):
        """Initialize the Taxi Fabric agent with configuration."""
        self.settings = settings
        self.project_client: Optional[AIProjectClient] = None
        self.agent = None
        self.thread = None
        
    def create(self) -> Dict[str, Any]:
        """
        Create the taxi fabric agent and conversation thread.
        
        Returns:
            Dict with agent and thread information
        """
        try:
            # Create the project client
            self.project_client = AIProjectClient(
                credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
                endpoint=self.settings.project_endpoint,
            )
            
            # Create function tool with taxi query functions
            functions = FunctionTool(functions=taxi_query_functions)
            toolset = ToolSet()
            toolset.add(functions)
            
            # Enable automatic function calls
            self.project_client.agents.enable_auto_function_calls(toolset)

            # Create agent with taxi data analysis personality
            agent_instructions = """You are a professional taxi data analysis assistant specializing in analyzing taxi trip data from Microsoft Fabric lakehouse.

Your expertise includes analyzing:
- Public holidays vs weekdays trip patterns and fare comparisons
- High-fare trip analysis (trips > $70) and their percentage distribution  
- Daytime (7:00-19:00) vs nighttime (19:00-7:00) trip and fare patterns
- Geographic analysis including top pickup locations and zip codes
- Passenger count distributions and modal analysis

You should:
1. Provide clear, structured responses with specific numbers and statistics
2. Use appropriate functions to retrieve real data from the lakehouse
3. Offer insights and trends based on the data analysis
4. Present information in Traditional Chinese while preserving technical terms and field names in English
5. Always maintain a professional and helpful tone

When users ask about taxi trip data, provide comprehensive analysis including relevant statistics, trends, and actionable insights."""

            self.agent = self.project_client.agents.create_agent(
                model=self.settings.model_deployment_name,
                name="TaxiDataAnalysisAgent",
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
                "error": f"Failed to create taxi fabric agent: {str(e)}"
            }
    
    def run(self, thread_id: str, prompt: str) -> Dict[str, Any]:
        """
        Run the taxi fabric agent with a user prompt.
        
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
                    "error": "Taxi fabric agent not properly initialized"
                }
            
            # Create message in thread
            self.project_client.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=prompt
            )
            
            # Process with retry mechanism
            max_retries = 3
            run = None
            
            for attempt in range(max_retries):
                try:
                    # Create and process the run
                    run = self.project_client.agents.runs.create_and_process(
                        thread_id=thread_id,
                        agent_id=self.agent.id
                    )
                    
                    # Wait for completion (for synchronous processing)
                    import time
                    while run.status in ["queued", "in_progress"]:
                        time.sleep(1)
                        run = self.project_client.agents.runs.get(thread_id=thread_id, run_id=run.id)
                    
                    if run.status == "completed":
                        break
                    elif run.status == "failed":
                        if attempt == max_retries - 1:
                            return {
                                "success": False,
                                "error": f"Run failed after {max_retries} attempts: {run.last_error}",
                                "run_status": run.status
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"Unexpected run status: {run.status}",
                            "run_status": run.status
                        }
                        
                except Exception as e:
                    if attempt == max_retries - 1:
                        return {
                            "success": False,
                            "error": f"Run failed after {max_retries} attempts: {str(e)}"
                        }
                    time.sleep(2)  # Wait before retry
            
            if run and run.status == "completed":
                # Get the latest assistant message
                messages = self.project_client.agents.messages.list(thread_id=thread_id)
                message_list = list(messages)
                
                for message in message_list:
                    if message.role == "assistant":
                        return {
                            "success": True,
                            "response": message.content,
                            "run_status": run.status
                        }
            
            return {
                "success": False,
                "error": "No valid assistant response found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Taxi fabric agent run failed: {str(e)}"
            }
    
    def tools(self) -> List[Dict[str, Any]]:
        """
        Return available tools/functions for this agent.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "get_daily_trip_stats",
                "description": "Get total trip count and revenue for a specific date",
                "parameters": {"date": "string (YYYY-MM-DD format)"}
            },
            {
                "name": "get_day_night_comparison", 
                "description": "Compare day vs night ride patterns and fares",
                "parameters": {"days": "integer (default 60)"}
            },
            {
                "name": "get_top_pickup_areas",
                "description": "Get top pickup areas by ride volume",
                "parameters": {"days": "integer (default 30)"}
            },
            {
                "name": "get_passenger_count_distribution",
                "description": "Get distribution of passenger counts",
                "parameters": {}
            },
            {
                "name": "get_highest_fares",
                "description": "Get highest fare amounts with trip details",
                "parameters": {"start_date": "string", "limit": "integer"}
            }
        ]
    
    def get_sample_questions(self) -> List[str]:
        """
        Get sample questions that showcase the taxi fabric agent's capabilities.
        
        Returns:
            List of sample questions
        """
        return [
            "Compare the total number of taxi trips on public holidays versus regular weekdays. In addition, analyze whether the average trip distance and average fare amount differ significantly between holidays and weekdays.",
            "Count the number of trips with fare amounts greater than 70. Also, calculate the percentage of these high-fare trips relative to all trips.",
            "Compare the number of trips and average fare amount between daytime (7:00–19:00) and nighttime (19:00–7:00). Additionally, show whether trip distances differ between daytime and nighttime trips.",
            "Identify the pickup zip code with the highest number of trips. Provide the top 5 pickup zip codes ranked by trip volume.",
            "Determine the most frequent passenger count value (mode) in the dataset. Provide the distribution of passenger counts across all trips."
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
                "name": "Taxi Data Analysis Agent (Fabric)",
                "role": "Microsoft Fabric Data Analysis",
                "agent_id": self.agent.id,
                "thread_id": self.thread.id,
                "description": "專業計程車數據分析助手 (Microsoft Fabric) / Professional taxi data analysis assistant (Microsoft Fabric)",
                "capabilities": [
                    "節假日 vs 平日分析 / Holiday vs weekday analysis",
                    "日夜時段比較 / Day/night time comparison",
                    "地理區域統計 / Geographic area statistics",
                    "乘客數分佈 / Passenger count distribution",
                    "高車資異常檢測 / High fare anomaly detection"
                ]
            }
        return {"name": "Taxi Data Analysis Agent (Fabric)", "status": "Not initialized"}