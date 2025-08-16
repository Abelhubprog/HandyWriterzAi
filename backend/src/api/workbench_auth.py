from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid

from backend.src.db.database import get_db
from src.services.security_service import RevolutionarySecurityService
from backend.src.api.schemas.workbench_auth import WorkbenchTokenResponse, WorkbenchUserCreate, WorkbenchUserResponse, WorkbenchUserUpdate
from backend.src.db.models import WorkbenchUser

# Import the new Dynamic.xyz-based Workbench auth service (aliased to avoid name clash)
from src.services.workbench_auth_service import (
    get_workbench_auth_service as get_dynamic_workbench_auth_service,
    WorkbenchAuthService as DynamicWorkbenchAuthService,
)
from pydantic import BaseModel

router = APIRouter(prefix="/workbench/auth", tags=["Workbench Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/workbench/auth/token")

def get_workbench_auth_service(db: Session = Depends(get_db)):
    """Best-effort factory for legacy password-based workbench auth service.
    Returns an instance if legacy module is available; otherwise raises 501.
    """
    try:
        from backend.src.auth.workbench_auth import WorkbenchAuthService as LegacyWorkbenchAuthService
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=f"Legacy workbench auth not available: {e}")
    security_service = RevolutionarySecurityService()
    return LegacyWorkbenchAuthService(db, security_service)  # type: ignore[no-any-return]

def get_current_workbench_user(token: str = Depends(oauth2_scheme), auth_service: Any = Depends(get_workbench_auth_service)) -> WorkbenchUser:
    return auth_service.get_current_workbench_user(token)

@router.post("/token", response_model=WorkbenchTokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: Any = Depends(get_workbench_auth_service)):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/users", response_model=WorkbenchUserResponse, status_code=status.HTTP_201_CREATED)
async def create_workbench_user(
    user_create: WorkbenchUserCreate,
    auth_service: Any = Depends(get_workbench_auth_service),
    current_user: WorkbenchUser = Depends(get_current_workbench_user) # Requires authentication
):
    auth_service.require_workbench_admin()(current_user) # Enforce admin role

    hashed_password = auth_service.get_password_hash(user_create.password)
    try:
        new_user = auth_service.user_repo.create_user(
            username=user_create.username,
            hashed_password=hashed_password,
            email=user_create.email,
            role=user_create.role
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/users/me", response_model=WorkbenchUserResponse)
async def read_users_me(current_user: WorkbenchUser = Depends(get_current_workbench_user)):
    return current_user

@router.get("/users", response_model=List[WorkbenchUserResponse])
async def list_workbench_users(
    skip: int = 0,
    limit: int = 100,
    auth_service: Any = Depends(get_workbench_auth_service),
    current_user: WorkbenchUser = Depends(get_current_workbench_user)
):
    auth_service.require_workbench_admin()(current_user) # Enforce admin role
    users = auth_service.user_repo.get_all_users(skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}", response_model=WorkbenchUserResponse)
async def update_workbench_user(
    user_id: uuid.UUID,
    user_update: WorkbenchUserUpdate,
    auth_service: Any = Depends(get_workbench_auth_service),
    current_user: WorkbenchUser = Depends(get_current_workbench_user)
):
    auth_service.require_workbench_admin()(current_user) # Enforce admin role

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = auth_service.get_password_hash(update_data["password"])
        del update_data["password"]

    updated_user = auth_service.user_repo.update_user(user_id, **update_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workbench_user(
    user_id: uuid.UUID,
    auth_service: Any = Depends(get_workbench_auth_service),
    current_user: WorkbenchUser = Depends(get_current_workbench_user)
):
    auth_service.require_workbench_admin()(current_user) # Enforce admin role

    if not auth_service.user_repo.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}

# ------------------------------
# Dynamic.xyz-based Workbench Auth Endpoints
# ------------------------------

class DynamicLoginRequest(BaseModel):
    dynamic_token: str


class WorkbenchLoginResponse(BaseModel):
    success: bool
    user: Dict[str, Any]
    token: str
    expires_at: str


class WorkbenchVerifyResponse(BaseModel):
    valid: bool
    user: Optional[Dict[str, Any]] = None


class WorkbenchLogoutResponse(BaseModel):
    success: bool


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


@router.post("/login", response_model=WorkbenchLoginResponse)
async def workbench_dynamic_login(
    payload: DynamicLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    dyn_auth: DynamicWorkbenchAuthService = Depends(get_dynamic_workbench_auth_service),
):
    """Login using Dynamic.xyz token and receive a Workbench JWT + user info."""
    result = dyn_auth.authenticate_workbench_user(payload.dynamic_token, db)
    # Normalize user payload to include isVerified
    user = dict(result.get("user") or {})
    if "isVerified" not in user:
        if "is_verified" in user:
            user["isVerified"] = user.get("is_verified")
        else:
            user["isVerified"] = True
    # Shape response to frontend expectations
    return {
        "success": True,
        "user": user,
        "token": result.get("token"),
        "expires_at": result.get("expires_at"),
    }


@router.post("/verify", response_model=WorkbenchVerifyResponse)
async def workbench_dynamic_verify(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    dyn_auth: DynamicWorkbenchAuthService = Depends(get_dynamic_workbench_auth_service),
):
    """Verify a Workbench JWT and return the embedded user payload."""
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    payload = dyn_auth.verify_workbench_token(token)
    # Map payload to user object expected by frontend
    user: Dict[str, Any] = {
        "id": payload.get("sub"),
        "username": payload.get("username"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "permissions": payload.get("permissions", []),
        "isVerified": True,
    }
    return {"valid": True, "user": user}


@router.post("/logout", response_model=WorkbenchLogoutResponse)
async def workbench_dynamic_logout(
    request: Request,
    authorization: Optional[str] = Header(default=None),
):
    """Stateless logout endpoint. Frontend should drop the token; we just acknowledge."""
    # Optionally inspect token for auditing
    _ = _extract_bearer_token(authorization)
    return {"success": True}
