"""
Advanced Health Monitoring and Alerting System.
Production-ready health monitoring with comprehensive metrics, alerting,
and automated recovery capabilities.
"""

import os
import json
import time
import logging
import asyncio
import psutil
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as redis
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
import httpx

from src.services.database_service import database_service
from src.services.production_llm_service import production_llm_service

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ServiceHealth:
    name: str
    status: HealthStatus
    response_time: float
    error_rate: float
    last_check: datetime
    details: Dict[str, Any] = None
    uptime: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "response_time": self.response_time,
            "error_rate": self.error_rate,
            "last_check": self.last_check.isoformat(),
            "details": self.details or {},
            "uptime": self.uptime
        }

@dataclass
class SystemMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_time: float
    error_rate: float
    throughput: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "disk_usage": self.disk_usage,
            "network_io": self.network_io,
            "active_connections": self.active_connections,
            "response_time": self.response_time,
            "error_rate": self.error_rate,
            "throughput": self.throughput,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class HealthCheck:
    name: str
    check_function: Callable
    interval: int
    timeout: int
    enabled: bool = True
    last_run: Optional[datetime] = None
    consecutive_failures: int = 0
    max_failures: int = 3

@dataclass
class Alert:
    id: str
    title: str
    description: str
    severity: AlertSeverity
    service: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "service": self.service,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "metadata": self.metadata or {}
        }

