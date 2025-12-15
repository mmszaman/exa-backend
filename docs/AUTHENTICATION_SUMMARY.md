# Authentication Summary

## Current Implementation Status

### ✅ Completed Features

1. **Rate Limiting** (`docs/RATE_LIMITING.md`)
   - Login: 5 attempts / 15 minutes (per IP)
   - Password reset: 3 attempts / hour (per email)
   - OTP verification: 5 attempts / 10 minutes (per IP)

2. **CSRF Protection** (`docs/CSRF_IMPLEMENTATION.md`)
   - Double-submit cookie pattern
   - Separate `csrf_token` cookie (readable by JS)
   - `X-CSRF-Token` header validation
   - Protected methods: POST, PUT, PATCH, DELETE

3. **Access/Refresh Token Split** (`docs/ACCESS_REFRESH_TOKENS.md`)
   - Access token: 15 minutes (httpOnly cookie)
   - Refresh token: 7 days (httpOnly cookie + database)
   - Automatic silent refresh support
   - Token rotation on refresh

4. **HttpOnly Cookies**
   - `exa_access_token`: Access token (XSS-safe)
   - `exa_refresh_token`: Refresh token (XSS-safe)
   - `csrf_token`: CSRF validation (readable by JS)

5. **OTP-based Password Reset**
   - 4-digit OTP sent via email
   - 10-minute expiry
   - Rate limited (3 attempts/hour per email)

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (Browser)                      │
├─────────────────────────────────────────────────────────────┤
│  Cookies (httpOnly):                                        │
│    - exa_access_token (15 min)  ← JWT access token         │
│    - exa_refresh_token (7 days) ← JWT refresh token        │
│                                                              │
│  Cookies (readable):                                         │
│    - csrf_token (7 days)        ← CSRF validation           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Request Flow                          │
├─────────────────────────────────────────────────────────────┤
│  1. Rate Limiting (slowapi)                                 │
│     └─ Check request limits by IP/email                     │
│                                                              │
│  2. CSRF Validation (middleware)                            │
│     └─ Compare X-CSRF-Token header vs cookie               │
│                                                              │
│  3. Token Validation (security.py)                          │
│     └─ Decode JWT, verify signature & expiry               │
│                                                              │
│  4. Database Validation                                      │
│     └─ Verify user active, refresh token matches           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│  users table:                                                │
│    - id, email, username, hashed_password                   │
│    - refresh_token (for validation & revocation)            │
│    - reset_otp, reset_otp_expiry                            │
│    - is_active, is_verified                                  │
└─────────────────────────────────────────────────────────────┘
```

## Token Lifecycle

### Login/Signup
```
POST /api/v1/auth/login
  ↓
Generate: access_token (15 min) + refresh_token (7 days)
  ↓
Store refresh_token in database
  ↓
Set 3 httpOnly cookies
  ↓
Return: { access_token, user }
```

### API Request
```
GET /api/v1/auth/me
Cookie: exa_access_token + csrf_token
Header: X-CSRF-Token
  ↓
Validate CSRF token
  ↓
Decode & validate access token
  ↓
Return user data
```

### Token Refresh (Before 15 min expires)
```
POST /api/v1/auth/refresh-token
Cookie: exa_refresh_token
  ↓
Validate refresh token (JWT + database)
  ↓
Generate new: access_token + refresh_token
  ↓
Update refresh_token in database
  ↓
Set new cookies
  ↓
Return: { access_token, user }
```

### Logout
```
POST /api/v1/auth/logout
  ↓
Delete all 3 cookies
  ↓
Optionally: Clear refresh_token from database
  ↓
Return: { message: "Logged out successfully" }
```

## Cookie Configuration

| Cookie Name | Duration | httpOnly | Purpose | Accessible by JS |
|------------|----------|----------|---------|------------------|
| `exa_access_token` | 15 min | ✅ Yes | API authentication | ❌ No (XSS-safe) |
| `exa_refresh_token` | 7 days | ✅ Yes | Token refresh | ❌ No (XSS-safe) |
| `csrf_token` | 7 days | ❌ No | CSRF protection | ✅ Yes (required) |

## Frontend Integration Checklist

### Required Changes

- [ ] Update cookie name: `exa_token` → `exa_access_token`
- [ ] Implement automatic token refresh (14-minute timer)
- [ ] Add axios/fetch interceptor for 401 handling
- [ ] Include `X-CSRF-Token` header in POST/PUT/PATCH/DELETE
- [ ] Read `csrf_token` from cookie for header value
- [ ] Set `credentials: 'include'` in all fetch requests
- [ ] Remove tokens from localStorage (use cookies only)
- [ ] Handle rate limit errors (429 status code)

### Example Implementation Files

1. **`utils/auth.ts`** - Axios setup with interceptors
2. **`utils/tokenRefresh.ts`** - Automatic refresh timer
3. **`components/LoginForm.tsx`** - Login with token refresh start
4. **`app/layout.tsx`** - Initialize refresh on app load
5. **`hooks/useAuth.ts`** - Authentication state management

See `docs/ACCESS_REFRESH_TOKENS.md` for complete code examples.

## Testing Endpoints

### Test Rate Limiting
```bash
# Try 6 login attempts (5th should succeed, 6th should fail with 429)
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}'
done
```

### Test Token Refresh
```bash
# 1. Login and save cookies
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt

