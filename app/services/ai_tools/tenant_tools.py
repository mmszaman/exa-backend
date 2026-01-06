"""
Tenant operation tools for SMBPilot AI Agent.
These tools allow the AI to manage tenant/organization operations.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.tenant_service import TenantService
from app.services.membership_service import MembershipService


async def list_tenants(
    db: AsyncSession,
    user_id: int,
) -> Dict[str, Any]:
    """
    List all tenants/organizations the user belongs to.
    The primary tenant is listed first.
    
    Returns:
        Dictionary containing list of tenants with membership info
    """
    # Get user's active memberships
    memberships = await MembershipService.get_user_memberships(
        db=db,
        user_id=user_id,
        active_only=True
    )
    
    if not memberships:
        return {
            "success": True,
            "count": 0,
            "tenants": [],
            "message": "You don't belong to any organizations yet"
        }
    
    # Sort by primary first
    memberships.sort(key=lambda m: (not m.is_primary, m.created_at))
    
    # Fetch tenant details
    tenant_list = []
    for membership in memberships:
        tenant = await TenantService.get_tenant_by_id(db, membership.tenant_id)
        if tenant:
            tenant_list.append({
                "id": tenant.id,
                "name": tenant.name,
                "slug": tenant.slug,
                "role": membership.role,
                "is_primary": membership.is_primary,
                "status": tenant.status,
            })
    
    primary_tenant = next((t for t in tenant_list if t["is_primary"]), None)
    primary_name = primary_tenant["name"] if primary_tenant else "None"
    
    return {
        "success": True,
        "count": len(tenant_list),
        "tenants": tenant_list,
        "primary_tenant": primary_name,
        "message": f"You have access to {len(tenant_list)} organization(s). Current primary: {primary_name}"
    }


async def get_current_tenant(
    db: AsyncSession,
    user_id: int,
    tenant_id: int,
) -> Dict[str, Any]:
    """
    Get information about the current active tenant.
    
    Returns:
        Dictionary containing current tenant information
    """
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    
    if not tenant:
        return {
            "success": False,
            "message": "Current tenant not found"
        }
    
    # Get user's membership to this tenant
    membership = await MembershipService.get_membership(db, user_id, tenant_id)
    
    return {
        "success": True,
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "status": tenant.status,
            "your_role": membership.role if membership else "unknown",
            "is_primary": membership.is_primary if membership else False,
        },
        "message": f"Current organization: {tenant.name}"
    }


async def set_primary_tenant(
    tenant_id: int,
    db: AsyncSession,
    user_id: int,
) -> Dict[str, Any]:
    """
    Set a tenant as the primary/default tenant for the user.
    This tenant will be used by default when you log in.
    
    Args:
        tenant_id: The ID of the tenant to set as primary
    
    Returns:
        Dictionary confirming the primary tenant change
    """
    try:
        membership = await MembershipService.set_primary_tenant(
            db=db,
            user_id=user_id,
            tenant_id=tenant_id
        )
        
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)
        
        return {
            "success": True,
            "tenant_id": tenant_id,
            "tenant_name": tenant.name if tenant else "Unknown",
            "message": f"Successfully set '{tenant.name}' as your primary organization"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to set primary tenant: {str(e)}"
        }


async def get_tenant_info(
    tenant_id: int,
    db: AsyncSession,
    user_id: int,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific tenant/organization.
    
    Args:
        tenant_id: The ID of the tenant to get information about
    
    Returns:
        Dictionary containing detailed tenant information
    """
    # Verify user has access to this tenant
    membership = await MembershipService.get_membership(db, user_id, tenant_id)
    
    if not membership or not membership.is_active:
        return {
            "success": False,
            "message": "You don't have access to this organization"
        }
    
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    
    if not tenant:
        return {
            "success": False,
            "message": "Organization not found"
        }
    
    return {
        "success": True,
        "tenant": {
            "id": tenant.id,
            "name": tenant.name,
            "slug": tenant.slug,
            "status": tenant.status,
            "email": tenant.email,
            "phone": tenant.phone,
            "website": tenant.website,
            "your_role": membership.role,
            "is_primary": membership.is_primary,
            "created_at": str(tenant.created_at),
        }
    }
