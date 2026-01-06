from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, Tuple
from datetime import datetime
from app.models.tenant import TenantModel
from app.schemas.tenant_schema import TenantCreate, TenantUpdate
from app.core.logger import get_logger

logger = get_logger("tenant_service")


class TenantService:
    """Service for tenant/organization management operations."""

    @staticmethod
    async def create_tenant(db: AsyncSession, tenant_data: TenantCreate) -> TenantModel:
        """Create a new tenant."""
        tenant = TenantModel(
            name=tenant_data.name,
            legal_name=tenant_data.legal_name,
            slug=tenant_data.slug,
            logo_url=tenant_data.logo_url,
            tax_id=tenant_data.tax_id,
            type=tenant_data.type,
            team_size=tenant_data.team_size,
            email=tenant_data.email,
            phone=tenant_data.phone,
            website=tenant_data.website,
            status=tenant_data.status,
            settings=tenant_data.settings,
            features=tenant_data.features,
            clerk_metadata=tenant_data.clerk_metadata
        )
        
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        
        logger.info(f"Created tenant: {tenant.id} ({tenant.name})")
        return tenant

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: int) -> Optional[TenantModel]:
        """Get tenant by ID."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.id == tenant_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenant_by_public_id(db: AsyncSession, public_id: str) -> Optional[TenantModel]:
        """Get tenant by public UUID."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.public_id == public_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenant_by_slug(db: AsyncSession, slug: str) -> Optional[TenantModel]:
        """Get tenant by slug."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.slug == slug,
                TenantModel.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenants(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[list[TenantModel], int]:
        """Get paginated list of tenants with filters."""
        # Build query
        query = select(TenantModel).filter(TenantModel.deleted_at.is_(None))
        
        # Apply filters
        if status:
            query = query.filter(TenantModel.status == status)
        if type:
            query = query.filter(TenantModel.type == type)
        if search:
            query = query.filter(
                or_(
                    TenantModel.name.ilike(f"%{search}%"),
                    TenantModel.slug.ilike(f"%{search}%"),
                    TenantModel.email.ilike(f"%{search}%")
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.alias())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(TenantModel.created_at.desc())
        result = await db.execute(query)
        tenants = result.scalars().all()
        
        return tenants, total

    @staticmethod
    async def update_tenant(
        db: AsyncSession,
        tenant_id: int,
        tenant_data: TenantUpdate
    ) -> Optional[TenantModel]:
        """Update a tenant."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.id == tenant_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return None
        
        # Update fields if provided
        update_data = tenant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tenant, field, value)
        
        tenant.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(tenant)
        
        logger.info(f"Updated tenant: {tenant.id}")
        return tenant

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: int) -> bool:
        """Soft delete a tenant."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.id == tenant_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return False
        
        tenant.deleted_at = datetime.utcnow()
        tenant.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(f"Soft deleted tenant: {tenant_id}")
        return True

    @staticmethod
    async def suspend_tenant(db: AsyncSession, tenant_id: int) -> Optional[TenantModel]:
        """Suspend a tenant."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.id == tenant_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return None
        
        tenant.status = "suspended"
        tenant.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(tenant)
        
        logger.info(f"Suspended tenant: {tenant_id}")
        return tenant

    @staticmethod
    async def activate_tenant(db: AsyncSession, tenant_id: int) -> Optional[TenantModel]:
        """Activate a tenant."""
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.id == tenant_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return None
        
        tenant.status = "active"
        tenant.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(tenant)
        
        logger.info(f"Activated tenant: {tenant_id}")
        return tenant
