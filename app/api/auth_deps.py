# FastAPI dependencies for authentication and user retrieval using Clerk
from typing import Optional, Annotated
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.core.logger import get_logger
from app.core.clerk_auth import (
    get_clerk_user_from_request,
    get_tenant_id_from_request,
    require_tenant_context
)
from app.models.user import UserModel

logger = get_logger("deps")


async def get_current_user_id(request: Request) -> str:
    clerk_user = await get_clerk_user_from_request(request)
    return clerk_user["user_id"]


async def get_current_tenant_id(request: Request) -> Optional[str]:
    return await get_tenant_id_from_request(request)


async def get_required_tenant_id(request: Request) -> str:
    return await require_tenant_context(request)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    
    from app.services.user_service import UserService
    from clerk_backend_api import Clerk
    
    clerk_user = await get_clerk_user_from_request(request)
    user_id = clerk_user["user_id"]
    
    # Try to get user from database
    user = await UserService.get_user_by_clerk_id(db, user_id)
    
    # Auto-provision user if not exists (will be synced via webhook)
    if not user:
        # Fetch user details from Clerk
        try:
            clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
            clerk_user_data = clerk_client.users.get(user_id=user_id)
            
            # Create user record
            user = await UserService.create_from_clerk(
                db=db,
                clerk_user_id=user_id,
                email=clerk_user_data.email_addresses[0].email_address if clerk_user_data.email_addresses else f"user_{user_id}@temp.com",
                username=clerk_user_data.username or user_id[:8],
                full_name=f"{clerk_user_data.first_name or ''} {clerk_user_data.last_name or ''}".strip() or None,
            )
        except Exception as e:
            logger.error(f"Failed to provision user from Clerk: {str(e)}")
            # Create minimal user record
            user = await UserService.create_from_clerk(
                db=db,
                clerk_user_id=user_id,
                email=f"user_{user_id}@temp.com",
                username=user_id[:8],
                full_name=None,
            )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


# Type aliases for dependency injection
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentTenantId = Annotated[Optional[str], Depends(get_current_tenant_id)]
RequiredTenantId = Annotated[str, Depends(get_required_tenant_id)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]