# 2. Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh-token \
  -b cookies.txt \
  -c cookies_new.txt

# 3. Verify new cookies
diff cookies.txt cookies_new.txt
```

### Test CSRF Protection
```bash
# Get CSRF token from cookies
CSRF_TOKEN=$(grep csrf_token cookies.txt | cut -f7)

# Valid request (with CSRF token)
curl -X POST http://localhost:8000/api/v1/some-endpoint \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -b cookies.txt

# Invalid request (without CSRF token) - should fail with 403
curl -X POST http://localhost:8000/api/v1/some-endpoint \
  -b cookies.txt
```

## Environment Variables

```env
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Optional (defaults shown)
APP_ENV=development  # production enables secure cookies
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Production Checklist

### Before Deployment

- [ ] Set `APP_ENV=production` (enables secure cookies)
- [ ] Use strong `SECRET_KEY` (32+ characters)
- [ ] Configure Redis for rate limiting (replace "memory://")
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for production domains
- [ ] Enable database connection pooling
- [ ] Set up monitoring for rate limit violations
- [ ] Test token refresh flow end-to-end

### Security Hardening

- [ ] Rotate `SECRET_KEY` periodically
- [ ] Implement refresh token revocation on password change
- [ ] Add IP tracking for suspicious activity
- [ ] Set up alerts for rate limit violations
- [ ] Monitor failed login attempts
- [ ] Implement account lockout after multiple failures

## Architecture Decisions

### Why Split Access/Refresh Tokens?
- **Security**: Short-lived access tokens reduce attack window
- **Revocation**: Can invalidate refresh tokens in database
- **Performance**: Access token validated without database lookup

### Why HttpOnly Cookies?
- **XSS Protection**: JavaScript cannot access tokens
- **Automatic Sending**: No manual header management needed
- **CSRF Protected**: Combined with CSRF tokens for defense-in-depth

### Why Store Refresh Token in Database?
- **Revocation**: Can invalidate specific sessions
- **Monitoring**: Track active sessions per user
- **Security**: Detect token reuse attacks

### Why Rate Limiting in Backend?
- **Cannot be Bypassed**: Frontend limits can be circumvented
- **Centralized**: Works for all clients (web, mobile, API)
- **Effective**: Prevents brute force and abuse

## Troubleshooting

### Common Issues

**"CSRF token missing" (403)**
- Frontend not including `X-CSRF-Token` header
- Check cookie exists: `document.cookie.includes('csrf_token')`

**"Refresh token not found" (401)**
- Cookies not being sent (`credentials: 'include'` missing)
- Cookie expired or was deleted

**"Invalid refresh token" (401)**
- Token was revoked (changed password, logout)
- Token doesn't match database value
- User may need to re-login

**"Rate limit exceeded" (429)**
- Too many requests from same IP/email
- Wait for rate limit window to reset
- Check `Retry-After` header for reset time

## Support & Documentation

- **Rate Limiting**: `docs/RATE_LIMITING.md`
- **CSRF Protection**: `docs/CSRF_IMPLEMENTATION.md`
- **Access/Refresh Tokens**: `docs/ACCESS_REFRESH_TOKENS.md`
- **Frontend Integration**: `docs/frontend_integration.md`

## API Changes Summary

### Breaking Changes
⚠️ **Cookie names changed** - All users must re-login
- `exa_token` → `exa_access_token`
- New cookie: `exa_refresh_token`

### New Behavior
- Access tokens expire in 15 minutes (was 7 days)
- Refresh endpoint now uses cookie (was request body)
- Three cookies set instead of two

### Migration Required
All frontend applications must update to:
1. New cookie names
2. Automatic token refresh
3. CSRF header inclusion
