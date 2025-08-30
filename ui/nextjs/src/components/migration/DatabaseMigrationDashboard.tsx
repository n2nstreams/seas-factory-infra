'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Database, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Play, 
  Stop, 
  RotateCcw,
  BarChart3,
  Shield,
  Activity
} from 'lucide-react'
import { 
  MigrationStatus, 
  DataValidationResult, 
  MigrationTable 
} from '@/lib/database-migration'

interface MigrationProgress {
  totalTables: number
  completedTables: number
  activeTables: number
  failedTables: number
  overallProgress: number
}

export default function DatabaseMigrationDashboard() {
  const [migrationStatus, setMigrationStatus] = useState<MigrationStatus[]>([])
  const [migrationProgress, setMigrationProgress] = useState<MigrationProgress | null>(null)
  const [migrationTables, setMigrationTables] = useState<MigrationTable[]>([])
  const [validationResults, setValidationResults] = useState<DataValidationResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    loadMigrationData()
    const interval = setInterval(loadMigrationData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const loadMigrationData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load migration status
      const statusResponse = await fetch('/api/migration?action=status')
      const statusData = await statusResponse.json()
      if (statusData.success) {
        setMigrationStatus(statusData.data)
      }

      // Load migration progress
      const progressResponse = await fetch('/api/migration?action=progress')
      const progressData = await progressResponse.json()
      if (progressData.success) {
        setMigrationProgress(progressData.data)
      }

      // Load migration tables
      const tablesResponse = await fetch('/api/migration?action=tables')
      const tablesData = await tablesResponse.json()
      if (tablesData.success) {
        setMigrationTables(tablesData.data)
      }

      // Load validation results
      const validationResponse = await fetch('/api/migration?action=validate-all')
      const validationData = await validationResponse.json()
      if (validationData.success) {
        setValidationResults(validationData.data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load migration data')
    } finally {
      setLoading(false)
    }
  }

  const handleMigrationAction = async (action: string, tableName?: string) => {
    try {
      const response = await fetch('/api/migration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, tableName })
      })

      const data = await response.json()
      if (data.success) {
        await loadMigrationData() // Refresh data
      } else {
        setError(data.error || 'Action failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed')
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-600"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>
      case 'active':
        return <Badge variant="default" className="bg-blue-600"><Activity className="w-3 h-3 mr-1" />Active</Badge>
      case 'failed':
        return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />Failed</Badge>
      case 'pending':
        return <Badge variant="secondary"><AlertTriangle className="w-3 h-3 mr-1" />Pending</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getDataQualityBadge = (quality: string) => {
    switch (quality) {
      case 'excellent':
        return <Badge variant="default" className="bg-green-600">Excellent</Badge>
      case 'good':
        return <Badge variant="default" className="bg-blue-600">Good</Badge>
      case 'fair':
        return <Badge variant="default" className="bg-yellow-600">Fair</Badge>
      case 'poor':
        return <Badge variant="destructive">Poor</Badge>
      default:
        return <Badge variant="outline">{quality}</Badge>
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Database className="w-8 h-8 mx-auto mb-4 animate-spin" />
          <p>Loading migration data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <XCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Database Migration Dashboard</h1>
          <p className="text-muted-foreground">
            Module 3: Database Migration Completion - Supabase PostgreSQL
          </p>
        </div>
        <Button onClick={loadMigrationData} variant="outline">
          <RotateCcw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Migration Progress Overview */}
      {migrationProgress && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Migration Progress
            </CardTitle>
            <CardDescription>
              Overall progress of database migration to Supabase
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Overall Progress</span>
                <span className="text-sm font-medium">{migrationProgress.overallProgress.toFixed(1)}%</span>
              </div>
              <Progress value={migrationProgress.overallProgress} className="w-full" />
              
              <div className="grid grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{migrationProgress.totalTables}</div>
                  <div className="text-sm text-muted-foreground">Total Tables</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{migrationProgress.completedTables}</div>
                  <div className="text-sm text-muted-foreground">Completed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{migrationProgress.activeTables}</div>
                  <div className="text-sm text-muted-foreground">Active</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{migrationProgress.failedTables}</div>
                  <div className="text-sm text-muted-foreground">Failed</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="validation">Data Validation</TabsTrigger>
          <TabsTrigger value="actions">Migration Actions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Migration Status by Table</CardTitle>
              <CardDescription>
                Current status of each table in the migration process
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {migrationStatus.map((status) => (
                  <div key={status.table} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Database className="w-4 h-4" />
                      <span className="font-medium">{status.table}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      {getStatusBadge(status.status)}
                      <span className="text-sm text-muted-foreground">
                        {status.recordsMigrated} / {status.recordsTotal}
                      </span>
                      {status.lastSync && (
                        <span className="text-xs text-muted-foreground">
                          {new Date(status.lastSync).toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="validation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Consistency Validation</CardTitle>
              <CardDescription>
                Validation results comparing migration source and Supabase data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {validationResults.map((result) => (
                  <div key={result.table} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{result.table}</span>
                      <div className="flex items-center gap-2">
                        {getDataQualityBadge(result.dataQuality)}
                        {result.consistent ? (
                          <Badge variant="default" className="bg-green-600">Consistent</Badge>
                        ) : (
                          <Badge variant="destructive">Inconsistent</Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                                        <span className="text-muted-foreground">Source Count:</span>
                <span className="ml-2 font-medium">{result.sourceCount}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Supabase Count:</span>
                        <span className="ml-2 font-medium">{result.supabaseCount}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Drift:</span>
                        <span className="ml-2 font-medium">{(result.driftPercentage * 100).toFixed(2)}%</span>
                      </div>
                    </div>
                    
                    {result.differences.length > 0 && (
                      <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                        <span className="font-medium text-yellow-800">Differences:</span>
                        <ul className="mt-1 text-yellow-700">
                          {result.differences.map((diff, index) => (
                            <li key={index}>• {diff}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="actions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Migration Control Actions</CardTitle>
              <CardDescription>
                Control the migration process for individual tables
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {migrationTables.map((table) => {
                  const status = migrationStatus.find(s => s.table === table.name)
                  const isActive = status?.status === 'active'
                  const isCompleted = status?.status === 'completed'
                  const isFailed = status?.status === 'failed'

                  return (
                    <div key={table.name} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-medium">{table.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {table.requiredColumns.length} required columns, {table.optionalColumns.length} optional
                          </p>
                        </div>
                        {getStatusBadge(status?.status || 'pending')}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {!isCompleted && !isActive && (
                          <Button
                            size="sm"
                            onClick={() => handleMigrationAction('start', table.name)}
                            disabled={isFailed}
                          >
                            <Play className="w-4 h-4 mr-1" />
                            Start Migration
                          </Button>
                        )}
                        
                        {isActive && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleMigrationAction('stop', table.name)}
                            >
                              <Stop className="w-4 h-4 mr-1" />
                              Stop Migration
                            </Button>
                            <Button
                              size="sm"
                              onClick={() => handleMigrationAction('complete', table.name)}
                            >
                              <CheckCircle className="w-4 h-4 mr-1" />
                              Complete Migration
                            </Button>
                          </>
                        )}
                        
                        {isFailed && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleMigrationAction('reset', table.name)}
                          >
                            <RotateCcw className="w-4 h-4 mr-1" />
                            Reset Status
                          </Button>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
