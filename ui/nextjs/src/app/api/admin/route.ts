import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/admin - Get admin dashboard data
export async function GET(request: NextRequest) {
  try {
    const userId = request.headers.get('X-User-ID')
    const tenantId = request.headers.get('X-Tenant-ID')
    const userRole = request.headers.get('X-User-Role')
    
    if (!userId || !tenantId) {
      return NextResponse.json({
        success: false,
        error: 'User ID and Tenant ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Check if user is admin
    if (userRole !== 'admin') {
      return NextResponse.json({
        success: false,
        error: 'Admin access required',
        timestamp: new Date().toISOString(),
      }, { status: 403 })
    }

    // Get tenant statistics
    const { data: tenantStats, error: tenantError } = await supabase
      .from('tenants')
      .select('*')
      .eq('id', tenantId)
      .single()

    if (tenantError) {
      console.error('Error fetching tenant stats:', tenantError)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch tenant statistics',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Get user count
    const { count: userCount, error: userCountError } = await supabase
      .from('users')
      .select('*', { count: 'exact', head: true })
      .eq('tenant_id', tenantId)

    if (userCountError) {
      console.error('Error counting users:', userCountError)
    }

    // Get project count
    const { count: projectCount, error: projectCountError } = await supabase
      .from('projects')
      .select('*', { count: 'exact', head: true })
      .eq('tenant_id', tenantId)

    if (projectCountError) {
      console.error('Error counting projects:', projectCountError)
    }

    // Get idea count by status
    const { data: ideaStats, error: ideaStatsError } = await supabase
      .from('ideas')
      .select('status')
      .eq('tenant_id', tenantId)

    if (ideaStatsError) {
      console.error('Error fetching idea stats:', ideaStatsError)
    }

    // Process idea statistics
    const ideaStatusCounts = ideaStats?.reduce((acc: any, idea: any) => {
      acc[idea.status] = (acc[idea.status] || 0) + 1
      return acc
    }, {}) || {}

    return NextResponse.json({
      success: true,
      dashboard: {
        tenant: tenantStats,
        statistics: {
          users: userCount || 0,
          projects: projectCount || 0,
          ideas: {
            total: ideaStats?.length || 0,
            by_status: ideaStatusCounts
          }
        }
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Admin API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// POST /api/admin - Perform admin actions
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const userId = request.headers.get('X-User-ID')
    const tenantId = request.headers.get('X-Tenant-ID')
    const userRole = request.headers.get('X-User-Role')
    
    if (!userId || !tenantId) {
      return NextResponse.json({
        success: false,
        error: 'User ID and Tenant ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Check if user is admin
    if (userRole !== 'admin') {
      return NextResponse.json({
        success: false,
        error: 'Admin access required',
        timestamp: new Date().toISOString(),
      }, { status: 403 })
    }

    // Validate required fields
    const requiredFields = ['action_type']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    let result: any = {}

    // Handle different admin actions
    switch (body.action_type) {
      case 'update_tenant_settings':
        if (!body.settings) {
          return NextResponse.json({
            success: false,
            error: 'Settings data required for tenant update',
            timestamp: new Date().toISOString(),
          }, { status: 400 })
        }

        const { data: updatedTenant, error: tenantError } = await supabase
          .from('tenants')
          .update({ settings: body.settings })
          .eq('id', tenantId)
          .select()
          .single()

        if (tenantError) {
          console.error('Error updating tenant settings:', tenantError)
          return NextResponse.json({
            success: false,
            error: 'Failed to update tenant settings',
            timestamp: new Date().toISOString(),
          }, { status: 500 })
        }

        result = { tenant: updatedTenant }
        break

      case 'get_audit_logs':
        const { data: auditLogs, error: auditError } = await supabase
          .from('audit_logs')
          .select('*')
          .eq('tenant_id', tenantId)
          .order('created_at', { ascending: false })
          .limit(body.limit || 100)

        if (auditError) {
          console.error('Error fetching audit logs:', auditError)
          return NextResponse.json({
            success: false,
            error: 'Failed to fetch audit logs',
            timestamp: new Date().toISOString(),
          }, { status: 500 })
        }

        result = { audit_logs: auditLogs }
        break

      default:
        return NextResponse.json({
          success: false,
          error: `Unknown action type: ${body.action_type}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
    }

    return NextResponse.json({
      success: true,
      action: body.action_type,
      result,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Admin API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
