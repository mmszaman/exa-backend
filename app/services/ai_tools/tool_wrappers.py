"""
Tool wrappers that hide injected parameters from LangChain schema generation.
These wrappers only expose user-facing parameters to the AI.
"""
from typing import Optional, Dict, Any, List
from langchain.tools import tool
from sqlalchemy.ext.asyncio import AsyncSession


# Business tools wrappers
@tool
async def create_business_wrapper(
    name: str,
    business_type: Optional[str] = None,
    description: Optional[str] = None,
    address: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    country: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None,
    industry: Optional[str] = None,
    established_date: Optional[str] = None,
    employee_count: Optional[int] = None,
    annual_revenue: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Create a new business for the current tenant.
    
    Args:
        name: Business name (required)
        business_type: Type of business (e.g., restaurant, retail, service)
        description: Business description
        address: Street address
        city: City name
        state: State/province
        zip_code: ZIP/postal code
        phone: Business phone number
        email: Business email
        website: Business website URL
        industry: Industry category
        established_date: Date business was established (YYYY-MM-DD)
        employee_count: Number of employees
        annual_revenue: Annual revenue amount
    """
    # This will be replaced at runtime
    pass


@tool
async def list_businesses_wrapper(
    status: Optional[str] = None,
    business_type: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    List all businesses for the current tenant.
    
    Args:
        status: Filter by status (active/inactive)
        business_type: Filter by business type
        limit: Maximum number of results to return
    """
    pass


@tool
async def get_business_wrapper(
    business_id: str,
) -> Dict[str, Any]:
    """
    Get details of a specific business.
    
    Args:
        business_id: The unique ID of the business
    """
    pass


@tool
async def update_business_wrapper(
    business_id: str,
    name: Optional[str] = None,
    business_type: Optional[str] = None,
    description: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update a business's information.
    
    Args:
        business_id: The unique ID of the business
        name: New business name
        business_type: New business type
        description: New description
        phone: New phone number
        email: New email
        website: New website
    """
    pass


@tool
async def delete_business_wrapper(
    business_id: str,
) -> Dict[str, Any]:
    """
    Delete a business (soft delete).
    
    Args:
        business_id: The unique ID of the business to delete
    """
    pass


# Tenant tools wrappers
@tool
async def list_tenants_wrapper() -> Dict[str, Any]:
    """
    List all tenants/organizations the user belongs to.
    Returns tenants sorted by primary status.
    """
    pass


@tool
async def get_current_tenant_wrapper() -> Dict[str, Any]:
    """
    Get information about the current active tenant/organization.
    """
    pass


@tool
async def set_primary_tenant_wrapper(
    tenant_id: int,
) -> Dict[str, Any]:
    """
    Set a tenant as the user's primary organization.
    
    Args:
        tenant_id: The ID of the tenant to set as primary
    """
    pass


@tool
async def get_tenant_info_wrapper(
    tenant_id: int,
) -> Dict[str, Any]:
    """
    Get detailed information about a specific tenant.
    
    Args:
        tenant_id: The ID of the tenant
    """
    pass
