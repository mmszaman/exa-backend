from typing import Optional, Annotated
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import requests  # type: ignore
from app.core.database import get_db
from app.core.config import settings
from app.core.logger import get_logger
from app.models.user import UserModel

logger = get_logger("clerk_auth")

# Cache for JWKS (JSON Web Key Set)
_jwks_cache = None

# Get JWKS for token verification
def get_clerk_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        jwks_url = "https://clerk.exateks.com/.well-known/jwks.json"
        
        # For development with Clerk's default domain
        if settings.CLERK_PUBLISHABLE_KEY.startswith("pk_test_"):
            jwks_url = "https://api.clerk.dev/v1/jwks"
        
        try:
            response = requests.get(jwks_url, headers={
                "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"
            })
            response.raise_for_status()
            _jwks_cache = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            raise
    return _jwks_cache

# Get user from request
# Input: Request; Output: User > user_id, session_id
async def get_clerk_user_from_request(request: Request) -> dict:
    try:
        # Get authorization header or session cookie
        auth_header = request.headers.get("authorization", "")
        session_token = None
        
        if auth_header.startswith("Bearer "):
            session_token = auth_header.replace("Bearer ", "")
        else:
            session_token = request.cookies.get("__session")
        
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authentication token provided"
            )
        
        # Decode JWT (TODO: verify signature against JWKS in production)
        payload = jwt.decode(
            session_token,
            options={"verify_signature": False}  # Temporary for testing
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not extract user information from token"
            )
        
        org_id = payload.get("org_id")
        logger.info(f"Authenticated user: {user_id}, org: {org_id}")
        
        return {
            "user_id": user_id,
            "session_id": payload.get("sid"),
        }
        
    except jwt.DecodeError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

# Get current user ID from request
# Input: Request; Output: user_id str
async def get_current_user_id(request: Request) -> str:
    clerk_user = await get_clerk_user_from_request(request)
    return clerk_user["user_id"]
    clerk_user = await get_clerk_user_from_request(request)
    tenant_id = clerk_user.get("org_id")
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires organization context. Please select or create an organization."
        )
    
    return tenant_id

# Get current user from request and database
# Input: Request, DB session; Output: UserModel
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
        try:
            clerk_client = Clerk(bearer_auth=settings.CLERK_SECRET_KEY)
            clerk_user_data = clerk_client.users.get(user_id=user_id)
            
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


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]
