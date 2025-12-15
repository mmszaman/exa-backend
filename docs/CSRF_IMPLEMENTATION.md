# CSRF Protection Implementation Guide

## Overview
The backend now implements CSRF (Cross-Site Request Forgery) protection using a double-submit cookie pattern.

## How It Works

### Backend (Already Implemented)

1. **Login/Signup/Reset Password**: Sets three cookies
   - `exa_access_token` (httpOnly): Access token (15 min) - JavaScript cannot read
   - `exa_refresh_token` (httpOnly): Refresh token (7 days) - JavaScript cannot read
   - `csrf_token` (non-httpOnly): CSRF token (7 days) - JavaScript CAN read

2. **Protected Endpoints**: Validates CSRF token for POST/PUT/PATCH/DELETE requests
   - Reads `csrf_token` from cookie
   - Requires `X-CSRF-Token` header with same value
   - Validates tokens match using constant-time comparison

3. **Exempt Endpoints**: Auth endpoints don't require CSRF tokens
   - `/api/v1/auth/login`
   - `/api/v1/auth/complete-signup/*`
   - `/api/v1/auth/request-signup`
   - `/api/v1/auth/forgot-password`
   - `/api/v1/auth/verify-otp`
   - `/api/v1/auth/reset-password`

### Frontend Implementation

#### 1. Get CSRF Token from Cookie

```typescript
// Helper function to read cookie
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

// Get CSRF token
const csrfToken = getCookie('csrf_token');
```

#### 2. Include CSRF Token in Requests

```typescript
// For fetch API
const response = await fetch(`${API_URL}/api/v1/some-endpoint`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': getCookie('csrf_token') || '',
  },
  credentials: 'include', // Include cookies
  body: JSON.stringify(data),
});

// For axios
import axios from 'axios';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Include cookies
});

// Add CSRF token to all requests
api.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrf_token');
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});
```

#### 3. React Hook Example

```typescript
// hooks/useApi.ts
import { useEffect, useState } from 'react';

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(';').shift() || null;
  }
  return null;
}

export function useApi() {
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  useEffect(() => {
    // Get CSRF token from cookie
    const token = getCookie('csrf_token');
    setCsrfToken(token);
  }, []);

  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add CSRF token for state-changing methods
    if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method || 'GET')) {
      headers['X-CSRF-Token'] = csrfToken;
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include', // Important: include cookies
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  };

  return { apiCall, csrfToken };
}
```

#### 4. Usage in Components

```typescript
// Example: Update user profile
import { useApi } from '@/hooks/useApi';

export function ProfileForm() {
  const { apiCall } = useApi();

  const handleSubmit = async (data: any) => {
    try {
      const result = await apiCall('/api/v1/user/profile', {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      console.log('Profile updated:', result);
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* form fields */}
    </form>
  );
}
```

## Security Benefits

1. **XSS Protection**: Access token is httpOnly, JavaScript cannot steal it
2. **CSRF Protection**: Attackers cannot read csrf_token from victim's cookies
3. **Double-Submit Pattern**: Both cookie and header must match
4. **Constant-Time Comparison**: Prevents timing attacks

## Testing CSRF Protection

### Valid Request (Should Succeed)
```bash
# Login first to get cookies
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt

# Extract CSRF token from cookies.txt and use it
CSRF_TOKEN=$(grep csrf_token cookies.txt | cut -f7)

# Make protected request with CSRF token
curl -X POST http://localhost:8000/api/v1/some-protected-endpoint \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -b cookies.txt \
  -d '{"data":"value"}'
```

### Invalid Request (Should Fail with 403)
```bash
# Without CSRF token header
curl -X POST http://localhost:8000/api/v1/some-protected-endpoint \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"data":"value"}'
```

## Troubleshooting

### "CSRF token missing" Error
- Ensure cookies are included in request (`credentials: 'include'` or `withCredentials: true`)
- Check that `csrf_token` cookie exists after login
- Verify `X-CSRF-Token` header is set for POST/PUT/PATCH/DELETE requests

### "CSRF token invalid" Error
- Cookie value and header value must match exactly
- CSRF token is regenerated on each login
- Check for cookie expiration (7 days)

### CORS Issues
- Backend allows `X-CSRF-Token` in CORS headers
- Frontend must use `credentials: 'include'`
- Backend `allow_credentials` must be `True`
