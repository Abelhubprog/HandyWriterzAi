"""
Railway PostgreSQL Service - Replacement for Supabase
Provides the same interface as SupabaseService but uses Railway PostgreSQL directly
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
import asyncpg
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class RailwayDBService:
    """A service for interacting with Railway PostgreSQL."""

    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set.")
        
        # Handle postgres:// to postgresql:// conversion (Railway compatibility)
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection with proper error handling."""
        conn = None
        try:
            conn = await asyncpg.connect(self.database_url)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                await conn.close()

    async def store_user_memory(self, user_id: str, fingerprint: dict) -> Optional[Dict[str, Any]]:
        """Stores or updates a user's writing fingerprint in Railway PostgreSQL."""
        try:
            async with self.get_connection() as conn:
                # Use UPSERT (ON CONFLICT) for PostgreSQL
                query = """
                INSERT INTO user_memories (user_id, fingerprint, updated_at) 
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    fingerprint = EXCLUDED.fingerprint,
                    updated_at = NOW()
                RETURNING id, user_id, created_at, updated_at;
                """
                
                fingerprint_json = json.dumps(fingerprint)
                result = await conn.fetchrow(query, user_id, fingerprint_json)
                
                if result:
                    return {
                        "id": result["id"],
                        "user_id": result["user_id"],
                        "created_at": result["created_at"].isoformat(),
                        "updated_at": result["updated_at"].isoformat()
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error storing user memory: {e}")
            return None

    async def get_user_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user's writing fingerprint from Railway PostgreSQL."""
        try:
            async with self.get_connection() as conn:
                query = """
                SELECT fingerprint, created_at, updated_at 
                FROM user_memories 
                WHERE user_id = $1;
                """
                
                result = await conn.fetchrow(query, user_id)
                
                if result:
                    # Parse JSON fingerprint back to dict
                    fingerprint = json.loads(result["fingerprint"]) if result["fingerprint"] else {}
                    return {
                        "fingerprint": fingerprint,
                        "created_at": result["created_at"].isoformat(),
                        "updated_at": result["updated_at"].isoformat()
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user memory: {e}")
            return None

    async def health_check(self) -> bool:
        """Check if the database connection is healthy."""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval("SELECT 1;")
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def initialize_tables(self):
        """Initialize required tables if they don't exist."""
        try:
            async with self.get_connection() as conn:
                # Create user_memories table
                await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_memories (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) UNIQUE NOT NULL,
                    fingerprint JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                
                # Create index for faster lookups
                await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_memories_user_id 
                ON user_memories(user_id);
                """)
                
                logger.info("✅ Railway PostgreSQL tables initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing tables: {e}")
            raise


# Compatibility layer - provides same interface as Supabase
class RailwayClient:
    """Mock Supabase client interface for Railway PostgreSQL."""
    
    def __init__(self):
        self.db_service = RailwayDBService()
    
    def table(self, table_name: str):
        """Return table interface."""
        return RailwayTable(table_name, self.db_service)


class RailwayTable:
    """Mock Supabase table interface for Railway PostgreSQL."""
    
    def __init__(self, table_name: str, db_service: RailwayDBService):
        self.table_name = table_name
        self.db_service = db_service
        self._where_clause = None
    
    def select(self, columns: str = "*"):
        """Select columns (mock interface)."""
        self._columns = columns
        return self
    
    def eq(self, column: str, value: str):
        """Add WHERE clause (mock interface)."""
        self._where_clause = (column, value)
        return self
    
    def single(self):
        """Return single result (mock interface)."""
        self._single = True
        return self
    
    async def execute(self):
        """Execute the query."""
        if self.table_name == "user_memories" and self._where_clause:
            column, value = self._where_clause
            if column == "user_id":
                result = await self.db_service.get_user_memory(value)
                return result, 1 if result else 0
        return None, 0
    
    def upsert(self, data: Dict[str, Any]):
        """Upsert data (mock interface)."""
        self._upsert_data = data
        return self
    
    async def execute_upsert(self):
        """Execute upsert operation."""
        if self.table_name == "user_memories" and self._upsert_data:
            user_id = self._upsert_data.get("user_id")
            fingerprint = self._upsert_data.get("fingerprint")
            if user_id and fingerprint:
                result = await self.db_service.store_user_memory(user_id, fingerprint)
                return result, 1 if result else 0
        return None, 0


def get_railway_client() -> RailwayClient:
    """Get Railway PostgreSQL client instance (Supabase replacement)."""
    return RailwayClient()


# For backwards compatibility - same interface as supabase_service.py
def get_supabase_client():
    """Backwards compatibility - returns Railway client instead."""
    try:
        return get_railway_client()
    except Exception as e:
        logger.warning(f"Railway client creation failed: {e}")
        # Return mock client for testing
        class MockClient:
            def table(self, table_name):
                return MockTable()
        return MockClient()


class MockTable:
    """Mock table for testing when Railway DB is not available."""
    def select(self, *args):
        return self
    def eq(self, *args):
        return self
    def single(self):
        return self
    async def execute(self):
        return None, 0
    def upsert(self, *args):
        return self
    async def execute_upsert(self):
        return None, 0


# Global service instance
_railway_service = None

def get_railway_service() -> RailwayDBService:
    """Get global Railway database service instance."""
    global _railway_service
    if _railway_service is None:
        _railway_service = RailwayDBService()
    return _railway_service