"""
Audit Logging Service - Task 14.1, 14.2
Log authentication events for security monitoring
Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth_audit_log import AuthAuditLog
from datetime import datetime


class AuditService:
    """
    Service for logging authentication events

    Requirements:
    - 12.1: Log all authentication events
    - 12.2: Include IP address and user agent
    - 12.3: Store in auth_audit_log table
    - 12.4: Async logging (non-blocking)
    - 12.5: Retention policy (implementation note)
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize audit service

        Args:
            db: Database session
        """
        self.db = db

    async def log_event(
        self,
        event_type: str,
        email: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ):
        """
        Log authentication event

        Event types:
        - login_success
        - login_failure
        - register_success
        - register_failure
        - token_refresh
        - logout
        - password_change
        - account_lockout
        - account_deleted

        Args:
            event_type: Type of authentication event
            email: User email
            user_id: User ID (if available)
            ip_address: Client IP address
            user_agent: Client user agent string
            success: Whether operation was successful

        Returns:
            AuthAuditLog: Created log entry
        """
        log_entry = AuthAuditLog(
            user_id=user_id,
            email=email,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            created_at=datetime.utcnow()
        )

        self.db.add(log_entry)
        await self.db.flush()

        return log_entry

    async def get_failed_login_attempts(
        self,
        email: str,
        minutes: int = 15
    ) -> int:
        """
        Count failed login attempts for email in time window

        Requirements:
        - Account lockout detection

        Args:
            email: User email
            minutes: Time window in minutes

        Returns:
            int: Number of failed attempts
        """
        from sqlalchemy import select, func
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

        result = await self.db.execute(
            select(func.count(AuthAuditLog.id))
            .where(
                AuthAuditLog.email == email,
                AuthAuditLog.event_type == "login_failure",
                AuthAuditLog.created_at >= cutoff_time
            )
        )

        return result.scalar() or 0
