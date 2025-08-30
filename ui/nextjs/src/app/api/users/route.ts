import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// GET /api/users - Get all users for a tenant
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

    // Get users for the tenant
    const { data: users, error } = await supabase
      .from('users')
      .select('*')
      .eq('tenant_id', tenantId)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching users:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to fetch users',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      users,
      count: users?.length || 0,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Users API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

// POST /api/users - Create a new user
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
    const requiredFields = ['email', 'name', 'role']
    for (const field of requiredFields) {
      if (!body[field]) {
        return NextResponse.json({
          success: false,
          error: `Missing required field: ${field}`,
          timestamp: new Date().toISOString(),
        }, { status: 400 })
      }
    }

    // Create user
    const userData = {
      tenant_id: tenantId,
      email: body.email,
      name: body.name,
      role: body.role || 'user',
      status: body.status || 'active',
      gdpr_consent_given: body.gdpr_consent_given || false,
      gdpr_consent_date: body.gdpr_consent_given ? new Date().toISOString() : null,
      gdpr_consent_ip: body.gdpr_consent_ip || null,
      privacy_policy_version: body.privacy_policy_version || '1.0',
      dpa_version: body.dpa_version || '1.0',
    }

    const { data: user, error } = await supabase
      .from('users')
      .insert(userData)
      .select()
      .single()

    if (error) {
      console.error('Error creating user:', error)
      return NextResponse.json({
        success: false,
        error: 'Failed to create user',
        timestamp: new Date().toISOString(),
      }, { status: 500 })
    }

    return NextResponse.json({
      success: true,
      user,
      timestamp: new Date().toISOString(),
    }, { status: 201 })

  } catch (error) {
    console.error('Users API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
