# Magentic One Team System
# Copyright (c) Microsoft Corporation.  
# Licensed under the MIT License.

"""
Magentic One Team System - Multi-Agent Orchestration Platform

A comprehensive system that orchestrates four specialized AI agents using
Semantic Kernel's MagenticOrchestration framework:

- 🏨 Hotel Agent (Azure AI Search)
- 🚕 Taxi Fabric Agent (Microsoft Fabric) 
- 🚕 Taxi Genie Agent (Databricks Genie)
- 📧 Email Agent (Azure Logic Apps)

USAGE:
    chainlit run app/ui/chainlit_entry.py -w

FEATURES:
    - Individual agent interactions
    - Multi-agent orchestrated workflows
    - Three main scenarios: travel planning, data consistency, decision packages
    - Mock mode for testing without full Azure setup
    - Real-time agent coordination and status monitoring

ARCHITECTURE:
    - Standardized agent interfaces (create/run/tools/cleanup)
    - Semantic Kernel orchestration with StandardMagenticManager
    - Chainlit web UI with interactive buttons and comprehensive queries
    - Type-safe configuration management
    - Conflict resolution strategies for multi-source data
"""

__version__ = "1.0.0"
__author__ = "Microsoft Corporation"
__license__ = "MIT"

# Core exports
from .config import load_settings, get_mock_settings, MagenticTeamSettings
from .agents import HotelAgent, TaxiFabricAgent, TaxiGenieAgent, EmailLogicAppsAgent
from .orchestrator import MagenticTeamRuntime, TaskGraphBuilder, ConflictResolutionStrategy

__all__ = [
    # Configuration
    "load_settings",
    "get_mock_settings", 
    "MagenticTeamSettings",
    
    # Individual Agents
    "HotelAgent",
    "TaxiFabricAgent",
    "TaxiGenieAgent", 
    "EmailLogicAppsAgent",
    
    # Orchestration
    "MagenticTeamRuntime",
    "TaskGraphBuilder",
    "ConflictResolutionStrategy",
    
    # Version info
    "__version__",
]