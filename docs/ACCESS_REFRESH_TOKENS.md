# Access/Refresh Token Implementation

## Overview
The authentication system now uses **split access/refresh tokens** for enhanced security. Access tokens are short-lived (15 minutes) while refresh tokens last longer (7 days), both stored in httpOnly cookies.

## Token Configuration

### Access Token
- **Duration**: 15 minutes
- **Cookie Name**: `exa_access_token`
- **Purpose**: Used for API authentication
- **Storage**: httpOnly cookie (XSS-safe)
- **Type**: JWT with `"type": "access"`

### Refresh Token
- **Duration**: 7 days
- **Cookie Name**: `exa_refresh_token`
- **Purpose**: Used to obtain new access tokens
- **Storage**: httpOnly cookie + database
- **Type**: JWT with `"type": "refresh"`

### CSRF Token
- **Duration**: 7 days (same as refresh token)
- **Cookie Name**: `csrf_token`
- **Purpose**: CSRF protection
- **Storage**: Non-httpOnly cookie (readable by JavaScript)

## Security Benefits

1. **Reduced Attack Window**: Access tokens expire quickly (15 minutes)
2. **Token Rotation**: New tokens issued on refresh
3. **Revocation Support**: Refresh tokens stored in database can be invalidated
4. **XSS Protection**: httpOnly cookies prevent JavaScript access
5. **CSRF Protection**: Separate CSRF token validates requests

## Authentication Flow

### 1. Login/Signup
```
Client → POST /api/v1/auth/login
         { email, password }

Server → Generates:
         - Access Token (15 min)
         - Refresh Token (7 days)
         - CSRF Token (7 days)
         
Server → Sets Cookies:
         - exa_access_token (httpOnly)
         - exa_refresh_token (httpOnly)
         - csrf_token (readable)
         
Server → Stores:
         - Refresh token in database
         
← Response: { access_token, user }
```

### 2. API Requests (Using Access Token)
```
Client → GET /api/v1/auth/me
         Cookie: exa_access_token=<token>
         Header: X-CSRF-Token=<csrf>

Server → Validates access token
         Validates CSRF token
         
← Response: { user data }
```

### 3. Silent Token Refresh
```
Client → POST /api/v1/auth/refresh-token
         Cookie: exa_refresh_token=<token>

Server → Validates refresh token
         Checks token against database
         Generates new tokens
         Updates database
         
Server → Sets New Cookies:
         - exa_access_token (new, 15 min)
         - exa_refresh_token (new, 7 days)
         - csrf_token (new, 7 days)
         
← Response: { access_token, user }
```

### 4. Logout
```
Client → POST /api/v1/auth/logout

Server → Deletes Cookies:
         - exa_access_token
         - exa_refresh_token
         - csrf_token
         
Server → Optionally:
         - Clears refresh token from database
         
← Response: { message: "Logged out successfully" }
```

## Frontend Implementation

### Automatic Token Refresh

The frontend should automatically refresh the access token before it expires using a timer or interceptor.

#### React Example with Axios

```typescript
// utils/auth.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;
let refreshTimer: NodeJS.Timeout | null = null;

export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Include cookies
});

// Get CSRF token from cookie
function getCsrfToken(): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; csrf_token=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

// Add CSRF token to all requests
api.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken();
  if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method?.toUpperCase() || '')) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});

// Handle 401 errors and refresh token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        await api.post('/api/v1/auth/refresh-token');
        
        // Retry original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Schedule automatic refresh before token expires
export function scheduleTokenRefresh() {
  // Refresh 1 minute before expiry (14 minutes)
  const refreshTime = 14 * 60 * 1000; // 14 minutes in ms

  if (refreshTimer) {
    clearTimeout(refreshTimer);
  }

  refreshTimer = setTimeout(async () => {
    try {
      await api.post('/api/v1/auth/refresh-token');
      console.log('Token refreshed successfully');
      
      // Schedule next refresh
      scheduleTokenRefresh();
    } catch (error) {
      console.error('Failed to refresh token:', error);
      window.location.href = '/login';
    }
  }, refreshTime);
}

// Call after login
export function startTokenRefreshTimer() {
  scheduleTokenRefresh();
}

// Call on logout
export function stopTokenRefreshTimer() {
  if (refreshTimer) {
    clearTimeout(refreshTimer);
    refreshTimer = null;
  }
}
```

#### Login Component Example

```typescript
// components/LoginForm.tsx
import { useState } from 'react';
import { api, startTokenRefreshTimer } from '@/utils/auth';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const response = await api.post('/api/v1/auth/login', {
        email,
        password,
      });

      // Start automatic token refresh
      startTokenRefreshTimer();

      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {error && <div className="error">{error}</div>}
      
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      
      <button type="submit">Login</button>
    </form>
  );
}
```

#### App Initialization

