
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Header, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.rate_limit import limiter, get_email_identifier
from app.schemas.user_schema import *
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.services.email_render import template_service
from app.core.security import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token, generate_csrf_token
from app.core.config import settings
from datetime import timedelta

router = APIRouter()

#################################################
#Param: response, access token, refresh token (optional)
def set_auth_cookies(response: Response, access_token: str, refresh_token: Optional[str] = None):
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    
    # Set httpOnly cookie for access token (15 minutes)
    response.set_cookie(
        key="exa_access_token",
        value=access_token,
        max_age=60 * 30,  # 30 minutes
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        path="/"
    )
    
    # Set httpOnly cookie for refresh token (7 days)
    if refresh_token:
        response.set_cookie(
            key="exa_refresh_token",
            value=refresh_token,
            max_age=60 * 60 * 24 * 7,  # 7 days
            httponly=True,
            secure=settings.APP_ENV == "production",
            samesite="lax",
            path="/"
        )
    
    # Set non-httpOnly cookie for CSRF token (accessible to JavaScript)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=60 * 60 * 24 * 7,  # 7 days
        httponly=False,  # JavaScript needs to read this
        secure=settings.APP_ENV == "production",
        samesite="lax",
        path="/"
    )

#################################################
# POST /api/v1/auth/request-signup
# Input: email, newsletter; Output: message, email
@router.post("/request-signup", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def request_signup(
    signup_data: SignupData,
    db: AsyncSession = Depends(get_db)
):
    """Step 1: Request signup with email only."""
    lead = await UserService.create_lead_srv(db, signup_data)
    
    # Send verification email_link points to backend API which will verify and redirect
    verification_link = f"{settings.BACKEND_ORIGINS}/api/v1/auth/verify-email/{lead.verification_token}"
    
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
            subject="Verify Your Email - Exakeep",
            body_text=body_text,
            body_html=body_html,
            from_name="Exakeep"
        )
    except Exception as e:
        # Log error but don't fail
        print(f"Failed to send verification email: {e}")
    
    return EmailResponse(
        message="Verification email sent. Please check your inbox.",
        email=lead.email
    )

#################################################
# GET /api/v1/auth/verify-email/{token}
# Output: RedirectResponse to frontend complete-signup page
@router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Step 2: Verify email with token and redirect to registration page."""
    lead = await UserService.verify_lead_email_srv(db, token)
    
    # Redirect to frontend registration page with token
    registration_url = f"{settings.FRONTEND_ORIGINS.split(',')[0]}/complete-signup?token={lead.verification_token}"
    return RedirectResponse(url=registration_url, status_code=status.HTTP_303_SEE_OTHER)

#################################################
# GET /api/v1/auth/validate-token/{token}
# Input: token in URL; Output: { message, email, verification_token, is_verified, token_expiry }
@router.get("/validate-token/{token}", response_model=TokenResponse)
async def validate_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """Validate registration token before showing complete-signup form."""
    lead = await UserService.verify_lead_email_srv(db, token)
    
    return TokenResponse(
        message="Token is valid. Please complete your registration.",
        email=lead.email,
        verification_token=lead.verification_token,
        is_verified=lead.is_verified,
        token_expiry=lead.token_expiry
    )

#################################################
# POST /api/v1/auth/complete-signup/{token}
# Input: verification_token, username, password, full_name; Output: access_token, user
@router.post("/complete-signup/{token}", response_model=AuthData, status_code=status.HTTP_201_CREATED)
async def complete_signup(
    token: str,
    user_data: UserData,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Step 3: Complete signup after email verification."""
    # Validate that URL token matches request body token
    if token != user_data.verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token mismatch. URL token does not match request token."
        )
    
    user = await UserService.user_signup_srv (db, user_data, token)
    
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
    
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=30)
    )

    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )

    await UserService.update_refresh_token_srv(db, user.id, refresh_token)

    set_auth_cookies(response, access_token, refresh_token)
    
    return AuthData(
        access_token=access_token,
        user=User.model_validate(user)
    )

#################################################
# POST /api/v1/auth/resend-verification
# Input: email; Output: message, email
@router.post("/resend-verification", response_model=EmailResponse)
async def resend_verification(
    user_email: UserEmail,
    db: AsyncSession = Depends(get_db)
):
    lead = await UserService.resend_lead_verification_srv(db, user_email.email)
    
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
        
        return EmailResponse(
            message="Verification email resent successfully.",
            email=lead.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )

#################################################
# POST /api/v1/auth/login
# Input: email, password; Output: access_token, user
@router.post("/login", response_model=AuthData)
@limiter.limit("5/15minutes")
async def login(
    login_data: LoginData,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # verify password and is_active > return user
    user = await UserService.authenticate_user_srv(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=30)
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )

    # Store refresh token in database
    await UserService.update_refresh_token_srv(db, user.id, refresh_token)

    # Set auth cookies (access token + CSRF token)
    set_auth_cookies(response, access_token)
    
    return AuthData(
        access_token=access_token,
        user=User.model_validate(user)
    )

#################################################
# POST /api/v1/auth/validate-access-token
# Input: token; Output: valid, user
@router.post("/validate-access-token")
async def validate_access_token(
    access_token: AccessToken,
    db: AsyncSession = Depends(get_db)
):
    """Validate JWT access token and return user information."""
    # Decode and validate token
    payload = decode_access_token(access_token.token)
    
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
    
    # Verify user exists in database
    user = await UserService.get_user_by_email_srv(db, email)
    
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
        "user": User.model_validate(user)
    }

