
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.core.clerk_auth import get_current_user, CurrentUser

from app.schemas.tenant_schema import Tenant, TenantCreate, TenantUpdate, TenantListResponse
from app.services.tenant_service import TenantService
from app.services.membership_service import MembershipService
from app.core.logger import get_logger

logger = get_logger("tenant_api")
router = APIRouter()

# POST /api/v1/tenants
# Create a new tenant
@router.post("", response_model=Tenant, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tenant/organization.
    
    Note: Typically called from Clerk webhooks when organization is created.
    Can also be used for manual tenant creation by admins.
    """
    # Check slug uniqueness
    existing_slug = await TenantService.get_tenant_by_slug(db, tenant_data.slug)
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tenant with slug '{tenant_data.slug}' already exists"
        )
    
    tenant = await TenantService.create_tenant(db, tenant_data)
    logger.info(f"Tenant created: {tenant.id} by user {current_user.id}")
    
    return tenant

# GET /api/v1/tenants/me
# Get tenants for current user
@router.get("/me", response_model=List[Tenant])
async def get_current_user_tenants(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tenants that the current user belongs to.
    
    Returns list of tenants based on user's active memberships.
    Primary tenant is listed first.
    """
    # Get user's active memberships
    memberships = await MembershipService.get_user_memberships(
        db=db,
        user_id=current_user.id,
        active_only=True
    )
    
    if not memberships:
        # Return empty list if user has no tenants
        return []
    
    # Sort memberships: primary first, then by created date
    memberships.sort(key=lambda m: (not m.is_primary, m.created_at))
    
    # Get all tenant_ids from memberships (already sorted)
    tenant_ids = [membership.tenant_id for membership in memberships]
    
    # Fetch all tenants in order
    tenants = []
    for tenant_id in tenant_ids:
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        if tenant:
            tenants.append(tenant)
    
    return tenants

# GET /api/v1/tenants/me/primary-id
# Get primary tenant ID for current user
@router.get("/me/primary-id")
async def get_primary_tenant_id(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the tenant_id of the user's primary tenant.
    
    Returns:
    - {"tenant_id": 123} if user has a primary tenant
    - HTTP 404 if user has no primary tenant
    """
    # Get user's active memberships
    memberships = await MembershipService.get_user_memberships(
        db=db,
        user_id=current_user.id,
        active_only=True
    )
    
    if not memberships:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no active tenant memberships"
        )
    
    # Find primary membership
    primary_membership = next((m for m in memberships if m.is_primary), None)
    
    if not primary_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User has no primary tenant set"
        )
    
    # Verify tenant is active
    tenant = await TenantService.get_tenant_by_id(db, primary_membership.tenant_id)
    if not tenant or tenant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primary tenant is not active"
        )
    
    logger.info(f"Primary tenant ID retrieved: tenant_id={primary_membership.tenant_id}, user_id={current_user.id}")
    return {"tenant_id": primary_membership.tenant_id}

# GET /api/v1/tenants/{tenant_id}
# Get tenant by ID
@router.get("/{tenant_id}", response_model=Tenant)
async def get_tenant(
    tenant_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Get tenant by ID.
    
    Returns tenant details if user has access.
    """
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    # TODO: Add permission check - user should belong to tenant or be admin
    
    return tenant

# GET /api/v1/tenants/slug/{slug}
# Get tenant by slug
@router.get("/slug/{slug}", response_model=Tenant)
async def get_tenant_by_slug(
    slug: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Get tenant by slug.
    
    Useful for tenant-specific subdomains or paths.
    """
    tenant = await TenantService.get_tenant_by_slug(db, slug)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with slug '{slug}' not found"
        )
    
    return tenant

# GET /api/v1/tenants
# List tenants with pagination and filters
@router.get("", response_model=TenantListResponse)
async def list_tenants(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    search: Optional[str] = Query(None, description="Search in name, slug, email")
):
    """
    List tenants with pagination and filters.
    
    Admin endpoint - requires admin role.
    """
    # TODO: Add admin permission check
    
    tenants, total = await TenantService.get_tenants(
        db,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        search=search
    )
    
    page = (skip // limit) + 1 if limit > 0 else 1
    
    return TenantListResponse(
        tenants=tenants,
        total=total,
        page=page,
        page_size=limit
    )

# PUT /api/v1/tenants/{tenant_id}
# Update tenant details
@router.put("/{tenant_id}", response_model=Tenant)
async def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Update tenant details.
    
    Requires owner or admin role for the tenant.
    Only active tenants can be updated.
    """
    # TODO: Add permission check - user should be owner/admin of tenant
    
    # Check if tenant exists
    existing_tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    # Log the update data for debugging
    update_dict = tenant_data.model_dump(exclude_unset=True)
    logger.info(f"Update tenant {tenant_id}: current_status={existing_tenant.status}, update_fields={list(update_dict.keys())}, update_data={update_dict}")
    
    # Only allow status updates on inactive tenants, block other field updates
    if existing_tenant.status != "active":
        # Check if only status is being updated
        if set(update_dict.keys()) != {"status"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot update inactive tenant fields other than status. Current status: {existing_tenant.status}. Fields being updated: {list(update_dict.keys())}"
            )
    
    tenant = await TenantService.update_tenant(db, tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    logger.info(f"Tenant updated: {tenant_id} by user {current_user.id}")
    return tenant

# POST /api/v1/tenants/{tenant_id}/suspend
# Suspend tenant
@router.post("/{tenant_id}/suspend", response_model=Tenant)
async def suspend_tenant(
    tenant_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Suspend a tenant.
    
    Prevents tenant from accessing the system.
    Requires admin role.
    """
    # TODO: Add admin permission check
    
    tenant = await TenantService.suspend_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    logger.info(f"Tenant suspended: {tenant_id} by user {current_user.id}")
    return tenant

# POST /api/v1/tenants/{tenant_id}/activate
# Activate tenant
@router.post("/{tenant_id}/activate", response_model=Tenant)
async def activate_tenant(
    tenant_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Activate a tenant.
    
    Restores access for a suspended tenant.
    Requires admin role.
    """
    # TODO: Add admin permission check
    
    tenant = await TenantService.activate_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    logger.info(f"Tenant activated: {tenant_id} by user {current_user.id}")
    return tenant

# DELETE /api/v1/tenants/{tenant_id}
# Soft delete tenant
@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete a tenant.
    
    Sets deleted_at timestamp. Tenant will be excluded from queries.
    Requires admin role.
    """
    # TODO: Add admin permission check
    
    success = await TenantService.delete_tenant(db, tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    logger.info(f"Tenant deleted: {tenant_id} by user {current_user.id}")
    return None

# PATCH /api/v1/tenants/{tenant_id}/set-primary
# Set a tenant as primary for the current user
@router.patch("/{tenant_id}/set-primary", response_model=Tenant)
async def set_primary_tenant(
    tenant_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Set a tenant as the primary tenant for the current user.
    
    The primary tenant is used as the default tenant when the user logs in.
    Only one tenant can be primary per user.
    Only active tenants can be set as primary.
    """
    # Check if tenant exists and is active
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    if tenant.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot set inactive tenant as primary. Current status: {tenant.status}"
        )
    
    # Set the tenant as primary for the user
    membership = await MembershipService.set_primary_tenant(
        db=db,
        user_id=current_user.id,
        tenant_id=tenant_id
    )
    
    logger.info(f"Primary tenant set: tenant_id={tenant_id}, user_id={current_user.id}")
    return tenant