```typescript
// app/layout.tsx or _app.tsx
import { useEffect } from 'react';
import { startTokenRefreshTimer, stopTokenRefreshTimer } from '@/utils/auth';

export default function RootLayout({ children }) {
  useEffect(() => {
    // Check if user is logged in (has cookies)
    const hasAuthCookie = document.cookie.includes('exa_access_token');
    
    if (hasAuthCookie) {
      // Start automatic token refresh
      startTokenRefreshTimer();
    }

    // Cleanup on unmount
    return () => {
      stopTokenRefreshTimer();
    };
  }, []);

  return <>{children}</>;
}
```

#### Logout Implementation

```typescript
// utils/auth.ts (continued)
export async function logout() {
  try {
    await api.post('/api/v1/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    stopTokenRefreshTimer();
    window.location.href = '/login';
  }
}
```

### Alternative: Visibility-based Refresh

Instead of a timer, refresh when the page becomes visible:

```typescript
// utils/auth.ts (alternative)
export function setupVisibilityRefresh() {
  document.addEventListener('visibilitychange', async () => {
    if (document.visibilityState === 'visible') {
      try {
        // Refresh token when user returns to tab
        await api.post('/api/v1/auth/refresh-token');
        console.log('Token refreshed on visibility change');
      } catch (error) {
        console.error('Failed to refresh token:', error);
      }
    }
  });
}
```

## Backend Endpoints

### Modified Endpoints

All authentication endpoints now set three cookies:
- `exa_access_token` (15 minutes)
- `exa_refresh_token` (7 days)
- `csrf_token` (7 days)

**Affected Endpoints:**
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/complete-signup/{token}`
- `POST /api/v1/auth/reset-password`
- `POST /api/v1/auth/refresh-token` (NEW behavior)

### New Refresh Token Endpoint Behavior

**Before:**
```json
POST /api/v1/auth/refresh-token
Body: { "token": "eyJhbGciOi..." }
```

**After:**
```json
POST /api/v1/auth/refresh-token
Cookie: exa_refresh_token=<token>
```

The refresh token is now read from the httpOnly cookie, not the request body.

## Database Changes

### Migration Applied
```sql
ALTER TABLE users ADD COLUMN refresh_token VARCHAR;
```

### User Model Updated
```python
class User(Base):
    # ... existing fields ...
    refresh_token = Column(String, nullable=True)
```

## Token Validation

### Access Token Validation
```python
from app.core.security import decode_access_token

payload = decode_access_token(token)
if not payload:
    raise HTTPException(status_code=401, detail="Invalid access token")
```

### Refresh Token Validation
```python
from app.core.security import decode_refresh_token

payload = decode_refresh_token(token)
if not payload:
    raise HTTPException(status_code=401, detail="Invalid refresh token")

# Also verify against database
user = await UserService.get_user_by_id_srv(db, user_id)
if user.refresh_token != token:
    raise HTTPException(status_code=401, detail="Invalid refresh token")
```

## Security Considerations

### Token Revocation
To revoke a user's refresh token:
```python
user.refresh_token = None
await db.commit()
```

### Force Re-login
To force all users to re-login, rotate the `SECRET_KEY` in your environment variables. This invalidates all existing tokens.

### Token Expiry Times
- **Development**: 15 min access, 7 days refresh
- **Production**: Consider shorter refresh token duration (1-3 days)

### HTTPS Required
In production, set `secure=True` for all cookies to ensure they're only sent over HTTPS:
```python
# app/core/config.py
APP_ENV = "production"  # Enables secure cookies
```

## Testing

### Test Login Flow
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' \
  -c cookies.txt \
  -v

# Check cookies (should see 3 cookies)
cat cookies.txt
```

### Test Token Refresh
```bash
# Refresh token (reads from cookie)
curl -X POST http://localhost:8000/api/v1/auth/refresh-token \
  -b cookies.txt \
  -c cookies_new.txt \
  -v

# Cookies should be updated
diff cookies.txt cookies_new.txt
```

### Test Expired Access Token
```bash
# Wait 15 minutes or manually expire token
# Then try to access protected endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -b cookies.txt

# Should return 401 if access token expired
# Frontend should automatically call /refresh-token
```

## Migration Guide

### Updating Existing Frontend Code

1. **Update cookie names:**
   - `exa_token` → `exa_access_token`

2. **Implement refresh logic:**
   - Add automatic refresh timer (14 minutes)
   - Or use axios interceptor for 401 handling

3. **Remove token from localStorage:**
   - Tokens should only be in httpOnly cookies

4. **Update refresh endpoint:**
   - Remove token from request body
   - Token now comes from cookie automatically

### Backward Compatibility

⚠️ **Breaking Change**: Old tokens will not work after this update. All users must re-login.

## Monitoring

Track token refresh patterns:
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/refresh-token")
async def refresh_token(...):
    logger.info(f"Token refresh for user_id: {user_id}")
    # ... rest of logic
```

## Troubleshooting

### "Refresh token not found" error
- Ensure cookies are being sent (`credentials: 'include'`)
- Check cookie domain/path settings
- Verify `exa_refresh_token` cookie exists

### "Invalid refresh token" error
- Token may have been revoked
- User may need to re-login
- Check database for stored refresh token

### Tokens not refreshing automatically
- Verify timer is running
- Check browser console for errors
- Ensure refresh endpoint is called before expiry
