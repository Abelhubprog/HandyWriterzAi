"""
Comprehensive Observability & Monitoring System
Distributed tracing, agent performance metrics, predictive analytics, and quality tracking.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel
import logging
from contextlib import asynccontextmanager
from collections import defaultdict, deque
import numpy as np
from opentelemetry import trace, metrics, baggage
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, Summary

logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class TraceSpan:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "success"  # success, error, timeout

@dataclass
class AgentMetrics:
    agent_id: str
    agent_type: str
    provider: str
    model: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    total_cost: float = 0.0
    avg_cost_per_request: float = 0.0
    quality_scores: List[float] = field(default_factory=list)
    error_rates: Dict[str, int] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SystemMetrics:
    timestamp: datetime = field(default_factory=datetime.utcnow)
    active_agents: int = 0
    active_workflows: int = 0
    queue_depth: int = 0
    cache_hit_rate: float = 0.0
    total_cost_per_hour: float = 0.0
    avg_workflow_duration: float = 0.0
    error_rate: float = 0.0
    throughput_per_minute: float = 0.0

@dataclass
class Alert:
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    metric_name: str
    threshold: float
    current_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False

class DistributedTracer:
    """Distributed tracing for multi-agent workflows"""
    
    def __init__(self, service_name: str = "handywriterz-agents"):
        self.service_name = service_name
        self.active_spans: Dict[str, TraceSpan] = {}
        
        # Initialize OpenTelemetry
        trace.set_tracer_provider(TracerProvider())
        self.tracer = trace.get_tracer(__name__)
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=14268,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument asyncio
        AsyncioInstrumentor().instrument()
    
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, **tags):
        """Context manager for tracing operations"""
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow(),
            tags=tags
        )
        
        self.active_spans[span_id] = span
        
        # OpenTelemetry span
        with self.tracer.start_as_current_span(operation_name) as otel_span:
            otel_span.set_attributes(tags)
            
            try:
                yield span
                span.status = "success"
            except Exception as e:
                span.status = "error"
                span.tags["error"] = str(e)
                otel_span.record_exception(e)
                raise
            finally:
                span.end_time = datetime.utcnow()
                span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
                
                # Clean up
                if span_id in self.active_spans:
                    del self.active_spans[span_id]
    
    async def add_span_log(self, span_id: str, event: str, **fields):
        """Add log entry to span"""
        if span_id in self.active_spans:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": event,
                **fields
            }
            self.active_spans[span_id].logs.append(log_entry)

class MetricsCollector:
    """Collects and aggregates system and agent metrics"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.system_metrics_history: deque = deque(maxlen=1440)  # 24 hours at 1min intervals
        
        # Prometheus metrics
        self.prometheus_metrics = {
            "agent_requests_total": Counter(
                "agent_requests_total",
                "Total number of agent requests",
                ["agent_type", "provider", "model", "status"]
            ),
            "agent_response_duration": Histogram(
                "agent_response_duration_seconds",
                "Agent response duration in seconds",
                ["agent_type", "provider", "model"]
            ),
            "agent_cost_total": Counter(
                "agent_cost_total_usd",
                "Total cost in USD",
                ["agent_type", "provider", "model"]
            ),
            "workflow_duration": Histogram(
                "workflow_duration_seconds",
                "Workflow duration in seconds",
                ["content_type", "complexity"]
            ),
            "cache_operations": Counter(
                "cache_operations_total",
                "Cache operations",
                ["operation", "level", "category"]
            ),
            "system_errors": Counter(
                "system_errors_total",
                "System errors",
                ["component", "error_type"]
            ),
            "active_agents": Gauge(
                "active_agents",
                "Number of active agents",
                ["agent_type"]
            ),
            "queue_depth": Gauge(
                "queue_depth",
                "Number of tasks in queue"
            )
        }
    
    async def record_agent_request(
        self,
        agent_id: str,
        agent_type: str,
        provider: str,
        model: str,
        duration_seconds: float,
        cost_usd: float,
        success: bool,
        quality_score: Optional[float] = None,
        error_type: Optional[str] = None
    ):
        """Record metrics for an agent request"""
        
        # Update agent metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_type=agent_type,
                provider=provider,
                model=model
            )
        
        metrics = self.agent_metrics[agent_id]
        metrics.total_requests += 1
        metrics.last_activity = datetime.utcnow()
        
        if success:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1
            if error_type:
                metrics.error_rates[error_type] = metrics.error_rates.get(error_type, 0) + 1
        
        # Update timing metrics
        metrics.avg_response_time = (
            (metrics.avg_response_time * (metrics.total_requests - 1) + duration_seconds) 
            / metrics.total_requests
        )
        metrics.min_response_time = min(metrics.min_response_time, duration_seconds)
        metrics.max_response_time = max(metrics.max_response_time, duration_seconds)
        
        # Update cost metrics
        metrics.total_cost += cost_usd
        metrics.avg_cost_per_request = metrics.total_cost / metrics.total_requests
        
        # Update quality scores
        if quality_score is not None:
            metrics.quality_scores.append(quality_score)
            # Keep only last 100 scores
            if len(metrics.quality_scores) > 100:
                metrics.quality_scores = metrics.quality_scores[-100:]
        
        # Prometheus metrics
        status = "success" if success else "error"
        self.prometheus_metrics["agent_requests_total"].labels(
            agent_type=agent_type,
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        self.prometheus_metrics["agent_response_duration"].labels(
            agent_type=agent_type,
            provider=provider,
            model=model
        ).observe(duration_seconds)
        
        self.prometheus_metrics["agent_cost_total"].labels(
            agent_type=agent_type,
            provider=provider,
            model=model
        ).inc(cost_usd)
        
        # Store in Redis for persistence
        await self._store_agent_metrics(agent_id, metrics)
    
    async def record_workflow_metrics(
        self,
        workflow_id: str,
        content_type: str,
        complexity_score: float,
        duration_seconds: float,
        total_cost: float,
        success: bool,
        quality_score: Optional[float] = None
    ):
        """Record metrics for a complete workflow"""
        
        complexity_bucket = "low" if complexity_score < 4 else "medium" if complexity_score < 7 else "high"
        
        self.prometheus_metrics["workflow_duration"].labels(
            content_type=content_type,
            complexity=complexity_bucket
        ).observe(duration_seconds)
        
        # Store workflow metrics
        workflow_metrics = {
            "workflow_id": workflow_id,
            "content_type": content_type,
            "complexity_score": complexity_score,
            "duration_seconds": duration_seconds,
            "total_cost": total_cost,
            "success": success,
            "quality_score": quality_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.redis.lpush(
            "handywriterz:workflow_metrics",
            json.dumps(workflow_metrics)
        )
        await self.redis.ltrim("handywriterz:workflow_metrics", 0, 10000)  # Keep last 10k
    
    async def record_system_metrics(self, metrics: SystemMetrics):
        """Record system-wide metrics"""
        
        self.system_metrics_history.append(metrics)
        
        # Update Prometheus gauges
        self.prometheus_metrics["queue_depth"].set(metrics.queue_depth)
        
        # Store in Redis
        await self.redis.lpush(
            "handywriterz:system_metrics",
            json.dumps(asdict(metrics), default=str)
        )
        await self.redis.ltrim("handywriterz:system_metrics", 0, 1440)  # Keep 24 hours
    
    async def get_agent_performance_report(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive performance report for an agent"""
        
        if agent_id not in self.agent_metrics:
            return None
        
        metrics = self.agent_metrics[agent_id]
        
        # Calculate derived metrics
        success_rate = metrics.successful_requests / metrics.total_requests if metrics.total_requests > 0 else 0
        avg_quality = np.mean(metrics.quality_scores) if metrics.quality_scores else 0
        quality_std = np.std(metrics.quality_scores) if len(metrics.quality_scores) > 1 else 0
        
        return {
            "agent_id": agent_id,
            "agent_type": metrics.agent_type,
            "provider": metrics.provider,
            "model": metrics.model,
            "performance": {
                "total_requests": metrics.total_requests,
                "success_rate": success_rate,
                "avg_response_time": metrics.avg_response_time,
                "response_time_range": {
                    "min": metrics.min_response_time,
                    "max": metrics.max_response_time
                }
            },
            "cost": {
                "total_cost": metrics.total_cost,
                "avg_cost_per_request": metrics.avg_cost_per_request
            },
            "quality": {
                "avg_score": avg_quality,
                "score_std": quality_std,
                "sample_count": len(metrics.quality_scores)
            },
            "errors": dict(metrics.error_rates),
            "last_activity": metrics.last_activity.isoformat()
        }
    
    async def _store_agent_metrics(self, agent_id: str, metrics: AgentMetrics):
        """Store agent metrics in Redis"""
        await self.redis.hset(
            "handywriterz:agent_metrics",
            agent_id,
            json.dumps(asdict(metrics), default=str)
        )

class AlertManager:
    """Manages alerts and notifications for system health"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # Initialize default alert rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alerting rules"""
        self.alert_rules = {
            "high_error_rate": {
                "metric": "error_rate",
                "threshold": 0.1,  # 10%
                "comparison": "greater_than",
                "window_minutes": 5,
                "level": AlertLevel.WARNING,
                "description": "Error rate exceeds 10% over 5 minutes"
            },
            "critical_error_rate": {
                "metric": "error_rate",
                "threshold": 0.25,  # 25%
                "comparison": "greater_than",
                "window_minutes": 2,
                "level": AlertLevel.CRITICAL,
                "description": "Error rate exceeds 25% over 2 minutes"
            },
            "high_response_time": {
                "metric": "avg_response_time",
                "threshold": 30.0,  # 30 seconds
                "comparison": "greater_than",
                "window_minutes": 5,
                "level": AlertLevel.WARNING,
                "description": "Average response time exceeds 30 seconds"
            },
            "budget_threshold": {
                "metric": "hourly_cost",
                "threshold": 15.0,  # $15/hour
                "comparison": "greater_than",
                "window_minutes": 60,
                "level": AlertLevel.WARNING,
                "description": "Hourly cost exceeds $15"
            },
            "queue_backlog": {
                "metric": "queue_depth",
                "threshold": 100,
                "comparison": "greater_than",
                "window_minutes": 5,
                "level": AlertLevel.WARNING,
                "description": "Queue depth exceeds 100 tasks"
            },
            "agent_failure": {
                "metric": "agent_availability",
                "threshold": 0.5,  # 50% agents down
                "comparison": "less_than",
                "window_minutes": 2,
                "level": AlertLevel.CRITICAL,
                "description": "More than 50% of agents are unavailable"
            }
        }
    
    async def check_alerts(self, current_metrics: Dict[str, float]):
        """Check current metrics against alert rules"""
        
        new_alerts = []
        resolved_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            metric_value = current_metrics.get(rule["metric"], 0)
            threshold = rule["threshold"]
            comparison = rule["comparison"]
            
            # Check if alert condition is met
            alert_triggered = False
            if comparison == "greater_than" and metric_value > threshold:
                alert_triggered = True
            elif comparison == "less_than" and metric_value < threshold:
                alert_triggered = True
            elif comparison == "equals" and metric_value == threshold:
                alert_triggered = True
            
            alert_id = f"{rule_name}_{int(datetime.utcnow().timestamp())}"
            
            if alert_triggered:
                # Check if this alert is already active
                existing_alert = next(
                    (alert for alert in self.active_alerts.values() 
                     if alert.metric_name == rule["metric"] and not alert.resolved),
                    None
                )
                
                if not existing_alert:
                    # Create new alert
                    alert = Alert(
                        alert_id=alert_id,
                        level=rule["level"],
                        title=f"Alert: {rule_name}",
                        description=rule["description"],
                        metric_name=rule["metric"],
                        threshold=threshold,
                        current_value=metric_value
                    )
                    
                    self.active_alerts[alert_id] = alert
                    new_alerts.append(alert)
                    
                    logger.warning(f"Alert triggered: {rule_name} - {rule['description']}")
            
            else:
                # Check if we should resolve any active alerts for this metric
                for alert_id, alert in list(self.active_alerts.items()):
                    if (alert.metric_name == rule["metric"] and 
                        not alert.resolved and 
                        not alert_triggered):
                        
                        alert.resolved = True
                        resolved_alerts.append(alert)
                        
                        logger.info(f"Alert resolved: {alert.title}")
        
        # Store alerts in Redis and history
        for alert in new_alerts:
            await self._store_alert(alert)
            self.alert_history.append(alert)
        
        for alert in resolved_alerts:
            await self._update_alert(alert)
        
        return new_alerts, resolved_alerts
    
    async def _store_alert(self, alert: Alert):
        """Store alert in Redis"""
        await self.redis.hset(
            "handywriterz:active_alerts",
            alert.alert_id,
            json.dumps(asdict(alert), default=str)
        )
        
        # Add to alert log
        await self.redis.lpush(
            "handywriterz:alert_log",
            json.dumps(asdict(alert), default=str)
        )
        await self.redis.ltrim("handywriterz:alert_log", 0, 1000)
    
    async def _update_alert(self, alert: Alert):
        """Update alert in Redis"""
        await self.redis.hset(
            "handywriterz:active_alerts",
            alert.alert_id,
            json.dumps(asdict(alert), default=str)
        )
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.acknowledged = True
            alert.tags = alert.tags or {}
            alert.tags["acknowledged_by"] = user_id
            alert.tags["acknowledged_at"] = datetime.utcnow().isoformat()
            
            await self._update_alert(alert)
            logger.info(f"Alert {alert_id} acknowledged by {user_id}")
            return True
        
        return False

class MonitoringSystem:
    """Main monitoring system orchestrator"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.tracer = DistributedTracer()
        self.metrics_collector = MetricsCollector(redis_client)
        self.alert_manager = AlertManager(redis_client)
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
        
        # Predictive analytics
        self.prediction_models: Dict[str, Any] = {}
        self.capacity_forecasts: Dict[str, List[float]] = defaultdict(list)
    
    async def start(self):
        """Start monitoring system"""
        self.running = True
        
        # Start background workers
        self.background_tasks = [
            asyncio.create_task(self._metrics_collection_worker()),
            asyncio.create_task(self._alert_checking_worker()),
            asyncio.create_task(self._capacity_prediction_worker()),
            asyncio.create_task(self._health_check_worker())
        ]
        
        logger.info("Monitoring system started")
    
    async def stop(self):
        """Stop monitoring system"""
        self.running = False
        
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        logger.info("Monitoring system stopped")
    
    async def _metrics_collection_worker(self):
        """Background worker for collecting system metrics"""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                await self.metrics_collector.record_system_metrics(system_metrics)
                
                # Collect agent pool metrics
                await self._collect_agent_pool_metrics()
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_checking_worker(self):
        """Background worker for checking alerts"""
        while self.running:
            try:
                # Get current metrics for alerting
                current_metrics = await self._get_current_metrics()
                
                # Check alerts
                new_alerts, resolved_alerts = await self.alert_manager.check_alerts(current_metrics)
                
                # Send notifications (implement as needed)
                for alert in new_alerts:
                    await self._send_alert_notification(alert)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert checking error: {e}")
                await asyncio.sleep(30)
    
    async def _capacity_prediction_worker(self):
        """Background worker for capacity prediction"""
        while self.running:
            try:
                # Simple linear regression for capacity forecasting
                await self._update_capacity_forecasts()
                
                # Check if scaling recommendations are needed
                recommendations = await self._generate_scaling_recommendations()
                
                if recommendations:
                    logger.info(f"Scaling recommendations: {recommendations}")
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Capacity prediction error: {e}")
                await asyncio.sleep(300)
    
    async def _health_check_worker(self):
        """Background worker for health checks"""
        while self.running:
            try:
                # Check component health
                health_status = await self._perform_health_checks()
                
                # Store health status
                await self.redis.hset(
                    "handywriterz:health_status",
                    "system",
                    json.dumps(health_status, default=str)
                )
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(120)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # Get active agents count
        active_agents = len(await self.redis.hgetall("handywriterz:agents"))
        
        # Get queue depth
        queue_depth = await self.redis.zcard("handywriterz:task_queue")
        
        # Get cache hit rate
        cache_stats = await self.redis.hgetall("handywriterz:cache_stats")
        cache_hit_rate = 0.0
        if cache_stats:
            hits = int(cache_stats.get("hits", 0))
            misses = int(cache_stats.get("misses", 0))
            total = hits + misses
            cache_hit_rate = hits / total if total > 0 else 0.0
        
        # Calculate error rate from recent requests
        recent_errors = await self._calculate_recent_error_rate()
        
        # Calculate throughput
        throughput = await self._calculate_throughput()
        
        return SystemMetrics(
            active_agents=active_agents,
            queue_depth=queue_depth,
            cache_hit_rate=cache_hit_rate,
            error_rate=recent_errors,
            throughput_per_minute=throughput
        )
    
    async def _collect_agent_pool_metrics(self):
        """Collect metrics for all agents in the pool"""
        agent_data = await self.redis.hgetall("handywriterz:agents")
        
        for agent_id, data in agent_data.items():
            try:
                agent_info = json.loads(data)
                # Update Prometheus gauge for active agents
                agent_type = agent_info.get("type", "unknown")
                self.metrics_collector.prometheus_metrics["active_agents"].labels(
                    agent_type=agent_type
                ).set(1)
                
            except Exception as e:
                logger.warning(f"Failed to parse agent data for {agent_id}: {e}")
    
    async def _get_current_metrics(self) -> Dict[str, float]:
        """Get current metrics for alert checking"""
        # This would typically aggregate from various sources
        return {
            "error_rate": await self._calculate_recent_error_rate(),
            "avg_response_time": await self._calculate_avg_response_time(),
            "queue_depth": await self.redis.zcard("handywriterz:task_queue"),
            "hourly_cost": await self._calculate_hourly_cost(),
            "agent_availability": await self._calculate_agent_availability()
        }
    
    async def _calculate_recent_error_rate(self) -> float:
        """Calculate error rate from recent requests"""
        # Get recent request logs
        logs = await self.redis.lrange("handywriterz:request_log", 0, 100)
        
        if not logs:
            return 0.0
        
        total_requests = len(logs)
        error_count = 0
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        for log_entry in logs:
            try:
                data = json.loads(log_entry)
                request_time = datetime.fromisoformat(data["timestamp"])
                
                if request_time >= cutoff_time:
                    if not data.get("success", True):
                        error_count += 1
            except Exception:
                continue
        
        return error_count / total_requests if total_requests > 0 else 0.0
    
    async def _calculate_avg_response_time(self) -> float:
        """Calculate average response time from recent requests"""
        logs = await self.redis.lrange("handywriterz:request_log", 0, 50)
        
        if not logs:
            return 0.0
        
        response_times = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        for log_entry in logs:
            try:
                data = json.loads(log_entry)
                request_time = datetime.fromisoformat(data["timestamp"])
                
                if request_time >= cutoff_time:
                    response_times.append(data.get("response_time", 0))
            except Exception:
                continue
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    async def _calculate_hourly_cost(self) -> float:
        """Calculate cost for the current hour"""
        current_hour = datetime.utcnow().hour
        hourly_key = f"handywriterz:budget:hourly:{current_hour}"
        cost = await self.redis.get(hourly_key)
        return float(cost) if cost else 0.0
    
    async def _calculate_agent_availability(self) -> float:
        """Calculate percentage of agents that are available"""
        agent_data = await self.redis.hgetall("handywriterz:agents")
        
        if not agent_data:
            return 0.0
        
        available_count = 0
        total_count = len(agent_data)
        
        for agent_id, data in agent_data.items():
            try:
                agent_info = json.loads(data)
                if agent_info.get("status") == "idle":
                    available_count += 1
            except Exception:
                continue
        
        return available_count / total_count if total_count > 0 else 0.0
    
    async def _calculate_throughput(self) -> float:
        """Calculate requests per minute"""
        logs = await self.redis.lrange("handywriterz:request_log", 0, 200)
        
        cutoff_time = datetime.utcnow() - timedelta(minutes=1)
        recent_requests = 0
        
        for log_entry in logs:
            try:
                data = json.loads(log_entry)
                request_time = datetime.fromisoformat(data["timestamp"])
                
                if request_time >= cutoff_time:
                    recent_requests += 1
            except Exception:
                continue
        
        return float(recent_requests)
    
    async def _update_capacity_forecasts(self):
        """Update capacity forecasting models"""
        # Simple implementation - in production, would use proper ML models
        
        # Get historical metrics
        metrics_history = await self.redis.lrange("handywriterz:system_metrics", 0, 144)  # Last 24 hours
        
        if len(metrics_history) < 10:
            return
        
        # Extract throughput data
        throughput_data = []
        for entry in metrics_history:
            try:
                data = json.loads(entry)
                throughput_data.append(data.get("throughput_per_minute", 0))
            except Exception:
                continue
        
        if throughput_data:
            # Simple linear regression for next hour prediction
            x = np.arange(len(throughput_data))
            y = np.array(throughput_data)
            
            if len(y) > 1:
                slope = np.polyfit(x, y, 1)[0]
                next_hour_forecast = y[-1] + slope * 60  # 60 minutes ahead
                
                self.capacity_forecasts["throughput"].append(next_hour_forecast)
                # Keep only last 24 forecasts
                if len(self.capacity_forecasts["throughput"]) > 24:
                    self.capacity_forecasts["throughput"] = self.capacity_forecasts["throughput"][-24:]
    
    async def _generate_scaling_recommendations(self) -> List[str]:
        """Generate scaling recommendations based on forecasts"""
        recommendations = []
        
        if "throughput" in self.capacity_forecasts:
            forecasts = self.capacity_forecasts["throughput"]
            if forecasts:
                avg_forecast = np.mean(forecasts[-3:])  # Average of last 3 forecasts
                current_capacity = await self._estimate_current_capacity()
                
                if avg_forecast > current_capacity * 0.8:  # 80% capacity threshold
                    recommendations.append("Consider scaling up agents to handle increased load")
                elif avg_forecast < current_capacity * 0.3:  # 30% capacity threshold
                    recommendations.append("Consider scaling down agents to reduce costs")
        
        return recommendations
    
    async def _estimate_current_capacity(self) -> float:
        """Estimate current system capacity"""
        active_agents = await self.redis.hlen("handywriterz:agents")
        # Rough estimate: each agent can handle ~10 requests per minute
        return active_agents * 10.0
    
    async def _perform_health_checks(self) -> Dict[str, Any]:
        """Perform comprehensive health checks"""
        health_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check Redis connectivity
        try:
            await self.redis.ping()
            health_status["components"]["redis"] = {"status": "healthy", "response_time": 0.001}
        except Exception as e:
            health_status["components"]["redis"] = {"status": "unhealthy", "error": str(e)}
            health_status["overall_status"] = "degraded"
        
        # Check agent pool health
        try:
            agent_count = await self.redis.hlen("handywriterz:agents")
            if agent_count > 0:
                health_status["components"]["agent_pool"] = {
                    "status": "healthy",
                    "active_agents": agent_count
                }
            else:
                health_status["components"]["agent_pool"] = {
                    "status": "warning",
                    "active_agents": 0,
                    "message": "No active agents"
                }
                health_status["overall_status"] = "degraded"
        except Exception as e:
            health_status["components"]["agent_pool"] = {"status": "unhealthy", "error": str(e)}
            health_status["overall_status"] = "unhealthy"
        
        # Check queue health
        try:
            queue_depth = await self.redis.zcard("handywriterz:task_queue")
            if queue_depth < 50:  # Healthy threshold
                health_status["components"]["task_queue"] = {
                    "status": "healthy",
                    "queue_depth": queue_depth
                }
            elif queue_depth < 200:  # Warning threshold
                health_status["components"]["task_queue"] = {
                    "status": "warning",
                    "queue_depth": queue_depth,
                    "message": "Queue depth elevated"
                }
                if health_status["overall_status"] == "healthy":
                    health_status["overall_status"] = "degraded"
            else:  # Critical threshold
                health_status["components"]["task_queue"] = {
                    "status": "critical",
                    "queue_depth": queue_depth,
                    "message": "Queue depth critical"
                }
                health_status["overall_status"] = "unhealthy"
        except Exception as e:
            health_status["components"]["task_queue"] = {"status": "unhealthy", "error": str(e)}
            health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification (implement based on requirements)"""
        # This would integrate with notification systems like:
        # - Slack webhooks
        # - Email notifications
        # - PagerDuty
        # - Discord webhooks
        
        logger.warning(f"ALERT: {alert.title} - {alert.description} (Value: {alert.current_value}, Threshold: {alert.threshold})")
        
        # Store alert for dashboard display
        await self.redis.lpush(
            "handywriterz:recent_alerts",
            json.dumps(asdict(alert), default=str)
        )
        await self.redis.ltrim("handywriterz:recent_alerts", 0, 50)  # Keep last 50 alerts
    
    async def get_system_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive system dashboard data"""
        
        # Get current system metrics
        current_metrics = await self._collect_system_metrics()
        
        # Get recent alerts
        alert_data = await self.redis.lrange("handywriterz:recent_alerts", 0, 10)
        recent_alerts = []
        for alert_json in alert_data:
            try:
                recent_alerts.append(json.loads(alert_json))
            except Exception:
                continue
        
        # Get health status
        health_data = await self.redis.hget("handywriterz:health_status", "system")
        health_status = json.loads(health_data) if health_data else {}
        
        # Get top performing agents
        top_agents = []
        for agent_id in list(self.metrics_collector.agent_metrics.keys())[:5]:
            agent_report = await self.metrics_collector.get_agent_performance_report(agent_id)
            if agent_report:
                top_agents.append(agent_report)
        
        # Get capacity forecasts
        forecasts = dict(self.capacity_forecasts) if self.capacity_forecasts else {}
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": asdict(current_metrics),
            "health_status": health_status,
            "recent_alerts": recent_alerts,
            "top_agents": top_agents,
            "capacity_forecasts": forecasts,
            "active_workflows": await self.redis.hlen("handywriterz:workflows"),
            "cache_stats": await self.redis.hgetall("handywriterz:cache_stats")
        }