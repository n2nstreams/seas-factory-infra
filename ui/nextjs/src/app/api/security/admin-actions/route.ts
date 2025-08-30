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
    const requiredFields = ['action_type', 'action_category', 'target_type', 'target_id', 'reason']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Create admin action audit record
    const adminAction = {
      tenant_id: tenantId,
      admin_user_id: body.admin_user_id || '00000000-0000-0000-0000-000000000000', // Default for testing
      action_type: body.action_type,
      action_category: body.action_category,
      target_type: body.target_type,
      target_id: body.target_id,
      action_data: body.action_data || {},
      old_values: body.old_values || null,
      new_values: body.new_values || null,
      reason: body.reason,
      business_justification: body.business_justification || null,
      risk_assessment: body.risk_assessment || 'low',
      requires_approval: body.requires_approval || false,
      ip_address: request.headers.get('X-Forwarded-For') || request.headers.get('X-Real-IP') || '127.0.0.1',
      user_agent: request.headers.get('User-Agent') || 'SecurityValidator/1.0',
      session_id: body.session_id || null,
      correlation_id: body.correlation_id || null,
      action_started_at: new Date().toISOString(),
      action_completed_at: new Date().toISOString(),
      duration_ms: body.duration_ms || 0
    }

    const { data, error } = await supabase
      .from('admin_actions_audit')
      .insert([adminAction])
      .select()
      .single()

    if (error) {
      console.error('Error creating admin action audit:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to create admin action audit record',
        details: error.message,
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      data: data,
      message: 'Admin action logged successfully',
      timestamp: new Date().toISOString(),
    }, { status: 201 })

  } catch (error) {
    console.error('Admin actions API error:', error)
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
    const actionType = searchParams.get('action_type')
    const riskLevel = searchParams.get('risk_level')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    let query = supabase
      .from('admin_actions_audit')
      .select('*')
      .eq('tenant_id', tenantId)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1)

    if (actionType) {
      query = query.eq('action_type', actionType)
    }

    if (riskLevel) {
      query = query.eq('risk_assessment', riskLevel)
    }

    const { data, error, count } = await query

    if (error) {
      console.error('Error fetching admin actions:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch admin actions',
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
    console.error('Admin actions API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
