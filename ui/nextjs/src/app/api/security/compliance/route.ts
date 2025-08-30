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
    const complianceType = searchParams.get('type') // 'gdpr', 'pci', 'soc2', or 'all'
    
    if (!tenantId) {
      return NextResponse.json({
        success: false,
        error: 'Tenant ID is required',
        timestamp: new Date().toISOString(),
      }, { status: 400 })
    }

    let complianceData: any = {}

    if (complianceType === 'gdpr' || complianceType === 'all' || !complianceType) {
      complianceData.gdpr = await checkGDPRCompliance(tenantId)
    }

    if (complianceType === 'pci' || complianceType === 'all' || !complianceType) {
      complianceData.pci = await checkPCICompliance(tenantId)
    }

    if (complianceType === 'soc2' || complianceType === 'all' || !complianceType) {
      complianceData.soc2 = await checkSOC2Compliance(tenantId)
    }

    return NextResponse.json({
      success: true,
      data: complianceData,
      timestamp: new Date().toISOString(),
    })

  } catch (error) {
    console.error('Compliance API error:', error)
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      timestamp: new Date().toISOString(),
    }, { status: 500 })
  }
}

async function checkGDPRCompliance(tenantId: string) {
  try {
    // Check data classification for PII data
    const { data: dataClassifications, error: dcError } = await supabase
      .from('data_classification')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('gdpr_impact', true)

    if (dcError) throw dcError

    // Check privacy consent audit
    const { data: privacyAudits, error: paError } = await supabase
      .from('privacy_consent_audit')
      .select('*')
      .eq('tenant_id', tenantId)
      .gte('timestamp', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()) // Last 30 days

    if (paError) throw paError

    // Calculate GDPR compliance score
    let complianceScore = 100
    let issues: string[] = []
    let isCompliant = true

    // Check PII data handling
    if (dataClassifications && dataClassifications.length > 0) {
      const piiData = dataClassifications.filter(dc => dc.classification_level === 'P0')
      if (piiData.length > 0) {
        // Check if retention policies are set
        const hasRetentionPolicies = piiData.every(dc => dc.retention_days !== null)
        if (!hasRetentionPolicies) {
          complianceScore -= 20
          issues.push('PII data missing retention policies')
          isCompliant = false
        }
      }
    } else {
      // No data classification - potential issue
      complianceScore -= 15
      issues.push('No data classification system in place')
      isCompliant = false
    }

    // Check privacy consent tracking
    if (!privacyAudits || privacyAudits.length === 0) {
      complianceScore -= 25
      issues.push('No privacy consent audit trail')
      isCompliant = false
    }

    // Check data minimization
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('*')
      .eq('tenant_id', tenantId)
      .limit(10)

    if (!usersError && users && users.length > 0) {
      // Check if only necessary user data is collected
      const hasExcessiveData = users.some(user => 
        user.email && user.first_name && user.last_name && user.phone && user.address
      )
      if (hasExcessiveData) {
        complianceScore -= 10
        issues.push('Potential excessive data collection')
        isCompliant = false
      }
    }

    return {
      is_compliant: isCompliant,
      compliance_score: Math.max(0, complianceScore),
      last_check_date: new Date().toISOString(),
      next_check_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days from now
      issues: issues,
      check_type: 'gdpr',
      check_frequency: 'monthly'
    }

  } catch (error) {
    console.error('GDPR compliance check error:', error)
    return {
      is_compliant: false,
      compliance_score: 0,
      last_check_date: new Date().toISOString(),
      next_check_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
      issues: ['Error during GDPR compliance check'],
      check_type: 'gdpr',
      check_frequency: 'monthly'
    }
  }
}

