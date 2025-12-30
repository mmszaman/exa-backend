from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import json
from app.models.session import SessionModel
from app.models.tenant import TenantModel
from app.core.logger import get_logger

logger = get_logger("session_service")


class SessionService:
    """Service for managing user sessions synced from Clerk."""
    
    @staticmethod
    async def create_or_update_session(
        db: AsyncSession,
        clerk_session_id: str,
        user_id: int,
        clerk_user_id: str,
        tenant_id: Optional[str] = None,
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
            session.tenant_id = tenant_id
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
                tenant_id=tenant_id,
                status=status,
                **kwargs
            )
            db.add(session)
            logger.info(f"Created new session: {clerk_session_id}")
        
        await db.commit()
        await db.refresh(session)
        return session
    
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


class TenantService:
    """Service for managing tenants/organizations synced from Clerk."""
    
    @staticmethod
    async def create_or_update_tenant(
        db: AsyncSession,
        clerk_org_id: str,
        name: str,
        slug: str,
        **kwargs
    ) -> TenantModel:
        """Create a new tenant or update existing one."""
        # Check if tenant exists
        result = await db.execute(
            select(TenantModel).filter(TenantModel.clerk_org_id == clerk_org_id)
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            # Update existing tenant
            tenant.name = name
            tenant.slug = slug
            
            for key, value in kwargs.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)
            
            logger.info(f"Updated tenant: {clerk_org_id}")
        else:
            # Create new tenant
            tenant = TenantModel(
                clerk_org_id=clerk_org_id,
                name=name,
                slug=slug,
                **kwargs
            )
            db.add(tenant)
            logger.info(f"Created new tenant: {clerk_org_id}")
        
        await db.commit()
        await db.refresh(tenant)
        return tenant
    
    @staticmethod
    async def get_tenant_by_clerk_id(db: AsyncSession, clerk_org_id: str) -> Optional[TenantModel]:
        """Get tenant by Clerk organization ID."""
        result = await db.execute(
            select(TenantModel).filter(TenantModel.clerk_org_id == clerk_org_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def deactivate_tenant(db: AsyncSession, clerk_org_id: str) -> Optional[TenantModel]:
        """Soft delete a tenant by deactivating it."""
        result = await db.execute(
            select(TenantModel).filter(TenantModel.clerk_org_id == clerk_org_id)
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            tenant.is_active = False
            await db.commit()
            await db.refresh(tenant)
            logger.info(f"Deactivated tenant: {clerk_org_id}")
            return tenant
        
        return None
