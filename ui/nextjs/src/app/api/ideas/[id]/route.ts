import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/ideas/[id] - Get a specific idea
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const ideaId = params.id
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Get idea by ID within tenant
    const { data: idea, error } = await supabase
      .from('ideas')
      .select('*, users(name, email)')
      .eq('id', ideaId)
      .eq('tenant_id', tenantId)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        return NextResponse.json({
          success: false,
          error: 'Idea not found',
          timestamp: new Date().toISOString(),
        }, { status: 404 })
      }
      
      console.error('Error fetching idea:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch idea',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      idea,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Idea API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// PUT /api/ideas/[id] - Update a specific idea
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const ideaId = params.id
    const body = await request.json()
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    const userRole = request.headers.get('X-User-Role')
    
    if (!tenantId || !userId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID and User ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Check if user can update this idea
    const { data: existingIdea, error: fetchError } = await supabase
      .from('ideas')
      .select('submitted_by, status')
      .eq('id', ideaId)
      .eq('tenant_id', tenantId)
      .single()

    if (fetchError) {
      console.error('Error fetching existing idea:', fetchError)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch idea',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Only allow updates if user is admin or the idea submitter
    if (userRole !== 'admin' && existingIdea.submitted_by !== userId) {
      return NextResponse.json({
        success: false,
        error: 'Not authorized to update this idea',
        timestamp: new Date().toISOString(),
      }, { status: 403 })
    }

    // Build update data
    const updateData: any = {}
    
    // Fields that can be updated by submitter
    if (body.project_name !== undefined) updateData.project_name = body.project_name
    if (body.description !== undefined) updateData.description = body.description
    if (body.problem !== undefined) updateData.problem = body.problem
    if (body.solution !== undefined) updateData.solution = body.solution
    if (body.target_audience !== undefined) updateData.target_audience = body.target_audience
    if (body.key_features !== undefined) updateData.key_features = body.key_features
    if (body.business_model !== undefined) updateData.business_model = body.business_model
    if (body.category !== undefined) updateData.category = body.category
    if (body.priority !== undefined) updateData.priority = body.priority
    if (body.timeline !== undefined) updateData.timeline = body.timeline
    if (body.budget !== undefined) updateData.budget = body.budget

    // Fields that can only be updated by admin
    if (userRole === 'admin') {
      if (body.status !== undefined) updateData.status = body.status
      if (body.admin_notes !== undefined) updateData.admin_notes = body.admin_notes
      if (body.reviewed_by !== undefined) updateData.reviewed_by = body.reviewed_by
      if (body.reviewed_at !== undefined) updateData.reviewed_at = body.reviewed_at
      if (body.project_id !== undefined) updateData.project_id = body.project_id
      if (body.promoted_at !== undefined) updateData.promoted_at = body.promoted_at
    }

    // Update idea
    const { data: idea, error } = await supabase
      .from('ideas')
      .update(updateData)
      .eq('id', ideaId)
      .eq('tenant_id', tenantId)
      .select('*, users(name, email)')
      .single()

    if (error) {
      console.error('Error updating idea:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to update idea',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Create audit log
    const auditLog = {
      tenant_id: tenantId,
      user_id: userId,
      table_name: 'ideas',
      record_id: ideaId,
      operation: 'UPDATE',
      old_values: existingIdea,
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
      message: 'Idea updated successfully',
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Idea API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// DELETE /api/ideas/[id] - Delete a specific idea
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const ideaId = params.id
    const tenantId = request.headers.get('X-Tenant-ID')
    const userId = request.headers.get('X-User-ID')
    const userRole = request.headers.get('X-User-Role')
    
    if (!tenantId || !userId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID and User ID are required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Check if user can delete this idea
    const { data: existingIdea, error: fetchError } = await supabase
      .from('ideas')
      .select('submitted_by, status')
      .eq('id', ideaId)
      .eq('tenant_id', tenantId)
      .single()

    if (fetchError) {
      console.error('Error fetching existing idea:', fetchError)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch idea',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Only allow deletion if user is admin or the idea submitter (and status is pending)
    if (userRole !== 'admin' && (existingIdea.submitted_by !== userId || existingIdea.status !== 'pending')) {
      return NextResponse.json({
        success: false,
        error: 'Not authorized to delete this idea',
        timestamp: new Date().toISOString(),
      }, { status: 403 })
    }

    // Delete idea
    const { error } = await supabase
      .from('ideas')
      .delete()
      .eq('id', ideaId)
      .eq('tenant_id', tenantId)

    if (error) {
      console.error('Error deleting idea:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to delete idea',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    // Create audit log
    const auditLog = {
      tenant_id: tenantId,
      user_id: userId,
      table_name: 'ideas',
      record_id: ideaId,
      operation: 'DELETE',
      old_values: existingIdea,
      ip_address: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip'),
      user_agent: request.headers.get('user-agent')
    }

    await supabase
      .from('audit_logs')
      .insert(auditLog)

    return NextResponse.json({
      success: true,
      message: 'Idea deleted successfully',
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Idea API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
