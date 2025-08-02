import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from src.services.document_processing_service import DocumentProcessingService, get_document_processing_service
from src.db.repositories.workbench_submission_repo import WorkbenchSubmissionRepository # Assuming this exists or will be created
from src.db.database import get_workbench_submission_repository # Assuming this exists or will be created
from src.db.models import WorkbenchAssignmentStatus, WorkbenchArtifactType # Assuming these exist

logger = logging.getLogger(__name__)

router = APIRouter()

class DocumentIngestionResponse(BaseModel):
    submission_id: str
    message: str
    filename: str
    processed_data: Dict[str, Any]

@router.post("/workbench/ingest-document", response_model=DocumentIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    file: UploadFile = File(...),
    document_processing_service: DocumentProcessingService = Depends(get_document_processing_service),
    workbench_submission_repo: WorkbenchSubmissionRepository = Depends(get_workbench_submission_repository)
):
    """
    Ingests a document (e.g., DOCX) into the Workbench for processing.
    This endpoint is intended for AI-initiated uploads or internal system use.
    """
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DOCX files are supported for ingestion."
        )

    try:
        file_content = await file.read()
        processed_data = await document_processing_service.process_docx(file_content)

        # Create a new WorkbenchSubmission entry
        # This is a simplified example; you might need more fields or logic here
        submission = await workbench_submission_repo.create_submission(
            assignment_id=None, # This might be linked to an existing assignment or created later
            document_type=WorkbenchArtifactType.ORIGINAL_DOCX_UPLOAD,
            file_name=file.filename,
            file_size=len(file_content),
            processed_text=processed_data.get("full_text"),
            highlighted_sections=processed_data.get("highlighted_sections"),
            status=WorkbenchAssignmentStatus.PENDING_AI_ANALYSIS # Initial status
        )

        logger.info(f"Document '{file.filename}' ingested and processed. Submission ID: {submission.id}")

        return DocumentIngestionResponse(
            submission_id=str(submission.id),
            message="Document successfully ingested and processing initiated.",
            filename=file.filename,
            processed_data=processed_data
        )

    except Exception as e:
        logger.error(f"Failed to ingest document '{file.filename}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {e}"
        )
