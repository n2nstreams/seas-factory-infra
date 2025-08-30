import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/projects - Get all projects for a tenant
export async function GET(request: NextRequest) {
  try {
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Get query parameters
    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')
    const projectType = searchParams.get('project_type')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')

    // Build query
    let query = supabase
      .from('projects')
      .select('*, users(name, email)')
      .eq('tenant_id', tenantId)

    // Apply filters
    if (status) query = query.eq('status', status)
    if (projectType) query = query.eq('project_type', projectType)

    // Apply pagination
    query = query.range(offset, offset + limit - 1)
    query = query.order('created_at', { ascending: false })

    const { data: projects, error } = await query

    if (error) {
      console.error('Error fetching projects:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch projects',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Get total count for pagination
    let countQuery = supabase
      .from('projects')
      .select('*', { count: 'exact', head: true })
      .eq('tenant_id', tenantId)

    if (status) countQuery = countQuery.eq('status', status)
    if (projectType) countQuery = countQuery.eq('project_type', projectType)

    const { count, error: countError } = await countQuery

    if (countError) {
      console.error('Error counting projects:', countError)
    }

    return NextResponse.json({
      success: true,
      projects,
      pagination: {
        limit,
        offset,
        total: count || 0,
        has_more: (offset + limit) < (count || 0)
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Projects API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// POST /api/projects - Create a new project
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    
    if (!tenantId || !userId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID and User ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate required fields
    const requiredFields = ['name', 'description', 'project_type']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Create project data
    const projectData = {
      tenant_id: tenantId,
      name: body.name,
      description: body.description,
      project_type: body.project_type,
      status: body.status || 'active',
      config: body.config || {},
      tech_stack: body.tech_stack || {},
      design_config: body.design_config || {},
      created_by: userId
    }

    // Insert project
    const { data: project, error } = await supabase
      .from('projects')
      .insert(projectData)
      .select('*, users(name, email)')
      .single()

    if (error) {
      console.error('Error creating project:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to create project',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Create audit log
    const auditLog = {
      tenant_id: tenantId,
      user_id: userId,
      table_name: 'projects',
      record_id: project.id,
      operation: 'INSERT',
      new_values: project,
      ip_address: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
      user_agent: request.headers.get('user-agent')
    }

    await supabase
      .from('audit_logs')
      .insert(auditLog)

    return NextResponse.json({
      success: true,
      project,
      message: 'Project created successfully',
      timestamp: new Date().toISOString(),
    }, { status: 201 })

  } catch (error) {
    console.error('Projects API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
