"""
User Service for Clerk Authentication Integration
Handles user synchronization between Clerk and local database.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import UserModel
from fastapi import HTTPException, status
from typing import Optional


class UserService:
    """Service for managing users with Clerk authentication."""
    
    @staticmethod
    async def get_user_by_clerk_id(db: AsyncSession, clerk_user_id: str) -> Optional[UserModel]:
        """Get user by Clerk user ID."""
        result = await db.execute(
            select(UserModel).where(UserModel.clerk_user_id == clerk_user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
        """Get user by email."""
        result = await db.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_from_clerk(
        db: AsyncSession,
        clerk_user_id: str,
        email: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        tenant_id: Optional[str] = None,
        role: str = "member",
        lead_source: Optional[str] = None,
        brand: Optional[str] = None,
        referral_code: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        newsletter: bool = False,
        clerk_metadata: Optional[str] = None
    ) -> UserModel:
        """
        Create a user from Clerk data.
        Used for auto-provisioning when a Clerk user first accesses the system.
        """
        # Check if user already exists
        existing = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        if existing:
            return existing
        
        # Check for email conflicts
        email_conflict = await UserService.get_user_by_email(db, email)
        if email_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists"
            )
        
        # Create new user
        user = UserModel(
            clerk_user_id=clerk_user_id,
            email=email.lower(),
            username=username or email.split('@')[0],
            full_name=full_name,
            avatar_url=avatar_url,
            phone_number=phone_number,
            tenant_id=tenant_id,
            role=role,
            lead_source=lead_source,
            brand=brand,
            referral_code=referral_code,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            is_active=True,
            newsletter=newsletter,
            clerk_metadata=clerk_metadata
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update_from_clerk(
        db: AsyncSession,
        clerk_user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        tenant_id: Optional[str] = None,
        clerk_metadata: Optional[str] = None
    ) -> UserModel:
        """Update user from Clerk webhook data."""
        user = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        if email is not None:
            user.email = email.lower()
        if username is not None:
            user.username = username
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        if phone_number is not None:
            user.phone_number = phone_number
        if tenant_id is not None:
            user.tenant_id = tenant_id
        if clerk_metadata is not None:
            user.clerk_metadata = clerk_metadata
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, clerk_user_id: str) -> bool:
        """Delete user (called from Clerk webhook)."""
        user = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, clerk_user_id: str) -> UserModel:
        """Deactivate user account."""
        user = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def activate_user(db: AsyncSession, clerk_user_id: str) -> UserModel:
        """Activate user account."""
        user = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        await db.commit()
        await db.refresh(user)
        return user
