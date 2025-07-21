"""
Advanced Database Service with Connection Pooling and Optimization.
Production-ready database management with connection pooling, query optimization,
and advanced monitoring capabilities.
"""

import os
import json
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager

import redis.asyncio as redis
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import DisconnectionError, TimeoutError

from src.services.error_handler import error_handler, ErrorCategory, ErrorSeverity, ErrorContext

logger = logging.getLogger(__name__)

class QueryType(Enum):
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    DDL = "ddl"

class OptimizationLevel(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"

@dataclass
class QueryMetrics:
    query_type: QueryType
    execution_time: float
    rows_affected: int
    query_hash: str
    timestamp: datetime
    parameters: Dict[str, Any]
    table_name: Optional[str] = None
    index_usage: List[str] = None
    query_plan: Optional[str] = None

@dataclass
class ConnectionPoolMetrics:
    total_connections: int
    active_connections: int
    idle_connections: int
    pool_size: int
    max_overflow: int
    checked_out: int
    checked_in: int
    invalidated: int
    timestamp: datetime

@dataclass
class DatabaseHealth:
    connection_pool_healthy: bool
    query_performance_healthy: bool
    disk_space_healthy: bool
    replication_healthy: bool
    slow_query_count: int
    deadlock_count: int
    connection_errors: int
    timestamp: datetime

class AdvancedDatabaseService:
    """Advanced database service with comprehensive optimization and monitoring"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/handywriterz")
        self.redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        
        # Connection pool configuration
        self.pool_config = {
            "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "30")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
            "pool_pre_ping": True,
            "echo": os.getenv("DB_ECHO", "false").lower() == "true"
        }
        
        # Query optimization settings
        self.optimization_level = OptimizationLevel(os.getenv("DB_OPTIMIZATION_LEVEL", "basic"))
        self.slow_query_threshold = float(os.getenv("DB_SLOW_QUERY_THRESHOLD", "1.0"))
        self.query_cache_ttl = int(os.getenv("DB_QUERY_CACHE_TTL", "300"))
        
        # Initialize engines and sessions
        self.engine = None
        self.session_factory = None
        self.query_cache = {}
        self.query_metrics = []
        self.connection_metrics = ConnectionPoolMetrics(
            total_connections=0,
            active_connections=0,
            idle_connections=0,
            pool_size=self.pool_config["pool_size"],
            max_overflow=self.pool_config["max_overflow"],
            checked_out=0,
            checked_in=0,
            invalidated=0,
            timestamp=datetime.now()
        )
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
    
    async def _initialize_database(self):
        """Initialize database connection and setup"""
        try:
            # Create async engine with optimized pool
            self.engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_config["pool_size"],
                max_overflow=self.pool_config["max_overflow"],
                pool_timeout=self.pool_config["pool_timeout"],
                pool_recycle=self.pool_config["pool_recycle"],
                pool_pre_ping=self.pool_config["pool_pre_ping"],
                echo=self.pool_config["echo"],
                # Additional optimization parameters
                connect_args={
                    "command_timeout": 30,
                    "server_settings": {
                        "application_name": "handywriterz_backend",
                        "jit": "off",  # Disable JIT for better performance on small queries
                        "shared_preload_libraries": "pg_stat_statements",
                        "log_min_duration_statement": str(int(self.slow_query_threshold * 1000)),
                        "log_checkpoints": "on",
                        "log_connections": "on",
                        "log_disconnections": "on",
                        "log_lock_waits": "on",
                        "log_statement": "none",
                        "log_line_prefix": "%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h "
                    }
                }
            )
            
            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )
            
            # Setup event listeners
            self._setup_event_listeners()
            
            # Test connection
            await self._test_connection()
            
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            await error_handler.handle_error(
                e,
                ErrorContext(
                    request_id="db_init",
                    additional_data={"database_url": self.database_url}
                ),
                ErrorCategory.DATABASE,
                ErrorSeverity.CRITICAL
            )
            raise
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self.engine.sync_engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Handle new database connections"""
            self.connection_metrics.total_connections += 1
            self.connection_metrics.checked_out += 1
            logger.debug("New database connection established")
        
        @event.listens_for(self.engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle connection checkout from pool"""
            self.connection_metrics.checked_out += 1
            self.connection_metrics.active_connections += 1
        
        @event.listens_for(self.engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Handle connection checkin to pool"""
            self.connection_metrics.checked_in += 1
            self.connection_metrics.active_connections -= 1
            self.connection_metrics.idle_connections += 1
        
        @event.listens_for(self.engine.sync_engine, "invalidate")
        def receive_invalidate(dbapi_connection, connection_record, exception):
            """Handle connection invalidation"""
            self.connection_metrics.invalidated += 1
            logger.warning(f"Database connection invalidated: {exception}")
    
    async def _test_connection(self):
        """Test database connection"""
        async with self.get_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            logger.info("Database connection test successful")
    
    @asynccontextmanager
    async def get_session(self, read_only: bool = False) -> AsyncSession:
        """Get database session with proper error handling"""
        if not self.session_factory:
            raise RuntimeError("Database service not initialized")
        
        session = self.session_factory()
        
        try:
            if read_only:
                # Set transaction to read-only for optimization
                await session.execute(text("SET TRANSACTION READ ONLY"))
            
            yield session
            
            if not read_only:
                await session.commit()
                
        except Exception as e:
            await session.rollback()
            
            # Handle different types of database errors
            if isinstance(e, DisconnectionError):
                logger.error("Database disconnection error, attempting to reconnect")
                await self._handle_disconnection()
            elif isinstance(e, TimeoutError):
                logger.warning("Database query timeout")
            
            # Log error with context
            await error_handler.handle_error(
                e,
                ErrorContext(
                    request_id="db_session",
                    additional_data={"read_only": read_only}
                ),
                ErrorCategory.DATABASE,
                ErrorSeverity.HIGH
            )
            raise
        finally:
            await session.close()
    
    async def execute_query(
        self,
        query: str,
        parameters: Dict[str, Any] = None,
        query_type: QueryType = QueryType.SELECT,
        use_cache: bool = True,
        timeout: int = 30
    ) -> Any:
        """Execute optimized database query with caching and monitoring"""
        
        start_time = time.time()
        parameters = parameters or {}
        
        # Generate query hash for caching
        query_hash = self._generate_query_hash(query, parameters)
        
        # Check cache for read queries
        if query_type == QueryType.SELECT and use_cache:
            cached_result = await self._get_cached_query(query_hash)
            if cached_result:
                logger.debug(f"Query cache hit: {query_hash}")
                return cached_result
        
        try:
            async with self.get_session(read_only=(query_type == QueryType.SELECT)) as session:
                # Set query timeout
                await session.execute(text(f"SET statement_timeout = {timeout * 1000}"))
                
                # Execute query with parameters
                if parameters:
                    result = await session.execute(text(query), parameters)
                else:
                    result = await session.execute(text(query))
                
                # Process result based on query type
                if query_type == QueryType.SELECT:
                    data = result.fetchall()
                    # Convert to dict format
                    result_data = [dict(row._mapping) for row in data]
                else:
                    result_data = result.rowcount
                
                execution_time = time.time() - start_time
                
                # Record query metrics
                await self._record_query_metrics(
                    query_type=query_type,
                    execution_time=execution_time,
                    rows_affected=len(result_data) if isinstance(result_data, list) else result_data,
                    query_hash=query_hash,
                    parameters=parameters
                )
                
                # Cache result if applicable
                if query_type == QueryType.SELECT and use_cache and execution_time < self.slow_query_threshold:
                    await self._cache_query_result(query_hash, result_data)
                
                # Alert on slow queries
                if execution_time > self.slow_query_threshold:
                    await self._handle_slow_query(query, parameters, execution_time)
                
                return result_data
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failed query
            await self._record_query_metrics(
                query_type=query_type,
                execution_time=execution_time,
                rows_affected=0,
                query_hash=query_hash,
                parameters=parameters
            )
            
            logger.error(f"Query execution failed: {e}")
            raise
    
    async def execute_transaction(
        self,
        operations: List[Callable],
        isolation_level: str = "READ_COMMITTED"
    ) -> List[Any]:
        """Execute multiple operations in a transaction"""
        
        results = []
        
        async with self.get_session() as session:
            try:
                # Set isolation level
                await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                
                # Execute all operations
                for operation in operations:
                    result = await operation(session)
                    results.append(result)
                
                # Commit transaction
                await session.commit()
                
                logger.info(f"Transaction completed successfully with {len(operations)} operations")
                return results
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction failed, rolled back: {e}")
                raise
    
    async def bulk_insert(
        self,
        table_name: str,
        data: List[Dict[str, Any]],
        batch_size: int = 1000,
        on_conflict: str = "IGNORE"
    ) -> int:
        """Perform optimized bulk insert operation"""
        
        if not data:
            return 0
        
        total_inserted = 0
        
        async with self.get_session() as session:
            try:
                # Process data in batches
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    
                    # Generate bulk insert query
                    columns = list(batch[0].keys())
                    placeholders = ", ".join([f":{col}" for col in columns])
                    
                    query = f"""
                        INSERT INTO {table_name} ({', '.join(columns)})
                        VALUES ({placeholders})
                    """
                    
                    if on_conflict == "IGNORE":
                        query += " ON CONFLICT DO NOTHING"
                    elif on_conflict == "UPDATE":
                        update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != "id"])
                        query += f" ON CONFLICT (id) DO UPDATE SET {update_clause}"
                    
                    # Execute batch
                    result = await session.execute(text(query), batch)
                    total_inserted += result.rowcount
                    
                    # Commit batch
                    await session.commit()
                    
                    logger.debug(f"Bulk insert batch {i//batch_size + 1}: {result.rowcount} rows inserted")
                
                logger.info(f"Bulk insert completed: {total_inserted} rows inserted into {table_name}")
                return total_inserted
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Bulk insert failed: {e}")
                raise
    
    async def optimize_table(self, table_name: str) -> Dict[str, Any]:
        """Optimize table performance"""
        
        optimization_results = {}
        
        async with self.get_session() as session:
            try:
                # Analyze table statistics
                await session.execute(text(f"ANALYZE {table_name}"))
                optimization_results["analyzed"] = True
                
                # Vacuum table if needed
                if self.optimization_level in [OptimizationLevel.ADVANCED, OptimizationLevel.AGGRESSIVE]:
                    await session.execute(text(f"VACUUM {table_name}"))
                    optimization_results["vacuumed"] = True
                
                # Reindex table if aggressive optimization
                if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                    await session.execute(text(f"REINDEX TABLE {table_name}"))
                    optimization_results["reindexed"] = True
                
                # Get table statistics
                stats_query = """
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del,
                        n_live_tup,
                        n_dead_tup,
                        last_vacuum,
                        last_autovacuum,
                        last_analyze,
                        last_autoanalyze
                    FROM pg_stat_user_tables 
                    WHERE tablename = :table_name
                """
                
                result = await session.execute(text(stats_query), {"table_name": table_name})
                stats = result.fetchone()
                
                if stats:
                    optimization_results["statistics"] = dict(stats._mapping)
                
                logger.info(f"Table optimization completed for {table_name}")
                return optimization_results
                
            except Exception as e:
                logger.error(f"Table optimization failed for {table_name}: {e}")
                raise
    
    async def get_database_health(self) -> DatabaseHealth:
        """Get comprehensive database health metrics"""
        
        try:
            async with self.get_session(read_only=True) as session:
                # Check connection pool health
                pool_healthy = (
                    self.connection_metrics.active_connections < self.pool_config["pool_size"] * 0.8
                )
                
                # Check query performance
                avg_query_time = sum(
                    metric.execution_time for metric in self.query_metrics[-100:]
                ) / len(self.query_metrics[-100:]) if self.query_metrics else 0
                
                query_performance_healthy = avg_query_time < self.slow_query_threshold
                
                # Check disk space
                disk_query = """
                    SELECT 
                        pg_database_size(current_database()) as database_size,
                        pg_size_pretty(pg_database_size(current_database())) as database_size_pretty
                """
                
                disk_result = await session.execute(text(disk_query))
                disk_info = disk_result.fetchone()
                
                # Simple disk space check (in production, you'd want more sophisticated monitoring)
                disk_space_healthy = True  # Placeholder
                
                # Check for slow queries
                slow_query_count = len([
                    m for m in self.query_metrics[-100:]
                    if m.execution_time > self.slow_query_threshold
                ])
                
                # Check for deadlocks (from pg_stat_database)
                deadlock_query = """
                    SELECT deadlocks 
                    FROM pg_stat_database 
                    WHERE datname = current_database()
                """
                
                deadlock_result = await session.execute(text(deadlock_query))
                deadlock_info = deadlock_result.fetchone()
                deadlock_count = deadlock_info[0] if deadlock_info else 0
                
                return DatabaseHealth(
                    connection_pool_healthy=pool_healthy,
                    query_performance_healthy=query_performance_healthy,
                    disk_space_healthy=disk_space_healthy,
                    replication_healthy=True,  # Placeholder
                    slow_query_count=slow_query_count,
                    deadlock_count=deadlock_count,
                    connection_errors=self.connection_metrics.invalidated,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Failed to get database health: {e}")
            
            return DatabaseHealth(
                connection_pool_healthy=False,
                query_performance_healthy=False,
                disk_space_healthy=False,
                replication_healthy=False,
                slow_query_count=0,
                deadlock_count=0,
                connection_errors=0,
                timestamp=datetime.now()
            )
    
    def _generate_query_hash(self, query: str, parameters: Dict[str, Any]) -> str:
        """Generate hash for query caching"""
        import hashlib
        
        query_signature = f"{query}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.md5(query_signature.encode()).hexdigest()
    
    async def _get_cached_query(self, query_hash: str) -> Optional[Any]:
        """Get cached query result"""
        try:
            cached_data = await self.redis.get(f"query_cache:{query_hash}")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to get cached query: {e}")
        
        return None
    
    async def _cache_query_result(self, query_hash: str, result: Any):
        """Cache query result"""
        try:
            await self.redis.setex(
                f"query_cache:{query_hash}",
                self.query_cache_ttl,
                json.dumps(result, default=str)
            )
        except Exception as e:
            logger.warning(f"Failed to cache query result: {e}")
    
    async def _record_query_metrics(self, **kwargs):
        """Record query execution metrics"""
        metrics = QueryMetrics(
            timestamp=datetime.now(),
            **kwargs
        )
        
        # Store in memory (limited size)
        self.query_metrics.append(metrics)
        if len(self.query_metrics) > 1000:
            self.query_metrics = self.query_metrics[-500:]  # Keep last 500
        
        # Store in Redis for monitoring
        try:
            await self.redis.lpush(
                "db_query_metrics",
                json.dumps({
                    "query_type": metrics.query_type.value,
                    "execution_time": metrics.execution_time,
                    "rows_affected": metrics.rows_affected,
                    "query_hash": metrics.query_hash,
                    "timestamp": metrics.timestamp.isoformat()
                })
            )
            await self.redis.ltrim("db_query_metrics", 0, 999)  # Keep last 1000
        except Exception as e:
            logger.warning(f"Failed to record query metrics: {e}")
    
    async def _handle_slow_query(self, query: str, parameters: Dict[str, Any], execution_time: float):
        """Handle slow query detection"""
        slow_query_data = {
            "query": query[:500],  # Truncate for logging
            "parameters": parameters,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log slow query
        logger.warning(f"Slow query detected: {execution_time:.2f}s")
        
        # Store for analysis
        try:
            await self.redis.lpush(
                "slow_queries",
                json.dumps(slow_query_data, default=str)
            )
            await self.redis.ltrim("slow_queries", 0, 99)  # Keep last 100
        except Exception as e:
            logger.error(f"Failed to log slow query: {e}")
    
    async def _handle_disconnection(self):
        """Handle database disconnection"""
        logger.warning("Handling database disconnection")
        
        try:
            # Attempt to recreate engine
            if self.engine:
                await self.engine.dispose()
            
            await self._initialize_database()
            
        except Exception as e:
            logger.error(f"Failed to reconnect to database: {e}")
            raise
    
    async def get_connection_metrics(self) -> Dict[str, Any]:
        """Get connection pool metrics"""
        pool = self.engine.pool
        
        return {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_in": pool.checkedin(),
            "total_connections": self.connection_metrics.total_connections,
            "invalidated": self.connection_metrics.invalidated,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_query_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent query metrics"""
        try:
            metrics_data = await self.redis.lrange("db_query_metrics", 0, limit - 1)
            return [json.loads(data) for data in metrics_data]
        except Exception as e:
            logger.error(f"Failed to get query metrics: {e}")
            return []
    
    async def close(self):
        """Close database service"""
        if self.engine:
            await self.engine.dispose()
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Database service closed")

# Create global database service instance
database_service = AdvancedDatabaseService()

# Export public interface
__all__ = [
    "AdvancedDatabaseService",
    "QueryType",
    "OptimizationLevel",
    "QueryMetrics",
    "ConnectionPoolMetrics",
    "DatabaseHealth",
    "database_service"
]