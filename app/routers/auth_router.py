from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.lead_schema import (
    EmailSignupRequest,
    EmailSignupResponse,
    ResendVerificationRequest,
    VerifySignupTokenResponse
)
from app.schemas.user_schema import (
    UserResponse, 
    UserLoginRequest, 
    TokenResponse, 
    UserSignupRequest, 
    ValidateAccessTokenRequest,
    ForgotPasswordRequest,
    VerifyResetTokenRequest,
    ResetPasswordRequest,
    PasswordResetResponse
)
from app.services.lead_service import LeadService
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.services.email_render import template_service
from app.core.security import create_access_token, decode_access_token
from app.config import settings
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/request-signup", response_model=EmailSignupResponse, status_code=status.HTTP_201_CREATED)
#LeadService.create_lead() > EmailService.send_email() for email verification
#Param: email only
async def request_signup(
    email_data: EmailSignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Step 1: Request signup with email only."""
    lead = await LeadService.create_lead_srv(db, email_data)
    
    # Send verification email_link points to backend API which will verify and redirect
    verification_link = f"{settings.BACKEND_ORIGINS}/api/auth/verify-email/{lead.verification_token}"
    
    try:
        # Render template
        body_html, body_text = template_service.render_template(
            template_name="verify_email",
            context={
                "username": lead.email.split('@')[0],  # Use email prefix as temporary name
                "verification_link": verification_link
            }
        )
        
        # Send email
        await EmailService.send_email(
            recipients=[lead.email],
            subject="Verify Your Email - ExaKeep",
            body_text=body_text,
            body_html=body_html,
            from_name="ExaKeep"
        )
    except Exception as e:
        # Log error but don't fail
        print(f"Failed to send verification email: {e}")
    
    return EmailSignupResponse(
        message="Verification email sent. Please check your inbox.",
        email=lead.email
    )


@router.get("/verify-email/{token}")
#LeadService.verify_email() > RedirectResponse to frontend signup page
#Param: token in URL
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Step 2: Verify email with token and redirect to registration page."""
    lead = await LeadService.verify_lead_email_srv(db, token)
    
    # Redirect to frontend registration page with token
    registration_url = f"{settings.FRONTEND_ORIGINS.split(',')[0]}/auth/complete-signup?token={lead.verification_token}"
    return RedirectResponse(url=registration_url, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/validate-token/{token}", response_model=VerifySignupTokenResponse)
#LeadService.verify_email() > Return token validation status
#Param: token in URL
async def validate_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate registration token before showing complete-signup form."""
    lead = await LeadService.verify_lead_email_srv(db, token)
    
    return VerifySignupTokenResponse(
        message="Token is valid. Please complete your registration.",
        email=lead.email,
        verification_token=lead.verification_token,
        is_verified=lead.is_verified,
        token_expiry=lead.token_expiry
    )


@router.post("/complete-signup/{token}", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
#UserService.user_signup() > EmailService.send_email() for welcome and admin notification
#Param: token in URL, signup data in body
async def complete_signup(
    token: str,
    signup_data: UserSignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Step 3: Complete signup after email verification."""
    # Validate that URL token matches request body token
    if token != signup_data.verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token mismatch. URL token does not match request token."
        )
    
    user = await UserService.user_signup_srv (db, signup_data, token)
    
    # Send welcome email to user
    try:
        welcome_html, welcome_text = template_service.render_template(
            template_name="welcome",
            context={
                "user_name": user.full_name or user.username,
                "company_name": "ExaKeep"
            }
        )
        await EmailService.send_email(
            recipients=[user.email],
            subject="Welcome to ExaKeep!",
            body_text=welcome_text,
            body_html=welcome_html,
            from_name="ExaKeep"
        )
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    
    # Send notification to admin
    try:
        admin_html, admin_text = template_service.render_template(
            template_name="admin_notification",
            context={
                "title": "New User Registration",
                "user_email": user.email,
                "email_purpose": f"New user {user.username} ({user.full_name}) has successfully registered."
            }
        )
        await EmailService.send_email(
            recipients=[settings.ADMIN_TO],
            subject="New User Registration - ExaKeep",
            body_text=admin_text,
            body_html=admin_html,
            from_name="ExaKeep System"
        )
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/resend-verification", response_model=EmailSignupResponse)
#LeadService.resend_verification() > EmailService.send_email() for email verification
#Param: email only
async def resend_verification(
    resend_data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email if token expired or email lost."""
    lead = await LeadService.resend_verification(db, resend_data.email)
    
    # Send verification email - link points to backend API which will verify and redirect
    verification_link = f"{settings.BACKEND_ORIGINS}/api/auth/verify-email/{lead.verification_token}"
    
    try:
        # Render template
        body_html, body_text = template_service.render_template(
            template_name="verify_email",
            context={
                "username": lead.email.split('@')[0],
                "verification_link": verification_link
            }
        )
        
        # Send email
        await EmailService.send_email(
            recipients=[lead.email],
            subject="Verify Your Email - ExaKeep",
            body_text=body_text,
            body_html=body_html,
            from_name="ExaKeep"
        )
        
        return EmailSignupResponse(
            message="Verification email resent successfully.",
            email=lead.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
#UserService.authenticate_user() > create_access_token()
#Param: email and password
async def login(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token."""
    user = await UserService.authenticate_user_srv(db, login_data.email, login_data.password)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/validate-access-token")
#Decode token, check user status in DB
#Param: token in body
async def validate_access_token(
    request: ValidateAccessTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Validate JWT access token and return user information."""
    # Decode and validate token
    payload = decode_access_token(request.token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    
    # Extract user info from token
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user still exists in database
    user = await UserService.get_user_by_id_srv(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return {
        "valid": True,
        "user": UserResponse.model_validate(user)
    }


@router.post("/refresh-token", response_model=TokenResponse)
#Decode old token, verify user, issue new token with extended expiry
#Param: Authorization header with Bearer token
async def refresh_token(
    request: ValidateAccessTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token by issuing a new token with extended expiry.
    
    This endpoint should be called when the current token is about to expire.
    It validates the old token and issues a new one with a fresh 7-day expiry.
    """
    # Decode and validate the current token
    payload = decode_access_token(request.token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )
    
    # Extract user info from token
    email = payload.get("sub")
    user_id = payload.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user still exists and is active
    user = await UserService.get_user_by_id_srv(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create new access token with fresh expiry (7 days)
    new_access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=new_access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/forgot-password", response_model=PasswordResetResponse)
#UserService.request_password_reset_srv() > EmailService.send_email()
#Param: email only
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset by email.
    Sends a password reset link to the user's email if account exists.
    """
    user = await UserService.request_password_reset_srv(db, request.email)
    
    # Send password reset email
    reset_link = f"{settings.FRONTEND_ORIGINS.split(',')[0]}/auth/reset-password?token={user.reset_token}"
    
    try:
        body_html, body_text = template_service.render_template(
            template_name="password_reset",
            context={
                "user_name": user.full_name or user.username,
                "company_name": "ExaKeep",
                "reset_url": reset_link,
                "expiry_hours": "1"
            }
        )
        
        await EmailService.send_email(
            recipients=[user.email],
            subject="Reset Your Password - ExaKeep",
            body_text=body_text,
            body_html=body_html,
            from_name="ExaKeep Security"
        )
        
        return PasswordResetResponse(
            message="Password reset email sent successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send password reset email: {str(e)}"
        )


@router.post("/verify-reset-token")
#UserService.verify_reset_token_srv()
#Param: token in body
async def verify_reset_token(
    request: VerifyResetTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify that password reset token is valid and not expired.
    Returns user email if token is valid.
    """
    user = await UserService.verify_reset_token_srv(db, request.token)
    
    return {
        "valid": True,
        "email": user.email
    }


@router.post("/reset-password", response_model=PasswordResetResponse)
#UserService.reset_password_srv() > create_access_token() for auto-login
#Param: token and new_password in body
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset user password using valid reset token.
    Returns new access token for automatic login after password reset.
    """
    user = await UserService.reset_password_srv(db, request.token, request.new_password)
    
    # Create access token for automatic login
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )
    
    return PasswordResetResponse(
        message="Password reset successfully",
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )
