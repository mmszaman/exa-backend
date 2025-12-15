from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from app.core.security import verify_csrf_token

# Middleware to protect against CSRF attacks
# Only applies to state-changing HTTP methods and excludes auth routes
class CSRFMiddleware(BaseHTTPMiddleware):
    
    # Methods that require CSRF protection
    # Only these HTTP methods will be checked for CSRF tokens
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Routes that don't require CSRF protection (auth endpoints)
    # These paths are exempt from CSRF checks
    EXEMPT_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/complete-signup",
        "/api/v1/auth/request-signup",
        "/api/v1/auth/verify-email",
        "/api/v1/auth/resend-verification",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/verify-otp",
        "/api/v1/auth/reset-password",
        "/",
        "/docs",
        "/redoc",
        "/openapi.json"
    }
    
    # Main dispatch method for the middleware
    # It checks for CSRF tokens on protected methods
    # Inputs: request - incoming HTTP request, call_next - next middleware or endpoint
    # Outputs: response from the next middleware or endpoint
    async def dispatch(self, request: Request, call_next: Callable):

        # Skip CSRF check for safe methods and exempt paths
        if request.method not in self.PROTECTED_METHODS:
            return await call_next(request)
        
        # Check if path is exempt
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Get CSRF token from header
        csrf_token_header = request.headers.get("X-CSRF-Token")
        
        # Get CSRF token from cookie
        csrf_token_cookie = request.cookies.get("csrf_token")
        
        # Validate CSRF token
        if not csrf_token_header or not csrf_token_cookie:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        if not verify_csrf_token(csrf_token_header, csrf_token_cookie):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token invalid"
            )
        
        response = await call_next(request)
        return response
