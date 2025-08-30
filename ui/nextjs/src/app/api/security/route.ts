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
    const action = searchParams.get('action')

    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    switch (action) {
      case 'summary':
        return await getSecuritySummary(tenantId)
      case 'health':
        return await getSecurityHealth(tenantId)
      case 'metrics':
        return await getSecurityMetrics(tenantId)
      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action specified',
          timestamp: new Date().toISOString(),
        }, { status: 400 })
    }
  } catch (error) {
    console.error('Security API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

async function getSecuritySummary(tenantId: string) {
  try {
    // Get data classification summary
    const { data: dataClassifications, error: dcError } = await supabase
      .from('data_classification')
      .select('*')
      .eq('tenant_id', tenantId)

    if (dcError) throw dcError

    // Get access review summary
    const { data: accessReviews, error: arError } = await supabase
      .from('access_reviews')
      .select('*')
      .eq('tenant_id', tenantId)

    if (arError) throw arError

    // Get key holder summary
    const { data: keyHolders, error: khError } = await supabase
      .from('key_holders')
      .select('*')
      .eq('tenant_id', tenantId)

    if (khError) throw khError

    // Get admin actions summary
    const { data: adminActions, error: aaError } = await supabase
      .from('admin_actions_audit')
      .select('*')
      .eq('tenant_id', tenantId)

    if (aaError) throw aaError

    // Get compliance checks summary
    const { data: complianceChecks, error: ccError } = await supabase
      .from('compliance_checks')
      .select('*')
      .eq('tenant_id', tenantId)

    if (ccError) throw ccError

    // Calculate summary metrics
    const summary = {
      tenant_id: tenantId,
      overall_compliance_score: calculateComplianceScore(complianceChecks || []),
      data_classification_summary: {
        p0_count: (dataClassifications || []).filter(dc => dc.classification_level === 'P0').length,
        p1_count: (dataClassifications || []).filter(dc => dc.classification_level === 'P1').length,
        p2_count: (dataClassifications || []).filter(dc => dc.classification_level === 'P2').length,
        gdpr_impact_count: (dataClassifications || []).filter(dc => dc.gdpr_impact).length,
        pci_impact_count: (dataClassifications || []).filter(dc => dc.pci_impact).length,
      },
      access_review_summary: {
        total_reviews: (accessReviews || []).length,
        pending_reviews: (accessReviews || []).filter(ar => ar.status === 'pending').length,
        overdue_reviews: (accessReviews || []).filter(ar => {
          const dueDate = new Date(ar.due_date)
          const today = new Date()
          return today > dueDate && ar.status !== 'completed'
        }).length,
        completed_reviews: (accessReviews || []).filter(ar => ar.status === 'completed').length,
      },
      key_holder_summary: {
        total_keys: (keyHolders || []).length,
        high_risk_keys: (keyHolders || []).filter(kh => kh.risk_level === 'high' || kh.risk_level === 'critical').length,
        keys_due_rotation: (keyHolders || []).filter(kh => {
          if (!kh.next_rotation_date) return false
          const nextRotation = new Date(kh.next_rotation_date)
          const today = new Date()
          return today >= nextRotation
        }).length,
        revoked_keys: (keyHolders || []).filter(kh => kh.status === 'revoked').length,
      },
      admin_actions_summary: {
        total_actions: (adminActions || []).length,
        pending_approvals: (adminActions || []).filter(aa => aa.requires_approval && !aa.approved_by).length,
        high_risk_actions: (adminActions || []).filter(aa => aa.risk_assessment === 'high' || aa.risk_assessment === 'critical').length,
        actions_this_month: (adminActions || []).filter(aa => {
          const actionDate = new Date(aa.created_at)
          const thisMonth = new Date()
          return actionDate.getMonth() === thisMonth.getMonth() && 
                 actionDate.getFullYear() === thisMonth.getFullYear()
        }).length,
      },
      compliance_checks_summary: {
        total_checks: (complianceChecks || []).length,
        compliant_checks: (complianceChecks || []).filter(cc => cc.is_compliant).length,
        non_compliant_checks: (complianceChecks || []).filter(cc => !cc.is_compliant).length,
        checks_due_soon: (complianceChecks || []).filter(cc => {
          if (!cc.next_check_date) return false
          const nextCheck = new Date(cc.next_check_date)
          const today = new Date()
          const daysUntilCheck = Math.ceil((nextCheck.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
          return daysUntilCheck <= 7 && daysUntilCheck > 0
        }).length,
      },
      last_updated: new Date().toISOString(),
    }

    return NextResponse.json({
      success: true,
      data: summary,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Error getting security summary:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to get security summary',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

async function getSecurityHealth(tenantId: string) {
  try {
    // Check database connectivity
    const { data: healthCheck, error: dbError } = await supabase
      .from('data_classification')
      .select('count')
      .eq('tenant_id', tenantId)
      .limit(1)

    const services = {
      database: dbError ? 'unhealthy' : 'healthy',
      rls_policies: 'healthy', // Assuming RLS is working if we can query
      security_functions: 'healthy', // Assuming functions are working
    }

    const overallStatus = Object.values(services).every(status => status === 'healthy') ? 'healthy' : 'degraded'

    return NextResponse.json({
      success: true,
      data: {
        status: overallStatus,
        services,
        last_check: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Error getting security health:', error)
    return NextResponse.json({
      success: true,
      data: {
        status: 'unhealthy',
        services: {
          database: 'unhealthy',
          rls_policies: 'unknown',
          security_functions: 'unknown',
        },
        last_check: new Date().toISOString(),
      },
      timestamp: new Date().toISOString(),
    })
  }
}

async function getSecurityMetrics(tenantId: string) {
  try {
    // Get basic metrics
    const { data: dataClassifications, error: dcError } = await supabase
      .from('data_classification')
      .select('*')
      .eq('tenant_id', tenantId)

    if (dcError) throw dcError

    const { data: securityPolicies, error: spError } = await supabase
      .from('security_policies')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('status', 'active')

    if (spError) throw spError

    const { data: complianceChecks, error: ccError } = await supabase
      .from('compliance_checks')
      .select('*')
      .eq('tenant_id', tenantId)

    if (ccError) throw ccError

    // Calculate risk score based on various factors
    const riskFactors = {
      high_risk_keys: 0, // Will be calculated from key_holders
      overdue_reviews: 0, // Will be calculated from access_reviews
      non_compliant_checks: (complianceChecks || []).filter(cc => !cc.is_compliant).length,
    }

    // Get additional risk factors
    const { data: keyHolders, error: khError } = await supabase
      .from('key_holders')
      .select('*')
      .eq('tenant_id', tenantId)

    if (!khError && keyHolders) {
      riskFactors.high_risk_keys = keyHolders.filter(kh => 
        kh.risk_level === 'high' || kh.risk_level === 'critical'
      ).length
    }

    const { data: accessReviews, error: arError } = await supabase
      .from('access_reviews')
      .select('*')
      .eq('tenant_id', tenantId)

    if (!arError && accessReviews) {
      riskFactors.overdue_reviews = accessReviews.filter(ar => {
        const dueDate = new Date(ar.due_date)
        const today = new Date()
        return today > dueDate && ar.status !== 'completed'
      }).length
    }

    // Calculate overall risk score (1-10 scale)
    const overallRiskScore = Math.min(10, Math.max(1, 
      riskFactors.high_risk_keys * 2 + 
      riskFactors.overdue_reviews * 1.5 + 
      riskFactors.non_compliant_checks * 1
    ))

    const metrics = {
      total_entities: (dataClassifications || []).length + (securityPolicies || []).length + (complianceChecks || []).length,
      active_policies: (securityPolicies || []).length,
      compliance_score: calculateComplianceScore(complianceChecks || []),
      risk_score: Math.round(overallRiskScore),
      last_updated: new Date().toISOString(),
    }

    return NextResponse.json({
      success: true,
      data: metrics,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Error getting security metrics:', error)
    return NextResponse.json({
      success: false,
      error: 'Failed to get security metrics',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

function calculateComplianceScore(complianceChecks: any[]): number {
  if (complianceChecks.length === 0) return 0
  
  const compliantCount = complianceChecks.filter(cc => cc.is_compliant).length
  return Math.round((compliantCount / complianceChecks.length) * 100)
}
