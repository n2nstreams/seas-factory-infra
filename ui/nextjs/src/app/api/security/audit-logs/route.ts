import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const tenantId = request.headers.get('X-Tenant-ID')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')
    const action = searchParams.get('action')
    const category = searchParams.get('category')
    const userId = searchParams.get('user_id')
    const startDate = searchParams.get('start_date')
    const endDate = searchParams.get('end_date')
    
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
      .order('timestamp', { ascending: false })
      .range(offset, offset + limit - 1)

    if (action) {
      query = query.eq('action', action)
    }

    if (category) {
      query = query.eq('category', category)
    }

    if (userId) {
      query = query.eq('user_id', userId)
    }

    if (startDate) {
      query = query.gte('timestamp', startDate)
    }

    if (endDate) {
      query = query.lte('timestamp', endDate)
    }

    const { data, error, count } = await query

    if (error) {
      console.error('Error fetching audit logs:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch audit logs',
        details: error.message,
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Filter for security-related events if no specific category is specified
    let filteredData = data || []
    if (!category) {
      filteredData = filteredData.filter(log => 
        log.category === 'security' || 
        log.category === 'user_management' || 
        log.category === 'system_config' ||
        log.action?.includes('security') ||
        log.action?.includes('audit')
      )
    }

    return NextResponse.json({
      success: true,
      data: filteredData,
      count: filteredData.length,
      pagination: {
        limit,
        offset,
        has_more: filteredData.length === limit
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Audit logs API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

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
    const requiredFields = ['action', 'category']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Create audit log record
    const auditLog = {
      tenant_id: tenantId,
      user_id: body.user_id || null,
      action: body.action,
      category: body.category,
      details: body.details || {},
      table_name: body.table_name || null,
      record_id: body.record_id || null,
      ip_address: body.ip_address || request.headers.get('X-Forwarded-For') || request.headers.get('X-Real-IP') || '127.0.0.1',
      user_agent: body.user_agent || request.headers.get('User-Agent') || 'SecurityValidator/1.0',
      timestamp: new Date().toISOString()
    }

    const { data, error } = await supabase
      .from('audit_logs')
      .insert([auditLog])
      .select()
      .single()

    if (error) {
      console.error('Error creating audit log:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to create audit log record',
        details: error.message,
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      data: data,
      message: 'Audit log created successfully',
      timestamp: new Date().toISOString(),
    }, { status: 201 })

  } catch (error) {
    console.error('Audit logs API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
