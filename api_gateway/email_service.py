#!/usr/bin/env python3
"""
Email Service Module for SaaS Factory
Night 55: SendGrid integration with email templates

This module provides:
- SendGrid email delivery
- HTML email templates with glassmorphism design
- Welcome emails for new users
- Payment receipt emails for successful transactions
- Template rendering with Jinja2
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, DictLoader

logger = logging.getLogger(__name__)

class EmailType(str, Enum):
    """Email template types"""
    WELCOME = "welcome"
    PAYMENT_RECEIPT = "payment_receipt"
    PASSWORD_RESET = "password_reset"
    SUBSCRIPTION_CONFIRMATION = "subscription_confirmation"
    TRIAL_ENDING = "trial_ending"

@dataclass
class EmailRecipient:
    """Email recipient information"""
    email: str
    name: Optional[str] = None

@dataclass
class EmailTemplate:
    """Email template data"""
    template_type: EmailType
    subject: str
    html_content: str
    text_content: Optional[str] = None

@dataclass
class WelcomeEmailData:
    """Data for welcome email template"""
    user_name: str
    user_email: str
    login_url: str
    dashboard_url: str
    plan_name: str
    trial_days: int = 14

@dataclass
class PaymentReceiptData:
    """Data for payment receipt email template"""
    user_name: str
    user_email: str
    invoice_number: str
    invoice_date: str
    amount: float
    plan_name: str
    billing_period: str
    currency: str = "USD"
    invoice_url: Optional[str] = None
    next_billing_date: Optional[str] = None

class EmailService:
    """Main email service class using SendGrid"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@forge95.com")
        self.from_name = os.getenv("FROM_NAME", "SaaS Factory")
        self.reply_to_email = os.getenv("REPLY_TO_EMAIL", "support@forge95.com")
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY not configured, email sending will be disabled")
            self.enabled = False
        else:
            self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
            self.enabled = True
        
        # Initialize Jinja2 environment with templates
        self.jinja_env = Environment(loader=DictLoader(self._get_email_templates()))
        
        logger.info(f"Email service initialized (enabled: {self.enabled})")
    
    def _get_email_templates(self) -> Dict[str, str]:
        """Get all email templates"""
        return {
            # Welcome email template
            "welcome.html": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to SaaS Factory</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .email-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #6B7B4F 0%, #8BA86E 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 16px;
        }
        .content {
            padding: 40px 30px;
        }
        .greeting {
            font-size: 18px;
            color: #2d3748;
            margin-bottom: 20px;
        }
        .message {
            font-size: 16px;
            line-height: 1.6;
            color: #4a5568;
            margin-bottom: 30px;
        }
        .cta-section {
            text-align: center;
            margin: 30px 0;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #6B7B4F 0%, #8BA86E 100%);
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 0 10px 20px rgba(107, 123, 79, 0.3);
            transition: transform 0.2s;
        }
        .cta-button:hover {
            transform: translateY(-2px);
        }
        .features {
            background: rgba(107, 123, 79, 0.05);
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
        }
        .features h3 {
            color: #6B7B4F;
            margin: 0 0 15px 0;
            font-size: 18px;
        }
        .feature-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .feature-list li {
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
            color: #4a5568;
        }
        .feature-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #6B7B4F;
            font-weight: bold;
        }
        .footer {
            background: #f7fafc;
            padding: 30px;
            text-align: center;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
        }
        .footer p {
            margin: 5px 0;
            color: #718096;
            font-size: 14px;
        }
        .social-links {
            margin: 20px 0;
        }
        .social-links a {
            display: inline-block;
            margin: 0 10px;
            color: #6B7B4F;
            text-decoration: none;
        }
        @media (max-width: 600px) {
            .container { padding: 20px 10px; }
            .content { padding: 30px 20px; }
            .header { padding: 30px 20px; }
            .footer { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="email-card">
            <div class="header">
                <h1>🚀 Welcome to SaaS Factory!</h1>
                <p>Your AI-powered development journey starts now</p>
            </div>
            
            <div class="content">
                <div class="greeting">
                    Hi {{ user_name }}! 👋
                </div>
                
                <div class="message">
                    Welcome to SaaS Factory! We're thrilled to have you join our community of innovators who are building the future with AI-powered development tools.
                </div>
                
                <div class="message">
                    Your <strong>{{ plan_name }}</strong> account is now active and ready to go. You have {{ trial_days }} days to explore all our features and see how our AI agents can transform your ideas into fully-functional applications.
                </div>
                
                <div class="cta-section">
                    <a href="{{ dashboard_url }}" class="cta-button">
                        Access Your Dashboard →
                    </a>
                </div>
                
                <div class="features">
                    <h3>🎯 What You Can Do Now:</h3>
                    <ul class="feature-list">
                        <li>Submit your first idea and watch our AI agents work</li>
                        <li>Explore tech stack recommendations tailored to your project</li>
                        <li>Generate Figma designs automatically</li>
                        <li>Get production-ready code with comprehensive testing</li>
                        <li>Deploy your application to the cloud seamlessly</li>
                    </ul>
                </div>
                
                <div class="message">
                    <strong>Next Steps:</strong><br>
                    1. <a href="{{ login_url }}" style="color: #6B7B4F;">Log into your account</a><br>
                    2. Complete your profile setup<br>
                    3. Submit your first project idea<br>
                    4. Watch the magic happen! ✨
                </div>
                
                <div class="message">
                    Need help getting started? Our team is here to support you every step of the way. Simply reply to this email or visit our help center.
                </div>
            </div>
            
            <div class="footer">
                <p><strong>SaaS Factory Team</strong></p>
                <p>Building tomorrow's applications today</p>
                <div class="social-links">
                    <a href="#">Twitter</a> |
                    <a href="#">LinkedIn</a> |
                    <a href="#">Documentation</a>
                </div>
                <p>© 2025 SaaS Factory. All rights reserved.</p>
                <p>
                    <a href="#" style="color: #718096;">Unsubscribe</a> |
                    <a href="#" style="color: #718096;">Privacy Policy</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
            """,
            
            # Payment receipt template
            "payment_receipt.html": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Receipt - SaaS Factory</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .email-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #6B7B4F 0%, #8BA86E 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 16px;
        }
        .content {
            padding: 40px 30px;
        }
        .receipt-info {
            background: rgba(107, 123, 79, 0.05);
            border-radius: 12px;
            padding: 25px;
            margin: 20px 0;
        }
        .receipt-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }
        .receipt-row:last-child {
            border-bottom: none;
            font-weight: 600;
            font-size: 18px;
            color: #6B7B4F;
        }
        .receipt-label {
            color: #4a5568;
        }
        .receipt-value {
            color: #2d3748;
            font-weight: 500;
        }
        .total-amount {
            background: #6B7B4F;
            color: white;
            border-radius: 8px;
            padding: 5px 12px;
        }
        .message {
            font-size: 16px;
            line-height: 1.6;
            color: #4a5568;
            margin-bottom: 20px;
        }
        .cta-section {
            text-align: center;
            margin: 30px 0;
        }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #6B7B4F 0%, #8BA86E 100%);
            color: white;
            text-decoration: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            margin: 0 10px;
        }
        .footer {
            background: #f7fafc;
            padding: 30px;
            text-align: center;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
        }
        .footer p {
            margin: 5px 0;
            color: #718096;
            font-size: 14px;
        }
        @media (max-width: 600px) {
            .container { padding: 20px 10px; }
            .content { padding: 30px 20px; }
            .header { padding: 30px 20px; }
            .footer { padding: 20px; }
            .receipt-row { flex-direction: column; align-items: flex-start; }
            .receipt-row .receipt-value { margin-top: 5px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="email-card">
            <div class="header">
                <h1>💳 Payment Received</h1>
                <p>Thank you for your payment!</p>
            </div>
            
            <div class="content">
                <div class="message">
                    Hi {{ user_name }},
                </div>
                
                <div class="message">
                    We've successfully processed your payment for SaaS Factory. Here are the details of your transaction:
                </div>
                
                <div class="receipt-info">
                    <div class="receipt-row">
                        <span class="receipt-label">Invoice #</span>
                        <span class="receipt-value">{{ invoice_number }}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Date</span>
                        <span class="receipt-value">{{ invoice_date }}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Plan</span>
                        <span class="receipt-value">{{ plan_name }}</span>
                    </div>
                    <div class="receipt-row">
                        <span class="receipt-label">Billing Period</span>
                        <span class="receipt-value">{{ billing_period }}</span>
                    </div>
                    {% if next_billing_date %}
                    <div class="receipt-row">
                        <span class="receipt-label">Next Billing</span>
                        <span class="receipt-value">{{ next_billing_date }}</span>
                    </div>
                    {% endif %}
                    <div class="receipt-row">
                        <span class="receipt-label">Total Amount</span>
                        <span class="receipt-value total-amount">${{ "%.2f"|format(amount) }} {{ currency }}</span>
                    </div>
                </div>
                
                <div class="message">
                    Your {{ plan_name }} subscription is now active and you have full access to all features. Start building amazing applications with our AI-powered development platform!
                </div>
                
                <div class="cta-section">
                    <a href="{{ dashboard_url }}" class="cta-button">
                        Go to Dashboard
                    </a>
                    {% if invoice_url %}
                    <a href="{{ invoice_url }}" class="cta-button">
                        Download Invoice
                    </a>
                    {% endif %}
                </div>
                
                <div class="message">
                    <strong>Questions about your billing?</strong><br>
                    Our support team is here to help. Reply to this email or contact us at support@saasfactory.com.
                </div>
            </div>
            
            <div class="footer">
                <p><strong>SaaS Factory Team</strong></p>
                <p>Building tomorrow's applications today</p>
                <p>© 2025 SaaS Factory. All rights reserved.</p>
                <p>
                    <a href="#" style="color: #718096;">Billing Portal</a> |
                    <a href="#" style="color: #718096;">Support</a> |
                    <a href="#" style="color: #718096;">Privacy Policy</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
            """,
            
            # Text versions
            "welcome.txt": """
Welcome to SaaS Factory, {{ user_name }}!

We're thrilled to have you join our community of innovators who are building the future with AI-powered development tools.

Your {{ plan_name }} account is now active and ready to go. You have {{ trial_days }} days to explore all our features and see how our AI agents can transform your ideas into fully-functional applications.

What You Can Do Now:
• Submit your first idea and watch our AI agents work
• Explore tech stack recommendations tailored to your project  
• Generate Figma designs automatically
• Get production-ready code with comprehensive testing
• Deploy your application to the cloud seamlessly

Next Steps:
1. Log into your account: {{ login_url }}
2. Complete your profile setup
3. Submit your first project idea
4. Watch the magic happen!

Access Your Dashboard: {{ dashboard_url }}

Need help getting started? Our team is here to support you every step of the way. Simply reply to this email or visit our help center.

Best regards,
The SaaS Factory Team

© 2025 SaaS Factory. All rights reserved.
            """,
            
            "payment_receipt.txt": """
Payment Receipt - SaaS Factory

Hi {{ user_name }},

We've successfully processed your payment for SaaS Factory. Here are the details:

Invoice #: {{ invoice_number }}
Date: {{ invoice_date }}
Plan: {{ plan_name }}
Billing Period: {{ billing_period }}
{% if next_billing_date %}Next Billing: {{ next_billing_date }}{% endif %}
Total Amount: ${{ "%.2f"|format(amount) }} {{ currency }}

Your {{ plan_name }} subscription is now active and you have full access to all features. Start building amazing applications with our AI-powered development platform!

Access your dashboard: {{ dashboard_url }}
{% if invoice_url %}Download invoice: {{ invoice_url }}{% endif %}

Questions about your billing? Our support team is here to help. Reply to this email or contact us at support@saasfactory.com.

Best regards,
The SaaS Factory Team

© 2025 SaaS Factory. All rights reserved.
            """
        }
    
    async def send_welcome_email(self, recipient: EmailRecipient, data: WelcomeEmailData) -> Dict[str, Any]:
        """Send welcome email to new user"""
        try:
            if not self.enabled:
                logger.warning("Email service disabled, skipping welcome email")
                return {"status": "disabled", "message": "Email service not configured"}
            
            # Render templates
            html_template = self.jinja_env.get_template("welcome.html")
            text_template = self.jinja_env.get_template("welcome.txt")
            
            template_data = {
                "user_name": data.user_name,
                "user_email": data.user_email,
                "login_url": data.login_url,
                "dashboard_url": data.dashboard_url,
                "plan_name": data.plan_name,
                "trial_days": data.trial_days
            }
            
            html_content = html_template.render(**template_data)
            text_content = text_template.render(**template_data)
            
            # Create email
            mail = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(recipient.email, recipient.name),
                subject=f"🚀 Welcome to SaaS Factory, {data.user_name}!",
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            # Set reply-to
            mail.reply_to = Email(self.reply_to_email)
            
            # Send email
            response = self.sg.send(mail)
            
            if response.status_code == 202:
                logger.info(f"Welcome email sent successfully to {recipient.email}")
                return {
                    "status": "sent",
                    "message": "Welcome email sent successfully",
                    "recipient": recipient.email
                }
            else:
                logger.warning(f"Welcome email send returned status: {response.status_code}")
                return {
                    "status": "error", 
                    "message": f"Email send failed with status: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_payment_receipt_email(self, recipient: EmailRecipient, data: PaymentReceiptData) -> Dict[str, Any]:
        """Send payment receipt email"""
        try:
            if not self.enabled:
                logger.warning("Email service disabled, skipping payment receipt email")
                return {"status": "disabled", "message": "Email service not configured"}
            
            # Render templates
            html_template = self.jinja_env.get_template("payment_receipt.html")
            text_template = self.jinja_env.get_template("payment_receipt.txt")
            
            template_data = {
                "user_name": data.user_name,
                "user_email": data.user_email,
                "invoice_number": data.invoice_number,
                "invoice_date": data.invoice_date,
                "amount": data.amount,
                "currency": data.currency,
                "plan_name": data.plan_name,
                "billing_period": data.billing_period,
                "invoice_url": data.invoice_url,
                "next_billing_date": data.next_billing_date,
                "dashboard_url": os.getenv("DASHBOARD_URL", "https://www.forge95.com/dashboard")
            }
            
            html_content = html_template.render(**template_data)
            text_content = text_template.render(**template_data)
            
            # Create email
            mail = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(recipient.email, recipient.name),
                subject=f"💳 Payment Receipt - Invoice #{data.invoice_number}",
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            # Set reply-to
            mail.reply_to = Email(self.reply_to_email)
            
            # Send email
            response = self.sg.send(mail)
            
            if response.status_code == 202:
                logger.info(f"Payment receipt email sent successfully to {recipient.email}")
                return {
                    "status": "sent",
                    "message": "Payment receipt email sent successfully",
                    "recipient": recipient.email,
                    "invoice_number": data.invoice_number
                }
            else:
                logger.warning(f"Payment receipt email send returned status: {response.status_code}")
                return {
                    "status": "error", 
                    "message": f"Email send failed with status: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error sending payment receipt email: {e}")
            return {"status": "error", "message": str(e)}
    
    async def send_custom_email(self, recipient: EmailRecipient, subject: str, 
                              html_content: str, text_content: Optional[str] = None) -> Dict[str, Any]:
        """Send custom email"""
        try:
            if not self.enabled:
                logger.warning("Email service disabled, skipping custom email")
                return {"status": "disabled", "message": "Email service not configured"}
            
            # Create email
            mail = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(recipient.email, recipient.name),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if text_content:
                mail.plain_text_content = Content("text/plain", text_content)
            
            # Set reply-to
            mail.reply_to = Email(self.reply_to_email)
            
            # Send email
            response = self.sg.send(mail)
            
            if response.status_code == 202:
                logger.info(f"Custom email sent successfully to {recipient.email}")
                return {
                    "status": "sent",
                    "message": "Custom email sent successfully",
                    "recipient": recipient.email
                }
            else:
                logger.warning(f"Custom email send returned status: {response.status_code}")
                return {
                    "status": "error", 
                    "message": f"Email send failed with status: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error sending custom email: {e}")
            return {"status": "error", "message": str(e)}


# Global instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance"""
    return email_service 