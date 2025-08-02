"""
Workbench authentication service using Dynamic.xyz
Handles secure login for workbench users (no signup, admin-managed only)
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import os

from ..db.models import User, UserType
from ..services.security_service import SecurityService

logger = logging.getLogger(__name__)

class WorkbenchAuthService:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-workbench-secret-key")
        self.jwt_algorithm = "HS256"
        self.token_expire_hours = 8  # Workbench sessions expire after 8 hours
        
    def verify_dynamic_token(self, dynamic_token: str) -> Dict[str, Any]:
        """
        Verify Dynamic.xyz JWT token and extract user information.
        In production, this would validate against Dynamic.xyz's public key.
        """
        try:
            # TODO: Replace with actual Dynamic.xyz token verification
            # For now, we'll decode without verification for demo purposes
            # In production, you would:
            # 1. Get Dynamic.xyz public key
            # 2. Verify token signature
            # 3. Check token expiration
            # 4. Validate issuer
            
            payload = jwt.decode(
                dynamic_token, 
                options={"verify_signature": False}  # TODO: Enable signature verification
            )
            
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "username": payload.get("username"),
                "wallet_address": payload.get("wallet_address"),
                "verified": payload.get("verified", False)
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Dynamic.xyz token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Dynamic.xyz token"
            )
    
    def authenticate_workbench_user(self, dynamic_token: str, db: Session) -> Dict[str, Any]:
        """
        Authenticate a workbench user using their Dynamic.xyz token.
        Only users created by admin can login.
        """
        try:
            # Verify Dynamic.xyz token
            dynamic_user_data = self.verify_dynamic_token(dynamic_token)
            
            # Find user in our database
            user = db.query(User).filter(
                User.subscription_tier == "workbench",
                User.dynamic_user_id == dynamic_user_data.get("user_id")
            ).first()
            
            if not user:
                # Check if user exists by email (fallback)
                user = db.query(User).filter(
                    User.subscription_tier == "workbench",
                    User.email == dynamic_user_data.get("email")
                ).first()
                
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not authorized for workbench access. Contact administrator."
                    )
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Get user permissions based on role
            permissions = self._get_user_permissions(user)
            
            # Generate workbench JWT token
            workbench_token = self._generate_workbench_token(user, permissions)
            
            logger.info(f"Workbench user authenticated: {user.username}")
            
            return {
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": "admin" if user.user_type == UserType.ADMIN else "checker",
                    "permissions": permissions,
                    "last_login": user.last_login.isoformat(),
                    "is_verified": True
                },
                "token": workbench_token,
                "expires_at": (datetime.utcnow() + timedelta(hours=self.token_expire_hours)).isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    def _get_user_permissions(self, user: User) -> list:
        """Get user permissions based on their role."""
        if user.user_type == UserType.ADMIN:
            return [
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
        else:  # checker
            return [
                'workbench.document.claim',
                'workbench.document.download',
                'workbench.document.upload_reports',
                'workbench.document.view'
            ]
    
    def _generate_workbench_token(self, user: User, permissions: list) -> str:
        """Generate a secure JWT token for workbench access."""
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": "admin" if user.user_type == UserType.ADMIN else "checker",
            "permissions": permissions,
            "iss": "handywriterz-workbench",
            "aud": "workbench-users",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours),
            "workbench": True  # Flag to identify workbench tokens
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_workbench_token(self, token: str) -> Dict[str, Any]:
        """Verify a workbench JWT token and return user data."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm],
                audience="workbench-users",
                issuer="handywriterz-workbench"
            )
            
            # Ensure this is a workbench token
            if not payload.get("workbench"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please login again."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def has_permission(self, token_payload: Dict[str, Any], required_permission: str) -> bool:
        """Check if user has required permission."""
        user_permissions = token_payload.get("permissions", [])
        return required_permission in user_permissions
    
    def require_workbench_permission(self, token: str, required_permission: str) -> Dict[str, Any]:
        """Verify token and check for required permission."""
        payload = self.verify_workbench_token(token)
        
        if not self.has_permission(payload, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {required_permission}"
            )
        
        return payload

# Global instance
workbench_auth_service = WorkbenchAuthService()

def get_workbench_auth_service() -> WorkbenchAuthService:
    return workbench_auth_service