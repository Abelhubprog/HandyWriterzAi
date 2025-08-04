"""
Feature Validator for Disabled Services
Provides structured validation and proper error responses for disabled features.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class FeatureStatus(str, Enum):
    """Feature status enumeration."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class DisabledReason(str, Enum):
    """Reasons why a feature might be disabled."""
    CONFIGURATION_MISMATCH = "configuration_mismatch"
    EXTERNAL_SERVICE_UNAVAILABLE = "external_service_unavailable"
    MAINTENANCE_MODE = "maintenance_mode"
    FEATURE_FLAG_DISABLED = "feature_flag_disabled"
    AUTHENTICATION_REQUIRED = "authentication_required"
    SCHEMA_MISMATCH = "schema_mismatch"

@dataclass
class FeatureInfo:
    """Information about a feature's status."""
    name: str
    status: FeatureStatus
    reason: Optional[DisabledReason] = None
    message: str = ""
    alternative_endpoint: Optional[str] = None
    documentation_url: Optional[str] = None
    expected_availability: Optional[str] = None

class FeatureValidator:
    """Validates feature availability and provides structured responses."""
    
    def __init__(self):
        self.features: Dict[str, FeatureInfo] = {}
        self._initialize_features()
    
    def _initialize_features(self):
        """Initialize feature status from environment and configuration."""
        
        # Payment system validation
        payments_enabled = os.getenv("FEATURE_PAYMENTS_ENABLED", "false").lower() == "true"
        wallet_escrow_ready = self._check_wallet_escrow_schema()
        
        if payments_enabled and wallet_escrow_ready:
            payments_status = FeatureStatus.ENABLED
            payments_reason = None
            payments_message = "Payment system is operational"
        elif payments_enabled and not wallet_escrow_ready:
            payments_status = FeatureStatus.DISABLED
            payments_reason = DisabledReason.SCHEMA_MISMATCH
            payments_message = "Payment system disabled due to WalletEscrow schema mismatch"
        else:
            payments_status = FeatureStatus.DISABLED
            payments_reason = DisabledReason.FEATURE_FLAG_DISABLED
            payments_message = "Payment system disabled by configuration"
        
        self.features["payments"] = FeatureInfo(
            name="Payment System",
            status=payments_status,
            reason=payments_reason,
            message=payments_message,
            alternative_endpoint=None,
            documentation_url="/docs#payments",
            expected_availability="TBD - pending schema alignment"
        )
        
        # Turnitin validation
        turnitin_enabled = os.getenv("FEATURE_TURNITIN_ENABLED", "false").lower() == "true"
        turnitin_credentials = self._check_turnitin_credentials()
        
        if turnitin_enabled and turnitin_credentials:
            turnitin_status = FeatureStatus.ENABLED
            turnitin_reason = None
            turnitin_message = "Turnitin plagiarism detection is operational"
        elif turnitin_enabled and not turnitin_credentials:
            turnitin_status = FeatureStatus.DISABLED
            turnitin_reason = DisabledReason.AUTHENTICATION_REQUIRED
            turnitin_message = "Turnitin disabled - credentials not configured"
        else:
            turnitin_status = FeatureStatus.DISABLED
            turnitin_reason = DisabledReason.FEATURE_FLAG_DISABLED
            turnitin_message = "Turnitin disabled by configuration"
        
        self.features["turnitin"] = FeatureInfo(
            name="Turnitin Plagiarism Detection",
            status=turnitin_status,
            reason=turnitin_reason,
            message=turnitin_message,
            alternative_endpoint="/api/plagiarism/basic",
            documentation_url="/docs#turnitin",
            expected_availability="Available with proper credentials"
        )
        
        # Workbench validation
        workbench_enabled = os.getenv("FEATURE_WORKBENCH_ENABLED", "true").lower() == "true"
        workbench_db = self._check_workbench_database()
        
        if workbench_enabled and workbench_db:
            workbench_status = FeatureStatus.ENABLED
            workbench_reason = None
            workbench_message = "Academic workbench is operational"
        elif workbench_enabled and not workbench_db:
            workbench_status = FeatureStatus.DISABLED
            workbench_reason = DisabledReason.CONFIGURATION_MISMATCH
            workbench_message = "Workbench disabled - database configuration missing"
        else:
            workbench_status = FeatureStatus.DISABLED
            workbench_reason = DisabledReason.FEATURE_FLAG_DISABLED
            workbench_message = "Academic workbench disabled by configuration"
        
        self.features["workbench"] = FeatureInfo(
            name="Academic Workbench",
            status=workbench_status,
            reason=workbench_reason,
            message=workbench_message,
            alternative_endpoint="/api/chat",
            documentation_url="/docs#workbench",
            expected_availability="Available with database configuration"
        )
    
    def _check_wallet_escrow_schema(self) -> bool:
        """Check if WalletEscrow schema is properly aligned."""
        try:
            # Try to import and validate the schema
            from src.blockchain.escrow import WalletEscrow
            # Basic validation - in production, this would check schema compatibility
            return hasattr(WalletEscrow, '__tablename__')
        except ImportError:
            return False
        except Exception as e:
            logger.warning(f"WalletEscrow schema validation failed: {e}")
            return False
    
    def _check_turnitin_credentials(self) -> bool:
        """Check if Turnitin credentials are properly configured."""
        required_vars = ["TURNITIN_API_KEY", "TURNITIN_API_URL"]
        return all(os.getenv(var) for var in required_vars)
    
    def _check_workbench_database(self) -> bool:
        """Check if workbench database is properly configured."""
        try:
            # Check for workbench-specific database configuration
            database_url = os.getenv("DATABASE_URL")
            workbench_db = os.getenv("WORKBENCH_DATABASE_URL", database_url)
            return workbench_db is not None
        except Exception:
            return False
    
    def get_feature_status(self, feature_name: str) -> Optional[FeatureInfo]:
        """Get status information for a specific feature."""
        return self.features.get(feature_name)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        feature = self.features.get(feature_name)
        return feature and feature.status == FeatureStatus.ENABLED
    
    def validate_feature_access(self, feature_name: str) -> None:
        """Validate access to a feature and raise appropriate HTTP exception if disabled."""
        feature = self.features.get(feature_name)
        
        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature '{feature_name}' not found"
            )
        
        if feature.status != FeatureStatus.ENABLED:
            status_code_map = {
                FeatureStatus.DISABLED: status.HTTP_503_SERVICE_UNAVAILABLE,
                FeatureStatus.MAINTENANCE: status.HTTP_503_SERVICE_UNAVAILABLE,
                FeatureStatus.DEPRECATED: status.HTTP_410_GONE
            }
            
            error_detail = {
                "error": "feature_unavailable",
                "feature": feature.name,
                "status": feature.status,
                "reason": feature.reason,
                "message": feature.message
            }
            
            if feature.alternative_endpoint:
                error_detail["alternative"] = feature.alternative_endpoint
            
            if feature.expected_availability:
                error_detail["expected_availability"] = feature.expected_availability
            
            raise HTTPException(
                status_code=status_code_map.get(feature.status, status.HTTP_503_SERVICE_UNAVAILABLE),
                detail=error_detail
            )
    
    def get_all_features_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all features."""
        return {
            name: {
                "name": info.name,
                "status": info.status,
                "reason": info.reason,
                "message": info.message,
                "alternative_endpoint": info.alternative_endpoint,
                "documentation_url": info.documentation_url,
                "expected_availability": info.expected_availability
            }
            for name, info in self.features.items()
        }
    
    def refresh_feature_status(self):
        """Refresh feature status by re-checking configurations."""
        logger.info("Refreshing feature status")
        self._initialize_features()

# Global feature validator instance
_feature_validator: Optional[FeatureValidator] = None

def get_feature_validator() -> FeatureValidator:
    """Get global feature validator instance."""
    global _feature_validator
    if _feature_validator is None:
        _feature_validator = FeatureValidator()
    return _feature_validator

def validate_feature(feature_name: str):
    """Decorator to validate feature access before endpoint execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            validator = get_feature_validator()
            validator.validate_feature_access(feature_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_feature_enabled(feature_name: str) -> bool:
    """Convenience function to check if feature is enabled."""
    validator = get_feature_validator()
    return validator.is_feature_enabled(feature_name)