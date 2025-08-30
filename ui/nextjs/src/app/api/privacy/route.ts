import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/privacy - Get privacy settings and consent status
export async function GET(request: NextRequest) {
  try {
    const userId = request.headers.get('X-User-ID')
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!userId || !tenantId) {
      return NextResponse.json({
        success: false,
        error: 'User ID and Tenant ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Get user privacy settings
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('gdpr_consent_given, gdpr_consent_date, privacy_policy_version, dpa_version')
      .eq('id', userId)
      .eq('tenant_id', tenantId)
      .single()

    if (userError) {
      console.error('Error fetching user privacy settings:', userError)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch privacy settings',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Get consent audit trail
    const { data: consentAudit, error: auditError } = await supabase
      .from('privacy_consent_audit')
      .select('*')
      .eq('user_id', userId)
      .eq('tenant_id', tenantId)
      .order('created_at', { ascending: false })

    if (auditError) {
      console.error('Error fetching consent audit:', auditError)
      // Don't fail the entire request for audit data
    }

    return NextResponse.json({
      success: true,
      privacy: {
        gdpr_consent_given: user.gdpr_consent_given,
        gdpr_consent_date: user.gdpr_consent_date,
        privacy_policy_version: user.privacy_policy_version,
        dpa_version: user.dpa_version,
        consent_history: consentAudit || []
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Privacy API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// POST /api/privacy - Update privacy consent
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const userId = request.headers.get('X-User-ID')
    const tenantId = request.headers.get('X-Tenant-ID')
    const userAgent = request.headers.get('user-agent')
    const ipAddress = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip')
    
    if (!userId || !tenantId) {
      return NextResponse.json({
        success: false,
        error: 'User ID and Tenant ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate required fields
    const requiredFields = ['consent_type', 'consent_given']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Record consent in audit table
    const consentAudit = {
      user_id: userId,
      tenant_id: tenantId,
      consent_type: body.consent_type,
      consent_given: body.consent_given,
      consent_date: new Date().toISOString(),
      consent_ip: ipAddress,
      document_version: body.document_version || '1.0',
      user_agent: userAgent,
      notes: body.notes || null
    }

    const { error: auditError } = await supabase
      .from('privacy_consent_audit')
      .insert(consentAudit)

    if (auditError) {
      console.error('Error recording consent audit:', auditError)
      return NextResponse.json({
        success: false,
        error: 'Failed to record consent',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Update user GDPR consent if this is a GDPR consent update
    if (body.consent_type === 'gdpr') {
      const updateData = {
        gdpr_consent_given: body.consent_given,
        gdpr_consent_date: body.consent_given ? new Date().toISOString() : null,
        gdpr_consent_ip: body.consent_given ? ipAddress : null
      }

      if (body.privacy_policy_version) {
        updateData.privacy_policy_version = body.privacy_policy_version
      }
      if (body.dpa_version) {
        updateData.dpa_version = body.dpa_version
      }

      const { error: updateError } = await supabase
        .from('users')
        .update(updateData)
        .eq('id', userId)
        .eq('tenant_id', tenantId)

      if (updateError) {
        console.error('Error updating user GDPR consent:', updateError)
        // Don't fail the entire request for user update
      }
    }

    return NextResponse.json({
      success: true,
      message: 'Consent updated successfully',
      consent: consentAudit,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Privacy API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
