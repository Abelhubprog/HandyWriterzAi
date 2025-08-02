"""
Distributed Coordinator for Multi-Agent Task Management
Handles task distribution, workflow coordination, and inter-agent communication across multiple instances.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager

from .agent_pool import AgentPool, AgentType, AgentInstance

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    task_id: str
    workflow_id: str
    agent_type: AgentType
    payload: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    required_capabilities: Set[str] = field(default_factory=set)
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class Workflow:
    workflow_id: str
    user_id: str
    workflow_type: str
    tasks: List[Task] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class DistributedCoordinator:
    """Coordinates multi-agent workflows across distributed instances"""
    
    def __init__(self, redis_client: redis.Redis, instance_id: str = None):
        self.redis = redis_client
        self.instance_id = instance_id or str(uuid.uuid4())
        self.agent_pool = AgentPool(redis_client)
        self.workflows: Dict[str, Workflow] = {}
        self.task_handlers: Dict[AgentType, Callable] = {}
        self.running = False
        self.worker_tasks: List[asyncio.Task] = []
        
    async def start(self):
        """Start the distributed coordinator"""
        self.running = True
        logger.info(f"Starting distributed coordinator {self.instance_id}")
        
        # Register this instance
        await self.redis.hset(
            "handywriterz:coordinators",
            self.instance_id,
            json.dumps({
                "started_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
        )
        
        # Start worker tasks
        self.worker_tasks = [
            asyncio.create_task(self._task_worker()),
            asyncio.create_task(self._workflow_monitor()),
            asyncio.create_task(self._heartbeat_worker())
        ]
        
        logger.info("Distributed coordinator started successfully")
    
    async def stop(self):
        """Stop the distributed coordinator"""
        self.running = False
        logger.info(f"Stopping distributed coordinator {self.instance_id}")
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        # Unregister this instance
        await self.redis.hdel("handywriterz:coordinators", self.instance_id)
        
        logger.info("Distributed coordinator stopped")
    
    def register_task_handler(self, agent_type: AgentType, handler: Callable):
        """Register a task handler for a specific agent type"""
        self.task_handlers[agent_type] = handler
        logger.info(f"Registered handler for agent type {agent_type.value}")
    
    async def submit_workflow(self, workflow: Workflow) -> str:
        """Submit a new workflow for execution"""
        workflow_id = workflow.workflow_id
        self.workflows[workflow_id] = workflow
        
        # Store workflow in Redis
        await self.redis.hset(
            "handywriterz:workflows",
            workflow_id,
            json.dumps(asdict(workflow), default=str)
        )
        
        # Queue initial tasks (those without dependencies)
        initial_tasks = [task for task in workflow.tasks if not task.dependencies]
        for task in initial_tasks:
            await self._queue_task(task)
        
        logger.info(f"Submitted workflow {workflow_id} with {len(workflow.tasks)} tasks")
        return workflow_id
    
    async def _queue_task(self, task: Task):
        """Queue a task for execution"""
        task_data = asdict(task)
        task_data["created_at"] = task.created_at.isoformat()
        
        # Add to priority queue based on task priority
        priority_score = task.priority.value
        
        await self.redis.zadd(
            "handywriterz:task_queue",
            {json.dumps(task_data, default=str): priority_score}
        )
        
        logger.debug(f"Queued task {task.task_id} with priority {task.priority.value}")
    
    async def _task_worker(self):
        """Worker that processes tasks from the queue"""
        while self.running:
            try:
                # Get highest priority task
                tasks = await self.redis.zpopmax("handywriterz:task_queue", 1)
                
                if not tasks:
                    await asyncio.sleep(1)
                    continue
                
                task_data = json.loads(tasks[0][0])
                task = Task(**{k: v for k, v in task_data.items() if k != "created_at"})
                task.created_at = datetime.fromisoformat(task_data["created_at"])
                
                await self._execute_task(task)
                
            except Exception as e:
                logger.error(f"Error in task worker: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: Task):
        """Execute a single task"""
        try:
            # Acquire agent from pool
            async with self.agent_pool.acquire_agent_context(
                task.agent_type, 
                task.task_id, 
                task.required_capabilities
            ) as agent:
                
                task.assigned_agent = agent.agent_id
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                
                await self._update_task_status(task)
                
                # Get task handler
                handler = self.task_handlers.get(task.agent_type)
                if not handler:
                    raise ValueError(f"No handler registered for agent type {task.agent_type.value}")
                
                # Execute task with timeout
                try:
                    result = await asyncio.wait_for(
                        handler(agent, task.payload),
                        timeout=task.timeout_seconds
                    )
                    
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
                    
                    logger.info(f"Task {task.task_id} completed successfully")
                    
                except asyncio.TimeoutError:
                    raise Exception(f"Task timed out after {task.timeout_seconds} seconds")
                
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            logger.error(f"Task {task.task_id} failed: {e}")
            
            # Retry if possible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.assigned_agent = None
                task.started_at = None
                task.completed_at = None
                task.error_message = None
                
                # Re-queue with delay
                await asyncio.sleep(min(2 ** task.retry_count, 30))  # Exponential backoff
                await self._queue_task(task)
                
                logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count + 1})")
        
        finally:
            await self._update_task_status(task)
            await self._check_workflow_completion(task.workflow_id)
    
    async def _update_task_status(self, task: Task):
        """Update task status in Redis"""
        await self.redis.hset(
            f"handywriterz:tasks:{task.workflow_id}",
            task.task_id,
            json.dumps(asdict(task), default=str)
        )
    
    async def _check_workflow_completion(self, workflow_id: str):
        """Check if a workflow is complete and queue dependent tasks"""
        if workflow_id not in self.workflows:
            return
        
        workflow = self.workflows[workflow_id]
        completed_tasks = set()
        failed_tasks = set()
        
        # Check status of all tasks
        for task in workflow.tasks:
            if task.status == TaskStatus.COMPLETED:
                completed_tasks.add(task.task_id)
            elif task.status == TaskStatus.FAILED and task.retry_count >= task.max_retries:
                failed_tasks.add(task.task_id)
        
        # Queue tasks whose dependencies are now satisfied
        for task in workflow.tasks:
            if (task.status == TaskStatus.PENDING and 
                set(task.dependencies).issubset(completed_tasks)):
                await self._queue_task(task)
        
        # Check if workflow is complete
        all_tasks_done = all(
            task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            for task in workflow.tasks
        )
        
        if all_tasks_done:
            if failed_tasks:
                workflow.status = TaskStatus.FAILED
                logger.warning(f"Workflow {workflow_id} failed with {len(failed_tasks)} failed tasks")
            else:
                workflow.status = TaskStatus.COMPLETED
                logger.info(f"Workflow {workflow_id} completed successfully")
            
            workflow.completed_at = datetime.utcnow()
            
            # Update workflow in Redis
            await self.redis.hset(
                "handywriterz:workflows",
                workflow_id,
                json.dumps(asdict(workflow), default=str)
            )
    
    async def _workflow_monitor(self):
        """Monitor workflows for timeouts and cleanup"""
        while self.running:
            try:
                # Check for timed out workflows
                cutoff_time = datetime.utcnow() - timedelta(hours=1)  # 1 hour timeout
                
                for workflow_id, workflow in list(self.workflows.items()):
                    if (workflow.status in [TaskStatus.PENDING, TaskStatus.RUNNING] and
                        workflow.created_at < cutoff_time):
                        
                        workflow.status = TaskStatus.FAILED
                        workflow.completed_at = datetime.utcnow()
                        
                        logger.warning(f"Workflow {workflow_id} timed out")
                        
                        # Update in Redis
                        await self.redis.hset(
                            "handywriterz:workflows",
                            workflow_id,
                            json.dumps(asdict(workflow), default=str)
                        )
                
                # Cleanup completed workflows older than 24 hours
                cleanup_cutoff = datetime.utcnow() - timedelta(hours=24)
                workflows_to_remove = [
                    workflow_id for workflow_id, workflow in self.workflows.items()
                    if (workflow.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and
                        workflow.completed_at and workflow.completed_at < cleanup_cutoff)
                ]
                
                for workflow_id in workflows_to_remove:
                    del self.workflows[workflow_id]
                    await self.redis.hdel("handywriterz:workflows", workflow_id)
                    await self.redis.delete(f"handywriterz:tasks:{workflow_id}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in workflow monitor: {e}")
                await asyncio.sleep(60)
    
    async def _heartbeat_worker(self):
        """Send periodic heartbeat to indicate this instance is alive"""
        while self.running:
            try:
                await self.redis.hset(
                    "handywriterz:coordinators",
                    self.instance_id,
                    json.dumps({
                        "last_heartbeat": datetime.utcnow().isoformat(),
                        "status": "active",
                        "workflows_count": len(self.workflows)
                    })
                )
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat worker: {e}")
                await asyncio.sleep(30)
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            return asdict(workflow)
        
        # Try to load from Redis
        workflow_data = await self.redis.hget("handywriterz:workflows", workflow_id)
        if workflow_data:
            return json.loads(workflow_data)
        
        return None
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        workflow.status = TaskStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()
        
        # Cancel all pending/running tasks
        for task in workflow.tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
        
        # Update in Redis
        await self.redis.hset(
            "handywriterz:workflows",
            workflow_id,
            json.dumps(asdict(workflow), default=str)
        )
        
        logger.info(f"Cancelled workflow {workflow_id}")
        return True
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        # Get coordinator stats
        coordinators = await self.redis.hgetall("handywriterz:coordinators")
        active_coordinators = []
        
        for coord_id, data in coordinators.items():
            coord_data = json.loads(data)
            coord_data["coordinator_id"] = coord_id
            active_coordinators.append(coord_data)
        
        # Get queue stats
        queue_size = await self.redis.zcard("handywriterz:task_queue")
        
        # Get agent pool stats
        pool_stats = await self.agent_pool.get_pool_stats()
        
        # Get workflow stats
        workflow_count = len(self.workflows)
        running_workflows = sum(1 for w in self.workflows.values() 
                              if w.status == TaskStatus.RUNNING)
        
        return {
            "coordinators": {
                "total": len(active_coordinators),
                "instances": active_coordinators
            },
            "queue": {
                "pending_tasks": queue_size
            },
            "workflows": {
                "total": workflow_count,
                "running": running_workflows
            },
            "agent_pool": pool_stats,
            "system": {
                "instance_id": self.instance_id,
                "uptime": datetime.utcnow().isoformat()
            }
        }