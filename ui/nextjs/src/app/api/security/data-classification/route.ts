import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const tenantId = searchParams.get('tenant_id')
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '50')
    const classificationLevel = searchParams.get('classification_level')
    const dataType = searchParams.get('data_type')
    const tableName = searchParams.get('table_name')
    const gdprImpact = searchParams.get('gdpr_impact')
    const pciImpact = searchParams.get('pci_impact')

    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Build query
    let query = supabase
      .from('data_classification')
      .select('*')
      .eq('tenant_id', tenantId)

    // Apply filters
    if (classificationLevel) {
      query = query.eq('classification_level', classificationLevel)
    }
    if (dataType) {
      query = query.eq('data_type', dataType)
    }
    if (tableName) {
      query = query.eq('table_name', tableName)
    }
    if (gdprImpact !== null) {
      query = query.eq('gdpr_impact', gdprImpact === 'true')
    }
    if (pciImpact !== null) {
      query = query.eq('pci_impact', pciImpact === 'true')
    }

    // Get total count for pagination
    const { count, error: countError } = await supabase
      .from('data_classification')
      .select('*', { count: 'exact', head: true })
      .eq('tenant_id', tenantId)

    if (countError) throw countError

    // Apply pagination
    const offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)

    // Execute query
    const { data, error } = await query

    if (error) throw error

    const totalPages = Math.ceil((count || 0) / limit)

    return NextResponse.json({
      success: true,
      data: data || [],
      pagination: {
        page,
        limit,
        total: count || 0,
        total_pages: totalPages,
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Data classification GET error:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to get data classifications',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { tenant_id, table_name, column_name, classification_level, data_type, gdpr_impact, pci_impact, retention_days } = body

    // Validate required fields
    if (!tenant_id || !table_name || !classification_level || !data_type) {
      return NextResponse.json({
        success: false,
        error: 'Missing required fields: tenant_id, table_name, classification_level, data_type',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate classification level
    if (!['P0', 'P1', 'P2'].includes(classification_level)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid classification_level. Must be P0, P1, or P2',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate data type
    if (!['pii', 'payment', 'user_content', 'telemetry'].includes(data_type)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid data_type. Must be pii, payment, user_content, or telemetry',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Check if record already exists
    const { data: existingRecord, error: checkError } = await supabase
      .from('data_classification')
      .select('id')
      .eq('tenant_id', tenant_id)
      .eq('table_name', table_name)
      .eq('column_name', column_name || null)
      .limit(1)

    if (checkError) throw checkError

    if (existingRecord && existingRecord.length > 0) {
      return NextResponse.json({
        success: false,
        error: 'Data classification record already exists for this table/column combination',
        timestamp: new Date().toISOString(),
      }, { status: 409 })
    }

    // Create new record
    const { data, error } = await supabase
      .from('data_classification')
      .insert({
        tenant_id,
        table_name,
        column_name,
        classification_level,
        data_type,
        gdpr_impact: gdpr_impact || false,
        pci_impact: pci_impact || false,
        retention_days,
        created_by: body.created_by || null,
        updated_by: body.updated_by || null,
      })
      .select()
      .single()

    if (error) throw error

    return NextResponse.json({
      success: true,
      data,
      timestamp: new Date().toISOString(),
    }, { status: 201 })
  } catch (error) {
    console.error('Data classification POST error:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to create data classification',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { id, classification_level, data_type, gdpr_impact, pci_impact, retention_days, updated_by } = body

    if (!id) {
      return NextResponse.json({
        success: false,
        error: 'Record ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate classification level if provided
    if (classification_level && !['P0', 'P1', 'P2'].includes(classification_level)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid classification_level. Must be P0, P1, or P2',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Validate data type if provided
    if (data_type && !['pii', 'payment', 'user_content', 'telemetry'].includes(data_type)) {
      return NextResponse.json({
        success: false,
        error: 'Invalid data_type. Must be pii, payment, user_content, or telemetry',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Update record
    const { data, error } = await supabase
      .from('data_classification')
      .update({
        classification_level,
        data_type,
        gdpr_impact,
        pci_impact,
        retention_days,
        updated_by,
        updated_at: new Date().toISOString(),
      })
      .eq('id', id)
      .select()
      .single()

    if (error) throw error

    if (!data) {
      return NextResponse.json({
        success: false,
        error: 'Record not found',
        timestamp: new Date().toISOString(),
      }, { status: 404 })
    }

    return NextResponse.json({
      success: true,
      data,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Data classification PUT error:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to update data classification',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const id = searchParams.get('id')

    if (!id) {
      return NextResponse.json({
        success: false,
        error: 'Record ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    // Delete record
    const { error } = await supabase
      .from('data_classification')
      .delete()
      .eq('id', id)

    if (error) throw error

    return NextResponse.json({
      success: true,
      data: null,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Data classification DELETE error:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to delete data classification',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}
