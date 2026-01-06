from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List
from app.models.business import BusinessModel
from app.schemas.business_schema import BusinessCreate, BusinessUpdate
from app.core.logger import get_logger

logger = get_logger("business_service")


class BusinessService:
    """Service class for business operations."""

    @staticmethod
    async def create_business(
        db: AsyncSession,
        business_data: BusinessCreate,
        tenant_id: int,
        user_id: int
    ) -> BusinessModel:
        """Create a new business."""
        # Convert address to dict if it's a Pydantic model
        address_dict = business_data.address.model_dump(by_alias=True) if hasattr(business_data.address, 'model_dump') else business_data.address
        
        business = BusinessModel(
            tenant_id=tenant_id,
            owner_user_id=user_id,
            name=business_data.name,
            legal_name=business_data.legal_name,
            type=business_data.type,
            status=business_data.status,
            tax_id=business_data.tax_id,
            email=business_data.email,
            phone=business_data.phone,
            website=business_data.website,
            address=address_dict,
            logo_url=business_data.logo_url,
            description=business_data.description,
            industry=business_data.industry,
            employee_count=business_data.employee_count,
            founded_year=business_data.founded_year
        )
        
        db.add(business)
        await db.commit()
        await db.refresh(business)
        
        logger.info(f"Created business: {business.id} for tenant: {tenant_id}")
        return business

    @staticmethod
    async def get_business_by_id(
        db: AsyncSession,
        business_id: int,
        tenant_id: int
    ) -> Optional[BusinessModel]:
        """Get a business by ID within tenant scope."""
        result = await db.execute(
            select(BusinessModel).filter(
                BusinessModel.id == business_id,
                BusinessModel.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_business_by_public_id(
        db: AsyncSession,
        public_id: str,
        tenant_id: int
    ) -> Optional[BusinessModel]:
        """Get a business by public_id (UUID) within tenant scope."""
        from uuid import UUID
        try:
            uuid_obj = UUID(public_id)
        except (ValueError, AttributeError):
            return None
        
        result = await db.execute(
            select(BusinessModel).filter(
                BusinessModel.public_id == uuid_obj,
                BusinessModel.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_businesses(
        db: AsyncSession,
        tenant_id: int,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[BusinessModel], int]:
        """Get paginated list of businesses with optional filters."""
        logger.info(f"🔍 QUERY PARAMETERS: tenant_id={tenant_id}, page={page}, limit={limit}, status={status}, type={type}, search={search}")
        
        # Build base query
        query = select(BusinessModel).filter(BusinessModel.tenant_id == tenant_id)
        logger.info(f"📋 BASE QUERY FILTERS: tenant_id = {tenant_id} (NO clerk_org_id dependency)")
        
        # Apply filters
        if status:
            query = query.filter(BusinessModel.status == status)
        
        if type:
            query = query.filter(BusinessModel.type == type)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    BusinessModel.name.ilike(search_term),
                    BusinessModel.legal_name.ilike(search_term),
                    BusinessModel.description.ilike(search_term)
                )
            )
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(BusinessModel.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        businesses = result.scalars().all()
        
        return list(businesses), total

    @staticmethod
    async def update_business(
        db: AsyncSession,
        business_id: int,
        tenant_id: int,
        business_data: BusinessUpdate,
        user_id: int
    ) -> Optional[BusinessModel]:
        """Update an existing business."""
        # Get the business
        result = await db.execute(
            select(BusinessModel).filter(
                BusinessModel.id == business_id,
                BusinessModel.tenant_id == tenant_id
            )
        )
        business = result.scalar_one_or_none()
        
        if not business:
            return None
        
        # Update fields
        update_data = business_data.model_dump(exclude_unset=True, by_alias=False)
        
        # Handle address separately if it's a Pydantic model
        if 'address' in update_data and update_data['address'] is not None:
            if hasattr(update_data['address'], 'model_dump'):
                update_data['address'] = update_data['address'].model_dump(by_alias=True)
        
        # Handle logo field name change
        if 'logo' in update_data:
            update_data['logo_url'] = update_data.pop('logo')
        
        for field, value in update_data.items():
            setattr(business, field, value)
        
        await db.commit()
        await db.refresh(business)
        
        logger.info(f"Updated business: {business_id}")
        return business

    @staticmethod
    async def delete_business(
        db: AsyncSession,
        business_id: int,
        tenant_id: int
    ) -> bool:
        """Delete a business (hard delete)."""
        result = await db.execute(
            select(BusinessModel).filter(
                BusinessModel.id == business_id,
                BusinessModel.tenant_id == tenant_id
            )
        )
        business = result.scalar_one_or_none()
        
        if not business:
            return False
        
        await db.delete(business)
        await db.commit()
        
        logger.info(f"Deleted business: {business_id}")
        return True

    @staticmethod
    async def get_business_by_email(
        db: AsyncSession,
        email: str,
        tenant_id: int
    ) -> Optional[BusinessModel]:
        """Get a business by email within tenant scope."""
        result = await db.execute(
            select(BusinessModel).filter(
                BusinessModel.email == email,
                BusinessModel.tenant_id == tenant_id
            )
        )
        return result.scalar_one_or_none()
