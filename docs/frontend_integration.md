# Frontend Integration Guide - Next.js + TypeScript

Simple guide to integrate email API endpoints with Next.js and TypeScript.

## API Base URL

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## TypeScript Types

```typescript
// types/email.ts

export interface EmailRecipient {
  email: string;
  success: boolean;
  error?: string;
  sent_at?: string;
}

export interface SendEmailRequest {
  recipients: string[];
  subject: string;
  from_name?: string;
  from_email?: string;
  body_text: string;
  body_html?: string;
}

export interface SendTemplateEmailRequest {
  recipients: string[];
  template_name: 'welcome' | 'password_reset' | 'email_verification' | 'notification';
  subject: string;
  from_name?: string;
  from_email?: string;
  context: Record<string, any>;
}

export interface EmailResponse {
  success: boolean;
  total_sent: number;
  total_failed: number;
  results: EmailRecipient[];
  message: string;
}
```

## API Functions

```typescript
// lib/email-api.ts

import type { SendEmailRequest, SendTemplateEmailRequest, EmailResponse } from '@/types/email';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function sendEmail(data: SendEmailRequest): Promise<EmailResponse> {
  const response = await fetch(`${API_BASE_URL}/api/email/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send email');
  }

  return response.json();
}

export async function sendTemplateEmail(data: SendTemplateEmailRequest): Promise<EmailResponse> {
  const response = await fetch(`${API_BASE_URL}/api/email/send-template`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send template email');
  }

  return response.json();
}
```

## Usage Examples

### 1. Send Plain/HTML Email

```typescript
// app/actions/send-email.ts
'use server';

import { sendEmail } from '@/lib/email-api';

export async function sendWelcomeEmail(userEmail: string) {
  try {
    const result = await sendEmail({
      recipients: [userEmail],
      subject: 'Welcome to Our Platform',
      from_name: 'Our Team',
      body_text: 'Welcome! We are glad to have you.',
      body_html: '<h1>Welcome!</h1><p>We are glad to have you.</p>',
    });

    return { success: true, data: result };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to send email' 
    };
  }
}
```

### 2. Send Template Email

```typescript
// app/actions/send-template.ts
'use server';

import { sendTemplateEmail } from '@/lib/email-api';

export async function sendVerificationEmail(userEmail: string, userName: string, verifyUrl: string) {
  try {
    const result = await sendTemplateEmail({
      recipients: [userEmail],
      template_name: 'email_verification',
      subject: 'Verify Your Email',
      from_name: 'Security Team',
      context: {
        user_name: userName,
        verify_url: verifyUrl,
        expiry_hours: 24,
      },
    });

    return { success: true, data: result };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to send verification email' 
    };
  }
}

export async function sendNotification(userEmail: string, userName: string, websiteUrl: string) {
  try {
    const result = await sendTemplateEmail({
      recipients: [userEmail],
      template_name: 'notification',
      subject: 'Website is Online!',
      context: {
        user_name: userName,
        title: 'Your Website is Live',
        message: 'Great news! The website you were monitoring is now online and accessible.',
        website_url: websiteUrl,
        action_url: websiteUrl,
        action_text: 'Visit Website',
      },
    });

    return { success: true, data: result };
  } catch (error) {
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to send notification' 
    };
  }
}
```

### 3. Client Component Example

```typescript
// app/components/email-form.tsx
'use client';

import { useState } from 'react';
import { sendWelcomeEmail } from '@/app/actions/send-email';

export function EmailForm() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    const result = await sendWelcomeEmail(email);

    if (result.success) {
      setMessage('Email sent successfully!');
      setEmail('');
    } else {
      setMessage(`Error: ${result.error}`);
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter email"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Email'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}
```

## Environment Setup

Add to your `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Template Context Variables

### Welcome Template
- `user_name` (required)
- `verify_url` (optional)

### Password Reset Template
- `user_name` (required)
- `reset_url` (required)
- `expiry_hours` (optional, default: 1)

### Email Verification Template
- `user_name` (required)
- `verify_url` (required)
- `verification_code` (optional)
- `expiry_hours` (optional, default: 24)

### Notification Template
- `user_name` (required)
- `title` (required)
- `message` (required)
- `website_url` (optional)
- `action_url` (optional)
- `action_text` (optional)

## Error Handling

```typescript
try {
  const result = await sendEmail(data);
  console.log('Success:', result.message);
} catch (error) {
  if (error instanceof Error) {
    console.error('Error:', error.message);
  }
}
```

## Best Practices

1. **Server Actions**: Use Next.js server actions for email sending to keep API credentials secure
2. **Validation**: Validate email addresses before sending
3. **Error Handling**: Always handle errors gracefully
4. **Loading States**: Show loading indicators during email sending
5. **Rate Limiting**: Implement client-side rate limiting to prevent abuse
