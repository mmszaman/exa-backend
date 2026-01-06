from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.clerk_auth import CurrentUser
from app.schemas.business_schema import (
    Business,
    BusinessCreate,
    BusinessUpdate,
    BusinessListResponse
)
from app.services.business_service import BusinessService
from app.services.tenant_service import TenantService
from app.core.logger import get_logger
import math

logger = get_logger("business_router")
router = APIRouter()


# Helper function to get tenant_id from user's membership
async def get_tenant_id_from_user(user_id: int, db: AsyncSession) -> int:
    """Get tenant_id from user's active membership or create default tenant."""
    from app.services.membership_service import MembershipService
    
    try:
        # Get user's active memberships
        memberships = await MembershipService.get_user_memberships(
            db=db,
            user_id=user_id,
            active_only=True
        )
        
        if not memberships:
            # Auto-create a default tenant for user
            from app.models.user import UserModel
            from app.models.tenant import TenantModel
            from sqlalchemy import select
            
            # Get user info
            user_stmt = select(UserModel).where(UserModel.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Create default tenant
            tenant = TenantModel(
                clerk_org_id=f"default_{user.clerk_user_id}",
                name=f"{user.full_name or user.email}'s Organization",
                slug=f"org-{user.id}",
                status="active"
            )
            db.add(tenant)
            await db.flush()
            
            # Create membership - set as primary since it's the first tenant
            membership = await MembershipService.create_membership(
                db=db,
                user_id=user_id,
                tenant_id=tenant.id,
                role="owner",
                is_primary=True
            )
            
            logger.info(f"Auto-created tenant {tenant.id} for user {user_id}")
            return tenant.id
        
        # Return first active membership's tenant
        return memberships[0].tenant_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tenant for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tenant context: {str(e)}"
        )


