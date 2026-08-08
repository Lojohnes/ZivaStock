from fastapi import Request
from sqlalchemy.orm import Session
from app.models.audit import AuditTrail
from app.models.user import User
from typing import Optional, Any
import json


async def log_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int],
    old_value: Optional[Any] = None,
    new_value: Optional[Any] = None,
    request: Optional[Request] = None
):
    """Log an audit entry. NOTE: most tables already get audit rows automatically
    via the `generic_audit_trigger` DB trigger (see V011__triggers.sql) — this
    helper is only for app-level events with no direct table trigger (e.g. login)."""
    try:
        audit_log = AuditTrail(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value if isinstance(old_value, dict) else None,
            new_value=new_value if isinstance(new_value, dict) else None,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        # Log error but don't fail the request
        print(f"Audit logging error: {e}")


class AuditMiddleware:
    """Middleware to automatically log audit trails"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Store request info for audit logging
            # This is a simplified version - in production, you'd want more sophisticated logging
            pass
        
        await self.app(scope, receive, send)
