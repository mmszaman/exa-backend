from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.tenant import TenantModel
from app.core.logger import get_logger

logger = get_logger("tenant_service")


class TenantService:

    ##Write code here##
    
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
