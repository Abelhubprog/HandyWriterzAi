import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models import WorkbenchSectionStatus, ChunkStatus, WorkbenchAssignment

class WorkbenchSectionStatusRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_section(
        self,
        assignment_id: uuid.UUID,
        section_id: str,
        status: ChunkStatus,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> WorkbenchSectionStatus:
        # Check if section status already exists for idempotency
        existing_status = self.session.execute(
            select(WorkbenchSectionStatus).where(
                WorkbenchSectionStatus.assignment_id == assignment_id,
                WorkbenchSectionStatus.section_id == section_id
            )
        ).scalar_one_or_none()

        if existing_status:
            # Update existing status
            existing_status.status = status
            existing_status.evidence = evidence
            existing_status.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(existing_status)
            return existing_status
        else:
            # Create new status
            section_status = WorkbenchSectionStatus(
                id=uuid.uuid4(),
                assignment_id=assignment_id,
                section_id=section_id,
                status=status,
                evidence=evidence,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(section_status)
            self.session.commit()
            self.session.refresh(section_status)
            return section_status

    def list_by_assignment(
        self, assignment_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[WorkbenchSectionStatus]:
        return self.session.execute(
            select(WorkbenchSectionStatus).where(
                WorkbenchSectionStatus.assignment_id == assignment_id
            ).order_by(WorkbenchSectionStatus.section_id.asc()).limit(limit).offset(offset)
        ).scalars().all()

    def get_by_assignment_and_section(
        self, assignment_id: uuid.UUID, section_id: str
    ) -> Optional[WorkbenchSectionStatus]:
        return self.session.execute(
            select(WorkbenchSectionStatus).where(
                WorkbenchSectionStatus.assignment_id == assignment_id,
                WorkbenchSectionStatus.section_id == section_id
            )
        ).scalar_one_or_none()
