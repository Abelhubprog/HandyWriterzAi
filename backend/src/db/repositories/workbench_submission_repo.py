import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models import WorkbenchSubmission, WorkbenchSubmissionStatus, Checker

class WorkbenchSubmissionRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_by_submission_id(
        self,
        assignment_id: uuid.UUID,
        checker_id: int,
        submission_id: str,
        similarity_report: Dict[str, Any],
        ai_report: Dict[str, Any],
        modified_document: Dict[str, Any],
        notes: Optional[str] = None,
    ) -> WorkbenchSubmission:
        # Check if submission_id already exists for idempotency
        existing_submission = self.session.execute(
            select(WorkbenchSubmission).where(
                WorkbenchSubmission.submission_id == submission_id
            )
        ).scalar_one_or_none()

        if existing_submission:
            # Update existing submission
            existing_submission.similarity_report = similarity_report
            existing_submission.ai_report = ai_report
            existing_submission.modified_document = modified_document
            existing_submission.notes = notes
            existing_submission.status = WorkbenchSubmissionStatus.SUBMITTED
            existing_submission.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(existing_submission)
            return existing_submission
        else:
            # Create new submission
            submission = WorkbenchSubmission(
                id=uuid.uuid4(),
                assignment_id=assignment_id,
                checker_id=checker_id,
                submission_id=submission_id,
                similarity_report=similarity_report,
                ai_report=ai_report,
                modified_document=modified_document,
                notes=notes,
                status=WorkbenchSubmissionStatus.SUBMITTED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(submission)
            self.session.commit()
            self.session.refresh(submission)
            return submission

    def list_by_assignment(
        self, assignment_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[WorkbenchSubmission]:
        return self.session.execute(
            select(WorkbenchSubmission).where(
                WorkbenchSubmission.assignment_id == assignment_id
            ).order_by(WorkbenchSubmission.created_at.desc()).limit(limit).offset(offset)
        ).scalars().all()

    def list_by_checker(
        self, checker_id: int, limit: int = 50, offset: int = 0
    ) -> List[WorkbenchSubmission]:
        return self.session.execute(
            select(WorkbenchSubmission).where(
                WorkbenchSubmission.checker_id == checker_id
            ).order_by(WorkbenchSubmission.created_at.desc()).limit(limit).offset(offset)
        ).scalars().all()

    def get_latest_by_assignment(self, assignment_id: uuid.UUID) -> Optional[WorkbenchSubmission]:
        return self.session.execute(
            select(WorkbenchSubmission).where(
                WorkbenchSubmission.assignment_id == assignment_id
            ).order_by(WorkbenchSubmission.created_at.desc())
        ).scalar_one_or_none()
