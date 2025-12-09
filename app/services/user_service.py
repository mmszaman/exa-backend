from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.lead import Lead
from app.core.security import get_password_hash, verify_password, generate_verification_token, get_token_expiry
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.schemas.user_schema import UserSignupRequest

class UserService:

    @staticmethod
    #Check token, verification status, user status > create user > delete lead
    #param: signup data and url token
    async def user_signup_srv (db: AsyncSession, signup_data: UserSignupRequest, url_token: str) -> User:
        """Complete signup by creating user after email verification."""
        # Verify token and get lead
        result = await db.execute(
            select(Lead).where(Lead.verification_token == signup_data.verification_token)
        )
        lead = result.scalar_one_or_none()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        # Validate URL token matches lead token
        if url_token != lead.verification_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token mismatch. URL token does not match lead token."
            )
        
        if not lead.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not verified. Please verify your email first."
            )
        
        # Check if token expired
        if lead.token_expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please request a new one."
            )
        
        # Check if username already taken
        username_result = await db.execute(
            select(User).where(User.username == signup_data.username)
        )
        if username_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Check if email already in users (extra safety)
        user_result = await db.execute(
            select(User).where(User.email == lead.email)
        )
        if user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists with this email"
            )
        
        # Create user (already verified since email was verified)
        user = User(
            email=lead.email,
            username=signup_data.username,
            hashed_password=get_password_hash(signup_data.password),
            full_name=signup_data.full_name,
            is_verified=True,  # Already verified via lead
            newsletter=lead.newsletter  # Transfer newsletter preference from lead
        )
        
        db.add(user)
        
        # Delete lead record (cleanup)
        await db.delete(lead)
        
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    #Get user by ID
    #param: user_id
    async def get_user_by_id_srv(db: AsyncSession, user_id: int) -> User:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


    @staticmethod
    #Authenticate user by email and password
    #param: email and password
    async def authenticate_user_srv (db: AsyncSession, email: str, password: str) -> User:
        """Authenticate user by email and password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        return user

    @staticmethod
    async def request_password_reset_srv(db: AsyncSession, email: str) -> User:
        """Generate password reset token for user."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists - security best practice
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="If this email exists, a password reset link has been sent"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Generate reset token (valid for 1 hour)
        user.reset_token = generate_verification_token()
        user.reset_token_expiry = get_token_expiry(hours=1)
        
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def verify_reset_token_srv(db: AsyncSession, token: str) -> User:
        """Verify password reset token is valid."""
        result = await db.execute(select(User).where(User.reset_token == token))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired reset token"
            )
        
        # Check if token expired
        if user.reset_token_expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired. Please request a new one"
            )
        
        return user

    @staticmethod
    async def reset_password_srv(db: AsyncSession, token: str, new_password: str) -> User:
        """Reset user password using valid reset token."""
        # Verify token
        user = await UserService.verify_reset_token_srv(db, token)
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Clear reset token
        user.reset_token = None
        user.reset_token_expiry = None
        
        await db.commit()
        await db.refresh(user)
        return user
