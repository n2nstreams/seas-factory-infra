'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/providers/AuthProvider'
import { finalDataMigrationService, CutoverTable, CutoverChecklist, FreezeWindow } from '@/lib/data-migration-final'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { CalendarIcon, ClockIcon, CheckCircleIcon, XCircleIcon, AlertTriangleIcon } from 'lucide-react'
import { format } from 'date-fns'

export default function FinalDataMigrationPage() {
  const { user, isLoading } = useAuth()
  const [cutoverTables, setCutoverTables] = useState<CutoverTable[]>([])
  const [freezeWindows, setFreezeWindows] = useState<FreezeWindow[]>([])
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [isPageLoading, setIsPageLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    if (user) {
      loadData()
    }
  }, [user])

  const loadData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      const [tables, windows] = await Promise.all([
        finalDataMigrationService.getCutoverStatus(),
        finalDataMigrationService.getFreezeWindows()
      ])
      
      setCutoverTables(tables)
      setFreezeWindows(windows)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load migration data')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePrepareCutover = async (tableName: string) => {
    try {
      setError(null)
      setSuccess(null)
      setIsLoading(true)
      
      const checklist = await finalDataMigrationService.prepareTableForCutover(tableName)
      
      // Reload data to show updated status
      await loadData()
      
      setSuccess(`Table ${tableName} prepared for cutover successfully`)
      setSelectedTable(tableName)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to prepare table for cutover')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExecuteCutover = async (tableName: string) => {
    if (!user) return
    
    try {
      setError(null)
      setSuccess(null)
      setIsLoading(true)
      
      const result = await finalDataMigrationService.executeTableCutover(tableName, user.id)
      
      if (result.success) {
        setSuccess(`Cutover completed successfully for table ${tableName}`)
        await loadData()
      } else {
        setError(`Cutover failed: ${result.errors.join(', ')}`)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute cutover')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRollbackCutover = async (tableName: string) => {
    if (!user) return
    
    try {
      setError(null)
      setSuccess(null)
      setIsLoading(true)
      
      await finalDataMigrationService.rollbackTableCutover(tableName, user.id, 'Manual rollback requested')
      
      setSuccess(`Rollback completed successfully for table ${tableName}`)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to rollback cutover')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusBadge = (status: CutoverTable['status']) => {
    const variants = {
      pending: 'secondary',
      ready: 'default',
      cutover: 'default',
      completed: 'default',
      rolled_back: 'destructive'
    } as const
    
    return <Badge variant={variants[status]}>{status.replace('_', ' ')}</Badge>
  }

  const getReadSourceBadge = (source: CutoverTable['readSource']) => {
    const variants = {
      legacy: 'secondary',
      supabase: 'default',
      dual: 'outline'
    } as const
    
    return <Badge variant={variants[source]}>{source}</Badge>
  }

  const getValidationStatusIcon = (status: CutoverTable['validationStatus']) => {
    switch (status) {
      case 'passed':
        return <CheckCircleIcon className="h-4 w-4 text-green-600" />
      case 'failed':
        return <XCircleIcon className="h-4 w-4 text-red-600" />
      default:
        return <AlertTriangleIcon className="h-4 w-4 text-yellow-600" />
    }
  }

  if (isLoading && cutoverTables.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p>Loading migration data...</p>
        </div>
      </div>
    )
  }

  if (!user || user.role !== 'admin') {
    return (
      <div className="container mx-auto py-8">
        <Alert>
          <AlertDescription>
            You don't have permission to access this page. Admin access required.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Final Data Migration</h1>
          <p className="text-muted-foreground">
            Module 13: Source-of-Truth Cutover - Migrate from legacy systems to Supabase
          </p>
        </div>
        <Button onClick={loadData} disabled={isLoading}>
          Refresh Data
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert>
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Migration Overview</TabsTrigger>
          <TabsTrigger value="tables">Table Status</TabsTrigger>
          <TabsTrigger value="freeze-windows">Freeze Windows</TabsTrigger>
          <TabsTrigger value="reconciliation">Reconciliation</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Tables</CardTitle>
                <Badge variant="outline">{cutoverTables.length}</Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{cutoverTables.length}</div>
                <p className="text-xs text-muted-foreground">
                  Tables configured for migration
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Ready for Cutover</CardTitle>
                <Badge variant="outline">
                  {cutoverTables.filter(t => t.status === 'ready').length}
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {cutoverTables.filter(t => t.status === 'ready').length}
                </div>
                <p className="text-xs text-muted-foreground">
                  Tables ready for source-of-truth switch
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <Badge variant="outline">
                  {cutoverTables.filter(t => t.status === 'completed').length}
                </Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {cutoverTables.filter(t => t.status === 'completed').length}
                </div>
                <p className="text-xs text-muted-foreground">
                  Tables successfully migrated
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Migration Progress</CardTitle>
              <CardDescription>
                Overall progress of the final data migration
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span>Migration Progress</span>
                  <span>
                    {cutoverTables.filter(t => t.status === 'completed').length} / {cutoverTables.length}
                  </span>
                </div>
                <Progress 
                  value={
                    (cutoverTables.filter(t => t.status === 'completed').length / cutoverTables.length) * 100
                  } 
                  className="w-full"
                />
                <div className="text-xs text-muted-foreground">
                  {cutoverTables.filter(t => t.status === 'completed').length} of {cutoverTables.length} tables completed
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tables" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Table Migration Status</CardTitle>
              <CardDescription>
                Monitor the status of each table's migration process
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {cutoverTables.map((table) => (
                  <div key={table.name} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold">{table.name}</h3>
                        {getStatusBadge(table.status)}
                        {getReadSourceBadge(table.readSource)}
                      </div>
                      <div className="flex items-center space-x-2">
                        {table.validationStatus !== 'pending' && (
                          <div className="flex items-center space-x-1">
                            {getValidationStatusIcon(table.validationStatus)}
                            <span className="text-sm text-muted-foreground">
                              {table.validationStatus}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Drift:</span>
                        <span className="ml-2 font-mono">
                          {table.driftPercentage.toFixed(2)}%
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Records:</span>
                        <span className="ml-2 font-mono">
                          {table.recordCount.legacy} → {table.recordCount.supabase}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Last Validation:</span>
                        <span className="ml-2">
                          {table.lastValidation ? format(table.lastValidation, 'MMM dd, HH:mm') : 'Never'}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Cutover Date:</span>
                        <span className="ml-2">
                          {table.cutoverDate ? format(table.cutoverDate, 'MMM dd, HH:mm') : 'Not cutover'}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {table.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => handlePrepareCutover(table.name)}
                          disabled={isLoading}
                        >
                          Prepare for Cutover
                        </Button>
                      )}
                      
                      {table.status === 'ready' && (
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleExecuteCutover(table.name)}
                          disabled={isLoading}
                        >
                          Execute Cutover
                        </Button>
                      )}
                      
                      {table.status === 'cutover' && (
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleRollbackCutover(table.name)}
                          disabled={isLoading}
                        >
                          Rollback
                        </Button>
                      )}
                      
                      {table.status === 'rolled_back' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handlePrepareCutover(table.name)}
                          disabled={isLoading}
                        >
                          Retry Preparation
                        </Button>
                      )}
                    </div>

                    {table.referentialIntegrity.issues.length > 0 && (
                      <Alert variant="destructive">
                        <AlertDescription>
                          Referential integrity issues detected:
                          <ul className="mt-2 list-disc list-inside">
                            {table.referentialIntegrity.issues.map((issue, index) => (
                              <li key={index}>{issue}</li>
                            ))}
                          </ul>
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="freeze-windows" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Freeze Windows</CardTitle>
              <CardDescription>
                Manage freeze windows for safe cutover operations
              </CardDescription>
            </CardHeader>
            <CardContent>
              {freezeWindows.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <CalendarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No freeze windows scheduled</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {freezeWindows.map((window) => (
                    <div key={window.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold">{window.description}</h3>
                        <Badge variant={
                          window.status === 'active' ? 'default' : 
                          window.status === 'scheduled' ? 'outline' : 'secondary'
                        }>
                          {window.status}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                        <div>
                          <span className="text-muted-foreground">Start:</span>
                          <span className="ml-2">
                            {format(window.startTime, 'MMM dd, yyyy HH:mm')}
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">End:</span>
                          <span className="ml-2">
                            {format(window.endTime, 'MMM dd, yyyy HH:mm')}
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Tables:</span>
                          <span className="ml-2">
                            {window.affectedTables.length}
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Created by:</span>
                          <span className="ml-2">
                            {window.createdBy}
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-sm">
                        <span className="text-muted-foreground">Affected tables:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {window.affectedTables.map((table) => (
                            <Badge key={table} variant="outline" className="text-xs">
                              {table}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reconciliation" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Reconciliation Monitoring</CardTitle>
              <CardDescription>
                Monitor data consistency and reconciliation jobs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <ClockIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Reconciliation monitoring will be active during cutover operations</p>
                <p className="text-sm mt-2">
                  This tab will show active reconciliation jobs and drift detection
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
