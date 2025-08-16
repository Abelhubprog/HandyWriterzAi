import logging
import os
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, File
try:
    from tusclient import client as tus_client  # type: ignore
    from tusclient.exceptions import TusCommunicationError  # type: ignore
except Exception:  # pragma: no cover
    tus_client = None  # type: ignore
    class TusCommunicationError(Exception):  # type: ignore
        pass

from ..services.security_service import get_current_user
from ..services.object_storage import get_r2_storage
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

# Direct multipart upload → Cloudflare R2 (S3-compatible)
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
        storage = None
        try:
            storage = get_r2_storage()
        except Exception as e:
            logger.error(f"Object storage not configured: {e}")
            raise HTTPException(status_code=500, detail="Object storage not configured")

        for file in files:
            # Check file size
            file_content = await file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File {file.filename} exceeds the limit of {MAX_FILE_SIZE // (1024*1024)}MB."
                )

            # Generate unique file ID and R2 object key
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename or "")[1] or ".bin"
            # Keep original name for convenience, but namespace by file_id
            safe_name = (file.filename or "upload").replace("/", "_").replace("\\", "_")
            object_key = f"uploads/{file_id}/{safe_name}"

            # Upload to R2
            storage.upload_bytes(object_key, file_content, content_type=file.content_type)

            # Build accessible URL
            public_url = storage.build_public_url(object_key) or storage.generate_presigned_url(object_key, expires_in=3600)

            uploaded_files.append({
                "file_id": file_id,
                "filename": file.filename,
                "size": len(file_content),
                "mime_type": file.content_type,
                "url": public_url,
                "key": object_key,
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
    """Serve file by ID via presigned URL or stream bytes from R2."""
    try:
        storage = get_r2_storage()
        prefix = f"uploads/{file_id}/"
        keys = storage.list_with_prefix(prefix)
        if not keys:
            raise HTTPException(status_code=404, detail="File not found")
        # Pick the first object under this prefix
        key = keys[0]
        # Prefer redirect to a presigned URL
        from fastapi.responses import RedirectResponse
        url = storage.build_public_url(key) or storage.generate_presigned_url(key, expires_in=300)
        return RedirectResponse(url=url, status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file")

@router.post("/files/presign")
async def create_upload(
    request: Request,
    filename: str = Form(...),
    filesize: int = Form(...),
    mime_type: str = Form(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """Presign a direct PUT to R2 for browser uploads."""
    if filesize > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds the limit of {MAX_FILE_SIZE // (1024*1024)}MB.")

    try:
        storage = get_r2_storage()
        file_id = str(uuid.uuid4())
        safe_name = (filename or "upload").replace("/", "_").replace("\\", "_")
        key = f"uploads/{file_id}/{safe_name}"
        url = storage.generate_presigned_put_url(key, content_type=mime_type, expires_in=3600)
        return {"file_id": file_id, "key": key, "upload_url": url, "headers": {"Content-Type": mime_type}}
    except Exception as e:
        logger.error(f"Failed to presign upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to create presigned upload URL")


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

# ---- Added helpers and routes: POST /api/files (alias) and GET /api/files/{id}/meta ----
from typing import Dict, Any  # added for metadata helper
from fastapi.responses import JSONResponse  # added for meta endpoint response

def _build_file_meta(file_id: str, file_path: str, original_name: Optional[str] = None, mime_type: Optional[str] = None) -> Dict[str, Any]:
    size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    filename = original_name or os.path.basename(file_path)
    return {
        "file_id": file_id,
        "filename": filename,
        "size": size,
        "mime_type": mime_type or "application/octet-stream",
        "url": f"/api/files/{file_id}",
        "path": file_path,
    }

@router.post("/files")
async def upload_files_alias(
    files: List[UploadFile] = File(...),
    current_user: Optional[dict] = Depends(get_current_user),
):
    # Alias handler for clients posting to /api/files
    # Reuse the existing /files/upload logic
    return await upload_files(files=files, current_user=current_user)

@router.get("/files/{file_id}/meta")
async def get_file_meta(file_id: str):
    """
    Return metadata for an uploaded file without serving bytes.
    """
    try:
        storage = get_r2_storage()
        prefix = f"uploads/{file_id}/"
        keys = storage.list_with_prefix(prefix)
        if not keys:
            raise HTTPException(status_code=404, detail="File not found")
        key = keys[0]
        # Basic meta (size requires head_object; keep minimal)
        url = storage.build_public_url(key) or None
        return JSONResponse(content={
            "file_id": file_id,
            "key": key,
            "url": url,
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get meta for {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metadata")
# ---- End additions ----
