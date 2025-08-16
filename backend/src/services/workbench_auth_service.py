"""
Workbench authentication service using Dynamic.xyz
Handles secure login for workbench users (no signup, admin-managed only)
"""

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..db.models import User, UserType

logger = logging.getLogger(__name__)


class WorkbenchAuthService:
    def __init__(self) -> None:
        self.jwt_secret: str = os.getenv("JWT_SECRET_KEY", "your-workbench-secret-key")
        self.jwt_algorithm: str = "HS256"
        # Workbench sessions expire after 8 hours
        self.token_expire_hours: int = 8
        # Dynamic.xyz config
        self.dynamic_jwks_url: Optional[str] = os.getenv("DYNAMIC_JWKS_URL")
        self.dynamic_issuer: Optional[str] = os.getenv("DYNAMIC_ISSUER")
        self.dynamic_audience: Optional[str] = os.getenv("DYNAMIC_AUDIENCE")
        self._jwk_client: Optional[jwt.PyJWKClient] = None
        if self.dynamic_jwks_url:
            try:
                self._jwk_client = jwt.PyJWKClient(self.dynamic_jwks_url)  # type: ignore[attr-defined]
            except Exception as e:
                logger.warning("Failed to initialize PyJWKClient for Dynamic.xyz: %s", e)

    def verify_dynamic_token(self, dynamic_token: str) -> Dict[str, Any]:
        """
        Verify Dynamic.xyz JWT using JWKS if configured; validate iss/aud/exp.
        Env (recommended):
          - DYNAMIC_JWKS_URL (e.g., https://<your-tenant>/.well-known/jwks.json)
          - DYNAMIC_ISSUER
          - DYNAMIC_AUDIENCE
        """
        try:
            if self._jwk_client is not None:
                signing_key = self._jwk_client.get_signing_key_from_jwt(dynamic_token).key  # type: ignore[union-attr]
                payload = jwt.decode(
                    dynamic_token,
                    signing_key,
                    algorithms=["RS256", "ES256", "ES384", "ES512"],
                    audience=self.dynamic_audience,
                    issuer=self.dynamic_issuer,
                )
            else:
                # Fallback: decode without signature verification (NOT recommended for production)
                logger.warning("Dynamic JWKS not configured; decoding token without signature verification")
                payload = jwt.decode(dynamic_token, options={"verify_signature": False})

        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Dynamic.xyz token has expired") from exc
        except jwt.InvalidAudienceError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience for Dynamic token") from exc
        except jwt.InvalidIssuerError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid issuer for Dynamic token") from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Dynamic.xyz token") from exc

        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "username": payload.get("username"),
            "wallet_address": payload.get("wallet_address"),
            "verified": payload.get("verified", False),
        }

    def authenticate_workbench_user(self, dynamic_token: str, db: Session) -> Dict[str, Any]:
        """
        Authenticate a workbench user using their Dynamic.xyz token.
        Only users created by admin can login.
        """
        # Verify Dynamic.xyz token
        dynamic_user_data = self.verify_dynamic_token(dynamic_token)

        # Find user in our database
        user: User | None = (
            db.query(User)
            .filter(
                User.subscription_tier == "workbench",
                User.dynamic_user_id == dynamic_user_data.get("user_id"),
            )
            .first()
        )

        if not user:
            # Check if user exists by email (fallback)
            user = (
                db.query(User)
                .filter(
                    User.subscription_tier == "workbench",
                    User.email == dynamic_user_data.get("email"),
                )
                .first()
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authorized for workbench access. Contact administrator.",
                )

        # Update last login (timezone-aware UTC)
        try:
            user.last_login = datetime.now(timezone.utc)  # type: ignore[assignment]
            db.commit()
        except Exception as exc:
            logger.warning("Failed to update last_login for %s: %s", user.id, exc)
            db.rollback()

        # Get user permissions based on role
        permissions: List[str] = self._get_user_permissions(user)

        # Generate workbench JWT token
        workbench_token = self._generate_workbench_token(user, permissions)

        logger.info("Workbench user authenticated: %s", user.username)

        return {
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": getattr(user, "full_name", None),
                "role": "admin" if self._is_admin(user) else "checker",
                "permissions": permissions,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_verified": True,
            },
            "token": workbench_token,
            "expires_at": (
                datetime.now(timezone.utc) + timedelta(hours=self.token_expire_hours)
            ).isoformat(),
        }

    def _is_admin(self, user: User) -> bool:
        """Safely determine if a user has admin role."""
        try:
            return bool(user.user_type == UserType.ADMIN)
        except Exception:
            # Fallback for any instrumentation types
            try:
                return str(getattr(user, "user_type", "")).lower() == "admin"
            except Exception:
                return False

    def _get_user_permissions(self, user: User) -> List[str]:
        """Get user permissions based on their role."""
        if self._is_admin(user):
            return [
                "workbench.document.claim",
                "workbench.document.download",
                "workbench.document.upload_reports",
                "workbench.document.view",
                "workbench.user.create",
                "workbench.user.update",
                "workbench.user.delete",
                "workbench.user.list",
                "workbench.system.configure",
                "workbench.reports.view_all",
            ]
        # checker
        return [
            "workbench.document.claim",
            "workbench.document.download",
            "workbench.document.upload_reports",
            "workbench.document.view",
        ]

    def _generate_workbench_token(self, user: User, permissions: List[str]) -> str:
        """Generate a secure JWT token for workbench access."""
        payload: Dict[str, Any] = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": "admin" if self._is_admin(user) else "checker",
            "permissions": permissions,
            "iss": "handywriterz-workbench",
            "aud": "workbench-users",
            "iat": int(time.time()),
            "exp": int(time.time() + (self.token_expire_hours * 3600)),
            "workbench": True,  # Flag to identify workbench tokens
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
                issuer="handywriterz-workbench",
            )

            # Ensure this is a workbench token
            if not payload.get("workbench"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            return payload
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please login again.",
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from exc

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
                detail=f"Permission denied. Required: {required_permission}",
            )

        return payload


# Global instance
workbench_auth_service = WorkbenchAuthService()


def get_workbench_auth_service() -> WorkbenchAuthService:
    return workbench_auth_service