async function checkPCICompliance(tenantId: string) {
  try {
    // Check if payment data is being processed
    const { data: dataClassifications, error: dcError } = await supabase
      .from('data_classification')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('pci_impact', true)

    if (dcError) throw dcError

    // Check for payment-related tables or fields
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('*')
      .eq('tenant_id', tenantId)
      .limit(5)

    if (usersError) throw usersError

    let complianceScore = 100
    let issues: string[] = []
    let isCompliant = true

    // Check if payment data exists
    if (dataClassifications && dataClassifications.length > 0) {
      const paymentData = dataClassifications.filter(dc => dc.data_type === 'payment')
      if (paymentData.length > 0) {
        // Check if encryption is mentioned in security policies
        const { data: securityPolicies, error: spError } = await supabase
          .from('security_policies')
          .select('*')
          .eq('tenant_id', tenantId)
          .eq('policy_type', 'data_protection')
          .eq('status', 'active')

        if (!spError && securityPolicies && securityPolicies.length > 0) {
          const hasEncryptionPolicy = securityPolicies.some(sp => 
            sp.policy_description?.toLowerCase().includes('encryption') ||
            sp.policy_rules?.encryption === true
          )
          if (!hasEncryptionPolicy) {
            complianceScore -= 30
            issues.push('Payment data encryption policy missing')
            isCompliant = false
          }
        } else {
          complianceScore -= 40
          issues.push('No data protection security policies')
          isCompliant = false
        }
      }
    }

    // Check for secure transmission
    const hasHTTPS = process.env.NODE_ENV === 'production' // Simplified check
    if (!hasHTTPS) {
      complianceScore -= 20
      issues.push('HTTPS not enforced in production')
      isCompliant = false
    }

    // Check access controls
    const { data: adminActions, error: aaError } = await supabase
      .from('admin_actions_audit')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('action_category', 'user_management')
      .gte('created_at', new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()) // Last 90 days

    if (!aaError && adminActions && adminActions.length > 0) {
      // Check if admin actions are properly logged
      const hasProperLogging = adminActions.every(aa => 
        aa.reason && aa.ip_address && aa.user_agent
      )
      if (!hasProperLogging) {
        complianceScore -= 15
        issues.push('Incomplete admin action logging')
        isCompliant = false
      }
    }

    return {
      is_compliant: isCompliant,
      compliance_score: Math.max(0, complianceScore),
      last_check_date: new Date().toISOString(),
      next_check_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(), // 90 days from now
      issues: issues,
      check_type: 'pci',
      check_frequency: 'quarterly'
    }

  } catch (error) {
    console.error('PCI compliance check error:', error)
    return {
      is_compliant: false,
      compliance_score: 0,
      last_check_date: new Date().toISOString(),
      next_check_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
      issues: ['Error during PCI compliance check'],
      check_type: 'pci',
      check_frequency: 'quarterly'
    }
  }
}

async function checkSOC2Compliance(tenantId: string) {
  try {
    let complianceScore = 100
    let issues: string[] = []
    let isCompliant = true

    // Check access controls (CC6.1)
    const { data: accessReviews, error: arError } = await supabase
      .from('access_reviews')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('status', 'completed')
      .gte('completed_at', new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString()) // Last year

    if (!arError && accessReviews && accessReviews.length > 0) {
      // Check if access reviews are being conducted regularly
      const hasRegularReviews = accessReviews.length >= 4 // At least quarterly
      if (!hasRegularReviews) {
        complianceScore -= 20
        issues.push('Insufficient access review frequency')
        isCompliant = false
      }
    } else {
      complianceScore -= 30
      issues.push('No access reviews conducted')
      isCompliant = false
    }

    // Check change management (CC8.1)
    const { data: adminActions, error: aaError } = await supabase
      .from('admin_actions_audit')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('requires_approval', true)
      .gte('created_at', new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString()) // Last 90 days

    if (!aaError && adminActions && adminActions.length > 0) {
      // Check if high-risk actions require approval
      const hasApprovalWorkflow = adminActions.every(aa => 
        aa.approved_by !== null || aa.requires_approval === true
      )
      if (!hasApprovalWorkflow) {
        complianceScore -= 15
        issues.push('Incomplete approval workflow for high-risk actions')
        isCompliant = false
      }
    }

    // Check monitoring and logging (CC7.1)
    const { data: auditLogs, error: alError } = await supabase
      .from('audit_logs')
      .select('*')
      .eq('tenant_id', tenantId)
      .gte('timestamp', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()) // Last 7 days

    if (!alError && auditLogs && auditLogs.length > 0) {
      // Check if comprehensive logging is in place
      const hasComprehensiveLogging = auditLogs.every(log => 
        log.action && log.category && log.ip_address && log.timestamp
      )
      if (!hasComprehensiveLogging) {
        complianceScore -= 15
        issues.push('Incomplete audit logging')
        isCompliant = false
      }
    } else {
      complianceScore -= 25
      issues.push('No audit logs generated')
      isCompliant = false
    }

    // Check security policies (CC9.1)
    const { data: securityPolicies, error: spError } = await supabase
      .from('security_policies')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('status', 'active')

    if (!spError && securityPolicies && securityPolicies.length > 0) {
      // Check if comprehensive security policies exist
      const hasComprehensivePolicies = securityPolicies.some(sp => 
        sp.policy_type === 'access_control' &&
        sp.policy_type === 'data_protection' &&
        sp.policy_type === 'audit'
      )
      if (!hasComprehensivePolicies) {
        complianceScore -= 10
        issues.push('Incomplete security policy coverage')
        isCompliant = false
      }
    } else {
      complianceScore -= 20
      issues.push('No security policies defined')
      isCompliant = false
    }

    return {
      is_compliant: isCompliant,
      compliance_score: Math.max(0, complianceScore),
      last_check_date: new Date().toISOString(),
      next_check_date: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(), // 90 days from now
      issues: issues,
      check_type: 'soc2',
      check_frequency: 'quarterly'
    }

  } catch (error) {
    console.error('SOC2 compliance check error:', error)
    return {
      is_compliant: false,
      compliance_score: 0,
      last_check_date: new Date().toISOString(),
      next_check_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
      issues: ['Error during SOC2 compliance check'],
      check_type: 'soc2',
      check_frequency: 'quarterly'
    }
  }
}
