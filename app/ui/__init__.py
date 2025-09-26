# Magentic One Team - UI Module
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
User interface module for the Magentic One team system.
Provides unified Chainlit interface for all agents and orchestrated workflows.
"""

from .chainlit_entry import *

__all__ = [
    # Main entry point for Chainlit UI
    "start",
    "main", 
    "on_stop"
]