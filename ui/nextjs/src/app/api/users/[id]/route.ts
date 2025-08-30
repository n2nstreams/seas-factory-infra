import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/users/[id] - Get a specific user
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Get user by ID within tenant
    const { data: user, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .eq('tenant_id', tenantId)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        return NextResponse.json({
          success: false,
          error: 'User not found',
          timestamp: new Date().toISOString(),
        }, { status: 404 })
      }
      
      console.error('Error fetching user:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch user',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      user,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('User API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// PUT /api/users/[id] - Update a specific user
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id
    const body = await request.json()
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Update user data
    const updateData: any = {}
    
    if (body.name !== undefined) updateData.name = body.name
    if (body.role !== undefined) updateData.role = body.role
    if (body.status !== undefined) updateData.status = body.status
    if (body.gdpr_consent_given !== undefined) {
      updateData.gdpr_consent_given = body.gdpr_consent_given
      if (body.gdpr_consent_given) {
        updateData.gdpr_consent_date = new Date().toISOString()
        updateData.gdpr_consent_ip = body.gdpr_consent_ip || null
      }
    }
    if (body.privacy_policy_version !== undefined) updateData.privacy_policy_version = body.privacy_policy_version
    if (body.dpa_version !== undefined) updateData.dpa_version = body.dpa_version

    // Update user
    const { data: user, error } = await supabase
      .from('users')
      .update(updateData)
      .eq('id', userId)
      .eq('tenant_id', tenantId)
      .select()
      .single()

    if (error) {
      console.error('Error updating user:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to update user',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      user,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('User API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// DELETE /api/users/[id] - Delete a specific user
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id
    const tenantId = request.headers.get('X-Tenant-ID')
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Delete user
    const { error } = await supabase
      .from('users')
      .delete()
      .eq('id', userId)
      .eq('tenant_id', tenantId)

    if (error) {
      console.error('Error deleting user:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to delete user',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      message: 'User deleted successfully',
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('User API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
