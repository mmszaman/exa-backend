from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ConversationModel(Base):
    """
    Conversation model for AI chat sessions.
    Each conversation belongs to a user and optionally a tenant.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=True)  # Auto-generated from first message
    status = Column(String(50), default="active", nullable=False)  # active, archived, deleted
    
    # Metadata
    context = Column(JSON, nullable=True)  # Store context like current_tenant, user_preferences
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="conversations")
    tenant = relationship("TenantModel", back_populates="conversations")
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")


class MessageModel(Base):
    """
    Message model for AI chat messages.
    Stores both user messages and AI responses.
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    role = Column(String(50), nullable=False)  # user, assistant, system, function
    content = Column(Text, nullable=False)
    
    # Function calling support
    function_call = Column(JSON, nullable=True)  # Store function call details
    function_response = Column(JSON, nullable=True)  # Store function response
    
    # Metadata - using extra_metadata to avoid conflict with SQLAlchemy's metadata
    extra_metadata = Column(JSON, nullable=True)  # Store additional context, tokens used, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")
