# app/core/rate_limit.py
# Rate limiting configuration using SlowAPI for FastAPI application.
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

# Function to get client identifier (IP address)
# This will be overridden for email-specific endpoints
def get_client_identifier(request: Request) -> str:
    # For email-specific endpoints, we'll override this in the route
    return get_remote_address(request)


# Initialize limiter
# Global rate limiter configuration
limiter = Limiter(
    key_func=get_client_identifier,
    default_limits=["100/minute"],  # Global default limit
    storage_uri="memory://",  # Use in-memory storage (for production, use Redis)
)

# Custom key function for email-based rate limiting
# This function extracts email from request state if available
def get_email_identifier(request: Request) -> str:
    # Custom key function to use email from request state if available
    try:
        if hasattr(request.state, "email"):
            return request.state.email
        return get_remote_address(request)
    except Exception:
        return get_remote_address(request)
