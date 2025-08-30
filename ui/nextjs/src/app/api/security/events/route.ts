import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate required fields
    const requiredFields = ['event_type', 'event_category']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Create security event record
    const securityEvent = {
      tenant_id: tenantId,
      event_type: body.event_type,
      event_category: body.event_category,
      event_data: body.event_data || {},
      ip_address: body.ip_address || request.headers.get('X-Forwarded-For') || request.headers.get('X-Real-IP') || '127.0.0.1',
      user_agent: body.user_agent || request.headers.get('User-Agent') || 'SecurityValidator/1.0',
      user_id: body.user_id || null,
      session_id: body.session_id || null,
      correlation_id: body.correlation_id || null,
      risk_level: body.risk_level || 'low',
      severity: body.severity || 'info',
      source: body.source || 'api',
      metadata: body.metadata || {},
      timestamp: new Date().toISOString()
    }

    // For now, we'll log to a simple audit_logs table since we don't have a dedicated security_events table
    // In production, you'd want a dedicated security_events table
    const { data, error } = await supabase
      .from('audit_logs')
      .insert([{
        tenant_id: tenantId,
        user_id: securityEvent.user_id,
        action: securityEvent.event_type,
        category: securityEvent.event_category,
        details: {
          ...securityEvent,
          table_name: 'security_events',
          record_id: null
        },
        ip_address: securityEvent.ip_address,
        user_agent: securityEvent.user_agent,
        timestamp: securityEvent.timestamp
      }])
      .select()
      .single()

    if (error) {
      console.error('Error creating security event:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to create security event record',
        details: error.message,
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      data: data,
      message: 'Security event logged successfully',
      timestamp: new Date().toISOString(),
    }, { status: 201 })

  } catch (error) {
    console.error('Security events API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const tenantId = request.headers.get('X-Tenant-ID')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')
    const eventType = searchParams.get('event_type')
    const eventCategory = searchParams.get('event_category')
    const riskLevel = searchParams.get('risk_level')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    let query = supabase
      .from('audit_logs')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('category', 'security') // Filter for security-related events
      .order('timestamp', { ascending: false })
      .range(offset, offset + limit - 1)

    if (eventType) {
      query = query.eq('action', eventType)
    }

    if (eventCategory) {
      query = query.eq('category', eventCategory)
    }

    const { data, error, count } = await query

    if (error) {
      console.error('Error fetching security events:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch security events',
        details: error.message,
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      data: data || [],
      count: count || 0,
      pagination: {
        limit,
        offset,
        has_more: (data || []).length === limit
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Security events API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
