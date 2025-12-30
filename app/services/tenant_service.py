from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.tenant import TenantModel
from app.core.logger import get_logger

logger = get_logger("tenant_service")


class TenantService:

    ##Write code here##

    @staticmethod
    async def get_tenant_by_tenant_id(db: AsyncSession, tenant_id: str) -> Optional[TenantModel]:
        """Get tenant by Clerk organization ID."""
        result = await db.execute(
            select(TenantModel).filter(TenantModel.clerk_org_id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def deactivate_tenant(db: AsyncSession, tenant_id: str) -> Optional[TenantModel]:
        """Soft delete a tenant by deactivating it."""
        result = await db.execute(
            select(TenantModel).filter(TenantModel.clerk_org_id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            tenant.is_active = False
            await db.commit()
            await db.refresh(tenant)
            logger.info(f"Deactivated tenant: {tenant_id}")
            return tenant
        
        return None
