'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Shield, 
  Lock, 
  Eye, 
  Key, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  Clock,
  TrendingUp,
  TrendingDown,
  Activity,
  Settings
} from 'lucide-react'
import { securityComplianceService } from '@/lib/security-compliance-service'
import { SecurityComplianceSummary, SECURITY_CONSTANTS } from '@/types/security'
import { useToast } from '@/hooks/use-toast'

interface SecurityComplianceDashboardProps {
  tenantId: string
}

export function SecurityComplianceDashboard({ tenantId }: SecurityComplianceDashboardProps) {
  const [summary, setSummary] = useState<SecurityComplianceSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const { toast } = useToast()

  useEffect(() => {
    loadSecuritySummary()
  }, [tenantId])

  const loadSecuritySummary = async () => {
    try {
      setLoading(true)
      const response = await securityComplianceService.getSecurityComplianceSummary(tenantId)
      
      if (response.success && response.data) {
        setSummary(response.data)
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Failed to load security summary',
          variant: 'destructive',
        })
      }
    } catch (error) {
      console.error('Error loading security summary:', error)
      toast({
        title: 'Error',
        description: 'Failed to load security summary',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const getComplianceScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getComplianceScoreBadge = (score: number) => {
    if (score >= 90) return <Badge variant="default" className="bg-green-100 text-green-800">Excellent</Badge>
    if (score >= 70) return <Badge variant="secondary">Good</Badge>
    if (score >= 50) return <Badge variant="outline" className="text-yellow-600">Fair</Badge>
    return <Badge variant="destructive">Poor</Badge>
  }

  const getRiskLevelBadge = (count: number) => {
    if (count === 0) return <Badge variant="default" className="bg-green-100 text-green-800">Low Risk</Badge>
    if (count <= 2) return <Badge variant="secondary">Medium Risk</Badge>
    if (count <= 5) return <Badge variant="outline" className="text-yellow-600">High Risk</Badge>
    return <Badge variant="destructive">Critical Risk</Badge>
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No security data available</h3>
        <p className="mt-1 text-sm text-gray-500">
          Security and compliance data has not been configured for this tenant.
        </p>
        <div className="mt-6">
          <Button onClick={loadSecuritySummary}>Retry</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security & Compliance</h1>
          <p className="text-muted-foreground">
            Monitor and manage security policies, compliance checks, and access controls
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Button>
          <Button size="sm">
            <Activity className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Overall Compliance Score */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <span className={getComplianceScoreColor(summary.overall_compliance_score)}>
                {summary.overall_compliance_score}%
              </span>
            </div>
            <div className="flex items-center justify-between mt-2">
              {getComplianceScoreBadge(summary.overall_compliance_score)}
              <p className="text-xs text-muted-foreground">
                Target: 90%+
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Data Classification */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Classification</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary.data_classification_summary.p0_count + 
               summary.data_classification_summary.p1_count + 
               summary.data_classification_summary.p2_count}
            </div>
            <div className="flex items-center space-x-2 mt-2">
              <Badge variant="outline" className="text-xs">
                P0: {summary.data_classification_summary.p0_count}
              </Badge>
              <Badge variant="outline" className="text-xs">
                P1: {summary.data_classification_summary.p1_count}
              </Badge>
              <Badge variant="outline" className="text-xs">
                P2: {summary.data_classification_summary.p2_count}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Access Reviews */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Access Reviews</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary.access_review_summary.total_reviews}
            </div>
            <div className="flex items-center space-x-2 mt-2">
              {summary.access_review_summary.overdue_reviews > 0 ? (
                <Badge variant="destructive" className="text-xs">
                  {summary.access_review_summary.overdue_reviews} Overdue
                </Badge>
              ) : (
                <Badge variant="default" className="bg-green-100 text-green-800 text-xs">
                  All Current
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Key Management */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Key Management</CardTitle>
            <Key className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {summary.key_holder_summary.total_keys}
            </div>
            <div className="flex items-center space-x-2 mt-2">
              {summary.key_holder_summary.keys_due_rotation > 0 ? (
                <Badge variant="destructive" className="text-xs">
                  {summary.key_holder_summary.keys_due_rotation} Due Rotation
                </Badge>
              ) : (
                <Badge variant="default" className="bg-green-100 text-green-800 text-xs">
                  All Current
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="data-classification">Data Classification</TabsTrigger>
          <TabsTrigger value="access-reviews">Access Reviews</TabsTrigger>
          <TabsTrigger value="key-management">Key Management</TabsTrigger>
          <TabsTrigger value="admin-actions">Admin Actions</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Risk Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  <span>Risk Assessment</span>
                </CardTitle>
                <CardDescription>
                  Current risk levels across security domains
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">High Risk Items</span>
                  <Badge variant="destructive">
                    {summary.key_holder_summary.high_risk_keys + 
                     summary.admin_actions_summary.high_risk_actions}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Overdue Reviews</span>
                  <Badge variant="destructive">
                    {summary.access_review_summary.overdue_reviews}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Keys Due Rotation</span>
                  <Badge variant="outline" className="text-yellow-600">
                    {summary.key_holder_summary.keys_due_rotation}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Pending Approvals</span>
                  <Badge variant="secondary">
                    {summary.admin_actions_summary.pending_approvals}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Compliance Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>Compliance Status</span>
                </CardTitle>
                <CardDescription>
                  Current compliance across different frameworks
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">GDPR Impact</span>
                  <Badge variant="outline">
                    {summary.data_classification_summary.gdpr_impact_count} Fields
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">PCI Impact</span>
                  <Badge variant="outline">
                    {summary.data_classification_summary.pci_impact_count} Fields
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Active Policies</span>
                  <Badge variant="default">
                    {summary.compliance_checks_summary.total_checks}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Checks Due Soon</span>
                  <Badge variant="outline" className="text-yellow-600">
                    {summary.compliance_checks_summary.checks_due_soon}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Security Activity</CardTitle>
              <CardDescription>
                Latest security and compliance events
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {summary.admin_actions_summary.actions_this_month > 0 ? (
                  <div className="flex items-center space-x-3 p-3 bg-muted rounded-lg">
                    <Activity className="h-4 w-4 text-blue-600" />
                    <div className="flex-1">
                      <p className="text-sm font-medium">
                        {summary.admin_actions_summary.actions_this_month} admin actions this month
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Last updated: {new Date(summary.last_updated).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4 text-muted-foreground">
                    No recent security activity
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Classification Tab */}
        <TabsContent value="data-classification" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Classification Overview</CardTitle>
              <CardDescription>
                Manage data sensitivity levels and compliance requirements
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {summary.data_classification_summary.p0_count}
                  </div>
                  <div className="text-sm font-medium">P0 - Critical</div>
                  <div className="text-xs text-muted-foreground">PII & Payment Data</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {summary.data_classification_summary.p1_count}
                  </div>
                  <div className="text-sm font-medium">P1 - High</div>
                  <div className="text-xs text-muted-foreground">User Content</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {summary.data_classification_summary.p2_count}
                  </div>
                  <div className="text-sm font-medium">P2 - Low</div>
                  <div className="text-xs text-muted-foreground">Telemetry</div>
                </div>
              </div>
              <div className="mt-4 flex justify-center">
                <Button variant="outline" size="sm">
                  Manage Classifications
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Access Reviews Tab */}
        <TabsContent value="access-reviews" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Access Review Status</CardTitle>
              <CardDescription>
                Monitor access review progress and identify overdue reviews
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {summary.access_review_summary.total_reviews}
                  </div>
                  <div className="text-sm font-medium">Total Reviews</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {summary.access_review_summary.pending_reviews}
                  </div>
                  <div className="text-sm font-medium">Pending</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {summary.access_review_summary.overdue_reviews}
                  </div>
                  <div className="text-sm font-medium">Overdue</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {summary.access_review_summary.completed_reviews}
                  </div>
                  <div className="text-sm font-medium">Completed</div>
                </div>
              </div>
              <div className="mt-4 flex justify-center space-x-2">
                <Button variant="outline" size="sm">
                  View All Reviews
                </Button>
                <Button size="sm">
                  Schedule Review
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Key Management Tab */}
        <TabsContent value="key-management" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Key Management Status</CardTitle>
              <CardDescription>
                Monitor key rotation schedules and identify keys due for rotation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {summary.key_holder_summary.total_keys}
                  </div>
                  <div className="text-sm font-medium">Total Keys</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {summary.key_holder_summary.high_risk_keys}
                  </div>
                  <div className="text-sm font-medium">High Risk</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {summary.key_holder_summary.keys_due_rotation}
                  </div>
                  <div className="text-sm font-medium">Due Rotation</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-gray-600">
                    {summary.key_holder_summary.revoked_keys}
                  </div>
                  <div className="text-sm font-medium">Revoked</div>
                </div>
              </div>
              <div className="mt-4 flex justify-center space-x-2">
                <Button variant="outline" size="sm">
                  View All Keys
                </Button>
                <Button size="sm">
                  Rotate Keys
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Admin Actions Tab */}
        <TabsContent value="admin-actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Admin Action Audit</CardTitle>
              <CardDescription>
                Monitor administrative actions and pending approvals
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {summary.admin_actions_summary.total_actions}
                  </div>
                  <div className="text-sm font-medium">Total Actions</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {summary.admin_actions_summary.pending_approvals}
                  </div>
                  <div className="text-sm font-medium">Pending Approval</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {summary.admin_actions_summary.high_risk_actions}
                  </div>
                  <div className="text-sm font-medium">High Risk</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {summary.admin_actions_summary.actions_this_month}
                  </div>
                  <div className="text-sm font-medium">This Month</div>
                </div>
              </div>
              <div className="mt-4 flex justify-center space-x-2">
                <Button variant="outline" size="sm">
                  View All Actions
                </Button>
                <Button size="sm">
                  Review Approvals
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Check Status</CardTitle>
              <CardDescription>
                Monitor compliance across different frameworks and standards
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {summary.compliance_checks_summary.total_checks}
                  </div>
                  <div className="text-sm font-medium">Total Checks</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {summary.compliance_checks_summary.compliant_checks}
                  </div>
                  <div className="text-sm font-medium">Compliant</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {summary.compliance_checks_summary.non_compliant_checks}
                  </div>
                  <div className="text-sm font-medium">Non-Compliant</div>
                </div>
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {summary.compliance_checks_summary.checks_due_soon}
                  </div>
                  <div className="text-sm font-medium">Due Soon</div>
                </div>
              </div>
              <div className="mt-4 flex justify-center space-x-2">
                <Button variant="outline" size="sm">
                  View All Checks
                </Button>
                <Button size="sm">
                  Run Checks
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer Actions */}
      <div className="flex items-center justify-between pt-6 border-t">
        <div className="text-sm text-muted-foreground">
          Last updated: {new Date(summary.last_updated).toLocaleString()}
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Clock className="mr-2 h-4 w-4" />
            Schedule Report
          </Button>
          <Button variant="outline" size="sm">
            <TrendingUp className="mr-2 h-4 w-4" />
            Export Data
          </Button>
          <Button size="sm">
            <Shield className="mr-2 h-4 w-4" />
            Security Scan
          </Button>
        </div>
      </div>
    </div>
  )
}
