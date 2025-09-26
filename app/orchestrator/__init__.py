# Magentic One Team - Orchestrator Module
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Orchestrator module for the Magentic One team system.
Manages multi-agent workflows using Semantic Kernel's MagenticOrchestration.
"""

from .magentic_runtime import MagenticTeamRuntime, MagenticTeamPlugin
from .task_graph import TaskGraphBuilder, TaskGraph, TaskType, TaskStatus, ConflictResolutionStrategy

__all__ = [
    "MagenticTeamRuntime",
    "MagenticTeamPlugin", 
    "TaskGraphBuilder",
    "TaskGraph",
    "TaskType",
    "TaskStatus", 
    "ConflictResolutionStrategy"
]