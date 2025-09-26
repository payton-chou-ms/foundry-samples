# Agent Coordination Core Implementation

"""
Core orchestration logic for multi-agent coordination using Semantic Kernel concepts.
This module provides the foundational classes and utilities for agent management,
task planning, and execution coordination.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import uuid

# Configure logging
logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ExecutionStrategy(Enum):
    """Execution strategy options"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel" 
    HYBRID = "hybrid"

@dataclass
class AgentCapability:
    """Describes an agent's capabilities"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    average_execution_time: float
    success_rate: float
    dependencies: List[str] = field(default_factory=list)

@dataclass
class ExecutionContext:
    """Context passed between agents during execution"""
    session_id: str
    user_id: str
    request_id: str
    timestamp: datetime
    user_request: str
    shared_data: Dict[str, Any] = field(default_factory=dict)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_execution_record(self, agent_name: str, status: str, result: Any = None, error: str = None):
        """Add an execution record to the history"""
        record = {
            'agent_name': agent_name,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result,
            'error': error
        }
        self.execution_history.append(record)

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str, capabilities: AgentCapability):
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.is_available = True
        self.current_load = 0
        self.max_concurrent_tasks = 5
    
    @abstractmethod
    async def execute_task(self, task: 'AgentTask', context: ExecutionContext) -> 'AgentResult':
        """Execute a specific task"""
        pass
    
    def can_handle_task(self, task: 'AgentTask') -> bool:
        """Determine if this agent can handle the given task"""
        return (self.is_available and 
                self.current_load < self.max_concurrent_tasks and
                task.agent_name == self.name)
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Basic health check implementation
            await asyncio.sleep(0.1)  # Simulate health check
            return True
        except Exception as e:
            logger.error(f"Health check failed for agent {self.name}: {e}")
            return False

class TaskPlanner:
    """Intelligent task planning using semantic analysis"""
    
    def __init__(self):
        self.planning_rules = self._load_planning_rules()
        self.agent_registry = {}
    
    def _load_planning_rules(self) -> Dict[str, Any]:
        """Load planning rules for task decomposition"""
        return {
            'hotel_search_triggers': [
                'hotel', 'accommodation', 'booking', 'stay', 'lodging', 'room'
            ],
            'data_analysis_triggers': [
                'analyze', 'data', 'pattern', 'trend', 'statistics', 'report'
            ],
            'automation_triggers': [
                'send', 'email', 'notify', 'automate', 'schedule', 'workflow'
            ],
            'advanced_analytics_triggers': [
                'correlate', 'predict', 'optimize', 'machine learning', 'advanced'
            ]
        }
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the planner"""
        self.agent_registry[agent.name] = agent
    
    async def create_execution_plan(self, user_request: str, context: ExecutionContext) -> 'ExecutionPlan':
        """Create an execution plan based on user request"""
        
        # Analyze request to determine required agents
        required_agents = await self._analyze_request(user_request)
        
        # Create tasks with dependencies
        tasks = await self._create_tasks(required_agents, user_request, context)
        
        # Optimize execution order
        execution_order = self._optimize_execution_order(tasks)
        
        # Determine execution strategy
        strategy = self._determine_execution_strategy(tasks)
        
        return ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            tasks=tasks,
            execution_order=execution_order,
            strategy=strategy,
            estimated_duration=self._estimate_duration(tasks),
            context=context
        )
    
    async def _analyze_request(self, user_request: str) -> List[str]:
        """Analyze user request to determine required agents"""
        request_lower = user_request.lower()
        required_agents = []
        
        # Check for hotel search requirements
        if any(trigger in request_lower for trigger in self.planning_rules['hotel_search_triggers']):
            required_agents.append('hotel_search')
        
        # Check for data analysis requirements  
        if any(trigger in request_lower for trigger in self.planning_rules['data_analysis_triggers']):
            required_agents.append('fabric_analyst')
        
        # Check for advanced analytics requirements
        if any(trigger in request_lower for trigger in self.planning_rules['advanced_analytics_triggers']):
            required_agents.append('databricks_genie')
        
        # Check for automation requirements
        if any(trigger in request_lower for trigger in self.planning_rules['automation_triggers']):
            required_agents.append('logic_app')
        
        return required_agents
    
    async def _create_tasks(self, required_agents: List[str], user_request: str, 
                           context: ExecutionContext) -> List['AgentTask']:
        """Create specific tasks for each required agent"""
        tasks = []
        
        for agent_name in required_agents:
            task = AgentTask(
                task_id=str(uuid.uuid4()),
                agent_name=agent_name,
                task_description=self._generate_task_description(agent_name, user_request),
                input_parameters=self._generate_input_parameters(agent_name, user_request, context),
                priority=TaskPriority.MEDIUM,
                dependencies=self._determine_dependencies(agent_name, required_agents),
                timeout_seconds=60,
                created_at=datetime.utcnow()
            )
            tasks.append(task)
        
        return tasks
    
    def _generate_task_description(self, agent_name: str, user_request: str) -> str:
        """Generate specific task description for an agent"""
        descriptions = {
            'hotel_search': f"Search for hotels based on user requirements: {user_request[:100]}",
            'fabric_analyst': f"Analyze data patterns related to: {user_request[:100]}", 
            'databricks_genie': f"Perform advanced analytics for: {user_request[:100]}",
            'logic_app': f"Execute automation workflow for: {user_request[:100]}"
        }
        return descriptions.get(agent_name, f"Execute task for {agent_name}")
    
    def _generate_input_parameters(self, agent_name: str, user_request: str, 
                                  context: ExecutionContext) -> Dict[str, Any]:
        """Generate input parameters specific to each agent"""
        base_params = {
            'user_request': user_request,
            'session_id': context.session_id,
            'request_id': context.request_id
        }
        
        # Agent-specific parameters
        if agent_name == 'hotel_search':
            base_params.update({
                'search_criteria': self._extract_hotel_criteria(user_request),
                'location': self._extract_location(user_request)
            })
        elif agent_name == 'fabric_analyst':
            base_params.update({
                'analysis_type': self._determine_analysis_type(user_request),
                'data_sources': ['taxi_trips']
            })
        elif agent_name == 'databricks_genie':
            base_params.update({
                'analytics_type': 'advanced',
                'require_context': True
            })
        elif agent_name == 'logic_app':
            base_params.update({
                'workflow_type': 'notification',
                'recipients': ['default@company.com']
            })
        
        return base_params
    
    def _determine_dependencies(self, agent_name: str, all_agents: List[str]) -> List[str]:
        """Determine dependencies for an agent"""
        dependency_rules = {
            'databricks_genie': ['hotel_search', 'fabric_analyst'],  # Needs context from other agents
            'logic_app': ['hotel_search', 'fabric_analyst', 'databricks_genie']  # Should run last
        }
        
        dependencies = dependency_rules.get(agent_name, [])
        return [dep for dep in dependencies if dep in all_agents]
    
    def _optimize_execution_order(self, tasks: List['AgentTask']) -> List[str]:
        """Optimize the execution order of tasks"""
        # Topological sort based on dependencies
        task_dict = {task.agent_name: task for task in tasks}
        visited = set()
        order = []
        
        def visit(agent_name: str):
            if agent_name in visited:
                return
            visited.add(agent_name)
            
            task = task_dict.get(agent_name)
            if task:
                for dep in task.dependencies:
                    if dep in task_dict:
                        visit(dep)
                order.append(agent_name)
        
        for task in tasks:
            visit(task.agent_name)
        
        return order
    
    def _determine_execution_strategy(self, tasks: List['AgentTask']) -> ExecutionStrategy:
        """Determine the best execution strategy"""
        has_dependencies = any(task.dependencies for task in tasks)
        
        if not has_dependencies:
            return ExecutionStrategy.PARALLEL
        elif len(tasks) <= 2:
            return ExecutionStrategy.SEQUENTIAL
        else:
            return ExecutionStrategy.HYBRID
    
    def _estimate_duration(self, tasks: List['AgentTask']) -> float:
        """Estimate total execution duration"""
        # Simple estimation based on average execution times
        agent_durations = {
            'hotel_search': 5.0,
            'fabric_analyst': 8.0,
            'databricks_genie': 12.0,
            'logic_app': 3.0
        }
        
        total_duration = sum(agent_durations.get(task.agent_name, 5.0) for task in tasks)
        
        # Adjust for parallelism
        if len(tasks) > 1 and not any(task.dependencies for task in tasks):
            total_duration *= 0.6  # Parallel execution benefit
        
        return total_duration
    
    def _extract_hotel_criteria(self, user_request: str) -> Dict[str, Any]:
        """Extract hotel search criteria from user request"""
        # Simple keyword extraction - in real implementation would use NLP
        criteria = {}
        request_lower = user_request.lower()
        
        if 'luxury' in request_lower or 'high-quality' in request_lower:
            criteria['rating_min'] = 4.5
        elif 'boutique' in request_lower:
            criteria['category'] = 'boutique'
        
        return criteria
    
    def _extract_location(self, user_request: str) -> Optional[str]:
        """Extract location from user request"""
        # Simple location extraction
        common_cities = ['new york', 'manhattan', 'chicago', 'los angeles', 'miami']
        request_lower = user_request.lower()
        
        for city in common_cities:
            if city in request_lower:
                return city.title()
        
        return None
    
    def _determine_analysis_type(self, user_request: str) -> str:
        """Determine the type of analysis needed"""
        request_lower = user_request.lower()
        
        if 'pattern' in request_lower or 'trend' in request_lower:
            return 'trend_analysis'
        elif 'compare' in request_lower or 'comparison' in request_lower:
            return 'comparative_analysis'
        else:
            return 'general_analysis'

