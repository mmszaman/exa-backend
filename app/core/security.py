import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets
from app.core.config import settings

######################################################################
# Password hashing and verification
# param: plain_password (str), hashed_password (str); returns: bool
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

######################################################################
# Password hashing
# param: password (str); returns: hashed password (str)
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

######################################################################
# JWT token creation and decoding
# param: data (dict), expires_delta (timedelta); returns: JWT token (
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token (short-lived: 15 minutes)."""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

######################################################################
# JWT token creation and decoding
# param: data (dict), expires_delta (timedelta); returns: JWT token (
def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """Create JWT refresh token (long-lived: 7 days)."""
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

######################################################################
# JWT token decoding and validation
# param: token (str); returns: payload (dict) or None
def decode_access_token(token: str):
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # Verify it's an access token
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None

######################################################################
# JWT token decoding and validation
# param: token (str); returns: payload (dict) or None
def decode_refresh_token(token: str):
    """Decode and validate JWT refresh token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None

######################################################################
# Generation of email verification tokens: random secure tokens
# param: none; returns: secure random token string
def generate_verification_token() -> str:
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)

######################################################################
# Get expiry time for verification token
# param: hours (int); returns: datetime
def get_token_expiry(hours: int = 24) -> datetime:
    """Get expiry time for verification token (default 24 hours)."""
    return datetime.now() + timedelta(hours=hours)

######################################################################
# Generate a 4-digit OTP
# param: none; returns: str
def generate_otp() -> str:
    """Generate a 4-digit OTP."""
    import random
    return str(random.randint(1000, 9999))

# Get expiry time for OTP
# param: minutes (int); returns: datetime
def get_otp_expiry(minutes: int = 10) -> datetime:
    """Get expiry time for OTP (default 10 minutes)."""
    return datetime.now() + timedelta(minutes=minutes)

######################################################################
# CSRF token generation and verification: random secure tokens
# param: none; returns: str
def generate_csrf_token() -> str:
    """Generate a secure CSRF token."""
    return secrets.token_urlsafe(32)

######################################################################
# Verify CSRF token
# param: token (str), expected_token (str); returns: bool
def verify_csrf_token(token: str, expected_token: str) -> bool:
    """Verify CSRF token matches expected value."""
    return secrets.compare_digest(token, expected_token)