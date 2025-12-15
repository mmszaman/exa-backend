from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import UserModel
from app.models.lead import LeadModel
from app.core.security import get_password_hash, verify_password, generate_verification_token, get_token_expiry
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.schemas.user_schema import *

from app.core.security import (
    generate_verification_token,
    get_token_expiry,
    get_password_hash
)

class UserService:

    # Create lead with email and send verification token
    # param: signup data; returns: LeadModel
    @staticmethod
    async def create_lead_srv (db: AsyncSession, signup_data: SignupData) -> LeadModel:
        email = signup_data.email.lower()
        
        # Check if email already exists in users table
        user_result = await db.execute(select(UserModel).where(UserModel.email == email))
        if user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if lead already exists
        lead_result = await db.execute(select(LeadModel).where(LeadModel.email == email))
        existing_lead = lead_result.scalar_one_or_none()
        
        if existing_lead:
            # If lead exists but not verified, update token
            if not existing_lead.is_verified:
                existing_lead.verification_token = generate_verification_token()
                existing_lead.token_expiry = get_token_expiry(24)
                existing_lead.newsletter = signup_data.newsletter
                await db.commit()
                await db.refresh(existing_lead)
                return existing_lead
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already verified. Please complete registration."
                )
        
        # Create new lead
        lead = LeadModel(
            email=email,
            verification_token=generate_verification_token(),
            token_expiry=get_token_expiry(24),
            newsletter=signup_data.newsletter
        )
        
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        return lead

    #Verify email with token and mark as verified
    # param: token only; returns: LeadModel
    @staticmethod
    async def verify_lead_email_srv (db: AsyncSession, token: str) -> LeadModel:
        """Verify email with token."""
        result = await db.execute(
            select(LeadModel).where(LeadModel.verification_token == token)
        )
        lead = result.scalar_one_or_none()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        # Check if already verified
        if lead.is_verified:
            return lead
        
        # Check if token expired
        if lead.token_expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired. Please request a new one."
            )
        
        # Mark as verified
        lead.is_verified = True
        await db.commit()
        await db.refresh(lead)
        return lead   
    
    # Resend verification email by generating new token
    # param: email only; returns: LeadModel
    @staticmethod
    async def resend_lead_verification_srv (db: AsyncSession, email: str) -> LeadModel:
        """Resend verification email by generating new token."""
        email = email.lower()
        
        result = await db.execute(select(LeadModel).where(LeadModel.email == email))
        lead = result.scalar_one_or_none()
        
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found. Please start signup process."
            )
        
        if lead.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified. Please complete registration."
            )
        
        # Generate new token
        lead.verification_token = generate_verification_token()
        lead.token_expiry = get_token_expiry(24)
        
        await db.commit()
        await db.refresh(lead)
        return lead

    # Check token, verification status, user status > create user > delete lead
    # param: signup data and url token
    @staticmethod
    async def user_signup_srv (db: AsyncSession, user_data: UserData, url_token: str) -> UserModel:
        """Complete signup by creating user after email verification."""
        # Verify token and get lead
        result = await db.execute(
            select(LeadModel).where(LeadModel.verification_token == user_data.verification_token)
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
            select(UserModel).where(UserModel.username == user_data.username)
        )
        if username_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Check if email already in users (extra safety)
        user_result = await db.execute(
            select(UserModel).where(UserModel.email == lead.email)
        )
        if user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists with this email"
            )
        
        # Create user (already verified since email was verified)
        user = UserModel(
            email=lead.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            is_verified=True,  # Already verified via lead
            newsletter=lead.newsletter  # Transfer newsletter preference from lead
        )
        db.add(user)
        await db.delete(lead)
        await db.commit()
        await db.refresh(user)
        return user

    # Authenticate user by email and password
    # param: email and password; returns: UserModel (only if active and verified)
    @staticmethod
    async def authenticate_user_srv (db: AsyncSession, email: str, password: str) -> UserModel:
        """Authenticate user by email and password."""
        result = await db.execute(select(UserModel).where(UserModel.email == email))
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

    # Get user by email
    # param: user_email only; returns: UserModel
    @staticmethod
    async def get_user_by_email_srv(db: AsyncSession, user_email: str) -> UserModel:
        result = await db.execute(select(UserModel).where(UserModel.email == user_email))
        return result.scalar_one_or_none()

    # Request password reset by generating OTP
    # param: email only; returns: UserModel
    @staticmethod
    async def request_password_reset_srv(db: AsyncSession, email: str) -> UserModel:
        """Generate password reset OTP for user."""
        from app.core.security import generate_otp, get_otp_expiry
        
        result = await db.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if email exists - security best practice
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="If this email exists, an OTP has been sent"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Generate 4-digit OTP (valid for 10 minutes)
        user.reset_otp = generate_otp()
        user.reset_otp_expiry = get_otp_expiry(minutes=10)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    # Verify OTP only
    # param: email and otp; returns: UserModel
    @staticmethod
    async def verify_otp_srv(db: AsyncSession, email: str, otp: str) -> UserModel:
        """Verify OTP only."""
        result = await db.execute(select(UserModel).where(UserModel.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or OTP"
            )
        
        if not user.reset_otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No OTP request found. Please request a new OTP"
            )
        
        # Check if OTP expired
        if user.reset_otp_expiry < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one"
            )
        
        # Verify OTP
        if user.reset_otp != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        return user

    # Reset password using OTP
    # param: email, otp, new_password; returns: UserModel
    @staticmethod
    async def reset_password_with_otp_srv(db: AsyncSession, email: str, otp: str, new_password: str) -> UserModel:
        """Reset user password using OTP."""
        # Verify OTP first
        user = await UserService.verify_otp_srv(db, email, otp)
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Clear OTP
        user.reset_otp = None
        user.reset_otp_expiry = None
        
        await db.commit()
        await db.refresh(user)
        return user

    # Update user's refresh token
    # param: user_email and refresh_token; returns: None
    @staticmethod
    async def update_refresh_token_srv(db: AsyncSession, user_email: str, refresh_token: Optional[str]) -> None:
        """Update user's refresh token."""
        user = await UserService.get_user_by_email_srv(db, user_email)
        if user:
            user.refresh_token = refresh_token
            await db.commit()
