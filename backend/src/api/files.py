import logging
import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from tusclient import client as tus_client
from tusclient.exceptions import TusCommunicationError

from ..workers.chunk_queue_worker import process_file_chunk
from ..services.security_service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
TUS_SERVER_URL = os.getenv("TUS_SERVER_URL", "http://localhost:1080/files/")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILE_COUNT = 50

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/files/presign")
async def create_upload(
    request: Request,
    filename: str = Form(...),
    filesize: int = Form(...),
    mime_type: str = Form(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Creates a new tus upload and returns the upload URL.
    """
    if filesize > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds the limit of {MAX_FILE_SIZE // (1024*1024)}MB.")

    # In a real application, you would check the user's file count against the limit here.
    # For now, we'll just log it.
    logger.info(f"User {current_user.get('id') if current_user else 'anonymous'} is uploading {filename}")

    try:
        # Create a tus client
        my_client = tus_client.TusClient(TUS_SERVER_URL)

        # Create a new uploader
        uploader = my_client.uploader(
            file_path=None,  # We are not uploading from a file path, but from a stream
            chunk_size=5 * 1024 * 1024,  # 5MB chunks
            metadata={"filename": filename, "mime_type": mime_type},
            # The client will handle the upload from the frontend
        )

        # The uploader object itself contains the upload URL
        upload_url = uploader.url

        return {"upload_url": upload_url}

    except TusCommunicationError as e:
        logger.error(f"Failed to communicate with tus server: {e}")
        raise HTTPException(status_code=503, detail="Could not connect to the upload server.")
    except Exception as e:
        logger.error(f"Failed to create upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to create upload.")


@router.post("/files/notify")
async def notify_upload_complete(
    request: Request,
    upload_url: str = Form(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Notified by the frontend when a tus upload is complete.
    The file is then enqueued for processing.
    """
    try:
        # In a real application, you would verify the upload with the tus server.
        # For this example, we'll assume the upload is complete and the file is available.

        # The filename is stored in the metadata of the tus upload.
        # We would need to retrieve it from the tus server.
        # For now, we'll generate a placeholder name.
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.dat"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Here, you would download the file from the tus server to the UPLOAD_DIR.
        # Since we don't have a running tus server in this context, we'll just create a dummy file.
        with open(file_path, "w") as f:
            f.write("This is a placeholder for the uploaded file.")

        # Enqueue the file for processing
        process_file_chunk.delay(file_path)

        logger.info(f"File {filename} enqueued for processing.")
        return {"status": "enqueued", "file_id": file_id}

    except Exception as e:
        logger.error(f"Failed to process completed upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to process completed upload.")
