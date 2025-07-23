import os
import json
import asyncio
from celery import Celery
from gateways.telegram_gateway import send_doc_and_get_reports
# Assuming you have a storage utility, e.g., for S3
# from utils.storage import upload_file

# Configure Celery
# It's recommended to use a config file for these settings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery('chunk_worker', broker=REDIS_URL)

# A (stubbed) function to update your database
def update_chunk_status_in_db(chunk_id, status, sim_pdf_url=None, ai_pdf_url=None):
    print(f"Updating chunk {chunk_id} to status {status} with reports: {sim_pdf_url}, {ai_pdf_url}")
    # In a real implementation, this would be a database call, e.g.:
    # with SessionLocal() as db:
    #     db.query(DocChunk).filter(DocChunk.id == chunk_id).update({
    #         "status": status,
    #         "similarity_report_url": sim_pdf_url,
    #         "ai_report_url": ai_pdf_url,
    #         "last_updated": datetime.utcnow()
    #     })
    #     db.commit()
    pass

@celery_app.task(name='process_chunk_for_turnitin', max_retries=2)
def process_chunk_for_turnitin(message: str):
    """
    Celery task to process a single document chunk.
    It downloads the chunk, runs it through the Telegram Turnitin bot,
    and uploads the resulting reports.
    """
    try:
        data = json.loads(message)
        chunk_id = data['chunk_id']
        s3_key = data['s3_key'] # The path to the chunk file in S3 or local storage

        print(f"Processing chunk_id: {chunk_id} from {s3_key}")

        # 1. Download the file from storage (if necessary).
        # For this example, we'll assume the file is accessible at `s3_key` path.
        local_path = s3_key # In reality, you'd download this file first.

        # 2. Run the Turnitin process via the Telegram gateway
        try:
            sim_pdf_bytes, ai_pdf_bytes = asyncio.run(send_doc_and_get_reports(local_path))
        except Exception as e:
            print(f"Telegram gateway failed for chunk {chunk_id}: {e}")
            update_chunk_status_in_db(chunk_id, 'telegram_failed')
            # Celery will retry based on `max_retries`
            raise e

        # 3. Upload the reports to your storage (e.g., S3)
        # This part is stubbed out.
        # sim_report_url = upload_file(sim_pdf_bytes, f"reports/{chunk_id}_sim.pdf", "application/pdf")
        # ai_report_url = upload_file(ai_pdf_bytes, f"reports/{chunk_id}_ai.pdf", "application/pdf")
        sim_report_url = f"s3://your-bucket/reports/{chunk_id}_sim.pdf"
        ai_report_url = f"s3://your-bucket/reports/{chunk_id}_ai.pdf"


        # 4. Update the chunk status in the database to 'needs_edit'
        # This indicates the chunk is ready for a human checker.
        update_chunk_status_in_db(chunk_id, 'needs_edit', sim_report_url, ai_report_url)

        print(f"Successfully processed chunk {chunk_id}. Ready for human checker.")

    except json.JSONDecodeError:
        print(f"Failed to decode message: {message}")
    except KeyError as e:
        print(f"Missing key in message: {e}")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")
        # This will trigger a retry if the task has `max_retries` set
        process_chunk_for_turnitin.retry(exc=exc)

if __name__ == '__main__':
    # To run this worker, you would use the command:
    # celery -A workers.chunk_queue_worker worker --loglevel=info
    pass