import os
import logging
from typing import Dict, Any, Optional

# Import Railway service as replacement for Supabase
from .railway_db_service import get_railway_service, get_railway_client

logger = logging.getLogger(__name__)

class SupabaseService:
    """A service for interacting with database (now uses Railway PostgreSQL)."""

    def __init__(self):
        # Use Railway PostgreSQL service instead of Supabase
        self.railway_service = get_railway_service()
        logger.info("✅ Using Railway PostgreSQL instead of Supabase")

    async def store_user_memory(self, user_id: str, fingerprint: dict):
        """Stores or updates a user's writing fingerprint in Railway PostgreSQL."""
        try:
            result = await self.railway_service.store_user_memory(user_id, fingerprint)
            return result
        except Exception as e:
            logger.error(f"Error storing user memory: {e}")
            return None

    async def get_user_memory(self, user_id: str):
        """Retrieves a user's writing fingerprint from Railway PostgreSQL."""
        try:
            result = await self.railway_service.get_user_memory(user_id)
            return result.get('fingerprint') if result else None
        except Exception as e:
            logger.error(f"Error retrieving user memory: {e}")
            return None


def get_supabase_client():
    """Get database client instance (now uses Railway PostgreSQL)."""
    try:
        return get_railway_client()
    except Exception as e:
        logger.warning(f"Railway client creation failed, using mock: {e}")
        # Return a mock client for testing
        class MockClient:
            def table(self, table_name):
                return MockTable()
        return MockClient()


class MockTable:
    """Mock table for testing."""
    def select(self, *args):
        return self
    def eq(self, *args):
        return self
    def single(self):
        return self
    def execute(self):
        return None, 0
    def upsert(self, *args):
        return self
