import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models import WorkbenchArtifact, WorkbenchArtifactType

class WorkbenchArtifactRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        assignment_id: Optional[uuid.UUID],
        submission_id: Optional[uuid.UUID],
        artifact_type: WorkbenchArtifactType,
        storage_provider: str,
        object_key: str,
        size_bytes: Optional[int] = None,
        mime_type: Optional[str] = None,
        checksum_sha256: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkbenchArtifact:
        artifact = WorkbenchArtifact(
            id=uuid.uuid4(),
            assignment_id=assignment_id,
            submission_id=submission_id,
            artifact_type=artifact_type,
            storage_provider=storage_provider,
            object_key=object_key,
            size_bytes=size_bytes,
            mime_type=mime_type,
            checksum_sha256=checksum_sha256,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        self.session.add(artifact)
        self.session.commit()
        self.session.refresh(artifact)
        return artifact

    def get_by_id(self, artifact_id: uuid.UUID) -> Optional[WorkbenchArtifact]:
        return self.session.execute(
            select(WorkbenchArtifact).where(WorkbenchArtifact.id == artifact_id)
        ).scalar_one_or_none()

    def list_by_assignment(
        self, assignment_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[WorkbenchArtifact]:
        return self.session.execute(
            select(WorkbenchArtifact).where(
                WorkbenchArtifact.assignment_id == assignment_id
            ).order_by(WorkbenchArtifact.created_at.desc()).limit(limit).offset(offset)
        ).scalars().all()

    def list_by_submission(
        self, submission_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> List[WorkbenchArtifact]:
        return self.session.execute(
            select(WorkbenchArtifact).where(
                WorkbenchArtifact.submission_id == submission_id
            ).order_by(WorkbenchArtifact.created_at.desc()).limit(limit).offset(offset)
        ).scalars().all()
