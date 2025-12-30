from sqlalchemy import Column, Integer, String, DateTime, Text, Index, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class SessionModel(Base):
    __tablename__ = "sessions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Clerk Integration
    clerk_session_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # User Association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    clerk_user_id = Column(String(255), index=True, nullable=False)
    
    # Session Details
    status = Column(String(50), index=True, nullable=False)  # active, ended, expired, revoked, etc.
    client_id = Column(String(255), nullable=True)  # Clerk client/app ID
    
    # Device & Browser Information
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    # Location (from IP or Clerk metadata)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    
    # Session Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_active_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional Metadata
    clerk_metadata = Column(Text, nullable=True)  # Store additional JSON data from Clerk
    
    # Relationships
    user = relationship("UserModel", back_populates="sessions")
    
    # Composite Indexes for common queries
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_clerk_user_status', 'clerk_user_id', 'status'),
        Index('idx_created_status', 'created_at', 'status'),
    )
