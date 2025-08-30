'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Upload, 
  Download, 
  Database, 
  Settings, 
  Play, 
  Pause, 
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  HardDrive,
  FileText,
  Image,
  Archive
} from 'lucide-react'
import { 
  storageManager, 
  STORAGE_BUCKETS, 
  StorageBucket 
} from '@/lib/storage'
import { 
  storageMigrationService, 
  MigrationStatus, 
  MigrationProgress 
} from '@/lib/storage-migration'
import { useAuth } from '@/components/providers/DualAuthProvider'

interface StorageUsage {
  bucket_id: string
  total_files: number
  total_size: number
  total_size_mb: number
}

interface StorageObject {
  id: string
  name: string
  bucket: string
  path: string
  size: number
  mime_type: string
  created_at: string
}

export default function StorageManagementDashboard() {
  const { user } = useAuth()
  const [storageUsage, setStorageUsage] = useState<StorageUsage[]>([])
  const [migrationStatuses, setMigrationStatuses] = useState<MigrationStatus[]>([])
  const [recentFiles, setRecentFiles] = useState<StorageObject[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [activeMigration, setActiveMigration] = useState<string | null>(null)
  const [migrationProgress, setMigrationProgress] = useState<MigrationProgress | null>(null)

  // Mock tenant ID for demo purposes
  const tenantId = user?.id || 'demo-tenant'

  useEffect(() => {
    loadStorageData()
  }, [tenantId])

  const loadStorageData = async () => {
    setIsLoading(true)
    try {
      // Load storage usage
      const usage = await getStorageUsage(tenantId)
      setStorageUsage(usage)

      // Load migration statuses
      const statuses = await storageMigrationService.getTenantMigrationStatuses(tenantId)
      setMigrationStatuses(statuses)

      // Load recent files
      const files = await getRecentFiles(tenantId)
      setRecentFiles(files)
    } catch (error) {
      console.error('Error loading storage data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStorageUsage = async (tenantId: string): Promise<StorageUsage[]> => {
    try {
      // This would call the Supabase function get_tenant_storage_usage
      // For now, return mock data
      return Object.values(STORAGE_BUCKETS).map(bucket => ({
        bucket_id: bucket,
        total_files: Math.floor(Math.random() * 100),
        total_size: Math.floor(Math.random() * 100 * 1024 * 1024), // Random size up to 100MB
        total_size_mb: Math.floor(Math.random() * 100)
      }))
    } catch (error) {
      console.error('Error getting storage usage:', error)
      return []
    }
  }

  const getRecentFiles = async (tenantId: string): Promise<StorageObject[]> => {
    try {
      // This would query the storage_objects table
      // For now, return mock data
      return [
        {
          id: '1',
          name: 'document.pdf',
          bucket: 'user-uploads',
          path: `${tenantId}/uploads/2024/12/document.pdf`,
          size: 1024 * 1024,
          mime_type: 'application/pdf',
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'image.jpg',
          bucket: 'project-assets',
          path: `${tenantId}/project-assets/2024/12/image.jpg`,
          size: 2 * 1024 * 1024,
          mime_type: 'image/jpeg',
          created_at: new Date().toISOString()
        }
      ]
    } catch (error) {
      console.error('Error getting recent files:', error)
      return []
    }
  }

  const startMigration = async (bucketId: string) => {
    try {
      setActiveMigration(bucketId)
      
      const success = await storageMigrationService.startMigration(
        tenantId,
        bucketId,
        {
          batchSize: 10,
          maxConcurrent: 3,
          dryRun: false,
          onProgress: (progress) => {
            setMigrationProgress(progress)
          }
        }
      )

      if (success) {
        console.log(`Migration completed for bucket ${bucketId}`)
      } else {
        console.error(`Migration failed for bucket ${bucketId}`)
      }
    } catch (error) {
      console.error('Error starting migration:', error)
    } finally {
      setActiveMigration(null)
      setMigrationProgress(null)
      loadStorageData() // Refresh data
    }
  }

  const stopMigration = async () => {
    try {
      await storageMigrationService.stopMigration()
      setActiveMigration(null)
      setMigrationProgress(null)
    } catch (error) {
      console.error('Error stopping migration:', error)
    }
  }

  const getBucketIcon = (bucketId: string) => {
    switch (bucketId) {
      case 'user-uploads':
        return <Upload className="w-4 h-4" />
      case 'project-assets':
        return <HardDrive className="w-4 h-4" />
      case 'temp-files':
        return <Clock className="w-4 h-4" />
      case 'public-assets':
        return <FileText className="w-4 h-4" />
      default:
        return <Database className="w-4 h-4" />
    }
  }

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return <Image className="w-4 h-4" />
    if (mimeType === 'application/pdf') return <FileText className="w-4 h-4" />
    if (mimeType.includes('zip') || mimeType.includes('compressed')) return <Archive className="w-4 h-4" />
    return <FileText className="w-4 h-4" />
  }

  const getMigrationStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge variant="default" className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>
      case 'in_progress':
        return <Badge variant="default" className="bg-blue-100 text-blue-800"><RefreshCw className="w-3 h-3 mr-1 animate-spin" />In Progress</Badge>
      case 'failed':
        return <Badge variant="destructive"><AlertCircle className="w-3 h-3 mr-1" />Failed</Badge>
      case 'pending':
        return <Badge variant="secondary"><Clock className="w-3 h-3 mr-1" />Pending</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <RefreshCw className="w-6 h-6 animate-spin" />
        <span className="ml-2">Loading storage data...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-stone-900">Storage Management</h1>
          <p className="text-stone-600">Monitor and manage file storage across all buckets</p>
        </div>
        <Button onClick={loadStorageData} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Storage Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.values(STORAGE_BUCKETS).map((bucket) => {
          const usage = storageUsage.find(u => u.bucket_id === bucket) || {
            total_files: 0,
            total_size_mb: 0
          }
          
          return (
            <Card key={bucket}>
              <CardHeader className="pb-2">
                <div className="flex items-center space-x-2">
                  {getBucketIcon(bucket)}
                  <CardTitle className="text-sm capitalize">
                    {bucket.replace('-', ' ')}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{usage.total_files}</div>
                <p className="text-xs text-stone-600">
                  {usage.total_size_mb} MB used
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="migration" className="space-y-4">
        <TabsList>
          <TabsTrigger value="migration">Migration Status</TabsTrigger>
          <TabsTrigger value="files">Recent Files</TabsTrigger>
          <TabsTrigger value="settings">Storage Settings</TabsTrigger>
        </TabsList>

        {/* Migration Status Tab */}
        <TabsContent value="migration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Storage Migration Status</CardTitle>
              <CardDescription>
                Monitor the progress of migrating files from legacy storage to Supabase
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {migrationStatuses.map((status) => (
                <div key={status.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {getBucketIcon(status.bucket_id)}
                      <span className="font-medium capitalize">
                        {status.bucket_id.replace('-', ' ')}
                      </span>
                      {getMigrationStatusBadge(status.migration_stage)}
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {status.migration_stage === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => startMigration(status.bucket_id)}
                          disabled={!!activeMigration}
                        >
                          <Play className="w-4 h-4 mr-1" />
                          Start Migration
                        </Button>
                      )}
                      
                      {status.migration_stage === 'in_progress' && (
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={stopMigration}
                        >
                          <Pause className="w-4 h-4 mr-1" />
                          Stop Migration
                        </Button>
                      )}
                    </div>
                  </div>

                  {status.migration_stage === 'in_progress' && migrationProgress && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Progress: {migrationProgress.current} / {migrationProgress.total}</span>
                        <span>{Math.round(migrationProgress.percentage)}%</span>
                      </div>
                      <Progress value={migrationProgress.percentage} className="h-2" />
                      {migrationProgress.currentFile && (
                        <p className="text-xs text-stone-600">
                          Current: {migrationProgress.currentFile}
                        </p>
                      )}
                    </div>
                  )}

                  {status.migration_stage === 'completed' && (
                    <div className="text-sm text-green-600">
                      ✓ Migration completed successfully
                    </div>
                  )}

                  {status.migration_stage === 'failed' && status.error_message && (
                    <div className="text-sm text-red-600">
                      ✗ Migration failed: {status.error_message}
                    </div>
                  )}

                  <div className="text-xs text-stone-500 mt-2">
                    Last updated: {new Date(status.updated_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recent Files Tab */}
        <TabsContent value="files" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Files</CardTitle>
              <CardDescription>
                Recently uploaded files across all storage buckets
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentFiles.map((file) => (
                  <div key={file.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                    {getFileIcon(file.mime_type)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{file.name}</p>
                      <p className="text-xs text-stone-500">
                        {file.bucket} • {formatFileSize(file.size)} • {new Date(file.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Button size="sm" variant="outline">
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Storage Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Storage Configuration</CardTitle>
              <CardDescription>
                Configure storage buckets, policies, and migration settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label htmlFor="default-bucket" className="text-sm font-medium">Default Bucket</label>
                  <select 
                    id="default-bucket"
                    className="w-full p-2 border rounded-md"
                    aria-label="Select default storage bucket"
                  >
                    {Object.values(STORAGE_BUCKETS).map((bucket) => (
                      <option key={bucket} value={bucket}>
                        {bucket.replace('-', ' ')}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-2">
                  <label htmlFor="max-file-size" className="text-sm font-medium">Max File Size (MB)</label>
                  <input 
                    id="max-file-size"
                    type="number" 
                    className="w-full p-2 border rounded-md" 
                    defaultValue="10"
                    aria-label="Maximum file size in megabytes"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Allowed File Types</label>
                <div className="flex flex-wrap gap-2">
                  {['image/*', 'application/pdf', 'text/*', 'application/zip'].map((type) => (
                    <Badge key={type} variant="outline" className="cursor-pointer hover:bg-stone-100">
                      {type}
                    </Badge>
                  ))}
                </div>
              </div>
              
              <Button>
                <Settings className="w-4 h-4 mr-2" />
                Save Configuration
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