@dataclass 
class AgentTask:
    """Represents a task to be executed by an agent"""
    task_id: str
    agent_name: str
    task_description: str
    input_parameters: Dict[str, Any]
    priority: TaskPriority
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 60
    max_retries: int = 2
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

@dataclass
class AgentResult:
    """Represents the result from an agent execution"""
    task_id: str
    agent_name: str
    status: str  # 'completed', 'failed', 'timeout', 'cancelled'
    result_data: Any = None
    error_message: str = ""
    execution_time_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class ExecutionPlan:
    """Represents an execution plan for multiple agents"""
    plan_id: str
    tasks: List[AgentTask]
    execution_order: List[str]
    strategy: ExecutionStrategy
    estimated_duration: float
    context: ExecutionContext
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, executing, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'plan_id': self.plan_id,
            'tasks': [task.to_dict() for task in self.tasks],
            'execution_order': self.execution_order,
            'strategy': self.strategy.value,
            'estimated_duration': self.estimated_duration,
            'created_at': self.created_at.isoformat(),
            'status': self.status
        }

class ExecutionMonitor:
    """Monitors and tracks execution progress"""
    
    def __init__(self):
        self.active_executions: Dict[str, ExecutionPlan] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, List[float]] = {}
    
    def start_monitoring(self, plan: ExecutionPlan):
        """Start monitoring an execution plan"""
        self.active_executions[plan.plan_id] = plan
        logger.info(f"Started monitoring execution plan {plan.plan_id}")
    
    def update_task_status(self, plan_id: str, task_id: str, status: str, result: AgentResult = None):
        """Update the status of a specific task"""
        if plan_id in self.active_executions:
            plan = self.active_executions[plan_id]
            
            # Find and update the task
            for task in plan.tasks:
                if task.task_id == task_id:
                    if status == 'started':
                        task.started_at = datetime.utcnow()
                    elif status in ['completed', 'failed', 'timeout']:
                        task.completed_at = datetime.utcnow()
                    break
            
            # Record performance metrics
            if result and result.status == 'completed':
                agent_name = result.agent_name
                if agent_name not in self.performance_metrics:
                    self.performance_metrics[agent_name] = []
                self.performance_metrics[agent_name].append(result.execution_time_seconds)
    
    def complete_monitoring(self, plan_id: str, final_status: str):
        """Complete monitoring for an execution plan"""
        if plan_id in self.active_executions:
            plan = self.active_executions[plan_id]
            plan.status = final_status
            
            # Move to history
            self.execution_history.append({
                'plan': plan.to_dict(),
                'completed_at': datetime.utcnow().isoformat(),
                'final_status': final_status
            })
            
            # Remove from active executions
            del self.active_executions[plan_id]
            
            logger.info(f"Completed monitoring for execution plan {plan_id} with status {final_status}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all agents"""
        summary = {}
        
        for agent_name, execution_times in self.performance_metrics.items():
            if execution_times:
                summary[agent_name] = {
                    'average_execution_time': sum(execution_times) / len(execution_times),
                    'min_execution_time': min(execution_times),
                    'max_execution_time': max(execution_times),
                    'total_executions': len(execution_times)
                }
        
        return summary

# Utility functions for agent coordination

def create_context(user_request: str, session_id: str = None, user_id: str = None) -> ExecutionContext:
    """Create a new execution context"""
    return ExecutionContext(
        session_id=session_id or str(uuid.uuid4()),
        user_id=user_id or "anonymous", 
        request_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        user_request=user_request
    )

async def validate_execution_plan(plan: ExecutionPlan) -> List[str]:
    """Validate an execution plan and return any issues found"""
    issues = []
    
    # Check for circular dependencies
    def has_circular_dependency(task_name: str, visited: set, path: set) -> bool:
        if task_name in path:
            return True
        if task_name in visited:
            return False
            
        visited.add(task_name)
        path.add(task_name)
        
        # Find task and check its dependencies
        task = next((t for t in plan.tasks if t.agent_name == task_name), None)
        if task:
            for dep in task.dependencies:
                if has_circular_dependency(dep, visited, path):
                    return True
        
        path.remove(task_name)
        return False
    
    visited = set()
    for task in plan.tasks:
        if has_circular_dependency(task.agent_name, visited, set()):
            issues.append(f"Circular dependency detected involving {task.agent_name}")
    
    # Check for missing dependencies
    task_names = {task.agent_name for task in plan.tasks}
    for task in plan.tasks:
        for dep in task.dependencies:
            if dep not in task_names:
                issues.append(f"Task {task.agent_name} depends on missing task {dep}")
    
    return issues

def optimize_parallel_execution(tasks: List[AgentTask]) -> List[List[str]]:
    """Optimize tasks for parallel execution, returning groups that can run in parallel"""
    execution_groups = []
    remaining_tasks = {task.agent_name: task for task in tasks}
    completed_tasks = set()
    
    while remaining_tasks:
        # Find tasks with satisfied dependencies
        ready_tasks = []
        for task_name, task in remaining_tasks.items():
            if all(dep in completed_tasks for dep in task.dependencies):
                ready_tasks.append(task_name)
        
        if not ready_tasks:
            # No more tasks can be executed - possible circular dependency
            break
        
        # Add ready tasks to current group
        execution_groups.append(ready_tasks)
        
        # Mark tasks as completed and remove from remaining
        for task_name in ready_tasks:
            completed_tasks.add(task_name)
            del remaining_tasks[task_name]
    
    return execution_groups