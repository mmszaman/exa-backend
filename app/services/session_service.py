import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
from app.models.session import SessionModel
from app.core.logger import get_logger
from app.services.user_service import UserService

logger = get_logger("session_service")


class SessionService:

    # Create or update a session    
    @staticmethod
    async def create_or_update_session(
        db: AsyncSession,
        clerk_session_id: str,
        user_id: int,
        clerk_user_id: str,
        status: str = "active",
        **kwargs
    ) -> SessionModel:
        """Create a new session or update existing one."""
        # Check if session exists
        result = await db.execute(
            select(SessionModel).filter(SessionModel.clerk_session_id == clerk_session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            # Update existing session
            session.status = status
            session.user_id = user_id
            session.clerk_user_id = clerk_user_id
            
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            logger.info(f"Updated session: {clerk_session_id}")
        else:
            # Create new session
            session = SessionModel(
                clerk_session_id=clerk_session_id,
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                status=status,
                **kwargs
            )
            db.add(session)
            logger.info(f"Created new session: {clerk_session_id}")
        
        await db.commit()
        await db.refresh(session)
        return session

    # Background task to retry session creation
    @staticmethod
    async def retry_session_creation(session_data: dict, max_retries: int = 3, delay: int = 2):
        from app.core.database import AsyncSessionLocal
        
        for attempt in range(max_retries):
            await asyncio.sleep(delay)
            
            async with AsyncSessionLocal() as db:
                user = await UserService.get_user_by_clerk_id(db, session_data["clerk_user_id"])
                if user:
                    try:
                        await SessionService.create_or_update_session(
                            db=db,
                            clerk_session_id=session_data["clerk_session_id"],
                            user_id=user.id,
                            clerk_user_id=session_data["clerk_user_id"],
                            status=session_data["status"],
                            client_id=session_data.get("client_id"),
                            expires_at=session_data.get("expires_at"),
                            clerk_metadata=session_data.get("clerk_metadata")
                        )
                        logger.info(f"✓ Retry succeeded: Created session {session_data['clerk_session_id']} for user {session_data['clerk_user_id']}")
                        return
                    except Exception as e:
                        logger.error(f"Retry {attempt + 1} failed for session {session_data['clerk_session_id']}: {str(e)}")
                else:
                    logger.warning(f"Retry {attempt + 1}/{max_retries}: User {session_data['clerk_user_id']} still not found")
        
        logger.error(f"✗ All retries exhausted for session {session_data['clerk_session_id']}")

    # End a session
    @staticmethod
    async def end_session(db: AsyncSession, clerk_session_id: str) -> Optional[SessionModel]:
        """Mark a session as ended."""
        result = await db.execute(
            select(SessionModel).filter(SessionModel.clerk_session_id == clerk_session_id)
        )
        session = result.scalar_one_or_none()
        
        if session:
            from datetime import datetime, timezone
            session.status = "ended"
            session.ended_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(session)
            logger.info(f"Ended session: {clerk_session_id}")
            return session
        
        return None
    
    # Get all active sessions for a user
    @staticmethod
    async def get_active_sessions_for_user(
        db: AsyncSession,
        user_id: int
    ) -> list[SessionModel]:
        """Get all active sessions for a user."""
        result = await db.execute(
            select(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.status == "active"
            )
        )
        return result.scalars().all()
    
    # Revoke all active sessions for a user
    @staticmethod
    async def revoke_user_sessions(db: AsyncSession, user_id: int) -> int:
        """Revoke all active sessions for a user. Returns count of revoked sessions."""
        result = await db.execute(
            select(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.status == "active"
            )
        )
        sessions = result.scalars().all()
        
        count = 0
        for session in sessions:
            from datetime import datetime, timezone
            session.status = "revoked"
            session.ended_at = datetime.now(timezone.utc)
            count += 1
        
        if count > 0:
            await db.commit()
            logger.info(f"Revoked {count} active session(s) for user_id: {user_id}")
        
        return count