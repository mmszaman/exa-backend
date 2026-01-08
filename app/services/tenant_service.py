from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, update
from typing import Optional, Tuple
from datetime import datetime
from app.models.tenant import TenantModel
from app.models.membership import MembershipModel
from app.schemas.tenant_schema import TenantInput
from app.core.logger import get_logger
from app.core.clerk_auth import get_clerk_org, create_clerk_org, sync_clerk_org_to_db, get_user_clerk_orgs

logger = get_logger("tenant_service")


class TenantService:

    ##################################################################################
    # Create a tenant from Clerk org (primary method for new tenants)
    @staticmethod
    async def create_tenant_from_clerk(
        db: AsyncSession, 
        clerk_org_id: str,
        clerk_user_id: str,
        tenant_data: TenantInput
    ) -> TenantModel:
        """Create a new tenant by creating Clerk org first, then syncing to DB."""
        try:
            # First, create organization in Clerk
            logger.info(f"Creating Clerk organization: {tenant_data.name}")
            clerk_org_data = await create_clerk_org(
                name=tenant_data.name,
                created_by=clerk_user_id,
                slug=tenant_data.slug
            )
            
            clerk_org_id = clerk_org_data.get('id')
            logger.info(f"Clerk org created: {clerk_org_id}")
            
            # Sync the Clerk org to our database
            tenant = await sync_clerk_org_to_db(db, clerk_org_id, clerk_org_data)
            
            # Update additional fields
            if tenant_data.status:
                tenant.status = tenant_data.status
            if tenant_data.suspension_reason:
                tenant.suspension_reason = tenant_data.suspension_reason
            
            await db.commit()
            await db.refresh(tenant)
            
            logger.info(f"Tenant synced from Clerk: {tenant.id} ({tenant.name})")
            return tenant
            
        except Exception as e:
            logger.error(f"Error creating tenant from Clerk: {str(e)}")
            await db.rollback()
            raise

    ##################################################################################
    # Get or create tenant from Clerk org ID
    @staticmethod
    async def get_or_sync_from_clerk(
        db: AsyncSession, 
        clerk_org_id: str
    ) -> Optional[TenantModel]:
        """Get tenant by clerk_org_id, or sync from Clerk if not found."""
        # First check if tenant exists in our DB
        result = await db.execute(
            select(TenantModel).filter(
                TenantModel.clerk_org_id == clerk_org_id,
                TenantModel.deleted_at.is_(None)
            )
        )
        tenant = result.scalar_one_or_none()
        
        if tenant:
            logger.info(f"Tenant found in DB: {tenant.id}")
            return tenant
        
        # If not in DB, fetch from Clerk and sync
        try:
            logger.info(f"Tenant not in DB, syncing from Clerk: {clerk_org_id}")
            tenant = await sync_clerk_org_to_db(db, clerk_org_id)
            logger.info(f"Tenant synced from Clerk: {tenant.id}")
            return tenant
        except Exception as e:
            logger.error(f"Error syncing tenant from Clerk: {str(e)}")
            return None

    ##################################################################################
    # Sync user's tenants from Clerk
    @staticmethod
    async def sync_user_tenants_from_clerk(
        db: AsyncSession,
        clerk_user_id: str
    ) -> list[TenantModel]:
        """Fetch user's organizations from Clerk and sync to DB."""
        try:
            # Get user's orgs from Clerk
            clerk_orgs = await get_user_clerk_orgs(clerk_user_id)
            logger.info(f"Found {len(clerk_orgs)} orgs for user {clerk_user_id} in Clerk")
            
            tenants = []
            for org_data in clerk_orgs:
                clerk_org_id = org_data.get('id')
                
                # Sync each org to DB
                tenant = await sync_clerk_org_to_db(db, clerk_org_id, org_data)
                tenants.append(tenant)
            
            logger.info(f"Synced {len(tenants)} tenants from Clerk for user {clerk_user_id}")
            return tenants
            
        except Exception as e:
            logger.error(f"Error syncing user tenants from Clerk: {str(e)}")
            return []

    ##################################################################################
    # Create a new tenant (legacy method - kept for backward compatibility)
    @staticmethod
    async def create_tenant(db: AsyncSession, tenant_data: TenantInput, clerk_org_id: Optional[str] = None) -> TenantModel:
        """Create a new tenant. If clerk_org_id provided, links to Clerk org."""
        tenant = TenantModel(
            name=tenant_data.name,
            slug=tenant_data.slug,
            status=tenant_data.status or "active",
            suspension_reason=tenant_data.suspension_reason,
            clerk_org_id=clerk_org_id
        )
        
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        
        logger.info(f"Created tenant: {tenant.id} ({tenant.name}), clerk_org_id={clerk_org_id}")
        return tenant

    ##################################################################################
    # Retrieve tenant tenant_id
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

    ##################################################################################
    # Retrieve tenant by public UUID
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

    ##################################################################################
    # Retrieve tenant by slug
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

    ##################################################################################
    # List tenants with pagination and filters
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

    ##################################################################################
    # Update tenant details
    @staticmethod
    async def update_tenant(
        db: AsyncSession,
        tenant_id: int,
        tenant_data: TenantInput
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
        
        # Track if status is changing
        old_status = tenant.status
        status_changed = 'status' in update_data and update_data['status'] != tenant.status
        new_status = update_data.get('status') if status_changed else None
        
        logger.info(f"Update tenant {tenant_id}: old_status={old_status}, new_status={update_data.get('status')}, status_changed={status_changed}, update_data={update_data}")
        
        for field, value in update_data.items():
            setattr(tenant, field, value)
        
        tenant.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # If status changed, sync membership status (after tenant commit)
        if status_changed:
            # Set is_active based on new status
            is_active = new_status == "active"
            logger.info(f"Updating memberships for tenant {tenant_id}: is_active={is_active}")
            
            result = await db.execute(
                update(MembershipModel)
                .where(MembershipModel.tenant_id == tenant_id)
                .values(is_active=is_active, updated_at=datetime.now())
            )
            await db.commit()
            
            logger.info(f"Updated tenant {tenant_id} status from {old_status} to {new_status}, {result.rowcount} memberships updated, is_active set to {is_active}")
        
        await db.refresh(tenant)
        
        logger.info(f"Updated tenant: {tenant.id}")
        return tenant

    ##################################################################################
    # Soft delete a tenant: deactivate and set deleted_at
    @staticmethod
    async def deactivate_tenant(db: AsyncSession, tenant_id: int) -> bool:
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
        
        tenant.status = "deactivated"
        tenant.deleted_at = datetime.now()
        tenant.updated_at = datetime.now()
        
        # Also deactivate all memberships for this tenant
        await db.execute(
            update(MembershipModel)
            .where(MembershipModel.tenant_id == tenant_id)
            .values(is_active=False, updated_at=datetime.now())
        )
        
        await db.commit()
        
        logger.info(f"Soft deleted tenant and deactivated memberships: {tenant_id}")
        return True

    ##################################################################################
    # Hard delete a tenant from database (permanent deletion)
    @staticmethod
    ### On hard delete, all related data should be handled appropriately (e.g., cascade delete) ###
    async def delete_tenant_permanent(db: AsyncSession, tenant_id: int) -> bool:
        """Permanently delete a tenant from database."""
        result = await db.execute(
            select(TenantModel).filter(TenantModel.id == tenant_id)
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return False
        
        await db.delete(tenant)
        await db.commit()
        
        logger.warning(f"PERMANENTLY deleted tenant: {tenant_id}")
        return True
