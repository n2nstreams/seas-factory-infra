import { Resend } from 'resend'

// Types for notification system
export interface EmailRecipient {
  email: string
  name?: string
}

export interface EmailTemplate {
  name: string
  subject: string
  html: string
  text?: string
  variables: string[]
}

export interface NotificationRequest {
  type: 'email' | 'sms' | 'push'
  template: string
  recipient: EmailRecipient
  variables: Record<string, any>
  correlationId?: string
  priority?: 'low' | 'normal' | 'high'
}

export interface NotificationResult {
  success: boolean
  message: string
  provider: string
  correlationId?: string
  timestamp: Date
  metadata?: Record<string, any>
}

// Email templates registry
export const EMAIL_TEMPLATES: Record<string, EmailTemplate> = {
  welcome: {
    name: 'welcome',
    subject: '🚀 Welcome to SaaS Factory, {{user_name}}!',
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Welcome to SaaS Factory</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%);">
          <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); overflow: hidden;">
              <div style="background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 600;">🚀 Welcome to SaaS Factory!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Your AI-powered development journey starts now</p>
              </div>
              <div style="padding: 40px 30px;">
                <div style="font-size: 18px; color: #2d3748; margin-bottom: 20px;">Hi {{user_name}}! 👋</div>
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 30px;">
                  Welcome to SaaS Factory! We're thrilled to have you join our community of innovators who are building the future with AI-powered development tools.
                </div>
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 30px;">
                  Your <strong>{{plan_name}}</strong> account is now active and ready to go. You have {{trial_days}} days to explore all our features.
                </div>
                <div style="text-align: center; margin: 30px 0;">
                  <a href="{{dashboard_url}}" style="display: inline-block; background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%); color: white; text-decoration: none; padding: 15px 30px; border-radius: 12px; font-weight: 600; font-size: 16px; box-shadow: 0 10px 20px rgba(90, 113, 90, 0.3);">
                    Access Your Dashboard →
                  </a>
                </div>
                <div style="background: rgba(90, 113, 90, 0.05); border-radius: 12px; padding: 25px; margin: 30px 0;">
                  <h3 style="color: #5a715a; margin: 0 0 15px 0; font-size: 18px;">🎯 What You Can Do Now:</h3>
                  <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #4a5568;">✓ Submit your first idea and watch our AI agents work</li>
                    <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #4a5568;">✓ Explore tech stack recommendations tailored to your project</li>
                    <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #4a5568;">✓ Generate Figma designs automatically</li>
                    <li style="padding: 8px 0; padding-left: 25px; position: relative; color: #4a5568;">✓ Get production-ready code with comprehensive testing</li>
                  </ul>
                </div>
              </div>
              <div style="background: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid rgba(0, 0, 0, 0.05);">
                <p style="margin: 5px 0; color: #718096; font-size: 14px;"><strong>SaaS Factory Team</strong></p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">Building tomorrow's applications today</p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">© 2025 SaaS Factory. All rights reserved.</p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">
                  <a href="#" style="color: #718096;">Unsubscribe</a> |
                  <a href="#" style="color: #718096;">Privacy Policy</a>
                </p>
              </div>
            </div>
          </div>
        </body>
      </html>
    `,
    text: `
      Welcome to SaaS Factory!
      
      Hi {{user_name}}!
      
      Welcome to SaaS Factory! We're thrilled to have you join our community of innovators who are building the future with AI-powered development tools.
      
      Your {{plan_name}} account is now active and ready to go. You have {{trial_days}} days to explore all our features.
      
      Access Your Dashboard: {{dashboard_url}}
      
      What You Can Do Now:
      ✓ Submit your first idea and watch our AI agents work
      ✓ Explore tech stack recommendations tailored to your project
      ✓ Generate Figma designs automatically
      ✓ Get production-ready code with comprehensive testing
      
      SaaS Factory Team
      Building tomorrow's applications today
      
      © 2025 SaaS Factory. All rights reserved.
    `,
    variables: ['user_name', 'plan_name', 'trial_days', 'dashboard_url']
  },
  payment_receipt: {
    name: 'payment_receipt',
    subject: '💳 Payment Received - SaaS Factory',
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Payment Receipt - SaaS Factory</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%);">
          <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); overflow: hidden;">
              <div style="background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 600;">💳 Payment Received</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Thank you for your payment!</p>
              </div>
              <div style="padding: 40px 30px;">
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 20px;">Hi {{user_name}},</div>
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 20px;">
                  We've successfully processed your payment for SaaS Factory. Here are the details of your transaction:
                </div>
                <div style="background: rgba(90, 113, 90, 0.05); border-radius: 12px; padding: 25px; margin: 20px 0;">
                  <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                    <span style="color: #4a5568;">Invoice #</span>
                    <span style="color: #2d3748; font-weight: 500;">{{invoice_number}}</span>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                    <span style="color: #4a5568;">Date</span>
                    <span style="color: #2d3748; font-weight: 500;">{{invoice_date}}</span>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                    <span style="color: #4a5568;">Plan</span>
                    <span style="color: #2d3748; font-weight: 500;">{{plan_name}}</span>
                  </div>
                  <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05);">
                    <span style="color: #4a5568;">Total Amount</span>
                    <span style="background: #5a715a; color: white; border-radius: 8px; padding: 5px 12px; font-weight: 600;">${{amount}} {{currency}}</span>
                  </div>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                  <a href="{{dashboard_url}}" style="display: inline-block; background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%); color: white; text-decoration: none; padding: 12px 25px; border-radius: 8px; font-weight: 500; font-size: 14px; margin: 0 10px;">
                    Go to Dashboard
                  </a>
                </div>
              </div>
              <div style="background: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid rgba(0, 0, 0, 0.05);">
                <p style="margin: 5px 0; color: #718096; font-size: 14px;"><strong>SaaS Factory Team</strong></p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">Building tomorrow's applications today</p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">© 2025 SaaS Factory. All rights reserved.</p>
              </div>
            </div>
          </div>
        </body>
      </html>
    `,
    text: `
      Payment Received - SaaS Factory
      
      Hi {{user_name}},
      
      We've successfully processed your payment for SaaS Factory. Here are the details of your transaction:
      
      Invoice #: {{invoice_number}}
      Date: {{invoice_date}}
      Plan: {{plan_name}}
      Total Amount: ${{amount}} {{currency}}
      
      Go to Dashboard: {{dashboard_url}}
      
      SaaS Factory Team
      Building tomorrow's applications today
      
      © 2025 SaaS Factory. All rights reserved.
    `,
    variables: ['user_name', 'invoice_number', 'invoice_date', 'plan_name', 'amount', 'currency', 'dashboard_url']
  },
  password_reset: {
    name: 'password_reset',
    subject: '🔐 Password Reset Request - SaaS Factory',
    html: `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Password Reset - SaaS Factory</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%);">
          <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1); overflow: hidden;">
              <div style="background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 28px; font-weight: 600;">🔐 Password Reset</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Reset your SaaS Factory password</p>
              </div>
              <div style="padding: 40px 30px;">
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 20px;">Hi {{user_name}},</div>
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 30px;">
                  We received a request to reset your password for your SaaS Factory account. Click the button below to create a new password:
                </div>
                <div style="text-align: center; margin: 30px 0;">
                  <a href="{{reset_url}}" style="display: inline-block; background: linear-gradient(135deg, #5a715a 0%, #8ba86e 100%); color: white; text-decoration: none; padding: 15px 30px; border-radius: 12px; font-weight: 600; font-size: 16px; box-shadow: 0 10px 20px rgba(90, 113, 90, 0.3);">
                    Reset Password
                  </a>
                </div>
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 20px;">
                  This link will expire in {{expiry_hours}} hours. If you didn't request this password reset, you can safely ignore this email.
                </div>
                <div style="font-size: 16px; line-height: 1.6; color: #4a5568; margin-bottom: 20px;">
                  If the button doesn't work, copy and paste this link into your browser: {{reset_url}}
                </div>
              </div>
              <div style="background: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid rgba(0, 0, 0, 0.05);">
                <p style="margin: 5px 0; color: #718096; font-size: 14px;"><strong>SaaS Factory Team</strong></p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">Building tomorrow's applications today</p>
                <p style="margin: 5px 0; color: #718096; font-size: 14px;">© 2025 SaaS Factory. All rights reserved.</p>
              </div>
            </div>
          </div>
        </body>
      </html>
    `,
    text: `
      Password Reset - SaaS Factory
      
      Hi {{user_name}},
      
      We received a request to reset your password for your SaaS Factory account. Click the link below to create a new password:
      
      Reset Password: {{reset_url}}
      
      This link will expire in {{expiry_hours}} hours. If you didn't request this password reset, you can safely ignore this email.
      
      SaaS Factory Team
      Building tomorrow's applications today
      
      © 2025 SaaS Factory. All rights reserved.
    `,
    variables: ['user_name', 'reset_url', 'expiry_hours']
  }
}

