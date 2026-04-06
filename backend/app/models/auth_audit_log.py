"""
AuthAuditLog model - Task 1.3
SQLAlchemy model for authentication event tracking
Requirements: 12.1, 12.2, 12.3, 12.5
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import relationship
from app.models.user import Base


class AuthAuditLog(Base):
    """
    Authentication audit log for security tracking

    Requirements:
    - 12.1: Log authentication attempts with timestamp, email, IP, result
    - 12.2: Log failure reasons
    - 12.3: Log session start with user ID and IP
    - 12.5: Store logs separately from application logs
    """
    __tablename__ = "auth_audit_log"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User reference (nullable for failed attempts with invalid email)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Authentication details (Requirements: 12.1)
    email = Column(String(255), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # 'login_success', 'login_failure', 'logout', 'register'

    # Request metadata (Requirements: 12.1, 12.3)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)

    # Success flag
    success = Column(Boolean, default=True, nullable=False)

    # Timestamp (Requirements: 12.1)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Relationship to User
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        """String representation"""
        return f"<AuthAuditLog(id={self.id}, event='{self.event_type}', email='{self.email}')>"

    def __str__(self):
        """Human-readable string"""
        return f"{self.event_type} for {self.email} at {self.created_at}"

    def to_dict(self) -> dict:
        """Convert audit log to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email,
            "event_type": self.event_type,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
