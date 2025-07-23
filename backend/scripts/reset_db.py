import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def reset_database():
    """
    Resets the database by dropping the model_map table if it exists,
    then creating it with the correct schema and data.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "handywriterz.db"))
        database_url = f"sqlite:///{db_path}"

    engine = create_engine(database_url)
    with engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS model_map"))
        connection.execute(text("""
            CREATE TABLE model_map (
                stage_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                PRIMARY KEY (stage_id),
                CHECK (stage_id IN ('INTENT', 'PLAN', 'SEARCH-A', 'SEARCH-B', 'SEARCH-C', 'EVIDENCE', 'WRITE', 'REWRITE', 'QA-1', 'QA-2', 'QA-3'))
            )
        """))
        connection.execute(text("""
            INSERT INTO model_map (stage_id, model_name) VALUES
                ('INTENT', 'gemini-2.5-pro'),
                ('PLAN', 'gemini-pro'),
                ('SEARCH-A', 'gemini-pro-web-tool'),
                ('SEARCH-B', 'grok-4-web'),
                ('SEARCH-C', 'openai-o3-browser'),
                ('EVIDENCE', 'gemini-pro-function-call'),
                ('WRITE', 'gemini-pro'),
                ('REWRITE', 'openai-o3'),
                ('QA-1', 'gemini-pro'),
                ('QA-2', 'grok-4'),
                ('QA-3', 'openai-o3')
        """))
        connection.commit()

if __name__ == "__main__":
    reset_database()
    print("Database reset successfully.")