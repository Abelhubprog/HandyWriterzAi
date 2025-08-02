import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models import WorkbenchAssignment, WorkbenchAssignmentStatus, WorkbenchDeliveryChannel, User, Checker

class WorkbenchAssignmentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        source_conversation_id: Optional[uuid.UUID],
        title: str,
        requirements: Optional[Dict[str, Any]] = None,
        delivery_channel: WorkbenchDeliveryChannel = WorkbenchDeliveryChannel.WORKBENCH,
        telegram_message_ref: Optional[Dict[str, Any]] = None,
        ai_metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkbenchAssignment:
        assignment = WorkbenchAssignment(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            source_conversation_id=source_conversation_id,
            title=title,
            requirements=requirements,
            delivery_channel=delivery_channel,
            telegram_message_ref=telegram_message_ref,
            ai_metadata=ai_metadata,
            status=WorkbenchAssignmentStatus.QUEUED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            soft_deleted=False
        )
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def get_by_id(self, tenant_id: uuid.UUID, assignment_id: uuid.UUID) -> Optional[WorkbenchAssignment]:
        return self.session.execute(
            select(WorkbenchAssignment).where(
                WorkbenchAssignment.id == assignment_id,
                WorkbenchAssignment.tenant_id == tenant_id,
                WorkbenchAssignment.soft_deleted == False
            )
        ).scalar_one_or_none()

    def list_by_status(
        self,
        tenant_id: uuid.UUID,
        status: WorkbenchAssignmentStatus,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkbenchAssignment]:
        return self.session.execute(
            select(WorkbenchAssignment).where(
                WorkbenchAssignment.tenant_id == tenant_id,
                WorkbenchAssignment.status == status,
                WorkbenchAssignment.soft_deleted == False
            ).order_by(WorkbenchAssignment.created_at.asc()).limit(limit).offset(offset)
        ).scalars().all()

    def claim_next(self, tenant_id: uuid.UUID, checker_id: int) -> Optional[WorkbenchAssignment]:
        # Atomically claim the next available assignment
        # Prioritize 'queued' then 'assigned' (if assigned to self)
        assignment = self.session.execute(
            select(WorkbenchAssignment).where(
                WorkbenchAssignment.tenant_id == tenant_id,
                WorkbenchAssignment.soft_deleted == False,
                (WorkbenchAssignment.status == WorkbenchAssignmentStatus.QUEUED) |
                ((WorkbenchAssignment.status == WorkbenchAssignmentStatus.ASSIGNED) & (WorkbenchAssignment.assigned_checker_id == checker_id))
            ).order_by(WorkbenchAssignment.created_at.asc()).with_for_update(skip_locked=True)
        ).scalar_one_or_none()

        if assignment:
            assignment.assigned_checker_id = checker_id
            assignment.status = WorkbenchAssignmentStatus.ASSIGNED
            assignment.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(assignment)
        return assignment

    def update_status(self, tenant_id: uuid.UUID, assignment_id: uuid.UUID, status: WorkbenchAssignmentStatus) -> Optional[WorkbenchAssignment]:
        assignment = self.get_by_id(tenant_id, assignment_id)
        if assignment:
            assignment.status = status
            assignment.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(assignment)
        return assignment

    def soft_delete(self, tenant_id: uuid.UUID, assignment_id: uuid.UUID) -> Optional[WorkbenchAssignment]:
        assignment = self.get_by_id(tenant_id, assignment_id)
        if assignment:
            assignment.soft_deleted = True
            assignment.updated_at = datetime.utcnow()
            self.session.commit()
            self.session.refresh(assignment)
        return assignment
