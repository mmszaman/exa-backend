# Rate Limiting Implementation

## Overview
Rate limiting is implemented in the **backend** using `slowapi` to prevent brute-force attacks and abuse. Frontend rate limiting can be bypassed, so all enforcement happens server-side.

## Rate Limits Applied

### 1. Login Endpoint
- **Endpoint**: `POST /api/v1/auth/login`
- **Limit**: 5 attempts per 15 minutes
- **Scope**: Per IP address
- **Purpose**: Prevent brute-force password attacks

### 2. Forgot Password
- **Endpoint**: `POST /api/v1/auth/forgot-password`
- **Limit**: 3 attempts per hour
- **Scope**: Per email address
- **Purpose**: Prevent OTP spam and enumeration attacks

### 3. OTP Verification
- **Endpoint**: `POST /api/v1/auth/verify-otp`
- **Limit**: 5 attempts per 10 minutes
- **Scope**: Per IP address
- **Purpose**: Prevent OTP brute-force attacks

## Implementation Details

### Backend Configuration

```python
# app/core/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://",  # In-memory for development
)
```

### Endpoint Decorators

```python
# Login - IP-based rate limiting
@router.post("/login")
@limiter.limit("5/15minutes")
async def login(request: Request, ...):
    pass

# Forgot Password - Email-based rate limiting
@router.post("/forgot-password")
@limiter.limit("3/hour", key_func=get_email_identifier)
async def forgot_password(http_request: Request, request: ForgotPasswordRequest, ...):
    http_request.state.email = request.email  # Store email for rate limiting
    pass

# OTP Verification - IP-based rate limiting
@router.post("/verify-otp")
@limiter.limit("5/10minutes")
async def verify_otp(request: Request, ...):
    pass
```

## Rate Limit Response

When rate limit is exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded: 5 per 15 minutes"
}
```

**HTTP Status**: `429 Too Many Requests`

**Headers**:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

## Frontend Handling

### Detecting Rate Limits

```typescript
async function login(email: string, password: string) {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    if (response.status === 429) {
      // Rate limit exceeded
      const retryAfter = response.headers.get('Retry-After');
      const error = await response.json();
      
      return {
        error: 'Too many attempts. Please try again later.',
        retryAfter: retryAfter ? parseInt(retryAfter) : null,
        details: error.error
      };
    }

    return await response.json();
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}
```

### UI Feedback Example

```tsx
import { useState } from 'react';

export function LoginForm() {
  const [rateLimited, setRateLimited] = useState(false);
  const [retryAfter, setRetryAfter] = useState<number | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const result = await login(email, password);
    
    if (result.error && result.retryAfter) {
      setRateLimited(true);
      setRetryAfter(result.retryAfter);
      
      // Show countdown timer
      const interval = setInterval(() => {
        setRetryAfter(prev => {
          if (prev && prev > 0) return prev - 1;
          setRateLimited(false);
          clearInterval(interval);
          return null;
        });
      }, 1000);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {rateLimited && (
        <div className="error">
          Too many login attempts. 
          Please try again in {retryAfter} seconds.
        </div>
      )}
      
      <button 
        type="submit" 
        disabled={rateLimited}
      >
        Login
      </button>
    </form>
  );
}
```

## Production Considerations

### Use Redis for Distributed Systems

For production with multiple servers, replace in-memory storage with Redis:

```python
# app/core/rate_limit.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="redis://localhost:6379",  # Production: use Redis
)
```

Install Redis support:
```bash
pip install redis
```

### Environment-based Configuration

```python
# app/core/config.py
class Settings(BaseSettings):
    # Rate limiting
    RATE_LIMIT_STORAGE: str = "memory://"  # Development
    # RATE_LIMIT_STORAGE: str = "redis://redis:6379"  # Production
    
    # Override rate limits
    LOGIN_RATE_LIMIT: str = "5/15minutes"
    FORGOT_PASSWORD_RATE_LIMIT: str = "3/hour"
    OTP_VERIFICATION_RATE_LIMIT: str = "5/10minutes"
```

### Behind Proxy/Load Balancer

If using nginx/CloudFlare, configure to get real IP:

```python
from slowapi.util import get_remote_address

def get_real_ip(request: Request) -> str:
    """Get real client IP behind proxy."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return get_remote_address(request)

limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["100/minute"],
)
```

## Testing Rate Limits

### Manual Testing with curl

```bash
# Test login rate limit (5 attempts per 15 minutes)
for i in {1..6}; do
  echo "Attempt $i:"
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}' \
    -v 2>&1 | grep -E "(HTTP|error)"
  sleep 1
done

# Test forgot-password rate limit (3 attempts per hour)
for i in {1..4}; do
  echo "Attempt $i:"
  curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com"}' \
    -v 2>&1 | grep -E "(HTTP|error)"
  sleep 1
done

# Test OTP verification rate limit (5 attempts per 10 minutes)
for i in {1..6}; do
  echo "Attempt $i:"
  curl -X POST http://localhost:8000/api/v1/auth/verify-otp \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","otp":"1234"}' \
    -v 2>&1 | grep -E "(HTTP|error)"
  sleep 1
done
```

### Automated Testing

```python
# tests/test_rate_limiting.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_rate_limit(client: AsyncClient):
    """Test login rate limit: 5 attempts per 15 minutes."""
    
    # Make 5 requests (should succeed or return auth errors)
    for i in range(5):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong"}
        )
        assert response.status_code in [200, 401]
    
    # 6th request should be rate limited
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 429
    assert "rate limit exceeded" in response.json()["error"].lower()
```

## Security Benefits

1. **Brute-Force Protection**: Prevents automated password guessing
2. **Account Enumeration Prevention**: Limits forgot-password attempts
3. **OTP Protection**: Makes OTP brute-forcing infeasible (4-digit = 10,000 combinations)
4. **DoS Mitigation**: Prevents spam and resource exhaustion
5. **IP-based Tracking**: Identifies and blocks malicious actors

## Monitoring

Track rate limit violations in logs:

```python
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}, Path: {request.url.path}")
    return JSONResponse(
        status_code=429,
        content={"error": str(exc.detail)}
    )
```
