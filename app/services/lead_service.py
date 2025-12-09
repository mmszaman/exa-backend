from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.lead import Lead
from app.models.user import User
from app.core.security import (
    generate_verification_token,
    get_token_expiry,
    get_password_hash
)
from app.schemas.lead_schema import EmailSignupRequest
from fastapi import HTTPException, status
from datetime import datetime, timezone

class LeadService:
    @staticmethod
    #Create lead with email and send verification token
    #param: email only
    async def create_lead_srv (db: AsyncSession, email_data: EmailSignupRequest) -> Lead:
        """Create new lead with verification token."""
        email = email_data.email.lower()
        
        # Check if email already exists in users table
        user_result = await db.execute(select(User).where(User.email == email))
        if user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if lead already exists
        lead_result = await db.execute(select(Lead).where(Lead.email == email))
        existing_lead = lead_result.scalar_one_or_none()
        
        if existing_lead:
            # If lead exists but not verified, update token
            if not existing_lead.is_verified:
                existing_lead.verification_token = generate_verification_token()
                existing_lead.token_expiry = get_token_expiry(24)
                existing_lead.newsletter = email_data.newsletter
                await db.commit()
                await db.refresh(existing_lead)
                return existing_lead
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already verified. Please complete registration."
                )
        
        # Create new lead
        lead = Lead(
            email=email,
            verification_token=generate_verification_token(),
            token_expiry=get_token_expiry(24),
            newsletter=email_data.newsletter
        )
        
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        return lead


    @staticmethod
    #Verify email with token and mark as verified
    #param: token only. only call automatically from verify endpoint
    async def verify_lead_email_srv (db: AsyncSession, token: str) -> Lead:
        """Verify email with token."""
        result = await db.execute(
            select(Lead).where(Lead.verification_token == token)
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
    
    
    @staticmethod
    #Resend verification email by generating new token
    #param: email only
    async def resend_lead_verification_srv (db: AsyncSession, email: str) -> Lead:
        """Resend verification email by generating new token."""
        email = email.lower()
        
        result = await db.execute(select(Lead).where(Lead.email == email))
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
