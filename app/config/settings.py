# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Configuration settings for the Magentic One team system.
Provides type-safe environment variable management for all agents and orchestration.
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AgentSettings:
    """Base settings for all agents."""
    project_endpoint: str
    model_deployment_name: str


@dataclass  
class HotelAgentSettings(AgentSettings):
    """Settings for the Hotel agent (Azure AI Search)."""
    azure_search_endpoint: str
    azure_search_api_key: str
    azure_search_index: str = "vector-search-quickstart"


@dataclass
class TaxiFabricAgentSettings(AgentSettings):
    """Settings for the Taxi Fabric agent."""
    pass  # Uses base agent settings only


@dataclass
class TaxiGenieAgentSettings(AgentSettings):
    """Settings for the Taxi Genie agent (Databricks)."""
    foundry_project_endpoint: str
    foundry_databricks_connection_name: str


@dataclass
class EmailAgentSettings(AgentSettings):
    """Settings for the Email agent (Logic Apps)."""
    azure_subscription_id: str
    azure_resource_group: str
    logic_app_name: str
    trigger_name: str
    recipient_email: str


@dataclass
class OrchestratorSettings:
    """Settings for the Magentic orchestrator."""
    azure_openai_endpoint: str
    bing_grounding_connection_name: Optional[str] = None


@dataclass
class MagenticTeamSettings:
    """Complete settings for the Magentic One team system."""
    hotel: HotelAgentSettings
    taxi_fabric: TaxiFabricAgentSettings
    taxi_genie: TaxiGenieAgentSettings
    email: EmailAgentSettings
    orchestrator: OrchestratorSettings


def load_settings() -> MagenticTeamSettings:
    """
    Load settings from environment variables with proper type checking.
    
    Returns:
        MagenticTeamSettings: Complete configuration for the system
        
    Raises:
        ValueError: If required environment variables are missing
    """
    load_dotenv(override=True)
    
    # Validate required base settings
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    if not project_endpoint:
        raise ValueError("PROJECT_ENDPOINT environment variable is required")
    
    model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4o")
    
    # Hotel agent settings
    azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    azure_search_api_key = os.getenv("AZURE_SEARCH_API_KEY") 
    azure_search_index = os.getenv("AZURE_SEARCH_INDEX", "vector-search-quickstart")
    
    if not azure_search_endpoint or not azure_search_api_key:
        raise ValueError("Hotel agent requires AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY")
    
    # Taxi Genie agent settings
    foundry_project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    foundry_databricks_connection_name = os.getenv("FOUNDRY_DATABRICKS_CONNECTION_NAME")
    
    if not foundry_project_endpoint or not foundry_databricks_connection_name:
        raise ValueError("Taxi Genie agent requires FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_DATABRICKS_CONNECTION_NAME")
    
    # Email agent settings
    azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    azure_resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    logic_app_name = os.getenv("LOGIC_APP_NAME")
    trigger_name = os.getenv("TRIGGER_NAME", "When_a_HTTP_request_is_received")
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    
    if not all([azure_subscription_id, azure_resource_group, logic_app_name, recipient_email]):
        raise ValueError("Email agent requires AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, LOGIC_APP_NAME, and RECIPIENT_EMAIL")
    
    # Orchestrator settings
    azure_openai_endpoint = os.getenv("MY_AZURE_OPENAI_ENDPOINT", project_endpoint)
    bing_grounding_connection_name = os.getenv("BING_GROUNDING_CONNECTION_NAME")
    
    return MagenticTeamSettings(
        hotel=HotelAgentSettings(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            azure_search_endpoint=azure_search_endpoint,
            azure_search_api_key=azure_search_api_key,
            azure_search_index=azure_search_index
        ),
        taxi_fabric=TaxiFabricAgentSettings(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name
        ),
        taxi_genie=TaxiGenieAgentSettings(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            foundry_project_endpoint=foundry_project_endpoint,
            foundry_databricks_connection_name=foundry_databricks_connection_name
        ),
        email=EmailAgentSettings(
            project_endpoint=project_endpoint,
            model_deployment_name=model_deployment_name,
            azure_subscription_id=azure_subscription_id,
            azure_resource_group=azure_resource_group,
            logic_app_name=logic_app_name,
            trigger_name=trigger_name,
            recipient_email=recipient_email
        ),
        orchestrator=OrchestratorSettings(
            azure_openai_endpoint=azure_openai_endpoint,
            bing_grounding_connection_name=bing_grounding_connection_name
        )
    )


def get_mock_settings() -> MagenticTeamSettings:
    """
    Get mock settings for testing without requiring all environment variables.
    
    Returns:
        MagenticTeamSettings: Mock configuration for testing
    """
    return MagenticTeamSettings(
        hotel=HotelAgentSettings(
            project_endpoint="https://mock-project.cognitiveservices.azure.com",
            model_deployment_name="gpt-4o",
            azure_search_endpoint="https://mock-search.search.windows.net",
            azure_search_api_key="mock-search-key",
            azure_search_index="mock-index"
        ),
        taxi_fabric=TaxiFabricAgentSettings(
            project_endpoint="https://mock-project.cognitiveservices.azure.com",
            model_deployment_name="gpt-4o"
        ),
        taxi_genie=TaxiGenieAgentSettings(
            project_endpoint="https://mock-project.cognitiveservices.azure.com",
            model_deployment_name="gpt-4o",
            foundry_project_endpoint="https://mock-foundry.cognitiveservices.azure.com",
            foundry_databricks_connection_name="mock-databricks-connection"
        ),
        email=EmailAgentSettings(
            project_endpoint="https://mock-project.cognitiveservices.azure.com",
            model_deployment_name="gpt-4o",
            azure_subscription_id="mock-subscription-id",
            azure_resource_group="mock-resource-group",
            logic_app_name="mock-logic-app",
            trigger_name="When_a_HTTP_request_is_received",
            recipient_email="test@example.com"
        ),
        orchestrator=OrchestratorSettings(
            azure_openai_endpoint="https://mock-openai.openai.azure.com",
            bing_grounding_connection_name="mock-bing-connection"
        )
    )