// Notification router with dual providers
export class NotificationRouter {
  private resend: Resend | null = null
  private supabaseEmailEnabled: boolean = false
  private featureFlagEnabled: boolean = false

  constructor() {
    // Initialize Resend if API key is available
    const resendApiKey = process.env.RESEND_API_KEY
    if (resendApiKey) {
      this.resend = new Resend(resendApiKey)
    }

    // Check if Supabase email is enabled
    this.supabaseEmailEnabled = !!process.env.SUPABASE_EMAIL_ENABLED

    // Check feature flag
    this.featureFlagEnabled = process.env.NEXT_PUBLIC_FEATURE_EMAILS_V2 === 'true'
  }

  // Send notification with dual provider support
  async sendNotification(request: NotificationRequest): Promise<NotificationResult> {
    const correlationId = request.correlationId || this.generateCorrelationId()
    const timestamp = new Date()

    try {
      // Check if new email system is enabled via feature flag
      if (!this.featureFlagEnabled) {
        // Fall back to legacy system
        return {
          success: false,
          message: 'New email system disabled by feature flag',
          provider: 'legacy',
          correlationId,
          timestamp,
          metadata: { fallback: true }
        }
      }

      // Send email notification
      if (request.type === 'email') {
        return await this.sendEmail(request, correlationId, timestamp)
      }

      // Unsupported notification type
      return {
        success: false,
        message: `Unsupported notification type: ${request.type}`,
        provider: 'none',
        correlationId,
        timestamp
      }

    } catch (error) {
      console.error('Notification error:', error)
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        provider: 'error',
        correlationId,
        timestamp,
        metadata: { error: true }
      }
    }
  }

  // Send email with dual provider support
  private async sendEmail(request: NotificationRequest, correlationId: string, timestamp: Date): Promise<NotificationResult> {
    const template = EMAIL_TEMPLATES[request.template]
    if (!template) {
      return {
        success: false,
        message: `Email template not found: ${request.template}`,
        provider: 'none',
        correlationId,
        timestamp
      }
    }

    // Validate required variables
    const missingVars = template.variables.filter(v => !request.variables[v])
    if (missingVars.length > 0) {
      return {
        success: false,
        message: `Missing required variables: ${missingVars.join(', ')}`,
        provider: 'none',
        correlationId,
        timestamp
      }
    }

    // Try Resend first (preferred provider)
    if (this.resend) {
      try {
        const result = await this.sendViaResend(request, template, correlationId)
        if (result.success) {
          return result
        }
      } catch (error) {
        console.warn('Resend failed, trying Supabase email:', error)
      }
    }

    // Fall back to Supabase email
    if (this.supabaseEmailEnabled) {
      try {
        return await this.sendViaSupabase(request, template, correlationId)
      } catch (error) {
        console.error('Supabase email failed:', error)
      }
    }

    // All providers failed
    return {
      success: false,
      message: 'All email providers failed',
      provider: 'none',
      correlationId,
      timestamp,
      metadata: { allProvidersFailed: true }
    }
  }

  // Send via Resend
  private async sendViaResend(request: NotificationRequest, template: EmailTemplate, correlationId: string): Promise<NotificationResult> {
    if (!this.resend) {
      throw new Error('Resend not configured')
    }

    const subject = this.renderTemplate(template.subject, request.variables)
    const html = this.renderTemplate(template.html, request.variables)
    const text = template.text ? this.renderTemplate(template.text, request.variables) : undefined

    const emailData: any = {
      from: process.env.FROM_EMAIL || 'noreply@saasfactory.com',
      to: request.recipient.email,
      subject,
      html,
      headers: {
        'X-Correlation-ID': correlationId,
        'X-Template': template.name,
        'X-Provider': 'resend'
      }
    }

    if (request.recipient.name) {
      emailData.to = [{ email: request.recipient.email, name: request.recipient.name }]
    }

    if (text) {
      emailData.text = text
    }

    const response = await this.resend.emails.send(emailData)

    if (response.error) {
      throw new Error(`Resend error: ${response.error.message}`)
    }

    return {
      success: true,
      message: 'Email sent successfully via Resend',
      provider: 'resend',
      correlationId,
      timestamp: new Date(),
      metadata: {
        messageId: response.data?.id,
        template: template.name
      }
    }
  }

  // Send via Supabase email (placeholder for future implementation)
  private async sendViaSupabase(request: NotificationRequest, template: EmailTemplate, correlationId: string): Promise<NotificationResult> {
    // TODO: Implement Supabase email sending
    // For now, return a placeholder response
    return {
      success: false,
      message: 'Supabase email not yet implemented',
      provider: 'supabase',
      correlationId,
      timestamp: new Date(),
      metadata: { notImplemented: true }
    }
  }

  // Render template with variables
  private renderTemplate(template: string, variables: Record<string, any>): string {
    let rendered = template
    for (const [key, value] of Object.entries(variables)) {
      const placeholder = `{{${key}}}`
      rendered = rendered.replace(new RegExp(placeholder, 'g'), String(value))
    }
    return rendered
  }

  // Generate correlation ID
  private generateCorrelationId(): string {
    return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  // Get available templates
  getAvailableTemplates(): string[] {
    return Object.keys(EMAIL_TEMPLATES)
  }

  // Get template details
  getTemplateDetails(templateName: string): EmailTemplate | null {
    return EMAIL_TEMPLATES[templateName] || null
  }

  // Check provider status
  getProviderStatus(): Record<string, boolean> {
    return {
      resend: !!this.resend,
      supabase: this.supabaseEmailEnabled,
      featureFlag: this.featureFlagEnabled
    }
  }
}

// Global notification router instance
export const notificationRouter = new NotificationRouter()

// Convenience functions
export async function sendEmail(
  template: string,
  recipient: EmailRecipient,
  variables: Record<string, any>,
  correlationId?: string
): Promise<NotificationResult> {
  return notificationRouter.sendNotification({
    type: 'email',
    template,
    recipient,
    variables,
    correlationId
  })
}

export async function sendWelcomeEmail(
  recipient: EmailRecipient,
  userData: { user_name: string; plan_name: string; trial_days: number; dashboard_url: string }
): Promise<NotificationResult> {
  return sendEmail('welcome', recipient, userData)
}

export async function sendPaymentReceiptEmail(
  recipient: EmailRecipient,
  receiptData: { user_name: string; invoice_number: string; invoice_date: string; plan_name: string; amount: number; currency: string; dashboard_url: string }
): Promise<NotificationResult> {
  return sendEmail('payment_receipt', recipient, receiptData)
}

export async function sendPasswordResetEmail(
  recipient: EmailRecipient,
  resetData: { user_name: string; reset_url: string; expiry_hours: number }
): Promise<NotificationResult> {
  return sendEmail('password_reset', recipient, resetData)
}
