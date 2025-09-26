# Magentic One Team - Configuration Module  
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Configuration module for the Magentic One team system.
Provides type-safe settings management for all agents and orchestration.
"""

from .settings import (
    load_settings,
    get_mock_settings,
    MagenticTeamSettings,
    AgentSettings,
    HotelAgentSettings,
    TaxiFabricAgentSettings,
    TaxiGenieAgentSettings,
    EmailAgentSettings,
    OrchestratorSettings
)

__all__ = [
    "load_settings",
    "get_mock_settings", 
    "MagenticTeamSettings",
    "AgentSettings",
    "HotelAgentSettings",
    "TaxiFabricAgentSettings",
    "TaxiGenieAgentSettings",
    "EmailAgentSettings",
    "OrchestratorSettings"
]