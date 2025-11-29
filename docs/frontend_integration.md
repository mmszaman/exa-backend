# Frontend Integration Guide - Email API

## Base URL
```javascript
const API_BASE_URL = 'http://localhost:8000';  // Development
// const API_BASE_URL = 'https://api.exateks.com';  // Production
```

---

## 1. Send Template Email

### Endpoint
`POST /api/email/send-template`

### JavaScript/TypeScript Example

```javascript
// Send welcome email
async function sendWelcomeEmail(userEmail, userName, verifyUrl) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/email/send-template`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recipients: [userEmail],
                template_name: 'welcome',
                context: {
                    user_name: userName,
                    verify_url: verifyUrl,
                    company_name: 'Exateks'
                }
            })
        });

        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Email sent successfully!');
            return result;
        } else {
            console.error('❌ Email failed:', result.message);
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('Error sending email:', error);
        throw error;
    }
}

// Usage
await sendWelcomeEmail('user@example.com', 'John Doe', 'https://yourapp.com/verify/token123');
```

---

## 2. React Example

### Custom Hook

```typescript
// hooks/useEmailAPI.ts
import { useState } from 'react';

interface SendTemplateEmailParams {
    recipients: string[];
    template_name: 'welcome' | 'password_reset' | 'email_verification' | 'notification';
    context: Record<string, any>;
    subject_override?: string;
    from_name_override?: string;
}

interface EmailResponse {
    success: boolean;
    total_sent: number;
    total_failed: number;
    message: string;
    results: Array<{
        recipient: string;
        success: boolean;
        error?: string;
        sent_at?: string;
    }>;
}

export function useEmailAPI() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const sendTemplateEmail = async (params: SendTemplateEmailParams): Promise<EmailResponse> => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/api/email/send-template', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: EmailResponse = await response.json();
            return data;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return { sendTemplateEmail, loading, error };
}
```

### Component Usage

```typescript
// components/UserRegistration.tsx
import { useEmailAPI } from '@/hooks/useEmailAPI';

export function UserRegistration() {
    const { sendTemplateEmail, loading, error } = useEmailAPI();

    const handleRegister = async (email: string, name: string) => {
        // Register user...
        const verifyToken = 'abc123'; // Get from your backend
        
        // Send welcome email
        try {
            const result = await sendTemplateEmail({
                recipients: [email],
                template_name: 'welcome',
                context: {
                    user_name: name,
                    verify_url: `https://yourapp.com/verify/${verifyToken}`,
                    company_name: 'Exateks'
                }
            });

            if (result.success) {
                console.log('Welcome email sent!');
            }
        } catch (error) {
            console.error('Failed to send welcome email:', error);
        }
    };

    return (
        <div>
            {/* Your registration form */}
            {loading && <p>Sending email...</p>}
            {error && <p className="error">{error}</p>}
        </div>
    );
}
```

---

## 3. Available Templates & Context

### Welcome Template
```javascript
{
    template_name: 'welcome',
    context: {
        user_name: 'John Doe',
        verify_url: 'https://yourapp.com/verify/token',  // Optional
        company_name: 'Exateks'  // Optional, defaults to 'Exa'
    }
}
```

### Password Reset Template
```javascript
{
    template_name: 'password_reset',
    context: {
        user_name: 'John Doe',
        reset_url: 'https://yourapp.com/reset-password/token',
        expiry_hours: '2',  // Optional, defaults to '1'
        company_name: 'Exateks'
    }
}
```

### Email Verification Template
```javascript
{
    template_name: 'email_verification',
    context: {
        user_name: 'John Doe',
        verify_url: 'https://yourapp.com/verify/token',
        verification_code: '123456',  // Optional
        expiry_hours: '48',  // Optional, defaults to '24'
        company_name: 'Exateks'
    }
}
```

### Notification Template
```javascript
{
    template_name: 'notification',
    context: {
        user_name: 'John Doe',
        notification_title: 'Payment Successful',
        message: 'Your payment has been processed.',
        notification_type: 'success',  // 'success', 'warning', 'error', 'info'
        notification_heading: 'Payment Confirmed',
        notification_text: 'We received your payment of $99.99',
        action_url: 'https://yourapp.com/dashboard',  // Optional
        action_text: 'View Dashboard',  // Optional
        additional_info: 'Your next billing date is Jan 1, 2026',  // Optional
        items: ['Item 1', 'Item 2', 'Item 3'],  // Optional
        company_name: 'Exateks'
    }
}
```

---

## 4. Send Raw Email (Custom HTML)

### Endpoint
`POST /api/email/send`

```javascript
async function sendCustomEmail(recipients, subject, html) {
    const response = await fetch(`${API_BASE_URL}/api/email/send`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipients: recipients,
            subject: subject,
            body_text: 'Plain text version',
            body_html: html,
            from_name: 'Exateks'
        })
    });

    return await response.json();
}
```

---

## 5. Health Check

### Endpoint
`GET /api/email/check`

```javascript
async function checkEmailService() {
    const response = await fetch(`${API_BASE_URL}/api/email/check`);
    const health = await response.json();
    
    console.log('Email service status:', health.status);
    console.log('Ready:', health.ready);
    
    return health;
}
```

---

## 6. Axios Example

```javascript
import axios from 'axios';

