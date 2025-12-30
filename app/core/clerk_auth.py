# Authentication and authorization utilities for Clerk integration
from typing import Optional
from fastapi import Request, HTTPException, status
import jwt
import requests
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("clerk_auth")

# Cache for JWKS (JSON Web Key Set)
_jwks_cache = None


def get_clerk_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        # Extract instance from publishable key (format: pk_test_xxx or pk_live_xxx)
        # For production, Clerk uses clerk.{your-domain}.com
        jwks_url = "https://clerk.smb-hub.dev/.well-known/jwks.json"
        
        # For development with Clerk's default domain
        if settings.CLERK_PUBLISHABLE_KEY.startswith("pk_test_"):
            # Use Clerk's development JWKS endpoint
            jwks_url = f"https://api.clerk.dev/v1/jwks"
        
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


async def get_clerk_user_from_request(request: Request) -> dict:
    try:
        # Get authorization header or session cookie
        auth_header = request.headers.get("authorization", "")
        session_token = None
        
        # Try to get token from Authorization header
        if auth_header.startswith("Bearer "):
            session_token = auth_header.replace("Bearer ", "")
        else:
            # Try to get from cookie (Clerk's default cookie name)
            session_token = request.cookies.get("__session")
        
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authentication token provided"
            )
        
        # Decode JWT without verification first to get the header
        unverified_header = jwt.get_unverified_header(session_token)
        
        # For now, decode without full verification (simplified for initial setup)
        # In production, verify against JWKS
        payload = jwt.decode(
            session_token,
            options={"verify_signature": False}  # Temporary for testing
        )
        
        # Extract user and organization information
        user_id = payload.get("sub")  # Subject is the user ID
        org_id = payload.get("org_id")  # Organization ID (tenant)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not extract user information from token"
            )
        
        logger.info(f"Authenticated user: {user_id}, org: {org_id}")
        
        return {
            "user_id": user_id,
            "org_id": org_id,  # Maps to tenant_id in our system
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


async def get_tenant_id_from_request(request: Request) -> Optional[str]:
    clerk_user = await get_clerk_user_from_request(request)
    return clerk_user.get("org_id")


async def require_tenant_context(request: Request) -> str:
    tenant_id = await get_tenant_id_from_request(request)
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires organization context. Please select or create an organization."
        )
    
    return tenant_id
