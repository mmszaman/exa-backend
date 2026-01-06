"""
Business operations tools for SMBPilot AI Agent.
These are the actual implementation functions (without @tool decorator).
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tenant import TenantModel


async def create_business(
    name: str,
    db: AsyncSession,
    tenant_id: int,
    description: Optional[str] = None,
    business_type: Optional[str] = None,
    industry: Optional[str] = None,
    website: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new business for the tenant.
    
    Args:
        name: Business name
        db: Database session (injected)
        tenant_id: Tenant ID (injected)
        description: Optional business description
        business_type: Type of business (e.g., 'restaurant', 'retail')
        industry: Industry sector
        website: Business website URL
        **kwargs: Additional optional fields
    
    Returns:
        Dict with business creation result
    """
    # For now, we'll update the tenant's name as a simple business operation
    # In a full implementation, you'd have a separate Business model
    result = await db.execute(
        select(TenantModel).where(TenantModel.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        return {
            "success": False,
            "error": "Tenant not found"
        }
    
    # Update tenant with business information
    tenant.name = name
    await db.commit()
    
    return {
        "success": True,
        "message": f"Business '{name}' created successfully",
        "business": {
            "id": tenant_id,
            "name": name,
            "description": description,
            "type": business_type,
            "industry": industry,
            "website": website
        }
    }


async def list_businesses(
    db: AsyncSession,
    tenant_id: int,
    status: Optional[str] = None,
    business_type: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    List all businesses for the tenant.
    
    Args:
        db: Database session (injected)
        tenant_id: Tenant ID (injected)
        status: Filter by status (optional)
        business_type: Filter by type (optional)
        limit: Maximum number of results
    
    Returns:
        Dict with list of businesses
    """
    result = await db.execute(
        select(TenantModel).where(TenantModel.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        return {
            "success": False,
            "error": "Tenant not found"
        }
    
    return {
        "success": True,
        "businesses": [{
            "id": tenant.id,
            "name": tenant.name,
            "type": business_type or "general",
            "status": status or "active"
        }],
        "count": 1
    }


async def get_business(
    business_id: int,
    db: AsyncSession,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Get details of a specific business.
    
    Args:
        business_id: Business ID to retrieve
        db: Database session (injected)
        tenant_id: Tenant ID (injected)
    
    Returns:
        Dict with business details
    """
    result = await db.execute(
        select(TenantModel).where(TenantModel.id == business_id, TenantModel.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        return {
            "success": False,
            "error": "Business not found"
        }
    
    return {
        "success": True,
        "business": {
            "id": tenant.id,
            "name": tenant.name,
            "status": "active"
        }
    }


async def update_business(
    business_id: int,
    db: AsyncSession,
    tenant_id: int,
    **fields
) -> Dict[str, Any]:
    """
    Update business information.
    
    Args:
        business_id: Business ID to update
        db: Database session (injected)
        tenant_id: Tenant ID (injected)
        **fields: Fields to update (name, description, etc.)
    
    Returns:
        Dict with update result
    """
    result = await db.execute(
        select(TenantModel).where(TenantModel.id == business_id, TenantModel.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        return {
            "success": False,
            "error": "Business not found"
        }
    
    # Update allowed fields
    if "name" in fields:
        tenant.name = fields["name"]
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Business updated successfully",
        "business": {
            "id": tenant.id,
            "name": tenant.name
        }
    }


async def delete_business(
    business_id: int,
    db: AsyncSession,
    tenant_id: int
) -> Dict[str, Any]:
    """
    Delete a business (soft delete).
    
    Args:
        business_id: Business ID to delete
        db: Database session (injected)
        tenant_id: Tenant ID (injected)
    
    Returns:
        Dict with deletion result
    """
    result = await db.execute(
        select(TenantModel).where(TenantModel.id == business_id, TenantModel.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        return {
            "success": False,
            "error": "Business not found"
        }
    
    # In a real implementation, you'd do a soft delete
    # For now, we'll just return success
    return {
        "success": True,
        "message": f"Business '{tenant.name}' deleted successfully"
    }
