
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models.user import UserModel
from fastapi import HTTPException, status
from typing import Optional
from app.core.logger import get_logger

logger = get_logger("user_service")


class UserService:
    
    # Get user by Clerk user ID
    # Input: DB session, clerk_user_id str; Output: UserModel or None
    @staticmethod
    async def get_user_by_clerk_id(db: AsyncSession, clerk_user_id: str) -> Optional[UserModel]:
        result = await db.execute(
            select(UserModel).where(UserModel.clerk_user_id == clerk_user_id)
        )
        return result.scalar_one_or_none()
    

    # Get user by email
    # Input: DB session, email str; Output: UserModel or None
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserModel]:
        """Get user by email."""
        result = await db.execute(
            select(UserModel).where(UserModel.email == email.lower())
        )
        return result.scalar_one_or_none()
    

    # Create user from Clerk data
    # Input: DB session, clerk_user_id str, email str, optional fields; Output: UserModel
    @staticmethod
    async def create_user(
        db: AsyncSession,
        clerk_user_id: str,
        email: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        lead_source: Optional[str] = None,
        brand: Optional[str] = None,
        referral_code: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        newsletter: bool = False,
        clerk_metadata: Optional[str] = None
    ) -> tuple[UserModel, bool]:
        """Create user or reactivate existing user. Returns (user, was_reactivated)."""
        # Check if user already exists by Clerk ID (handle retries)
        existing = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        if existing:
            # Reactivate if they were deactivated
            if not existing.is_active:
                from datetime import datetime, timezone
                existing.is_active = True
                # Update last_login_at on reactivation
                existing.last_login_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(existing)
                logger.info(f"Reactivated user: {clerk_user_id}")
                return existing, True  # Return True for reactivation
            return existing, False  # Already active, just return
        
        # Check for email conflicts - if inactive user exists, reactivate with new clerk_user_id
        email_conflict = await UserService.get_user_by_email(db, email)
        if email_conflict:
            if not email_conflict.is_active:
                # User was deleted from Clerk and is re-signing up with new clerk_user_id
                # Update clerk_user_id and reactivate
                from datetime import datetime, timezone
                email_conflict.clerk_user_id = clerk_user_id
                email_conflict.is_active = True
                email_conflict.last_login_at = datetime.now(timezone.utc)
                # Update other fields
                if username:
                    email_conflict.username = username
                if full_name:
                    email_conflict.full_name = full_name
                if avatar_url:
                    email_conflict.avatar_url = avatar_url
                if phone_number:
                    email_conflict.phone_number = phone_number
                if clerk_metadata:
                    email_conflict.clerk_metadata = clerk_metadata
                await db.commit()
                await db.refresh(email_conflict)
                logger.info(f"Reactivated user by email with new clerk_user_id: {email} -> {clerk_user_id}")
                return email_conflict, True  # Return True for reactivation
            else:
                # Active user with this email already exists
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
        return user, False  # Return False for new user
    

    # Create user from Clerk data (simplified auto-provision)
    # Input: DB session, clerk_user_id str, email str, optional fields; Output: UserModel
    @staticmethod
    async def create_from_clerk(
        db: AsyncSession,
        clerk_user_id: str,
        email: str,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> UserModel:
        """Create user from Clerk data during auto-provisioning."""
        user, _ = await UserService.create_user(
            db=db,
            clerk_user_id=clerk_user_id,
            email=email,
            username=username,
            full_name=full_name,
            avatar_url=avatar_url,
            phone_number=phone_number
        )
        logger.info(f"Auto-provisioned user from Clerk: {clerk_user_id}")
        return user
    

    # Update user from Clerk data
    # Input: DB session, clerk_user_id str, optional fields; Output: UserModel
    @staticmethod
    async def update_user(
        db: AsyncSession,
        clerk_user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        phone_number: Optional[str] = None,
        clerk_metadata: Optional[str] = None
    ) -> UserModel:
        
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
        if clerk_metadata is not None:
            user.clerk_metadata = clerk_metadata
        
        await db.commit()
        await db.refresh(user)
        return user
    

    # Delete user by Clerk user ID
    # Input: DB session, clerk_user_id str; Output: bool
    @staticmethod
    async def delete_user(db: AsyncSession, clerk_user_id: str) -> bool:
        """Delete user (called from Clerk webhook)."""
        user = await UserService.get_user_by_clerk_id(db, clerk_user_id)
        
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False
    

    # Deactivate user account
    # Input: DB session, clerk_user_id str; Output: UserModel
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
    

    # Activate user account
    # Input: DB session, clerk_user_id str; Output: UserModel
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
    

    # Update last login timestamp
    # Input: DB session, user_id int; Output: None
    @staticmethod
    async def update_last_login(db: AsyncSession, user_id: int) -> None:
        """Update user's last login timestamp."""
        from datetime import datetime, timezone
        from app.core.logger import get_logger
        logger = get_logger("user_service")
        
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Updated last_login_at for user_id: {user_id} to {user.last_login_at}")
        else:
            logger.warning(f"User not found for updating last_login_at: user_id={user_id}")
