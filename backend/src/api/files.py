import logging
import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, File
from tusclient import client as tus_client
from tusclient.exceptions import TusCommunicationError

from ..services.security_service import get_current_user
# Celery worker in workers.chunk_queue_worker exposes 'process_chunk_for_turnitin'
# Import lazily to avoid hard dependency if Celery isn't running
try:
    from ..workers.chunk_queue_worker import process_chunk_for_turnitin  # type: ignore
except Exception:  # pragma: no cover
    process_chunk_for_turnitin = None  # Fallback when worker isn't importable

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
TUS_SERVER_URL = os.getenv("TUS_SERVER_URL", "http://localhost:1080/files/")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILE_COUNT = 50

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/files/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Simple file upload endpoint for the chat interface.
    Accepts multiple files and returns file IDs for context processing.
    """
    if len(files) > MAX_FILE_COUNT:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files. Maximum {MAX_FILE_COUNT} files allowed."
        )

    uploaded_files = []
    file_ids = []

    try:
        for file in files:
            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File {file.filename} exceeds the limit of {MAX_FILE_SIZE // (1024*1024)}MB."
                )

            # Generate unique file ID and save to disk
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename or "")[1] or ".txt"
            saved_filename = f"{file_id}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, saved_filename)

            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Create file URL for frontend
            file_url = f"/api/files/{file_id}"

            uploaded_files.append({
                "file_id": file_id,
                "filename": file.filename,
                "size": len(file_content),
                "mime_type": file.content_type,
                "url": file_url,
                "path": file_path
            })

            file_ids.append(file_id)

            # Queue for processing if needed
            try:
                if process_chunk_for_turnitin:
                    # Align with Celery task signature (expects a JSON string payload)
                    import json
                    payload = json.dumps({"chunk_id": file_id, "s3_key": file_path})
                    process_chunk_for_turnitin.delay(payload)
                    logger.info(f"File {file.filename} queued for processing")
                else:
                    logger.warning("Celery worker not available; skipping queueing")
            except Exception as e:
                logger.warning(f"Could not queue file for processing: {e}")

        logger.info(f"Successfully uploaded {len(files)} files for user {current_user.get('id') if current_user else 'anonymous'}")

        return {
            "success": True,
            "message": f"Successfully uploaded {len(files)} files",
            "files": uploaded_files,
            "file_ids": file_ids
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/files/{file_id}")
async def get_file(file_id: str):
    """
    Serve uploaded files by their ID.
    """
    # Find the file in upload directory
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(file_id):
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(file_path):
                from fastapi.responses import FileResponse
                return FileResponse(
                    file_path,
                    filename=filename,
                    media_type="application/octet-stream"
                )

    raise HTTPException(status_code=404, detail="File not found")

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
        try:
            if process_chunk_for_turnitin:
                import json
                payload = json.dumps({"chunk_id": file_id, "s3_key": file_path})
                process_chunk_for_turnitin.delay(payload)
                logger.info(f"File {filename} enqueued for processing.")
            else:
                logger.warning("Celery worker not available; skipping queueing from notify endpoint")
        except Exception as e:
            logger.warning(f"Queue enqueue failed for {filename}: {e}")
        return {"status": "enqueued", "file_id": file_id}

    except Exception as e:
        logger.error(f"Failed to process completed upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to process completed upload.")
