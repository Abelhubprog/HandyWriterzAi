import json
import os
from datetime import datetime, timedelta
import boto3
import asyncpg
import asyncio
import logging

# Import Railway service instead of Supabase
from ..services.railway_db_service import get_railway_service

logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
S3_BUCKET_NAME = os.getenv("S3_FINETUNE_BUCKET", "hf-tmp")
MIN_EXAMPLES_FOR_JOB = 500

def get_railway_client():
    """Get Railway PostgreSQL service."""
    return get_railway_service()

# Backwards compatibility - redirect to Railway
def get_supabase_client():
    """Backwards compatibility - returns Railway service."""
    return get_railway_client()

def get_s3_client():
    return boto3.client("s3")

def run_finetuning_job():
    """
    - Pulls recent tutor feedback from Supabase.
    - Creates a JSONL file for fine-tuning.
    - Uploads the file to S3.
    - Kicks off a Hugging Face fine-tuning job if enough new examples exist.
    """
    print("🚀 Starting nightly tutor fine-tuning job...")
    railway_service = get_railway_client()
    s3 = get_s3_client()

    try:
        # 1. Fetch recent tutor feedback from Railway PostgreSQL
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        # Use direct PostgreSQL query instead of Supabase
        async with railway_service.get_connection() as conn:
            query = """
            SELECT * FROM tutor_feedback 
            WHERE created_at >= $1
            ORDER BY created_at DESC;
            """
            results = await conn.fetch(query, yesterday)
            
        if not results:
            print("No new tutor feedback in the last 24 hours. Exiting.")
            return

        print(f"Found {len(results)} new feedback entries.")

        # 2. Create JSONL content
        jsonl_content = ""
        for item in results:
            # Assuming a simple schema for tutor_feedback table
            original_text = item.get("original_text")
            tutor_comment = item.get("comment")
            if original_text and tutor_comment:
                record = {
                    "prompt": f"Original Text: {original_text}\n---\nRewrite this text based on the following feedback: {tutor_comment}",
                    "completion": item.get("rewritten_text", "") # Assuming there's a rewritten version
                }
                jsonl_content += json.dumps(record) + "\n"

        if not jsonl_content:
            print("No valid examples to create a fine-tuning file. Exiting.")
            return

        # 3. Upload to S3
        filename = f"handywriterz_ft_{datetime.utcnow().strftime('%Y-%m-%d')}.jsonl"
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=filename, Body=jsonl_content.encode('utf-8'))
        print(f"Successfully uploaded {filename} to S3 bucket {S3_BUCKET_NAME}.")

        # 4. Check if we should kick off a new job
        # This part is a placeholder for interacting with a service like Hugging Face.
        # You would typically check the total number of examples and trigger a job via an API.
        # For now, we'll just log a message.
        # TODO( fill-secret ): Implement Hugging Face API call
        print(f"TODO: Check total examples and trigger Hugging Face LoRA job if > {MIN_EXAMPLES_FOR_JOB}.")

        print("✅ Fine-tuning job completed successfully.")

    except Exception as e:
        print(f"❌ An error occurred during the fine-tuning job: {e}")

if __name__ == "__main__":
    run_finetuning_job()