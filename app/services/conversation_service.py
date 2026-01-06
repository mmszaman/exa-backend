"""
Conversation Service for managing AI chat conversations and messages.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from fastapi import HTTPException, status

from app.models.conversation import ConversationModel, MessageModel
from app.schemas.conversation_schema import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
)
from app.core.logger import get_logger

logger = get_logger("conversation_service")


class ConversationService:
    """Service for managing conversations"""
    
    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: int,
        tenant_id: Optional[int] = None,
        title: Optional[str] = None,
    ) -> ConversationModel:
        """Create a new conversation"""
        conversation = ConversationModel(
            user_id=user_id,
            tenant_id=tenant_id,
            title=title,
            status="active",
            context={}
        )
        
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation
    
    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> Optional[ConversationModel]:
        """Get a conversation by ID (with user ownership check)"""
        result = await db.execute(
            select(ConversationModel).where(
                ConversationModel.id == conversation_id,
                ConversationModel.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_conversations(
        db: AsyncSession,
        user_id: int,
        tenant_id: Optional[int] = None,
        status: str = "active",
        limit: int = 50,
        skip: int = 0
    ) -> List[ConversationModel]:
        """Get all conversations for a user"""
        query = select(ConversationModel).where(
            ConversationModel.user_id == user_id,
            ConversationModel.status == status
        )
        
        if tenant_id:
            query = query.where(ConversationModel.tenant_id == tenant_id)
        
        query = query.order_by(desc(ConversationModel.updated_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int,
        update_data: ConversationUpdate
    ) -> Optional[ConversationModel]:
        """Update a conversation"""
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        
        if not conversation:
            return None
        
        # Update fields
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(conversation, field, value)
        
        await db.commit()
        await db.refresh(conversation)
        
        return conversation
    
    @staticmethod
    async def archive_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Archive a conversation"""
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        
        if not conversation:
            return False
        
        conversation.status = "archived"
        await db.commit()
        
        logger.info(f"Archived conversation {conversation_id}")
        return True
    
    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Delete a conversation (soft delete)"""
        conversation = await ConversationService.get_conversation(db, conversation_id, user_id)
        
        if not conversation:
            return False
        
        conversation.status = "deleted"
        await db.commit()
        
        logger.info(f"Deleted conversation {conversation_id}")
        return True


class MessageService:
    """Service for managing messages"""
    
    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: int,
        role: str,
        content: str,
        function_call: Optional[Dict[str, Any]] = None,
        function_response: Optional[Dict[str, Any]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> MessageModel:
        """Create a new message"""
        message = MessageModel(
            conversation_id=conversation_id,
            role=role,
            content=content,
            function_call=function_call,
            function_response=function_response,
            extra_metadata=extra_metadata
        )
        
        db.add(message)
        await db.commit()
        await db.refresh(message)
        
        # Update conversation's updated_at timestamp
        result = await db.execute(
            select(ConversationModel).where(ConversationModel.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            # Auto-generate title from first user message if not set
            if not conversation.title and role == "user":
                # Use first 50 chars of message as title
                conversation.title = content[:50] + ("..." if len(content) > 50 else "")
            await db.commit()
        
        return message
    
    @staticmethod
    async def get_conversation_messages(
        db: AsyncSession,
        conversation_id: int,
        limit: int = 100,
        skip: int = 0
    ) -> List[MessageModel]:
        """Get all messages for a conversation"""
        result = await db.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_recent_messages(
        db: AsyncSession,
        conversation_id: int,
        limit: int = 10
    ) -> List[MessageModel]:
        """Get recent messages for context"""
        result = await db.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(desc(MessageModel.created_at))
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order
