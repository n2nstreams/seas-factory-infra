import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/ideas - Get all ideas for a tenant
export async function GET(request: NextRequest) {
  try {
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    const userRole = request.headers.get('X-User-Role')
    
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
    const priority = searchParams.get('priority')
    const category = searchParams.get('category')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')

    // Build query
    let query = supabase
      .from('ideas')
      .select('*, users(name, email)')
      .eq('tenant_id', tenantId)

    // Apply filters
    if (status) query = query.eq('status', status)
    if (priority) query = query.eq('priority', priority)
    if (category) query = query.eq('category', category)

    // Apply pagination
    query = query.range(offset, offset + limit - 1)
    query = query.order('created_at', { ascending: false })

    const { data: ideas, error } = await query

    if (error) {
      console.error('Error fetching ideas:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch ideas',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Get total count for pagination
    let countQuery = supabase
      .from('ideas')
      .select('*', { count: 'exact', head: true })
      .eq('tenant_id', tenantId)

    if (status) countQuery = countQuery.eq('status', status)
    if (priority) countQuery = countQuery.eq('priority', priority)
    if (category) countQuery = countQuery.eq('category', category)

    const { count, error: countError } = await countQuery

    if (countError) {
      console.error('Error counting ideas:', countError)
    }

    return NextResponse.json({
      success: true,
      ideas,
      pagination: {
        limit,
        offset,
        total: count || 0,
        has_more: (offset + limit) < (count || 0)
      },
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Ideas API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// POST /api/ideas - Submit a new idea
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
    const requiredFields = ['project_name', 'description', 'problem', 'solution']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Create idea data
    const ideaData = {
      tenant_id: tenantId,
      submitted_by: userId,
      project_name: body.project_name,
      description: body.description,
      problem: body.problem,
      solution: body.solution,
      target_audience: body.target_audience || null,
      key_features: body.key_features || null,
      business_model: body.business_model || null,
      category: body.category || 'general',
      priority: body.priority || 'medium',
      status: 'pending',
      timeline: body.timeline || null,
      budget: body.budget || null,
      submission_data: {
        source: body.source || 'web',
        user_agent: request.headers.get('user-agent'),
        ip_address: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip')
      }
    }

    // Insert idea
    const { data: idea, error } = await supabase
      .from('ideas')
      .insert(ideaData)
      .select('*, users(name, email)')
      .single()

    if (error) {
      console.error('Error creating idea:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to create idea',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Create audit log
    const auditLog = {
      tenant_id: tenantId,
      user_id: userId,
      table_name: 'ideas',
      record_id: idea.id,
      operation: 'INSERT',
      new_values: idea,
      ip_address: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
      user_agent: request.headers.get('user-agent')
    }

    await supabase
      .from('audit_logs')
      .insert(auditLog)

    return NextResponse.json({
      success: true,
      idea,
      message: 'Idea submitted successfully',
      timestamp: new Date().toISOString(),
    }, { status: 201 })

  } catch (error) {
    console.error('Ideas API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
