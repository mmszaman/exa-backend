from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.user_history import UserHistoryModel
from app.core.logger import get_logger

logger = get_logger("user_history_service")


class UserHistoryService:
    """Service for logging user actions and history"""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: int,
        clerk_user_id: str,
        action: str,
        description: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        action_metadata: Optional[str] = None
    ) -> UserHistoryModel:
        """Log a user action to history"""
        history = UserHistoryModel(
            user_id=user_id,
            clerk_user_id=clerk_user_id,
            action=action,
            description=description,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action_metadata=action_metadata
        )
        
        db.add(history)
        await db.commit()
        await db.refresh(history)
        
        logger.info(f"Logged action '{action}' for user {clerk_user_id}")
        return history
    
    @staticmethod
    async def get_user_history(
        db: AsyncSession,
        user_id: int,
        limit: int = 100
    ) -> List[UserHistoryModel]:
        """Get user's action history"""
        stmt = select(UserHistoryModel).where(
            UserHistoryModel.user_id == user_id
        ).order_by(UserHistoryModel.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_history_by_action(
        db: AsyncSession,
        action: str,
        limit: int = 100
    ) -> List[UserHistoryModel]:
        """Get history by action type"""
        stmt = select(UserHistoryModel).where(
            UserHistoryModel.action == action
        ).order_by(UserHistoryModel.created_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
