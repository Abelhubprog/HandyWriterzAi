from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid
from datetime import datetime
from backend.src.db.models import WorkbenchUserRole

class WorkbenchUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class WorkbenchUserCreate(WorkbenchUserBase):
    password: str = Field(..., min_length=8)
    role: WorkbenchUserRole = WorkbenchUserRole.CHECKER

class WorkbenchUserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[WorkbenchUserRole] = None
    is_active: Optional[bool] = None

class WorkbenchUserResponse(WorkbenchUserBase):
    id: uuid.UUID
    role: WorkbenchUserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkbenchLoginRequest(BaseModel):
    username: str
    password: str

class WorkbenchTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: WorkbenchUserResponse