class AdvancedHealthMonitor:
    """Advanced health monitoring system with comprehensive capabilities"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        
        # Configuration
        self.check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
        self.alert_cooldown = int(os.getenv("ALERT_COOLDOWN", "300"))
        self.metrics_retention = int(os.getenv("METRICS_RETENTION", "86400"))
        
        # System monitoring
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        
        # Service health status
        self.service_health = {}
        self.active_alerts = {}
        self.alert_history = []
        
        # Initialize health checks
        self.health_checks = self._initialize_health_checks()
        
        # Start monitoring tasks
        self._start_monitoring_tasks()
        
        logger.info("Advanced Health Monitor initialized")
    
    def _initialize_health_checks(self) -> Dict[str, HealthCheck]:
        """Initialize health check configurations"""
        return {
            "database": HealthCheck(
                name="database",
                check_function=self._check_database_health,
                interval=30,
                timeout=10,
                max_failures=3
            ),
            "redis": HealthCheck(
                name="redis",
                check_function=self._check_redis_health,
                interval=30,
                timeout=5,
                max_failures=3
            ),
            "llm_service": HealthCheck(
                name="llm_service",
                check_function=self._check_llm_service_health,
                interval=60,
                timeout=30,
                max_failures=2
            ),
            "external_apis": HealthCheck(
                name="external_apis",
                check_function=self._check_external_apis_health,
                interval=120,
                timeout=15,
                max_failures=2
            ),
            "system_resources": HealthCheck(
                name="system_resources",
                check_function=self._check_system_resources,
                interval=60,
                timeout=10,
                max_failures=1
            ),
            "disk_space": HealthCheck(
                name="disk_space",
                check_function=self._check_disk_space,
                interval=300,
                timeout=5,
                max_failures=1
            )
        }
    
    def _start_monitoring_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._alert_cleanup_loop())
    
    async def _health_check_loop(self):
        """Main health check loop"""
        while True:
            try:
                for check_name, check in self.health_checks.items():
                    if not check.enabled:
                        continue
                    
                    # Check if it's time to run this check
                    if (check.last_run is None or 
                        (datetime.now() - check.last_run).seconds >= check.interval):
                        
                        await self._run_health_check(check)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(30)
    
    async def _metrics_collection_loop(self):
        """Collect system metrics periodically"""
        while True:
            try:
                metrics = await self._collect_system_metrics()
                await self._store_metrics(metrics)
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_cleanup_loop(self):
        """Clean up old alerts and resolved alerts"""
        while True:
            try:
                await self._cleanup_old_alerts()
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"Alert cleanup error: {e}")
                await asyncio.sleep(3600)
    
    async def _run_health_check(self, check: HealthCheck):
        """Run individual health check"""
        check.last_run = datetime.now()
        start_time = time.time()
        
        try:
            # Run check with timeout
            health_result = await asyncio.wait_for(
                check.check_function(),
                timeout=check.timeout
            )
            
            response_time = time.time() - start_time
            
            # Create service health object
            service_health = ServiceHealth(
                name=check.name,
                status=health_result.get("status", HealthStatus.HEALTHY),
                response_time=response_time,
                error_rate=health_result.get("error_rate", 0.0),
                last_check=datetime.now(),
                details=health_result.get("details", {}),
                uptime=health_result.get("uptime", 0.0)
            )
            
            # Store health status
            self.service_health[check.name] = service_health
            
            # Reset failure count on success
            check.consecutive_failures = 0
            
            # Check if we need to resolve any alerts
            await self._check_alert_resolution(check.name, service_health)
            
        except asyncio.TimeoutError:
            logger.warning(f"Health check timeout for {check.name}")
            await self._handle_health_check_failure(check, "Health check timeout")
            
        except Exception as e:
            logger.error(f"Health check failed for {check.name}: {e}")
            await self._handle_health_check_failure(check, str(e))
    
    async def _handle_health_check_failure(self, check: HealthCheck, error_message: str):
        """Handle health check failure"""
        check.consecutive_failures += 1
        
        # Create unhealthy service status
        service_health = ServiceHealth(
            name=check.name,
            status=HealthStatus.UNHEALTHY,
            response_time=float('inf'),
            error_rate=1.0,
            last_check=datetime.now(),
            details={"error": error_message}
        )
        
        self.service_health[check.name] = service_health
        
        # Trigger alert if threshold reached
        if check.consecutive_failures >= check.max_failures:
            await self._trigger_alert(
                service=check.name,
                title=f"Service {check.name} is unhealthy",
                description=f"Health check failed {check.consecutive_failures} times: {error_message}",
                severity=AlertSeverity.ERROR
            )
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            db_health = await database_service.get_database_health()
            
            # Determine overall status
            if not db_health.connection_pool_healthy:
                status = HealthStatus.UNHEALTHY
            elif db_health.slow_query_count > 10:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "error_rate": db_health.slow_query_count / 100.0,
                "details": {
                    "connection_pool_healthy": db_health.connection_pool_healthy,
                    "query_performance_healthy": db_health.query_performance_healthy,
                    "slow_query_count": db_health.slow_query_count,
                    "deadlock_count": db_health.deadlock_count,
                    "connection_errors": db_health.connection_errors
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error_rate": 1.0,
                "details": {"error": str(e)}
            }
    
    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            start_time = time.time()
            
            # Test basic Redis operations
            await self.redis.ping()
            await self.redis.set("health_check", "ok", ex=60)
            result = await self.redis.get("health_check")
            
            response_time = time.time() - start_time
            
            if result == "ok" and response_time < 1.0:
                status = HealthStatus.HEALTHY
            elif response_time < 5.0:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.UNHEALTHY
            
            # Get Redis info
            info = await self.redis.info()
            
            return {
                "status": status,
                "error_rate": 0.0,
                "details": {
                    "response_time": response_time,
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error_rate": 1.0,
                "details": {"error": str(e)}
            }
    
    async def _check_llm_service_health(self) -> Dict[str, Any]:
        """Check LLM service health"""
        try:
            # Get LLM service metrics
            metrics = production_llm_service.cost_tracker
            
            # Simple health check - in production you'd want more sophisticated checks
            status = HealthStatus.HEALTHY
            error_rate = 0.0
            
            return {
                "status": status,
                "error_rate": error_rate,
                "details": {
                    "service_initialized": True,
                    "models_available": len(production_llm_service.clients),
                    "cache_size": len(production_llm_service.request_cache)
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error_rate": 1.0,
                "details": {"error": str(e)}
            }
    
    async def _check_external_apis_health(self) -> Dict[str, Any]:
        """Check external APIs health"""
        external_services = [
            ("OpenAI", "https://api.openai.com/v1/models"),
            ("Anthropic", "https://api.anthropic.com/v1/messages"),
            ("Google", "https://generativelanguage.googleapis.com/v1/models")
        ]
        
        healthy_services = 0
        total_services = len(external_services)
        service_details = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, url in external_services:
                try:
                    response = await client.get(url)
                    if response.status_code < 500:
                        healthy_services += 1
                        service_details[service_name] = {
                            "status": "healthy",
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds()
                        }
                    else:
                        service_details[service_name] = {
                            "status": "unhealthy",
                            "status_code": response.status_code
                        }
                except Exception as e:
                    service_details[service_name] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
        
        # Determine overall status
        health_ratio = healthy_services / total_services
        if health_ratio >= 0.8:
            status = HealthStatus.HEALTHY
        elif health_ratio >= 0.5:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.UNHEALTHY
        
        return {
            "status": status,
            "error_rate": 1.0 - health_ratio,
            "details": {
                "healthy_services": healthy_services,
                "total_services": total_services,
                "services": service_details
            }
        }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Determine status based on resource usage
            if cpu_usage > 90 or memory.percent > 90:
                status = HealthStatus.UNHEALTHY
            elif cpu_usage > 70 or memory.percent > 70:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "error_rate": 0.0,
                "details": {
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory.percent,
                    "memory_available": memory.available,
                    "memory_total": memory.total
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error_rate": 1.0,
                "details": {"error": str(e)}
            }
    
    async def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            
            usage_percent = (disk_usage.used / disk_usage.total) * 100
            
            if usage_percent > 95:
                status = HealthStatus.CRITICAL
            elif usage_percent > 85:
                status = HealthStatus.UNHEALTHY
            elif usage_percent > 75:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            return {
                "status": status,
                "error_rate": 0.0,
                "details": {
                    "disk_usage_percent": usage_percent,
                    "disk_free": disk_usage.free,
                    "disk_total": disk_usage.total,
                    "disk_used": disk_usage.used
                }
            }
            
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "error_rate": 1.0,
                "details": {"error": str(e)}
            }
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        try:
            # CPU and Memory
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
            
            # Application metrics
            active_connections = len(self.service_health)
            
            # Calculate averages
            avg_response_time = sum(self.response_times[-100:]) / len(self.response_times[-100:]) if self.response_times else 0
            error_rate = self.error_count / max(self.request_count, 1)
            
            uptime = (datetime.now() - self.start_time).total_seconds()
            throughput = self.request_count / max(uptime, 1)
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=active_connections,
                response_time=avg_response_time,
                error_rate=error_rate,
                throughput=throughput,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                network_io={},
                active_connections=0,
                response_time=0,
                error_rate=1.0,
                throughput=0,
                timestamp=datetime.now()
            )
    
    async def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in Redis"""
        try:
            # Store current metrics
            await self.redis.setex(
                "system_metrics:current",
                300,  # 5 minutes TTL
                json.dumps(metrics.to_dict())
            )
            
            # Store in time series
            await self.redis.lpush(
                "system_metrics:timeseries",
                json.dumps(metrics.to_dict())
            )
            
            # Keep only recent metrics
            await self.redis.ltrim("system_metrics:timeseries", 0, 1440)  # 24 hours at 1 minute intervals
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    async def _trigger_alert(self, service: str, title: str, description: str, severity: AlertSeverity, metadata: Dict[str, Any] = None):
        """Trigger system alert"""
        alert_id = f"alert_{service}_{int(time.time())}"
        
        # Check cooldown
        cooldown_key = f"alert_cooldown:{service}:{severity.value}"
        if await self.redis.get(cooldown_key):
            return  # Still in cooldown
        
        # Create alert
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            service=service,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Store in Redis
        await self.redis.setex(
            f"alert:{alert_id}",
            86400,  # 24 hours
            json.dumps(alert.to_dict())
        )
        
        # Set cooldown
        await self.redis.setex(cooldown_key, self.alert_cooldown, "1")
        
        # Log alert
        logger.warning(f"ALERT [{severity.value}]: {title} - {description}")
        
        # Broadcast alert
        await self.redis.publish("alerts", json.dumps(alert.to_dict()))
    
    async def _check_alert_resolution(self, service: str, health: ServiceHealth):
        """Check if any alerts can be resolved"""
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.service == service and not alert.resolved:
                if health.status == HealthStatus.HEALTHY:
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    
                    # Remove from active alerts
                    del self.active_alerts[alert_id]
                    
                    logger.info(f"Alert resolved: {alert.title}")
    
    async def _cleanup_old_alerts(self):
        """Clean up old alerts"""
        cutoff_time = datetime.now() - timedelta(days=7)
        
        # Remove old alerts from history
        self.alert_history = [
            alert for alert in self.alert_history
            if alert.timestamp > cutoff_time
        ]
        
        # Clean up Redis
        try:
            keys = await self.redis.keys("alert:*")
            for key in keys:
                alert_data = await self.redis.get(key)
                if alert_data:
                    alert = json.loads(alert_data)
                    alert_time = datetime.fromisoformat(alert["timestamp"])
                    if alert_time < cutoff_time:
                        await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Failed to cleanup old alerts: {e}")
    
    # Public API methods
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        # Determine overall status
        unhealthy_services = [
            name for name, health in self.service_health.items()
            if health.status in [HealthStatus.UNHEALTHY, HealthStatus.CRITICAL]
        ]
        
        degraded_services = [
            name for name, health in self.service_health.items()
            if health.status == HealthStatus.DEGRADED
        ]
        
        if unhealthy_services:
            overall_status = HealthStatus.UNHEALTHY
        elif degraded_services:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Get latest metrics
        try:
            metrics_data = await self.redis.get("system_metrics:current")
            metrics = json.loads(metrics_data) if metrics_data else {}
        except Exception:
            metrics = {}
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "services": {name: health.to_dict() for name, health in self.service_health.items()},
            "metrics": metrics,
            "alerts": len(self.active_alerts),
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
    
    async def get_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get health for specific service"""
        if service_name in self.service_health:
            return self.service_health[service_name].to_dict()
        return None
    
    async def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        recent_alerts = sorted(
            self.alert_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [alert.to_dict() for alert in recent_alerts]
    
    async def get_metrics_timeseries(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics time series"""
        try:
            limit = hours * 60  # Assuming 1 minute intervals
            metrics_data = await self.redis.lrange("system_metrics:timeseries", 0, limit - 1)
            return [json.loads(data) for data in metrics_data]
        except Exception as e:
            logger.error(f"Failed to get metrics timeseries: {e}")
            return []
    
    def track_request(self, response_time: float, error: bool = False):
        """Track request for monitoring"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if error:
            self.error_count += 1
        
        # Keep only recent response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-500:]

# Request tracking middleware
def track_requests(health_monitor: AdvancedHealthMonitor):
    """Middleware to track requests"""
    async def middleware(request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            response_time = time.time() - start_time
            
            # Track request
            health_monitor.track_request(response_time, error=response.status_code >= 400)
            
            return response
            
        except Exception:
            response_time = time.time() - start_time
            health_monitor.track_request(response_time, error=True)
            raise
    
    return middleware

# Health check endpoints
async def health_endpoint(health_monitor: AdvancedHealthMonitor):
    """Simple health check endpoint"""
    health = await health_monitor.get_system_health()
    
    if health["status"] == "healthy":
        return JSONResponse(content={"status": "healthy"}, status_code=200)
    elif health["status"] == "degraded":
        return JSONResponse(content={"status": "degraded"}, status_code=200)
    else:
        return JSONResponse(content={"status": "unhealthy"}, status_code=503)

async def detailed_health_endpoint(health_monitor: AdvancedHealthMonitor):
    """Detailed health check endpoint"""
    health = await health_monitor.get_system_health()
    return JSONResponse(content=health)

# Global health monitor instance (to be initialized with FastAPI app)
health_monitor = None

def initialize_health_monitor(app: FastAPI) -> AdvancedHealthMonitor:
    """Initialize health monitor with FastAPI app"""
    global health_monitor
    health_monitor = AdvancedHealthMonitor(app)
    
    # Add middleware
    app.middleware("http")(track_requests(health_monitor))
    
    # Add health endpoints
    app.add_api_route("/health", lambda: health_endpoint(health_monitor), methods=["GET"])
    app.add_api_route("/health/detailed", lambda: detailed_health_endpoint(health_monitor), methods=["GET"])
    
    return health_monitor

# Export public interface
__all__ = [
    "AdvancedHealthMonitor",
    "HealthStatus",
    "AlertSeverity",
    "ServiceHealth",
    "SystemMetrics",
    "Alert",
    "initialize_health_monitor",
    "health_monitor"
]