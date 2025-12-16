"""
Audit logging service for HIPAA compliance
"""
from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


class AuditService:
    """Log all data access for compliance"""

    @staticmethod
    def log_action(
        db: Session,
        action_type: str,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_details: Optional[Dict[str, Any]] = None,
        response_status: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create an audit log entry"""
        audit_entry = AuditLog(
            user_id=user_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_details=request_details,
            response_status=response_status,
            additional_data=additional_data
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)
        return audit_entry

    @staticmethod
    def log_user_login(
        db: Session,
        user_id: UUID,
        ip_address: str,
        user_agent: str,
        success: bool
    ):
        """Log user login attempt"""
        AuditService.log_action(
            db=db,
            action_type="USER_LOGIN_SUCCESS" if success else "USER_LOGIN_FAILED",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data={"success": success}
        )

    @staticmethod
    def log_data_access(
        db: Session,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID,
        action: str,
        ip_address: str
    ):
        """Log data access for HIPAA compliance"""
        AuditService.log_action(
            db=db,
            action_type=f"DATA_{action.upper()}",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address
        )

    @staticmethod
    def log_sensitive_data_export(
        db: Session,
        user_id: UUID,
        ip_address: str,
        export_type: str
    ):
        """Log when user exports their data"""
        AuditService.log_action(
            db=db,
            action_type="DATA_EXPORT",
            user_id=user_id,
            ip_address=ip_address,
            additional_data={"export_type": export_type}
        )
