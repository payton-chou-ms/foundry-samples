# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Task Graph module for the Magentic One team system.
Defines task graphs and strategies for the three main scenarios.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Types of tasks that can be executed by agents."""
    HOTEL_SEARCH = "hotel_search"
    TAXI_ANALYSIS_FABRIC = "taxi_analysis_fabric"  
    TAXI_ANALYSIS_GENIE = "taxi_analysis_genie"
    EMAIL_SEND = "email_send"
    DATA_FUSION = "data_fusion"
    CONFLICT_RESOLUTION = "conflict_resolution"


class TaskStatus(Enum):
    """Status of task execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskNode:
    """Represents a task node in the execution graph."""
    task_id: str
    task_type: TaskType
    agent_name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    dependencies: List[str]  # Task IDs this task depends on
    priority: int = 1  # Higher numbers = higher priority
    timeout_seconds: int = 300  # Default 5 minute timeout
    retry_count: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass 
class TaskGraph:
    """Represents a complete task execution graph."""
    graph_id: str
    scenario: str
    description: str
    nodes: Dict[str, TaskNode]  # task_id -> TaskNode
    completion_criteria: Dict[str, Any]
    
    def get_ready_tasks(self) -> List[TaskNode]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        
        for task in self.nodes.values():
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            dependencies_satisfied = True
            for dep_id in task.dependencies:
                dep_task = self.nodes.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_satisfied = False
                    break
            
            if dependencies_satisfied:
                ready_tasks.append(task)
        
        # Sort by priority (highest first)
        ready_tasks.sort(key=lambda t: t.priority, reverse=True)
        return ready_tasks
    
    def is_complete(self) -> bool:
        """Check if the task graph execution is complete."""
        return all(task.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED] for task in self.nodes.values())
    
    def has_failures(self) -> bool:
        """Check if any critical tasks have failed."""
        return any(task.status == TaskStatus.FAILED for task in self.nodes.values())


