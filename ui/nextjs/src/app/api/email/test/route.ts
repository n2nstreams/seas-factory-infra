import { NextRequest, NextResponse } from 'next/server'
import { sendWelcomeEmail, sendPaymentReceiptEmail, sendPasswordResetEmail, notificationRouter } from '@/lib/notification-router'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { template, recipient, variables, correlationId } = body

    // Validate request
    if (!template || !recipient || !recipient.email) {
      return NextResponse.json(
        { error: 'Missing required fields: template, recipient.email' },
        { status: 400 }
      )
    }

    // Check if emails_v2 feature flag is enabled
    const emailsV2Enabled = process.env.NEXT_PUBLIC_FEATURE_EMAILS_V2 === 'true'
    
    if (!emailsV2Enabled) {
      return NextResponse.json(
        { 
          error: 'Email system v2 disabled by feature flag',
          featureFlag: 'emails_v2',
          status: 'disabled'
        },
        { status: 403 }
      )
    }

    let result

    // Send email based on template
    switch (template) {
      case 'welcome':
        if (!variables.user_name || !variables.plan_name || !variables.trial_days || !variables.dashboard_url) {
          return NextResponse.json(
            { error: 'Missing required variables for welcome email' },
            { status: 400 }
          )
        }
        result = await sendWelcomeEmail(recipient, variables)
        break

      case 'payment_receipt':
        if (!variables.user_name || !variables.invoice_number || !variables.invoice_date || 
            !variables.plan_name || !variables.amount || !variables.currency || !variables.dashboard_url) {
          return NextResponse.json(
            { error: 'Missing required variables for payment receipt email' },
            { status: 400 }
          )
        }
        result = await sendPaymentReceiptEmail(recipient, variables)
        break

      case 'password_reset':
        if (!variables.user_name || !variables.reset_url || !variables.expiry_hours) {
          return NextResponse.json(
            { error: 'Missing required variables for password reset email' },
            { status: 400 }
          )
        }
        result = await sendPasswordResetEmail(recipient, variables)
        break

      default:
        return NextResponse.json(
          { error: `Unsupported template: ${template}` },
          { status: 400 }
        )
    }

    // Return result
    return NextResponse.json({
      success: true,
      result,
      provider: result.provider,
      correlationId: result.correlationId,
      timestamp: result.timestamp
    })

  } catch (error) {
    console.error('Email test error:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    // Get provider status and available templates
    const providerStatus = notificationRouter.getProviderStatus()
    const availableTemplates = notificationRouter.getAvailableTemplates()
    
    // Get template details
    const templateDetails = availableTemplates.map(name => {
      const template = notificationRouter.getTemplateDetails(name)
      return {
        name: template?.name,
        subject: template?.subject,
        variables: template?.variables
      }
    })

    return NextResponse.json({
      success: true,
      providerStatus,
      availableTemplates,
      templateDetails,
      featureFlag: {
        emails_v2: process.env.NEXT_PUBLIC_FEATURE_EMAILS_V2 === 'true'
      }
    })

  } catch (error) {
    console.error('Email status error:', error)
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
