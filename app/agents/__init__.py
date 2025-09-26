# Magentic One Team - Agents Module
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Unified agent module for the Magentic One team system.
Provides standardized interfaces for Hotel, Taxi (Fabric & Genie), and Email agents.
"""

from .hotel_agent import HotelAgent
from .taxi_fabric_agent import TaxiFabricAgent  
from .taxi_genie_agent import TaxiGenieAgent
from .email_logicapps_agent import EmailLogicAppsAgent

__all__ = [
    "HotelAgent",
    "TaxiFabricAgent", 
    "TaxiGenieAgent",
    "EmailLogicAppsAgent"
]