#!/usr/bin/env python3
"""
Test script for Email Service
Night 55: Test SendGrid integration and email templates

This script tests:
- SendGrid API connectivity
- Email template rendering
- Welcome email functionality
- Payment receipt email functionality
"""

import os
import asyncio
import logging
from datetime import datetime
import sys

# Add agents/shared to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents', 'shared'))

from email_service import (
    get_email_service, 
    EmailRecipient, 
    WelcomeEmailData, 
    PaymentReceiptData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_service():
    """Test the email service functionality"""
    print("🧪 Testing SaaS Factory Email Service")
    print("=" * 50)
    
    # Initialize email service
    email_service = get_email_service()
    
    # Check if SendGrid is configured
    if not email_service.enabled:
        print("❌ SendGrid not configured. Set SENDGRID_API_KEY environment variable.")
        print("   You can get a free SendGrid account at: https://signup.sendgrid.com/")
        return
    
    print("✅ SendGrid API key found")
    print(f"📧 From email: {email_service.from_email}")
    print(f"👤 From name: {email_service.from_name}")
    print()
    
    # Test email recipient (change this to your email for testing)
    test_email = os.getenv("TEST_EMAIL", "test@example.com")
    print(f"📬 Test recipient: {test_email}")
    print()
    
    # Test 1: Welcome Email
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
            trial_days=14
        )
        
        result = await email_service.send_welcome_email(recipient, welcome_data)
        
        if result["status"] == "sent":
            print(f"✅ Welcome email sent successfully!")
            print(f"   Recipient: {result['recipient']}")
        else:
            print(f"❌ Welcome email failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error testing welcome email: {e}")
    
    print()
    
    # Test 2: Payment Receipt Email
    print("🎯 Test 2: Payment Receipt Email")
    print("-" * 30)
    
    try:
        recipient = EmailRecipient(email=test_email, name="Test User")
        receipt_data = PaymentReceiptData(
            user_name="Test User",
            user_email=test_email,
            invoice_number="INV-20250115-TEST001",
            invoice_date=datetime.now().strftime('%B %d, %Y'),
            amount=99.00,
            currency="USD",
            plan_name="Pro Plan",
            billing_period="Monthly",
            next_billing_date="February 15, 2025"
        )
        
        result = await email_service.send_payment_receipt_email(recipient, receipt_data)
        
        if result["status"] == "sent":
            print(f"✅ Payment receipt email sent successfully!")
            print(f"   Recipient: {result['recipient']}")
            print(f"   Invoice: {result['invoice_number']}")
        else:
            print(f"❌ Payment receipt email failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error testing payment receipt email: {e}")
    
    print()
    
    # Test 3: Template Rendering (without sending)
    print("🎯 Test 3: Template Rendering")
    print("-" * 30)
    
    try:
        # Test HTML template rendering
        html_template = email_service.jinja_env.get_template("welcome.html")
        html_content = html_template.render(
            user_name="Test User",
            plan_name="Starter",
            trial_days=14,
            login_url="https://test.com/login",
            dashboard_url="https://test.com/dashboard"
        )
        
        if "Test User" in html_content and "Starter" in html_content:
            print("✅ HTML template rendering successful")
        else:
            print("❌ HTML template rendering failed")
        
        # Test text template rendering
        text_template = email_service.jinja_env.get_template("welcome.txt")
        text_content = text_template.render(
            user_name="Test User",
            plan_name="Starter",
            trial_days=14,
            login_url="https://test.com/login",
            dashboard_url="https://test.com/dashboard"
        )
        
        if "Test User" in text_content and "Starter" in text_content:
            print("✅ Text template rendering successful")
        else:
            print("❌ Text template rendering failed")
            
    except Exception as e:
        print(f"❌ Error testing template rendering: {e}")
    
    print()
    print("🎉 Email service testing completed!")
    print()
    print("Next steps:")
    print("1. Check your email for test messages")
    print("2. Verify email design matches the glassmorphism theme")
    print("3. Test the links in the email")
    print("4. Check spam folder if emails don't appear in inbox")

def check_environment():
    """Check required environment variables"""
    print("🔍 Checking Environment Configuration")
    print("=" * 40)
    
    required_vars = [
        "SENDGRID_API_KEY",
    ]
    
    optional_vars = [
        "FROM_EMAIL",
        "FROM_NAME", 
        "REPLY_TO_EMAIL",
        "TEST_EMAIL"
    ]
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20}")  # Mask the actual value
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
        print()
        print("To set up SendGrid:")
        print("1. Sign up at: https://signup.sendgrid.com/")
        print("2. Create an API key in Settings > API Keys")
        print("3. Set environment variable: export SENDGRID_API_KEY='your-api-key'")
        print("4. Optional: export TEST_EMAIL='your-email@domain.com'")
        print()
        return False
    
    return True

async def main():
    """Main test function"""
    print("📧 SaaS Factory Email Service Test")
    print("=" * 50)
    print()
    
    # Check environment
    if not check_environment():
        return
    
    print()
    
    # Test email service
    await test_email_service()

if __name__ == "__main__":
    asyncio.run(main()) 