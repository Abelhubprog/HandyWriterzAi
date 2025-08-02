import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.src.db.models import WorkbenchUser, WorkbenchUserRole
from backend.src.db.repositories import WorkbenchUserRepository
from backend.src.core.config import settings
from backend.src.services.security_service import SecurityService # Assuming this exists for password hashing

class WorkbenchAuthService:
    def __init__(self, db: Session, security_service: SecurityService):
        self.db = db
        self.user_repo = WorkbenchUserRepository(db)
        self.security_service = security_service
        self.SECRET_KEY = settings.WORKBENCH_SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.security_service.verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.security_service.get_password_hash(password)

    def authenticate_user(self, username: str, password: str) -> Optional[WorkbenchUser]:
        user = self.user_repo.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def get_current_workbench_user(self, token: str) -> WorkbenchUser:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            user = self.user_repo.get_user_by_id(uuid.UUID(user_id))
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return user
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def require_workbench_role(self, required_role: WorkbenchUserRole):
        def role_checker(current_user: WorkbenchUser = Depends(self.get_current_workbench_user)):
            if current_user.role != required_role and current_user.role != WorkbenchUserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized. Requires {required_role.value} role."
                )
            return current_user
        return role_checker

    def require_workbench_admin(self):
        return self.require_workbench_role(WorkbenchUserRole.ADMIN)

    def require_workbench_checker(self):
        return self.require_workbench_role(WorkbenchUserRole.CHECKER)