#################################################
# GET /api/v1/businesses
# Get all businesses with pagination and filters
@router.get("", response_model=BusinessListResponse)
async def get_businesses(
    current_user: CurrentUser,
    tenant_id: int = Query(..., description="Tenant ID (required for data isolation)"),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by business type"),
    search: Optional[str] = Query(None, description="Search by name, legal name, or description")
):
    """
    Get all businesses for a specific tenant.
    
    **Required:**
    - tenant_id: Must be provided and user must have access to this tenant
    
    **Authorization:**
    - User must be an active member of the specified tenant
    """
    # Validate user has access to the provided tenant_id
    from app.services.membership_service import MembershipService
    membership = await MembershipService.get_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have access to tenant {tenant_id}"
        )
    
    businesses, total = await BusinessService.get_businesses(
        db=db,
        tenant_id=tenant_id,
        page=page,
        limit=limit,
        status=status,
        type=type,
        search=search
    )
    
    total_pages = math.ceil(total / limit) if total > 0 else 0
    
    return BusinessListResponse(
        data=businesses,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


#################################################
# GET /api/v1/businesses/{business_id}
# Get single business by ID
@router.get("/{business_id}", response_model=Business)
async def get_business(
    business_id: str,
    current_user: CurrentUser,
    tenant_id: int = Query(..., description="Tenant ID (required for data isolation)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single business by public_id (UUID).
    
    **Required:**
    - tenant_id: Must be provided and user must have access to this tenant
    
    **Authorization:**
    - User must be an active member of the specified tenant
    - Business must belong to the specified tenant
    """
    # Validate user has access to the provided tenant_id
    from app.services.membership_service import MembershipService
    membership = await MembershipService.get_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have access to tenant {tenant_id}"
        )
    
    business = await BusinessService.get_business_by_public_id(
        db=db,
        public_id=business_id,
        tenant_id=tenant_id
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    return business


#################################################
# POST /api/v1/businesses
# Create new business
@router.post("", response_model=Business, status_code=status.HTTP_201_CREATED)
async def create_business(
    request: Request,
    current_user: CurrentUser,
    tenant_id: int = Query(..., description="Tenant ID (required for data isolation)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new business.
    
    **Required:**
    - tenant_id: Must be provided and user must have access to this tenant
    
    **Authorization:**
    - User must be an active member of the specified tenant
    - Email must be unique within tenant
    """
    # Log raw request body for debugging
    body = await request.json()
    logger.info(f"📥 RAW REQUEST BODY: {body}")
    logger.info(f"📥 BODY TYPE: {type(body)}")
    logger.info(f"📥 BODY KEYS: {body.keys() if isinstance(body, dict) else 'Not a dict'}")
    
    # Now validate with Pydantic
    try:
        business_data = BusinessCreate(**body)
        logger.info(f"✅ VALIDATED DATA: {business_data.model_dump()}")
    except Exception as e:
        logger.error(f"❌ VALIDATION ERROR: {str(e)}")
        logger.error(f"❌ ERROR TYPE: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    
    # Validate user has access to the provided tenant_id
    from app.services.membership_service import MembershipService
    membership = await MembershipService.get_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have access to tenant {tenant_id}"
        )
    
    # Check if business with same email already exists (only if email provided)
    if business_data.email:
        existing_business = await BusinessService.get_business_by_email(
            db=db,
            email=business_data.email,
            tenant_id=tenant_id
        )
        
        if existing_business:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business with email {business_data.email} already exists"
            )
    
    business = await BusinessService.create_business(
        db=db,
        business_data=business_data,
        tenant_id=tenant_id,
        user_id=current_user.id
    )
    
    logger.info(f"Created business {business.id} by user {current_user.id}")
    return business


#################################################
# PUT /api/v1/businesses/{business_id}
# Update existing business
@router.put("/{business_id}", response_model=Business)
async def update_business(
    business_id: str,
    request: Request,
    current_user: CurrentUser,
    tenant_id: int = Query(..., description="Tenant ID (required for data isolation)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing business by public_id (UUID).
    
    **Required:**
    - tenant_id: Must be provided and user must have access to this tenant
    
    **Authorization:**
    - User must be an active member of the specified tenant
    - Business must belong to the specified tenant
    - Only provided fields will be updated
    """
    # Log raw request body for debugging
    body = await request.json()
    logger.info(f"📥 UPDATE RAW REQUEST BODY: {body}")
    logger.info(f"📥 BODY TYPE: {type(body)}")
    
    # Now validate with Pydantic
    try:
        business_data = BusinessUpdate(**body)
        logger.info(f"✅ VALIDATED UPDATE DATA: {business_data.model_dump(exclude_unset=True)}")
    except Exception as e:
        logger.error(f"❌ UPDATE VALIDATION ERROR: {str(e)}")
        logger.error(f"❌ ERROR TYPE: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    
    # Validate user has access to the provided tenant_id
    from app.services.membership_service import MembershipService
    membership = await MembershipService.get_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have access to tenant {tenant_id}"
        )
    
    # Get the business by public_id first
    existing = await BusinessService.get_business_by_public_id(
        db=db,
        public_id=business_id,
        tenant_id=tenant_id
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    # Check if email is being updated and if it's unique (only if email provided and not empty)
    if business_data.email:
        existing_business = await BusinessService.get_business_by_email(
            db=db,
            email=business_data.email,
            tenant_id=tenant_id
        )
        
        if existing_business and existing_business.id != existing.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business with email {business_data.email} already exists"
            )
    
    business = await BusinessService.update_business(
        db=db,
        business_id=existing.id,
        tenant_id=tenant_id,
        business_data=business_data,
        user_id=current_user.id
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    logger.info(f"Updated business {business_id} by user {current_user.id}")
    return business


#################################################
# DELETE /api/v1/businesses/{business_id}
# Delete business
@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(
    business_id: str,
    current_user: CurrentUser,
    tenant_id: int = Query(..., description="Tenant ID (required for data isolation)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a business by public_id (UUID).
    
    **Required:**
    - tenant_id: Must be provided and user must have access to this tenant
    
    **Authorization:**
    - User must be an active member of the specified tenant
    - Business must belong to the specified tenant
    
    **Warning:**
    - This is a hard delete operation
    - All associated data will be permanently removed
    """
    # Validate user has access to the provided tenant_id
    from app.services.membership_service import MembershipService
    membership = await MembershipService.get_membership(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    if not membership or not membership.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have access to tenant {tenant_id}"
        )
    
    # Get the business by public_id first
    existing = await BusinessService.get_business_by_public_id(
        db=db,
        public_id=business_id,
        tenant_id=tenant_id
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    success = await BusinessService.delete_business(
        db=db,
        business_id=existing.id,
        tenant_id=tenant_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID {business_id} not found"
        )
    
    logger.info(f"Deleted business {business_id} by user {current_user.id}")
    return None