class TaskGraphBuilder:
    """Builder for creating task graphs for different scenarios."""
    
    @staticmethod
    def create_travel_query_scenario(user_query: str) -> TaskGraph:
        """
        Create task graph for travel query + notification scenario.
        User input: "Help me find NYC hotels with parking, estimate day/night taxi costs, and email summary."
        """
        nodes = {
            "hotel_search": TaskNode(
                task_id="hotel_search",
                task_type=TaskType.HOTEL_SEARCH,
                agent_name="hotel",
                description="Search for hotels with parking in NYC",
                input_schema={"query": "string", "location": "string", "requirements": "list"},
                output_schema={"hotels": "list", "recommendations": "list", "reasoning": "string"},
                dependencies=[],
                priority=3
            ),
            "taxi_fabric_analysis": TaskNode(
                task_id="taxi_fabric_analysis", 
                task_type=TaskType.TAXI_ANALYSIS_FABRIC,
                agent_name="taxi_fabric",
                description="Analyze day/night taxi costs using Fabric data",
                input_schema={"analysis_type": "string", "time_periods": "list"},
                output_schema={"day_stats": "dict", "night_stats": "dict", "cost_comparison": "dict"},
                dependencies=[],
                priority=3
            ),
            "taxi_genie_analysis": TaskNode(
                task_id="taxi_genie_analysis",
                task_type=TaskType.TAXI_ANALYSIS_GENIE,
                agent_name="taxi_genie", 
                description="Analyze day/night taxi costs using Genie data",
                input_schema={"analysis_type": "string", "time_periods": "list"},
                output_schema={"day_stats": "dict", "night_stats": "dict", "cost_comparison": "dict"},
                dependencies=[],
                priority=3
            ),
            "data_fusion": TaskNode(
                task_id="data_fusion",
                task_type=TaskType.DATA_FUSION,
                agent_name="orchestrator",
                description="Combine and reconcile Fabric and Genie taxi analysis results",
                input_schema={"fabric_result": "dict", "genie_result": "dict"},
                output_schema={"unified_analysis": "dict", "differences": "list", "confidence": "float"},
                dependencies=["taxi_fabric_analysis", "taxi_genie_analysis"],
                priority=2
            ),
            "email_summary": TaskNode(
                task_id="email_summary",
                task_type=TaskType.EMAIL_SEND,
                agent_name="email",
                description="Send comprehensive travel summary email",
                input_schema={"recipient": "string", "hotel_data": "dict", "taxi_data": "dict", "summary": "string"},
                output_schema={"email_sent": "bool", "delivery_status": "string", "tracking_info": "dict"},
                dependencies=["hotel_search", "data_fusion"],
                priority=1
            )
        }
        
        return TaskGraph(
            graph_id="travel_query_001",
            scenario="travel_query_notification", 
            description="Find hotels, analyze taxi costs, send email summary",
            nodes=nodes,
            completion_criteria={
                "required_tasks": ["hotel_search", "email_summary"],
                "optional_tasks": ["taxi_fabric_analysis", "taxi_genie_analysis", "data_fusion"]
            }
        )
    
    @staticmethod
    def create_data_consistency_scenario(user_query: str) -> TaskGraph:
        """
        Create task graph for data consistency check scenario.
        User input: "Compare last 30 days taxi data between Fabric and Genie, report differences >5%."
        """
        nodes = {
            "fabric_data_pull": TaskNode(
                task_id="fabric_data_pull",
                task_type=TaskType.TAXI_ANALYSIS_FABRIC,
                agent_name="taxi_fabric",
                description="Pull 30-day taxi statistics from Fabric",
                input_schema={"period_days": "int", "metrics": "list"},
                output_schema={"metrics": "dict", "period": "string", "data_quality": "dict"},
                dependencies=[],
                priority=3
            ),
            "genie_data_pull": TaskNode(
                task_id="genie_data_pull",
                task_type=TaskType.TAXI_ANALYSIS_GENIE,
                agent_name="taxi_genie",
                description="Pull 30-day taxi statistics from Genie", 
                input_schema={"period_days": "int", "metrics": "list"},
                output_schema={"metrics": "dict", "period": "string", "data_quality": "dict"},
                dependencies=[],
                priority=3
            ),
            "consistency_check": TaskNode(
                task_id="consistency_check",
                task_type=TaskType.CONFLICT_RESOLUTION,
                agent_name="orchestrator",
                description="Compare metrics and identify differences >5%",
                input_schema={"fabric_data": "dict", "genie_data": "dict", "threshold": "float"},
                output_schema={"consistent": "bool", "differences": "list", "variance_report": "dict"},
                dependencies=["fabric_data_pull", "genie_data_pull"],
                priority=2
            ),
            "consistency_report_email": TaskNode(
                task_id="consistency_report_email",
                task_type=TaskType.EMAIL_SEND,
                agent_name="email",
                description="Send data consistency report email (optional)",
                input_schema={"recipient": "string", "report": "dict", "send_requested": "bool"},
                output_schema={"email_sent": "bool", "delivery_status": "string"},
                dependencies=["consistency_check"],
                priority=1
            )
        }
        
        return TaskGraph(
            graph_id="data_consistency_001",
            scenario="data_consistency_check",
            description="Compare Fabric vs Genie data consistency and report differences",
            nodes=nodes,
            completion_criteria={
                "required_tasks": ["fabric_data_pull", "genie_data_pull", "consistency_check"],
                "optional_tasks": ["consistency_report_email"]
            }
        )
    
    @staticmethod
    def create_decision_package_scenario(user_query: str) -> TaskGraph:
        """
        Create task graph for hotel + transport insights + decision email scenario.
        User input: "Recommend 3 4.5★+ hotels near Times Square with parking, analyze nearby taxi hotspots, email decision package."
        """
        nodes = {
            "hotel_recommendations": TaskNode(
                task_id="hotel_recommendations",
                task_type=TaskType.HOTEL_SEARCH,
                agent_name="hotel", 
                description="Find 3 top-rated hotels with parking near Times Square",
                input_schema={"location": "string", "min_rating": "float", "requirements": "list", "limit": "int"},
                output_schema={"hotels": "list", "amenities": "dict", "pricing": "dict", "locations": "list"},
                dependencies=[],
                priority=3
            ),
            "taxi_hotspot_analysis": TaskNode(
                task_id="taxi_hotspot_analysis",
                task_type=TaskType.TAXI_ANALYSIS_FABRIC,
                agent_name="taxi_fabric",
                description="Analyze taxi pickup hotspots and peak times near hotels",
                input_schema={"location": "string", "radius_km": "float", "analysis_type": "string"},
                output_schema={"hotspots": "list", "peak_times": "list", "avg_fares": "dict"},
                dependencies=["hotel_recommendations"], 
                priority=2
            ),
            "genie_validation": TaskNode(
                task_id="genie_validation",
                task_type=TaskType.TAXI_ANALYSIS_GENIE,
                agent_name="taxi_genie",
                description="Validate hotspot analysis with Genie data",
                input_schema={"location": "string", "hotspots_to_validate": "list"},
                output_schema={"validated_hotspots": "list", "discrepancies": "list", "confidence_score": "float"},
                dependencies=["taxi_hotspot_analysis"],
                priority=2
            ),
            "decision_package": TaskNode(
                task_id="decision_package",
                task_type=TaskType.EMAIL_SEND,
                agent_name="email",
                description="Send comprehensive decision package with hotels, transport insights, and recommendations",
                input_schema={"recipient": "string", "hotel_data": "dict", "transport_data": "dict", "package_type": "string"},
                output_schema={"email_sent": "bool", "package_delivered": "bool", "tracking_info": "dict"},
                dependencies=["hotel_recommendations", "taxi_hotspot_analysis"],  # Genie validation is optional
                priority=1
            )
        }
        
        return TaskGraph(
            graph_id="decision_package_001", 
            scenario="hotel_transport_decision_package",
            description="Hotel recommendations + transport insights + email decision package",
            nodes=nodes,
            completion_criteria={
                "required_tasks": ["hotel_recommendations", "taxi_hotspot_analysis", "decision_package"],
                "optional_tasks": ["genie_validation"]
            }
        )


