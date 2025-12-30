from sqlalchemy import Column, Integer, String, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserHistoryModel(Base):
    __tablename__ = "user_history"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    clerk_user_id = Column(String(255), index=True, nullable=False)
    
    # Action Details
    action = Column(String(100), index=True, nullable=False)  # signed_up, logged_in, account_deactivated, account_reactivated, etc.
    description = Column(Text, nullable=True)  # Additional context about the action
    
    # Optional: Related entity tracking (e.g., which tenant was updated)
    entity_type = Column(String(50), nullable=True, index=True)  # tenant, membership, session, etc.
    entity_id = Column(String(255), nullable=True)  # ID of the related entity
    
    # IP and Device Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Additional Metadata (JSON as text)
    action_metadata = Column(Text, nullable=True)  # Store additional JSON data
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("UserModel", backref="history")
    
    # Composite Indexes for queries
    __table_args__ = (
        Index('idx_user_action', 'user_id', 'action'),
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_action_created', 'action', 'created_at'),
        Index('idx_entity', 'entity_type', 'entity_id'),
    )
