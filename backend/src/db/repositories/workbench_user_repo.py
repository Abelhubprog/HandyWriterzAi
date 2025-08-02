from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.src.db.models import WorkbenchUser, WorkbenchUserRole
from typing import Optional, List
import uuid

class WorkbenchUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, hashed_password: str, email: str, role: WorkbenchUserRole = WorkbenchUserRole.CHECKER) -> WorkbenchUser:
        new_user = WorkbenchUser(
            username=username,
            hashed_password=hashed_password,
            email=email,
            role=role
        )
        self.db.add(new_user)
        try:
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Username or email already registered.")

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[WorkbenchUser]:
        return self.db.query(WorkbenchUser).filter(WorkbenchUser.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[WorkbenchUser]:
        return self.db.query(WorkbenchUser).filter(WorkbenchUser.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[WorkbenchUser]:
        return self.db.query(WorkbenchUser).filter(WorkbenchUser.email == email).first()

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[WorkbenchUser]:
        return self.db.query(WorkbenchUser).offset(skip).limit(limit).all()

    def update_user(self, user_id: uuid.UUID, username: Optional[str] = None, hashed_password: Optional[str] = None, email: Optional[str] = None, role: Optional[WorkbenchUserRole] = None, is_active: Optional[bool] = None) -> Optional[WorkbenchUser]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        if username:
            user.username = username
        if hashed_password:
            user.hashed_password = hashed_password
        if email:
            user.email = email
        if role:
            user.role = role
        if is_active is not None:
            user.is_active = is_active
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Username or email already exists.")

    def delete_user(self, user_id: uuid.UUID) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        self.db.delete(user)
        self.db.commit()
        return True
