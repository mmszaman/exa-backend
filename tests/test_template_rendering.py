"""
Simple template rendering test (no server needed).
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_template_service import template_service


# Test 1: Welcome template
print("=" * 60)
print("🎉 Test 1: Welcome Template")
print("=" * 60)

context = {
    "user_name": "Muhammad Salah",
    "verify_url": "https://example.com/verify/abc123"
}

welcome_html = template_service.render_template("welcome", context)

print(f"Template rendered: {len(welcome_html)} characters")
print(f"Subject: {template_service.get_subject('welcome', context)}")
print(f"From Name: {template_service.get_from_name('welcome', context)}")
print("\nFirst 500 chars of HTML:")
print(welcome_html[:500])


# Test 2: Password Reset template
print("\n" + "=" * 60)
print("🔒 Test 2: Password Reset Template")
print("=" * 60)

reset_context = {
    "user_name": "John Doe",
    "reset_url": "https://example.com/reset/xyz789",
    "expiry_hours": "2"
}

reset_html = template_service.render_template("password_reset", reset_context)

print(f"Template rendered: {len(reset_html)} characters")
print(f"Subject: {template_service.get_subject('password_reset', reset_context)}")
print("\nFirst 500 chars of HTML:")
print(reset_html[:500])


# Test 3: Email Verification template
print("\n" + "=" * 60)
print("✉️ Test 3: Email Verification Template")
print("=" * 60)

verification_context = {
    "user_name": "Jane Smith",
    "verify_url": "https://example.com/verify/token123",
    "verification_code": "123456"
}

verification_html = template_service.render_template("email_verification", verification_context)

print(f"Template rendered: {len(verification_html)} characters")
print(f"Subject: {template_service.get_subject('email_verification', verification_context)}")


# Test 4: Notification template (success type)
print("\n" + "=" * 60)
print("🔔 Test 4: Notification Template (Success)")
print("=" * 60)

notification_context = {
    "user_name": "Test User",
    "notification_title": "Payment Successful",
    "notification_type": "success",
    "notification_heading": "Payment Confirmed",
    "notification_text": "Your payment was processed successfully.",
    "action_url": "https://example.com/dashboard",
    "action_text": "View Dashboard"
}

notification_html = template_service.render_template("notification", notification_context)

print(f"Template rendered: {len(notification_html)} characters")
print(f"Subject: {template_service.get_subject('notification', notification_context)}")


print("\n" + "=" * 60)
print("✅ All template rendering tests passed!")
print("=" * 60)
