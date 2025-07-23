"""
Enhanced File API for Railway Deployment
Optimized for chat context files with improved processing pipeline
"""

import asyncio
import logging
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import mimetypes

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from ..services.security_service import get_current_user
from ..services.chunking_service import get_chunking_service
from ..services.embedding_service import get_embedding_service
from ..services.vector_storage import get_vector_storage
from ..services.railway_db_service import get_railway_service
from ..workers.chunk_queue_worker import process_file_chunk

logger = logging.getLogger(__name__)
router = APIRouter()

# Railway-optimized configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (Railway friendly)
MAX_FILES_PER_REQUEST = 10
SUPPORTED_TYPES = {
    'text/plain', 'text/markdown', 'text/csv',
    'application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'audio/mpeg', 'audio/wav', 'audio/ogg',
    'video/mp4', 'video/webm', 'video/avi'
}

# Create upload directory
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    type: str
    status: str
    upload_url: Optional[str] = None
    message: str

class FileProcessingResponse(BaseModel):
    file_id: str
    status: str
    chunks: int
    embeddings: int
    processing_time: float
    message: str

class ChatContextFile(BaseModel):
    file_id: str
    filename: str
    size: int
    type: str
    chunks: int
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime]

@router.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    context: str = Form(default="chat"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Upload a single file for chat context with Railway optimization.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Check file type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if content_type not in SUPPORTED_TYPES:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {content_type}"
            )
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        user_id = current_user.get("id") if current_user else "anonymous"
        
        # Create file path
        safe_filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store file metadata in Railway PostgreSQL
        railway_service = get_railway_service()
        async with railway_service.get_connection() as conn:
            await conn.execute("""
                INSERT INTO chat_files (
                    file_id, user_id, filename, file_path, 
                    size, content_type, context, status, uploaded_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, 
            file_id, user_id, file.filename, file_path,
            len(content), content_type, context, "uploaded", datetime.utcnow()
            )
        
        logger.info(f"File uploaded: {file.filename} ({len(content)} bytes) by user {user_id}")
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            size=len(content),
            type=content_type,
            status="uploaded",
            message="File uploaded successfully. Ready for processing."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

@router.post("/files/{file_id}/process", response_model=FileProcessingResponse)
async def process_file(
    file_id: str,
    context: str = Form(default="chat"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    chunking_service = Depends(get_chunking_service),
    embedding_service = Depends(get_embedding_service),
    vector_storage = Depends(get_vector_storage)
):
    """
    Process uploaded file: chunk, embed, and store in vector database.
    """
    start_time = datetime.utcnow()
    
    try:
        # Get file metadata from Railway PostgreSQL
        railway_service = get_railway_service()
        async with railway_service.get_connection() as conn:
            file_record = await conn.fetchrow(
                "SELECT * FROM chat_files WHERE file_id = $1", file_id
            )
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_record["status"] == "processed":
            return FileProcessingResponse(
                file_id=file_id,
                status="already_processed",
                chunks=file_record.get("chunk_count", 0),
                embeddings=file_record.get("embedding_count", 0),
                processing_time=0,
                message="File already processed"
            )
        
        # Read file content
        file_path = file_record["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File content not found")
        
        with open(file_path, "rb") as f:
            content = f.read()
        
        # Extract text based on file type
        text_content = await extract_text(content, file_record["content_type"])
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content extracted")
        
        # Chunk the text
        chunks = chunking_service.chunk_text(text_content)
        logger.info(f"File {file_id} chunked into {len(chunks)} pieces")
        
        # Generate embeddings and store
        embeddings_created = 0
        user_id = current_user.get("id") if current_user else "anonymous"
        
        for i, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = await embedding_service.embed_text(
                    chunk, 
                    context="document_chunk"
                )
                
                # Store in vector database
                await vector_storage.store_document_chunk(
                    user_id=user_id,
                    file_id=file_id,
                    chunk_index=i,
                    content=chunk,
                    embedding=embedding,
                    metadata={
                        "filename": file_record["filename"],
                        "content_type": file_record["content_type"],
                        "context": context,
                        "chunk_size": len(chunk),
                        "total_chunks": len(chunks)
                    }
                )
                
                embeddings_created += 1
                
            except Exception as e:
                logger.error(f"Failed to process chunk {i} of file {file_id}: {e}")
                continue
        
        # Update file status in database
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        async with railway_service.get_connection() as conn:
            await conn.execute("""
                UPDATE chat_files 
                SET status = $1, chunk_count = $2, embedding_count = $3, 
                    processing_time = $4, processed_at = $5
                WHERE file_id = $6
            """, 
            "processed", len(chunks), embeddings_created, 
            processing_time, datetime.utcnow(), file_id
            )
        
        logger.info(f"File {file_id} processed: {len(chunks)} chunks, {embeddings_created} embeddings")
        
        return FileProcessingResponse(
            file_id=file_id,
            status="processed",
            chunks=len(chunks),
            embeddings=embeddings_created,
            processing_time=processing_time,
            message=f"File processed successfully into {len(chunks)} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File processing failed for {file_id}: {e}")
        
        # Update status to error
        try:
            async with railway_service.get_connection() as conn:
                await conn.execute(
                    "UPDATE chat_files SET status = $1 WHERE file_id = $2",
                    "error", file_id
                )
        except:
            pass
        
        raise HTTPException(status_code=500, detail="Processing failed")

@router.get("/files/chat-context")
async def get_chat_context_files(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    limit: int = 50
) -> List[ChatContextFile]:
    """
    Get user's chat context files from Railway PostgreSQL.
    """
    try:
        user_id = current_user.get("id") if current_user else "anonymous"
        
        railway_service = get_railway_service()
        async with railway_service.get_connection() as conn:
            records = await conn.fetch("""
                SELECT file_id, filename, size, content_type, 
                       chunk_count, status, uploaded_at, processed_at
                FROM chat_files 
                WHERE user_id = $1 AND context = 'chat'
                ORDER BY uploaded_at DESC 
                LIMIT $2
            """, user_id, limit)
        
        return [
            ChatContextFile(
                file_id=r["file_id"],
                filename=r["filename"],
                size=r["size"],
                type=r["content_type"],
                chunks=r["chunk_count"] or 0,
                status=r["status"],
                uploaded_at=r["uploaded_at"],
                processed_at=r["processed_at"]
            )
            for r in records
        ]
        
    except Exception as e:
        logger.error(f"Failed to get chat context files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    Delete a file and its associated data.
    """
    try:
        user_id = current_user.get("id") if current_user else "anonymous"
        
        railway_service = get_railway_service()
        vector_storage_service = get_vector_storage()
        
        # Get file record
        async with railway_service.get_connection() as conn:
            file_record = await conn.fetchrow(
                "SELECT * FROM chat_files WHERE file_id = $1 AND user_id = $2",
                file_id, user_id
            )
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete physical file
        file_path = file_record["file_path"]
        if os.path.exists(file_path):
            os.unlink(file_path)
        
        # Delete from vector database
        await vector_storage_service.delete_document_chunks(file_id)
        
        # Delete from PostgreSQL
        async with railway_service.get_connection() as conn:
            await conn.execute(
                "DELETE FROM chat_files WHERE file_id = $1 AND user_id = $2",
                file_id, user_id
            )
        
        logger.info(f"File {file_id} deleted by user {user_id}")
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {e}")
        raise HTTPException(status_code=500, detail="Delete failed")

async def extract_text(content: bytes, content_type: str) -> str:
    """
    Extract text content from various file types.
    """
    try:
        if content_type.startswith('text/'):
            return content.decode('utf-8', errors='ignore')
        
        elif content_type == 'application/pdf':
            # Use PyPDF2 or similar library
            import PyPDF2
            from io import BytesIO
            
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif content_type.startswith('image/'):
            # Use OCR for images (requires additional setup)
            # For now, return filename as context
            return f"[Image file - OCR not implemented yet]"
        
        elif 'word' in content_type or 'document' in content_type:
            # Use python-docx for Word documents
            import docx
            from io import BytesIO
            
            doc = docx.Document(BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        else:
            # Try to decode as text
            return content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        logger.error(f"Text extraction failed for type {content_type}: {e}")
        return ""

# Add router to main application
__all__ = ['router']