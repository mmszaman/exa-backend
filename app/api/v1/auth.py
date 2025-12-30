from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.core.logger import get_logger
from app.services.user_service import UserService
from app.core.clerk_auth import CurrentUser
from app.schemas.user_schema import User

logger = get_logger("auth")
router = APIRouter()


#################################################
# GET /api/v1/auth/me
# Get current authenticated user information
@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: CurrentUser
):
    return User(
        id=current_user.id,
        clerk_user_id=current_user.clerk_user_id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        phone_number=current_user.phone_number,
        is_active=current_user.is_active,
        role=current_user.role,
        lead_source=current_user.lead_source,
        brand=current_user.brand,
        referral_code=current_user.referral_code,
        utm_source=current_user.utm_source,
        utm_medium=current_user.utm_medium,
        utm_campaign=current_user.utm_campaign,
        newsletter=current_user.newsletter,
        email_notifications=current_user.email_notifications,
        marketing_emails=current_user.marketing_emails,
        metadata=current_user.metadata,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login_at=current_user.last_login_at
    )


#################################################
# GET /api/v1/auth/health
# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "ok", "auth_provider": "clerk"}
