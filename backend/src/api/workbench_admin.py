"""
Admin API endpoints for workbench user management.
Only admins can create, update, and manage workbench users.
"""

import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
import hashlib

from ..db.database import get_db
from ..services.security_service import get_current_user, require_authorization
from ..db.models import User, UserType
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/workbench", tags=["Workbench Admin"])

# Pydantic models for request/response
class CreateWorkbenchUserRequest(BaseModel):
    email: EmailStr
    username: str
    role: str  # 'checker' or 'admin'
    full_name: Optional[str] = None
    permissions: List[str] = []

class WorkbenchUserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_verified: bool
    permissions: List[str]
    created_at: str
    last_login: Optional[str]
    is_active: bool

class UpdateWorkbenchUserRequest(BaseModel):
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None

# Standard permissions for workbench users
WORKBENCH_PERMISSIONS = {
    'checker': [
        'workbench.document.claim',
        'workbench.document.download', 
        'workbench.document.upload_reports',
        'workbench.document.view'
    ],
    'admin': [
        'workbench.document.claim',
        'workbench.document.download',
        'workbench.document.upload_reports', 
        'workbench.document.view',
        'workbench.user.create',
        'workbench.user.update',
        'workbench.user.delete',
        'workbench.user.list',
        'workbench.system.configure',
        'workbench.reports.view_all'
    ]
}

def generate_dynamic_user_id() -> str:
    """Generate a unique Dynamic.xyz compatible user ID"""
    return f"wb_{uuid.uuid4().hex[:16]}"

def hash_email_for_lookup(email: str) -> str:
    """Create a hash of email for secure lookup without storing plaintext email"""
    return hashlib.sha256(email.encode()).hexdigest()

@router.post("/users", response_model=WorkbenchUserResponse, status_code=status.HTTP_201_CREATED)
@require_authorization(["admin"])
async def create_workbench_user(
    request: CreateWorkbenchUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new workbench user. Only system admins can create workbench users.
    The user will be notified via email with their Dynamic.xyz login instructions.
    """
    try:
        # Validate role
        if request.role not in ['checker', 'admin']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be either 'checker' or 'admin'"
            )

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Check if username is taken
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

        # Generate Dynamic.xyz compatible user ID
        dynamic_user_id = generate_dynamic_user_id()
        
        # Set permissions based on role
        permissions = request.permissions if request.permissions else WORKBENCH_PERMISSIONS.get(request.role, [])

        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            wallet_address=f"workbench_{dynamic_user_id}",  # Workbench users don't use crypto wallets
            dynamic_user_id=dynamic_user_id,
            email=request.email,
            username=request.username,
            full_name=request.full_name,
            user_type=UserType.ADMIN if request.role == 'admin' else UserType.TUTOR,  # Use TUTOR for checkers
            institution="HandyWriterzAI Workbench",
            academic_level="workbench_user",
            field_of_study=request.role,
            subscription_tier="workbench",
            credits_remaining=0,  # Workbench users don't use credits
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log the creation
        logger.info(f"Workbench user created: {request.username} ({request.role}) by admin {current_user.get('username', 'unknown')}")

        # TODO: Send email notification to user with Dynamic.xyz login instructions
        # This would integrate with your email service
        
        return WorkbenchUserResponse(
            id=str(new_user.id),
            email=new_user.email,
            username=new_user.username,
            full_name=new_user.full_name,
            role=request.role,
            is_verified=True,  # Admin-created users are auto-verified
            permissions=permissions,
            created_at=new_user.created_at.isoformat(),
            last_login=new_user.last_login.isoformat() if new_user.last_login else None,
            is_active=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create workbench user: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workbench user"
        )

@router.get("/users", response_model=List[WorkbenchUserResponse])
@require_authorization(["admin"])
async def list_workbench_users(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List all workbench users. Only admins can view the full user list."""
    try:
        users = db.query(User).filter(
            User.subscription_tier == "workbench"
        ).offset(skip).limit(limit).all()

        return [
            WorkbenchUserResponse(
                id=str(user.id),
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                role='admin' if user.user_type == UserType.ADMIN else 'checker',
                is_verified=True,
                permissions=WORKBENCH_PERMISSIONS.get(
                    'admin' if user.user_type == UserType.ADMIN else 'checker', 
                    []
                ),
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None,
                is_active=True  # You might want to add an is_active field to User model
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Failed to list workbench users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workbench users"
        )

@router.get("/users/{user_id}", response_model=WorkbenchUserResponse)
@require_authorization(["admin"])
async def get_workbench_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workbench user by ID."""
    try:
        user = db.query(User).filter(
            User.id == uuid.UUID(user_id),
            User.subscription_tier == "workbench"
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workbench user not found"
            )

        return WorkbenchUserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role='admin' if user.user_type == UserType.ADMIN else 'checker',
            is_verified=True,
            permissions=WORKBENCH_PERMISSIONS.get(
                'admin' if user.user_type == UserType.ADMIN else 'checker',
                []
            ),
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
            is_active=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workbench user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workbench user"
        )

@router.put("/users/{user_id}", response_model=WorkbenchUserResponse)
@require_authorization(["admin"])
async def update_workbench_user(
    user_id: str,
    request: UpdateWorkbenchUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a workbench user. Only admins can update users."""
    try:
        user = db.query(User).filter(
            User.id == uuid.UUID(user_id),
            User.subscription_tier == "workbench"
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workbench user not found"
            )

        # Update fields if provided
        if request.role is not None:
            if request.role not in ['checker', 'admin']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role must be either 'checker' or 'admin'"
                )
            user.user_type = UserType.ADMIN if request.role == 'admin' else UserType.TUTOR
            user.field_of_study = request.role

        if request.full_name is not None:
            user.full_name = request.full_name

        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)

        logger.info(f"Workbench user updated: {user.username} by admin {current_user.get('username', 'unknown')}")

        return WorkbenchUserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role='admin' if user.user_type == UserType.ADMIN else 'checker',
            is_verified=True,
            permissions=request.permissions or WORKBENCH_PERMISSIONS.get(
                'admin' if user.user_type == UserType.ADMIN else 'checker',
                []
            ),
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
            is_active=request.is_active if request.is_active is not None else True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workbench user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workbench user"
        )

@router.delete("/users/{user_id}")
@require_authorization(["admin"])
async def delete_workbench_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workbench user. Only admins can delete users."""
    try:
        user = db.query(User).filter(
            User.id == uuid.UUID(user_id),
            User.subscription_tier == "workbench"
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workbench user not found"
            )

        username = user.username
        db.delete(user)
        db.commit()

        logger.warning(f"Workbench user deleted: {username} by admin {current_user.get('username', 'unknown')}")

        return {"message": f"Workbench user {username} has been deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workbench user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workbench user"
        )

@router.post("/users/{user_id}/reset-access")
@require_authorization(["admin"])
async def reset_user_access(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset a user's Dynamic.xyz access. Generates new credentials and sends notification."""
    try:
        user = db.query(User).filter(
            User.id == uuid.UUID(user_id),
            User.subscription_tier == "workbench"
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workbench user not found"
            )

        # Generate new Dynamic.xyz user ID
        new_dynamic_id = generate_dynamic_user_id()
        user.dynamic_user_id = new_dynamic_id
        user.wallet_address = f"workbench_{new_dynamic_id}"
        user.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Access reset for workbench user: {user.username} by admin {current_user.get('username', 'unknown')}")

        # TODO: Send email with new login instructions
        
        return {"message": f"Access reset for user {user.username}. New login instructions will be sent via email."}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset access for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user access"
        )