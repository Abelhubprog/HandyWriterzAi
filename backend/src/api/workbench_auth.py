from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import uuid

from backend.src.db.database import get_db
from backend.src.db.repositories import WorkbenchUserRepository
from backend.src.auth.workbench_auth import WorkbenchAuthService
from backend.src.services.security_service import SecurityService
from backend.src.api.schemas.workbench_auth import WorkbenchLoginRequest, WorkbenchTokenResponse, WorkbenchUserCreate, WorkbenchUserResponse, WorkbenchUserUpdate
from backend.src.db.models import WorkbenchUserRole, WorkbenchUser

router = APIRouter(prefix="/workbench/auth", tags=["Workbench Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/workbench/auth/token")

def get_workbench_auth_service(db: Session = Depends(get_db)) -> WorkbenchAuthService:
    security_service = SecurityService()
    return WorkbenchAuthService(db, security_service)

def get_current_workbench_user(token: str = Depends(oauth2_scheme), auth_service: WorkbenchAuthService = Depends(get_workbench_auth_service)) -> WorkbenchUser:
    return auth_service.get_current_workbench_user(token)

@router.post("/token", response_model=WorkbenchTokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: WorkbenchAuthService = Depends(get_workbench_auth_service)):
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
    auth_service: WorkbenchAuthService = Depends(get_workbench_auth_service),
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
    auth_service: WorkbenchAuthService = Depends(get_workbench_auth_service),
    current_user: WorkbenchUser = Depends(get_current_workbench_user)
):
    auth_service.require_workbench_admin()(current_user) # Enforce admin role
    users = auth_service.user_repo.get_all_users(skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}", response_model=WorkbenchUserResponse)
async def update_workbench_user(
    user_id: uuid.UUID,
    user_update: WorkbenchUserUpdate,
    auth_service: WorkbenchAuthService = Depends(get_workbench_auth_service),
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
    auth_service: WorkbenchAuthService = Depends(get_workbench_auth_service),
    current_user: WorkbenchUser = Depends(get_current_workbench_user)
):
    auth_service.require_workbench_admin()(current_user) # Enforce admin role

    if not auth_service.user_repo.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message": "User deleted successfully"}