const emailAPI = axios.create({
    baseURL: 'http://localhost:8000/api/email',
    headers: {
        'Content-Type': 'application/json',
    }
});

// Send welcome email
async function sendWelcome(email, name) {
    try {
        const { data } = await emailAPI.post('/send-template', {
            recipients: [email],
            template_name: 'welcome',
            context: {
                user_name: name,
                company_name: 'Exateks'
            }
        });
        
        return data;
    } catch (error) {
        console.error('Email error:', error.response?.data);
        throw error;
    }
}
```

---

## 7. Complete User Registration Flow

```typescript
// services/auth.service.ts
import { emailAPI } from './email.api';

export async function registerUser(email: string, password: string, name: string) {
    try {
        // 1. Create user account
        const user = await createUserAccount(email, password, name);
        
        // 2. Generate verification token
        const verifyToken = generateVerificationToken(user.id);
        
        // 3. Send welcome email with verification
        await emailAPI.sendTemplateEmail({
            recipients: [email],
            template_name: 'welcome',
            context: {
                user_name: name,
                verify_url: `${window.location.origin}/verify/${verifyToken}`,
                company_name: 'Exateks'
            }
        });
        
        return { success: true, user };
        
    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
}

// Password reset flow
export async function requestPasswordReset(email: string) {
    try {
        // 1. Generate reset token
        const resetToken = generateResetToken(email);
        
        // 2. Send password reset email
        await emailAPI.sendTemplateEmail({
            recipients: [email],
            template_name: 'password_reset',
            context: {
                user_name: await getUserName(email),
                reset_url: `${window.location.origin}/reset-password/${resetToken}`,
                expiry_hours: '2',
                company_name: 'Exateks'
            }
        });
        
        return { success: true };
        
    } catch (error) {
        console.error('Password reset failed:', error);
        throw error;
    }
}
```

---

## 8. Error Handling

```typescript
interface APIError {
    detail: string;
}

async function sendEmailWithErrorHandling() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/email/send-template`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipients: ['user@example.com'],
                template_name: 'welcome',
                context: { user_name: 'John' }
            })
        });

        if (!response.ok) {
            const error: APIError = await response.json();
            
            if (response.status === 400) {
                console.error('Invalid request:', error.detail);
            } else if (response.status === 500) {
                console.error('Server error:', error.detail);
            }
            
            throw new Error(error.detail);
        }

        return await response.json();
        
    } catch (error) {
        console.error('Email send failed:', error);
        // Show user-friendly error message
        throw error;
    }
}
```

---

## 9. CORS Configuration

Make sure your frontend URL is added to `FRONTEND_ORIGINS` in your `.env`:

```env
FRONTEND_ORIGINS=http://localhost:3000,http://localhost:5173,https://yourapp.com
```

---

## 10. API Documentation (Swagger)

Visit: `http://localhost:8000/docs`

This provides interactive API documentation where you can:
- Test all endpoints
- See request/response schemas
- Get code examples

---

## Response Format

All email endpoints return:

```typescript
{
    success: boolean;           // Overall success status
    total_sent: number;         // Number of emails sent
    total_failed: number;       // Number of failed emails
    message: string;            // Human-readable message
    results: [                  // Detailed results for each recipient
        {
            recipient: string;
            success: boolean;
            error?: string;
            sent_at?: string;   // ISO timestamp
        }
    ]
}
```

---

## Best Practices

1. **Always handle errors** - Email sending can fail
2. **Don't block UI** - Send emails asynchronously
3. **Provide user feedback** - Show success/error messages
4. **Use environment variables** - Don't hardcode API URLs
5. **Validate email addresses** - Before sending to API
6. **Monitor failures** - Log failed email attempts
7. **Rate limiting** - Don't spam the API
8. **Retry logic** - Implement for transient failures

---

## Example: Next.js API Route

```typescript
// app/api/auth/register/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    const { email, name } = await request.json();
    
    // Register user...
    
    // Send welcome email
    try {
        await fetch('http://localhost:8000/api/email/send-template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recipients: [email],
                template_name: 'welcome',
                context: {
                    user_name: name,
                    company_name: 'Exateks'
                }
            })
        });
    } catch (error) {
        console.error('Failed to send welcome email:', error);
        // Don't fail registration if email fails
    }
    
    return NextResponse.json({ success: true });
}
```

---

## Testing

```bash
# Start backend server
python -m uvicorn app.main:app --reload

# Test from browser console
fetch('http://localhost:8000/api/email/send-template', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        recipients: ['your@email.com'],
        template_name: 'welcome',
        context: { user_name: 'Test User', company_name: 'Exateks' }
    })
}).then(r => r.json()).then(console.log);
```

---

Your email API is ready for frontend integration! 🚀
