#!/usr/bin/env python3
"""
Test script for Email Service (relocated under tests/scripts)
Night 55: Test SendGrid integration and email templates
"""
import os
import asyncio
import logging
from datetime import datetime
import sys

# Ensure project root and shared agents are importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
SHARED_DIR = os.path.join(PROJECT_ROOT, "agents", "shared")
if SHARED_DIR not in sys.path:
    sys.path.append(SHARED_DIR)

from email_service import (  # type: ignore
    get_email_service,
    EmailRecipient,
    WelcomeEmailData,
    PaymentReceiptData,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_email_service():
    print("🧪 Testing SaaS Factory Email Service")
    print("=" * 50)

    email_service = get_email_service()
    if not email_service.enabled:
        print("❌ SendGrid not configured. Set SENDGRID_API_KEY environment variable.")
        return

    print("✅ SendGrid API key found")
    print(f"📧 From email: {email_service.from_email}")
    print(f"👤 From name: {email_service.from_name}")
    print()

    test_email = os.getenv("TEST_EMAIL", "test@example.com")
    print(f"📬 Test recipient: {test_email}")
    print()

    # Welcome Email
    print("🎯 Test 1: Welcome Email")
    print("-" * 30)
    try:
        recipient = EmailRecipient(email=test_email, name="Test User")
        welcome_data = WelcomeEmailData(
            user_name="Test",
            user_email=test_email,
            login_url="https://app.saasfactory.com/login",
            dashboard_url="https://app.saasfactory.com/dashboard",
            plan_name="Pro",
            trial_days=14,
        )
        result = await email_service.send_welcome_email(recipient, welcome_data)
        if result["status"] == "sent":
            print("✅ Welcome email sent successfully!")
        else:
            print(f"❌ Welcome email failed: {result['message']}")
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error testing welcome email: {e}")
    print()

    # Payment Receipt Email
    print("🎯 Test 2: Payment Receipt Email")
    print("-" * 30)
    try:
        recipient = EmailRecipient(email=test_email, name="Test User")
        receipt_data = PaymentReceiptData(
            user_name="Test User",
            user_email=test_email,
            invoice_number="INV-20250115-TEST001",
            invoice_date=datetime.now().strftime("%B %d, %Y"),
            amount=99.00,
            currency="USD",
            plan_name="Pro Plan",
            billing_period="Monthly",
            next_billing_date="February 15, 2025",
        )
        result = await email_service.send_payment_receipt_email(recipient, receipt_data)
        if result["status"] == "sent":
            print("✅ Payment receipt email sent successfully!")
        else:
            print(f"❌ Payment receipt email failed: {result['message']}")
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error testing payment receipt email: {e}")
    print()

    # Template Rendering
    print("🎯 Test 3: Template Rendering")
    print("-" * 30)
    try:
        html_template = email_service.jinja_env.get_template("welcome.html")
        html_content = html_template.render(
            user_name="Test User",
            plan_name="Starter",
            trial_days=14,
            login_url="https://test.com/login",
            dashboard_url="https://test.com/dashboard",
        )
        if "Test User" in html_content and "Starter" in html_content:
            print("✅ HTML template rendering successful")
        else:
            print("❌ HTML template rendering failed")

        text_template = email_service.jinja_env.get_template("welcome.txt")
        text_content = text_template.render(
            user_name="Test User",
            plan_name="Starter",
            trial_days=14,
            login_url="https://test.com/login",
            dashboard_url="https://test.com/dashboard",
        )
        if "Test User" in text_content and "Starter" in text_content:
            print("✅ Text template rendering successful")
        else:
            print("❌ Text template rendering failed")
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error testing template rendering: {e}")

    print()
    print("🎉 Email service testing completed!")


def check_environment() -> bool:
    print("🔍 Checking Environment Configuration")
    print("=" * 40)
    required_vars = ["SENDGRID_API_KEY"]
    optional_vars = ["FROM_EMAIL", "FROM_NAME", "REPLY_TO_EMAIL", "TEST_EMAIL"]
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20}")
        else:
            print(f"❌ {var}: Not set (REQUIRED)")
            all_good = False
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (using default)")
    print()
    if not all_good:
        print("❌ Missing required environment variables!")
        return False
    return True


async def main() -> None:
    print("📧 SaaS Factory Email Service Test")
    print("=" * 50)
    print()
    if not check_environment():
        return
    await test_email_service()


if __name__ == "__main__":
    asyncio.run(main())


