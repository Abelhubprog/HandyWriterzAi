"""
Advanced Caching & Performance Optimization Layer
Multi-level caching with intelligent invalidation, preemptive search caching, and streaming aggregation.
"""

import asyncio
import json
import hashlib
import time
import pickle
import gzip
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import redis.asyncio as redis
from pydantic import BaseModel
import logging
from collections import defaultdict, OrderedDict
import asyncpg
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    L1_MEMORY = "l1_memory"  # In-process memory cache
    L2_REDIS = "l2_redis"    # Redis distributed cache
    L3_DATABASE = "l3_database"  # PostgreSQL persistent cache

class CacheStrategy(Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    SMART = "smart"  # ML-based intelligent caching

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    size_bytes: int = 0
    tags: Set[str] = field(default_factory=set)

@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    writes: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

class LRUCache:
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check TTL
                if entry.ttl_seconds:
                    age = (datetime.utcnow() - entry.created_at).total_seconds()
                    if age > entry.ttl_seconds:
                        del self.cache[key]
                        self.stats.misses += 1
                        return None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                entry.last_accessed = datetime.utcnow()
                entry.access_count += 1
                
                self.stats.hits += 1
                return entry.value
            
            self.stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, tags: Set[str] = None):
        """Set value in cache"""
        async with self._lock:
            # Calculate size
            size_bytes = len(pickle.dumps(value))
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl_seconds,
                size_bytes=size_bytes,
                tags=tags or set()
            )
            
            # Remove existing entry if present
            if key in self.cache:
                old_entry = self.cache[key]
                self.stats.size_bytes -= old_entry.size_bytes
                del self.cache[key]
            
            # Add new entry
            self.cache[key] = entry
            self.stats.size_bytes += size_bytes
            self.stats.entry_count = len(self.cache)
            self.stats.writes += 1
            
            # Evict if necessary
            await self._evict_if_needed()
    
    async def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                self.stats.size_bytes -= entry.size_bytes
                del self.cache[key]
                self.stats.entry_count = len(self.cache)
                return True
            return False
    
    async def delete_by_tags(self, tags: Set[str]) -> int:
        """Delete all entries matching any of the given tags"""
        async with self._lock:
            keys_to_delete = []
            for key, entry in self.cache.items():
                if entry.tags.intersection(tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                entry = self.cache[key]
                self.stats.size_bytes -= entry.size_bytes
                del self.cache[key]
            
            self.stats.entry_count = len(self.cache)
            return len(keys_to_delete)
    
    async def _evict_if_needed(self):
        """Evict entries if cache limits are exceeded"""
        while (len(self.cache) > self.max_size or 
               self.stats.size_bytes > self.max_memory_bytes):
            if not self.cache:
                break
            
            # Remove least recently used
            key, entry = self.cache.popitem(last=False)
            self.stats.size_bytes -= entry.size_bytes
            self.stats.evictions += 1
        
        self.stats.entry_count = len(self.cache)
    
    async def clear(self):
        """Clear all entries"""
        async with self._lock:
            self.cache.clear()
            self.stats = CacheStats()

class CacheManager:
    """Multi-level cache manager with intelligent strategies"""
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool = None):
        self.redis = redis_client
        self.db_pool = db_pool
        
        # L1 Memory caches by category
        self.l1_caches = {
            "search_results": LRUCache(max_size=500, max_memory_mb=50),
            "embeddings": LRUCache(max_size=1000, max_memory_mb=100),
            "model_responses": LRUCache(max_size=200, max_memory_mb=200),
            "aggregations": LRUCache(max_size=100, max_memory_mb=50),
            "metadata": LRUCache(max_size=1000, max_memory_mb=10)
        }
        
        # Cache configuration
        self.cache_config = {
            "search_results": {"ttl": 3600, "strategy": CacheStrategy.LRU},  # 1 hour
            "embeddings": {"ttl": 86400, "strategy": CacheStrategy.LFU},     # 24 hours
            "model_responses": {"ttl": 1800, "strategy": CacheStrategy.SMART}, # 30 minutes
            "aggregations": {"ttl": 7200, "strategy": CacheStrategy.LRU},    # 2 hours
            "metadata": {"ttl": 3600, "strategy": CacheStrategy.TTL}         # 1 hour
        }
        
        # Preemptive caching
        self.trending_topics: Dict[str, int] = defaultdict(int)
        self.search_patterns: Dict[str, List[str]] = defaultdict(list)
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.running = False
    
    async def start(self):
        """Start background cache management tasks"""
        self.running = True
        
        self.background_tasks = [
            asyncio.create_task(self._preemptive_cache_worker()),
            asyncio.create_task(self._cache_cleanup_worker()),
            asyncio.create_task(self._trending_analysis_worker())
        ]
        
        logger.info("Cache manager started with background workers")
    
    async def stop(self):
        """Stop background tasks"""
        self.running = False
        
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        logger.info("Cache manager stopped")
    
    def _generate_cache_key(self, category: str, **kwargs) -> str:
        """Generate a deterministic cache key"""
        # Sort kwargs for consistent key generation
        key_data = json.dumps(kwargs, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        return f"{category}:{key_hash}"
    
    async def get(
        self,
        category: str,
        use_l1: bool = True,
        use_l2: bool = True,
        use_l3: bool = True,
        **kwargs
    ) -> Optional[Any]:
        """Get value from multi-level cache"""
        
        cache_key = self._generate_cache_key(category, **kwargs)
        
        # L1 Memory Cache
        if use_l1 and category in self.l1_caches:
            value = await self.l1_caches[category].get(cache_key)
            if value is not None:
                logger.debug(f"L1 cache hit: {cache_key}")
                return value
        
        # L2 Redis Cache
        if use_l2:
            value = await self._get_from_redis(cache_key)
            if value is not None:
                logger.debug(f"L2 cache hit: {cache_key}")
                
                # Populate L1 cache
                if use_l1 and category in self.l1_caches:
                    config = self.cache_config.get(category, {})
                    await self.l1_caches[category].set(
                        cache_key, value, ttl_seconds=config.get("ttl")
                    )
                
                return value
        
        # L3 Database Cache
        if use_l3 and self.db_pool:
            value = await self._get_from_database(cache_key)
            if value is not None:
                logger.debug(f"L3 cache hit: {cache_key}")
                
                # Populate upper levels
                if use_l2:
                    await self._set_to_redis(cache_key, value, ttl_seconds=3600)
                
                if use_l1 and category in self.l1_caches:
                    config = self.cache_config.get(category, {})
                    await self.l1_caches[category].set(
                        cache_key, value, ttl_seconds=config.get("ttl")
                    )
                
                return value
        
        logger.debug(f"Cache miss: {cache_key}")
        return None
    
    async def set(
        self,
        category: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Set[str] = None,
        use_l1: bool = True,
        use_l2: bool = True,
        use_l3: bool = False,
        **kwargs
    ):
        """Set value in multi-level cache"""
        
        cache_key = self._generate_cache_key(category, **kwargs)
        config = self.cache_config.get(category, {})
        ttl = ttl_seconds or config.get("ttl", 3600)
        
        # L1 Memory Cache
        if use_l1 and category in self.l1_caches:
            await self.l1_caches[category].set(
                cache_key, value, ttl_seconds=ttl, tags=tags
            )
        
        # L2 Redis Cache
        if use_l2:
            await self._set_to_redis(cache_key, value, ttl_seconds=ttl, tags=tags)
        
        # L3 Database Cache
        if use_l3 and self.db_pool:
            await self._set_to_database(cache_key, value, ttl_seconds=ttl, tags=tags)
        
        logger.debug(f"Cached: {cache_key} (TTL: {ttl}s)")
    
    async def delete(self, category: str, **kwargs):
        """Delete from all cache levels"""
        cache_key = self._generate_cache_key(category, **kwargs)
        
        # Delete from all levels
        if category in self.l1_caches:
            await self.l1_caches[category].delete(cache_key)
        
        await self.redis.delete(cache_key)
        
        if self.db_pool:
            await self._delete_from_database(cache_key)
        
        logger.debug(f"Deleted: {cache_key}")
    
    async def invalidate_by_tags(self, tags: Set[str]):
        """Invalidate cache entries by tags across all levels"""
        
        # L1 caches
        for cache in self.l1_caches.values():
            await cache.delete_by_tags(tags)
        
        # L2 Redis (using key patterns)
        for tag in tags:
            pattern = f"*tag:{tag}*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        
        # L3 Database
        if self.db_pool:
            await self._delete_from_database_by_tags(tags)
        
        logger.info(f"Invalidated cache entries with tags: {tags}")
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """Get value from Redis with decompression"""
        try:
            compressed_data = await self.redis.get(key)
            if compressed_data:
                data = gzip.decompress(compressed_data)
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Redis get error for {key}: {e}")
        return None
    
    async def _set_to_redis(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
        tags: Set[str] = None
    ):
        """Set value to Redis with compression"""
        try:
            # Serialize and compress
            data = pickle.dumps(value)
            compressed_data = gzip.compress(data)
            
            # Set with TTL
            await self.redis.setex(key, ttl_seconds, compressed_data)
            
            # Set tag mappings for invalidation
            if tags:
                for tag in tags:
                    tag_key = f"tag:{tag}:{key}"
                    await self.redis.setex(tag_key, ttl_seconds, "1")
            
        except Exception as e:
            logger.warning(f"Redis set error for {key}: {e}")
    
    async def _get_from_database(self, key: str) -> Optional[Any]:
        """Get value from database cache"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT value, expires_at FROM cache_entries WHERE key = $1",
                    key
                )
                
                if row and (not row['expires_at'] or row['expires_at'] > datetime.utcnow()):
                    return pickle.loads(row['value'])
                    
        except Exception as e:
            logger.warning(f"Database get error for {key}: {e}")
        return None
    
    async def _set_to_database(
        self,
        key: str,
        value: Any,
        ttl_seconds: int,
        tags: Set[str] = None
    ):
        """Set value to database cache"""
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            data = pickle.dumps(value)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO cache_entries (key, value, expires_at, tags, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (key) DO UPDATE SET
                        value = $2, expires_at = $3, tags = $4, updated_at = NOW()
                """, key, data, expires_at, list(tags) if tags else [], datetime.utcnow())
                
        except Exception as e:
            logger.warning(f"Database set error for {key}: {e}")
    
    async def _delete_from_database(self, key: str):
        """Delete from database cache"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("DELETE FROM cache_entries WHERE key = $1", key)
        except Exception as e:
            logger.warning(f"Database delete error for {key}: {e}")
    
    async def _delete_from_database_by_tags(self, tags: Set[str]):
        """Delete from database by tags"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM cache_entries WHERE tags && $1",
                    list(tags)
                )
        except Exception as e:
            logger.warning(f"Database delete by tags error: {e}")
    
    # Preemptive Caching Methods
    
    async def record_search_pattern(self, user_id: str, query: str, results: List[str]):
        """Record search patterns for preemptive caching"""
        pattern_key = f"user:{user_id}:searches"
        
        # Store recent searches
        self.search_patterns[pattern_key].append({
            "query": query,
            "results": results[:5],  # Top 5 results
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last 20 searches
        if len(self.search_patterns[pattern_key]) > 20:
            self.search_patterns[pattern_key] = self.search_patterns[pattern_key][-20:]
        
        # Track trending topics
        query_terms = query.lower().split()
        for term in query_terms:
            if len(term) > 3:  # Skip short words
                self.trending_topics[term] += 1
    
    async def _preemptive_cache_worker(self):
        """Background worker for preemptive caching"""
        while self.running:
            try:
                # Find trending search terms
                trending = sorted(
                    self.trending_topics.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]  # Top 10 trending
                
                for term, count in trending:
                    if count > 5:  # Threshold for preemptive caching
                        await self._preemptively_cache_search(term)
                
                # Reset trending counts periodically
                if len(self.trending_topics) > 1000:
                    self.trending_topics.clear()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Preemptive cache worker error: {e}")
                await asyncio.sleep(60)
    
    async def _preemptively_cache_search(self, term: str):
        """Preemptively cache search results for trending terms"""
        try:
            # Generate common variations
            variations = [
                term,
                f"{term} research",
                f"{term} analysis",
                f"{term} study"
            ]
            
            for variation in variations:
                cache_key = self._generate_cache_key("search_results", query=variation)
                
                # Check if already cached
                existing = await self.get("search_results", query=variation)
                if existing:
                    continue
                
                # TODO: Implement actual search execution
                # For now, just log the intent
                logger.info(f"Would preemptively cache search for: {variation}")
                
        except Exception as e:
            logger.warning(f"Preemptive caching error for {term}: {e}")
    
    async def _cache_cleanup_worker(self):
        """Background worker for cache cleanup and optimization"""
        while self.running:
            try:
                # Clean expired entries from database
                if self.db_pool:
                    async with self.db_pool.acquire() as conn:
                        deleted = await conn.fetchval("""
                            DELETE FROM cache_entries 
                            WHERE expires_at < NOW() 
                            RETURNING COUNT(*)
                        """)
                        if deleted:
                            logger.info(f"Cleaned {deleted} expired cache entries")
                
                # Optimize Redis memory
                await self.redis.execute_command("MEMORY", "PURGE")
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Cache cleanup worker error: {e}")
                await asyncio.sleep(3600)
    
    async def _trending_analysis_worker(self):
        """Background worker for analyzing and updating trending topics"""
        while self.running:
            try:
                # Analyze search patterns for ML insights
                current_hour = datetime.utcnow().hour
                
                # Store hourly trending data
                trending_data = {
                    "hour": current_hour,
                    "trends": dict(list(self.trending_topics.items())[:20]),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self.redis.lpush(
                    "handywriterz:trending_history",
                    json.dumps(trending_data)
                )
                await self.redis.ltrim("handywriterz:trending_history", 0, 168)  # Keep 7 days
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Trending analysis worker error: {e}")
                await asyncio.sleep(3600)
    
    # Streaming Aggregation Methods
    
    async def stream_aggregate(
        self,
        stream_id: str,
        data_points: List[Dict[str, Any]],
        aggregation_func: Callable,
        window_size: int = 100
    ) -> Any:
        """Perform streaming aggregation with caching"""
        
        # Check for cached partial results
        cache_key = self._generate_cache_key("streaming_agg", stream_id=stream_id)
        cached_state = await self.get("aggregations", stream_id=stream_id)
        
        if cached_state:
            # Continue from cached state
            aggregated_result = aggregation_func(cached_state, data_points)
        else:
            # Start fresh aggregation
            aggregated_result = aggregation_func(None, data_points)
        
        # Cache the intermediate result
        await self.set(
            "aggregations",
            aggregated_result,
            ttl_seconds=1800,  # 30 minutes
            stream_id=stream_id
        )
        
        return aggregated_result
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "l1_memory": {},
            "l2_redis": {},
            "l3_database": {},
            "trending": {
                "topics": dict(list(self.trending_topics.items())[:10]),
                "pattern_count": len(self.search_patterns)
            }
        }
        
        # L1 stats
        for category, cache in self.l1_caches.items():
            stats["l1_memory"][category] = {
                "hits": cache.stats.hits,
                "misses": cache.stats.misses,
                "hit_rate": cache.stats.hit_rate,
                "size_bytes": cache.stats.size_bytes,
                "entry_count": cache.stats.entry_count
            }
        
        # L2 Redis stats
        try:
            redis_info = await self.redis.info("memory")
            stats["l2_redis"] = {
                "used_memory": redis_info.get("used_memory", 0),
                "used_memory_human": redis_info.get("used_memory_human", "0B"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.warning(f"Could not get Redis stats: {e}")
            stats["l2_redis"] = {"error": str(e)}
        
        # L3 Database stats
        if self.db_pool:
            try:
                async with self.db_pool.acquire() as conn:
                    db_stats = await conn.fetchrow("""
                        SELECT 
                            COUNT(*) as entry_count,
                            SUM(LENGTH(value)) as total_bytes,
                            COUNT(*) FILTER (WHERE expires_at > NOW()) as active_entries
                        FROM cache_entries
                    """)
                    stats["l3_database"] = dict(db_stats) if db_stats else {}
            except Exception as e:
                logger.warning(f"Could not get database stats: {e}")
                stats["l3_database"] = {"error": str(e)}
        
        return stats