class ConflictResolutionStrategy:
    """Strategies for resolving conflicts between different data sources."""
    
    @staticmethod
    def resolve_conflicts(fabric_data: Dict[str, Any], genie_data: Dict[str, Any], rule: str = "newest_priority") -> Dict[str, Any]:
        """
        Resolve conflicts between Fabric and Genie data sources.
        
        Args:
            fabric_data: Data from Fabric source
            genie_data: Data from Genie source  
            rule: Resolution rule ("newest_priority", "fabric_priority", "genie_priority", "report_difference")
            
        Returns:
            Resolved data with conflict resolution metadata
        """
        resolved_data = {}
        conflicts = []
        
        # Find common fields
        common_fields = set(fabric_data.keys()) & set(genie_data.keys())
        
        for field in common_fields:
            fabric_value = fabric_data.get(field)
            genie_value = genie_data.get(field)
            
            # Check if values are significantly different (for numeric data)
            if isinstance(fabric_value, (int, float)) and isinstance(genie_value, (int, float)):
                if fabric_value != 0:
                    variance = abs(fabric_value - genie_value) / abs(fabric_value)
                    if variance > 0.05:  # 5% threshold
                        conflicts.append({
                            "field": field,
                            "fabric_value": fabric_value,
                            "genie_value": genie_value,
                            "variance_percent": variance * 100
                        })
                        
                        # Apply resolution rule
                        if rule == "newest_priority":
                            resolved_data[field] = genie_value  # Assume Genie is newer
                        elif rule == "fabric_priority":
                            resolved_data[field] = fabric_value
                        elif rule == "genie_priority":
                            resolved_data[field] = genie_value
                        else:  # report_difference
                            resolved_data[field] = {
                                "fabric": fabric_value,
                                "genie": genie_value,
                                "status": "conflict"
                            }
                    else:
                        resolved_data[field] = (fabric_value + genie_value) / 2  # Average for close values
                else:
                    resolved_data[field] = genie_value
            else:
                # For non-numeric data, use rule directly
                if fabric_value != genie_value:
                    conflicts.append({
                        "field": field,
                        "fabric_value": fabric_value,
                        "genie_value": genie_value,
                        "variance_type": "categorical"
                    })
                    
                    if rule == "fabric_priority":
                        resolved_data[field] = fabric_value
                    elif rule == "genie_priority":
                        resolved_data[field] = genie_value
                    else:
                        resolved_data[field] = {
                            "fabric": fabric_value,
                            "genie": genie_value,
                            "status": "conflict"
                        }
                else:
                    resolved_data[field] = fabric_value
        
        # Add fields unique to each source
        for field in fabric_data:
            if field not in common_fields:
                resolved_data[field] = fabric_data[field]
                
        for field in genie_data:
            if field not in common_fields:
                resolved_data[field] = genie_data[field]
        
        return {
            "resolved_data": resolved_data,
            "conflicts": conflicts,
            "resolution_rule": rule,
            "conflict_count": len(conflicts),
            "data_quality_score": max(0, 1 - (len(conflicts) / max(len(common_fields), 1)))
        }