################################################
# POST /api/v1/auth/refresh-token
# Input: refresh token in cookie; Output: access_token, user
@router.post("/refresh-token", response_model=AuthData)
async def refresh_token(
    response: Response,
    exa_refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    if not exa_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    payload = decode_refresh_token(exa_refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    email = payload.get("sub")
    user_email = payload.get("user_id")
    
    if not email or not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = await UserService.get_user_by_email_srv(db, email)
    
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
    
    # Verify refresh token matches stored token
    if user.refresh_token != exa_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token (15 minutes)
    new_access_token = create_access_token(
        data={"sub": user.email, "user_email": user.email},
        expires_delta=timedelta(minutes=30
        )
    )
    
    # Set auth cookies (access + refresh + CSRF)
    set_auth_cookies(response, new_access_token)
    
    return AuthData(
        access_token=new_access_token,
        user=User.model_validate(user)
    )

################################################
# POST /api/v1/auth/forgot-password
# Input: email; Output: message
@router.post("/forgot-password", response_model=EmailResponse)
@limiter.limit("3/hour", key_func=get_email_identifier)
async def forgot_password(
    http_request: Request,
    request: UserEmail,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset by email.
    Sends a 4-digit OTP to the user's email if account exists.
    Rate limited: 3 attempts per hour per email.
    """
    # Store email in request state for rate limiting
    http_request.state.email = request.email
    user = await UserService.request_password_reset_srv(db, request.email)
    
    # Send OTP email
    try:
        body_html = f"""
        <html>
        <body>
            <h2>Password Reset OTP</h2>
            <p>Hello {user.full_name or user.username},</p>
            <p>Your password reset OTP is:</p>
            <h1 style="color: #4F46E5; font-size: 32px; letter-spacing: 8px;">{user.reset_otp}</h1>
            <p>This OTP will expire in 10 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>ExaKeep Security Team</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Password Reset OTP
        
        Hello {user.full_name or user.username},
        
        Your password reset OTP is: {user.reset_otp}
        
        This OTP will expire in 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        ExaKeep Security Team
        """
        
        await EmailService.send_email(
            recipients=[user.email],
            subject="Password Reset OTP - ExaKeep",
            body_text=body_text,
            body_html=body_html,
            from_name="ExaKeep Security"
        )
        
        return EmailResponse(
            message="OTP sent to your email",
            email=user.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP email: {str(e)}"
        )

################################################
# POST /api/v1/auth/verify-otp
# Input: email, otp; Output: valid, message
@router.post("/verify-otp", response_model=OtpResponse)
@limiter.limit("5/10minutes")
async def verify_otp(
    http_request: Request,
    otp_data: OtpData,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify OTP only.
    Returns success message if OTP is valid.
    Rate limited: 5 attempts per 10 minutes per IP.
    """
    user = await UserService.verify_otp_srv(db, otp_data.email, otp_data.otp)
    
    return OtpResponse(
        valid=True,
        message="OTP verified successfully"
    )

##################################################
# POST /api/v1/auth/reset-password
# Input: email, otp, new_password; Output: message, access_token, user
@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    reset_data: ResetPasswordData,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset user password using OTP.
    Returns new access token for automatic login after password reset.
    """
    user = await UserService.reset_password_with_otp_srv(db, reset_data.email, reset_data.otp, reset_data.new_password)
    
    # Send password reset confirmation email
    try:
        body_html, body_text = template_service.render_template(
            template_name="user_notification",
            context={
                "user_name": user.full_name or user.username,
                "company_name": "Exakeep",
                "title": "Password Reset Successful",
                "message": "Your password has been successfully reset. If you did not make this change, please contact our support team immediately."
            }
        )
        
        await EmailService.send_email(
            recipients=[user.email],
            subject="Password Reset Confirmation - ExaKeep",
            body_text=body_text,
            body_html=body_html,
            from_name="ExaKeep Security"
        )
    except Exception as e:
        print(f"Failed to send password reset confirmation email: {e}")
    
    # Create new access token (15 minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(minutes=15)
    )
    
    # Create new refresh token (7 days)
    refresh_token = create_refresh_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=timedelta(days=7)
    )
    
    # Store refresh token in database
    await UserService.update_refresh_token_srv(db, user.id, refresh_token)
    
    # Set auth cookies (access + refresh + CSRF)
    set_auth_cookies(response, access_token, refresh_token)
    
    return ResetPasswordResponse(
        message="Password reset successfully",
        access_token=access_token,
        user=User.model_validate(user)
    )

################################################
# GET /api/v1/auth/me
# Input: Authorization header or exa_token cookie; Output: user
@router.get("/me", response_model=User)
async def get_current_user(
    authorization: Optional[str] = Header(None),
    exa_access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user from Authorization header or exa_token cookie.
    Returns user details if token is valid.
    """
    # Try cookie first (httpOnly secure), then Authorization header
    token = None
    
    if exa_access_token:
        token = exa_access_token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Decode and verify token
    try:
        payload = decode_access_token(token)
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    user = await UserService.get_user_by_email_srv(db, user_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User.model_validate(user)


###################################################
# POST /api/v1/auth/logout
# Input: response; Output: message
@router.post("/logout")
async def logout(
    response: Response,
    exa_access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by deleting cookies and clearing refresh token from database.
    """
    # Clear refresh token from database
    if exa_access_token:
        try:
            payload = decode_access_token(exa_access_token)
            if payload:
                email = payload.get("sub")
                if email:
                    await UserService.update_refresh_token_srv(db, email, None)
        except Exception:
            # If token is invalid, continue with cookie deletion
            pass
    
    # Delete access token cookie
    response.delete_cookie(
        key="exa_access_token",
        path="/",
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax"
    )
    
    # Delete refresh token cookie
    response.delete_cookie(
        key="exa_refresh_token",
        path="/",
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax"
    )
    
    # Delete CSRF token cookie
    response.delete_cookie(
        key="csrf_token",
        path="/",
        httponly=False,
        secure=settings.APP_ENV == "production",
        samesite="lax"
    )

    return {"message": "Logged out successfully"}

