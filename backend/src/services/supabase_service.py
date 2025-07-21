import os
from supabase import create_client, Client

class SupabaseService:
    """A service for interacting with Supabase."""

    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables not set.")
        self.client: Client = create_client(url, key)

    async def store_user_memory(self, user_id: str, fingerprint: dict):
        """Stores or updates a user's writing fingerprint in Supabase."""
        try:
            data, count = await self.client.table('user_memories').upsert({
                'user_id': user_id,
                'fingerprint': fingerprint,
            }).execute()
            return data
        except Exception as e:
            # In a real application, you'd want more robust error handling here.
            print(f"Error storing user memory: {e}")
            return None

    async def get_user_memory(self, user_id: str):
        """Retrieves a user's writing fingerprint from Supabase."""
        try:
            data, count = await self.client.table('user_memories').select('fingerprint').eq('user_id', user_id).single().execute()
            return data.get('fingerprint') if data else None
        except Exception as e:
            print(f"Error retrieving user memory: {e}")
            return None


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        # Return a mock client for testing
        class MockClient:
            def table(self, table_name):
                return MockTable()
        return MockClient()
    return create_client(url, key)


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
