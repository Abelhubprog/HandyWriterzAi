"""
Initializes the database with system prompts.
"""

import asyncio
import logging
import os

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text

# Add the src directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from prompts.system_prompts import get_initial_prompts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """
    Connects to the database and populates it with the initial system prompts.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ DATABASE_URL environment variable is not set.")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(db_url)

    async with engine.connect() as conn:
        logger.info("🚀 Populating database with initial system prompts...")
        
        initial_prompts = get_initial_prompts()
        
        for prompt in initial_prompts:
            try:
                # Check if the prompt already exists
                result = await conn.execute(
                    text("SELECT id FROM system_prompts WHERE stage_id = :stage_id AND version = :version"),
                    {"stage_id": prompt["stage_id"], "version": prompt["version"]}
                )
                
                if result.first():
                    logger.info(f"✅ Prompt for stage '{prompt['stage_id']}' version {prompt['version']} already exists. Skipping.")
                    continue

                # Insert the new prompt
                await conn.execute(
                    text(
                        """
                        INSERT INTO system_prompts (stage_id, template, version)
                        VALUES (:stage_id, :template, :version)
                        """
                    ),
                    prompt
                )
                logger.info(f"✅ Inserted prompt for stage: {prompt['stage_id']}")
            except Exception as e:
                logger.error(f"❌ Error inserting prompt for stage {prompt['stage_id']}: {e}")
        
        logger.info("✅ Database population complete.")
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(main())