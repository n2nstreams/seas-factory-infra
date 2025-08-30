'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Upload, 
  Download, 
  Trash2, 
  Eye,
  FileText,
  Image,
  Archive,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import FileUpload from '@/components/ui/FileUpload'
import { STORAGE_BUCKETS, StorageBucket } from '@/lib/storage'

interface DemoFile {
  id: string
  name: string
  bucket: StorageBucket
  path: string
  size: number
  mimeType: string
  url: string
  uploadedAt: Date
}

export default function StorageDemoPage() {
  const [uploadedFiles, setUploadedFiles] = useState<DemoFile[]>([])
  const [activeTab, setActiveTab] = useState('upload')

  const handleUploadComplete = (files: Array<{ path: string; url: string; name: string }>) => {
    const newFiles: DemoFile[] = files.map((file, index) => ({
      id: `demo-${Date.now()}-${index}`,
      name: file.name,
      bucket: 'user-uploads' as StorageBucket,
      path: file.path,
      size: Math.floor(Math.random() * 5 * 1024 * 1024) + 1024 * 1024, // 1-6MB
      mimeType: getMimeType(file.name),
      url: file.url,
      uploadedAt: new Date()
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error)
    // You could show a toast notification here
  }

  const getMimeType = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase()
    switch (ext) {
      case 'jpg':
      case 'jpeg':
        return 'image/jpeg'
      case 'png':
        return 'image/png'
      case 'pdf':
        return 'application/pdf'
      case 'txt':
        return 'text/plain'
      case 'zip':
        return 'application/zip'
      default:
        return 'application/octet-stream'
    }
  }

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return <Image className="w-4 h-4" />
    if (mimeType === 'application/pdf') return <FileText className="w-4 h-4" />
    if (mimeType.includes('zip')) return <Archive className="w-4 h-4" />
    return <FileText className="w-4 h-4" />
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id))
  }

  const downloadFile = (file: DemoFile) => {
    // Create a temporary link to download the file
    const link = document.createElement('a')
    link.href = file.url
    link.download = file.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const viewFile = (file: DemoFile) => {
    if (file.mimeType.startsWith('image/')) {
      window.open(file.url, '_blank')
    } else {
      // For non-image files, try to open in new tab
      window.open(file.url, '_blank')
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold text-stone-900">Storage Demo</h1>
        <p className="text-stone-600">
          Test the new Supabase storage system with file uploads and management
        </p>
        <div className="flex items-center justify-center space-x-2">
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <CheckCircle className="w-3 h-3 mr-1" />
            Supabase Storage Active
          </Badge>
          <Badge variant="outline">
            Feature Flag: storage_supabase
          </Badge>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload">File Upload</TabsTrigger>
          <TabsTrigger value="files">File Management</TabsTrigger>
          <TabsTrigger value="info">Storage Info</TabsTrigger>
        </TabsList>

        {/* File Upload Tab */}
        <TabsContent value="upload" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="w-5 h-5" />
                <span>Upload Files</span>
              </CardTitle>
              <CardDescription>
                Test the new file upload system with drag & drop support
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FileUpload
                bucket="user-uploads"
                orgId="demo-org"
                resource="demo-uploads"
                maxFiles={10}
                maxFileSize={10 * 1024 * 1024} // 10MB
                allowedTypes={[
                  'image/*',
                  'application/pdf',
                  'text/*',
                  'application/zip'
                ]}
                onUploadComplete={handleUploadComplete}
                onUploadError={handleUploadError}
                showPreview={true}
                multiple={true}
              />
            </CardContent>
          </Card>

          {/* Upload Instructions */}
          <Card>
            <CardHeader>
              <CardTitle>How to Test</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium text-stone-900">Supported File Types</h4>
                  <ul className="text-sm text-stone-600 space-y-1">
                    <li>• Images (JPG, PNG, GIF)</li>
                    <li>• Documents (PDF, TXT)</li>
                    <li>• Archives (ZIP, RAR)</li>
                    <li>• Maximum size: 10MB per file</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-stone-900">Features</h4>
                  <ul className="text-sm text-stone-600 space-y-1">
                    <li>• Drag & drop support</li>
                    <li>• Progress tracking</li>
                    <li>• File validation</li>
                    <li>• Automatic path generation</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* File Management Tab */}
        <TabsContent value="files" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>Uploaded Files</span>
                <Badge variant="secondary">{uploadedFiles.length} files</Badge>
              </CardTitle>
              <CardDescription>
                Manage and view your uploaded files
              </CardDescription>
            </CardHeader>
            <CardContent>
              {uploadedFiles.length === 0 ? (
                <div className="text-center py-8 text-stone-500">
                  <Upload className="w-12 h-12 mx-auto mb-2 text-stone-300" />
                  <p>No files uploaded yet</p>
                  <p className="text-sm">Upload some files in the Upload tab to see them here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {uploadedFiles.map((file) => (
                    <div
                      key={file.id}
                      className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-stone-50 transition-colors"
                    >
                      {getFileIcon(file.mimeType)}
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-stone-900 truncate">
                            {file.name}
                          </p>
                          <Badge variant="outline" className="text-xs">
                            {file.bucket}
                          </Badge>
                        </div>
                        <p className="text-xs text-stone-500">
                          {formatFileSize(file.size)} • {file.mimeType} • {file.uploadedAt.toLocaleDateString()}
                        </p>
                        <p className="text-xs text-stone-400 font-mono truncate">
                          {file.path}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-1">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => viewFile(file)}
                          title="View file"
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => downloadFile(file)}
                          title="Download file"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => removeFile(file.id)}
                          title="Remove file"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Storage Info Tab */}
        <TabsContent value="info" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Storage Buckets */}
            <Card>
              <CardHeader>
                <CardTitle>Storage Buckets</CardTitle>
                <CardDescription>
                  Available storage buckets and their purposes
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.values(STORAGE_BUCKETS).map((bucket) => (
                  <div key={bucket} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Upload className="w-4 h-4 text-stone-400" />
                      <span className="font-medium capitalize">
                        {bucket.replace('-', ' ')}
                      </span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {bucket === 'public-assets' ? 'Public' : 'Private'}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Migration Status */}
            <Card>
              <CardHeader>
                <CardTitle>Migration Status</CardTitle>
                <CardDescription>
                  Current status of storage migration from legacy system
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {Object.values(STORAGE_BUCKETS).map((bucket) => (
                  <div key={bucket} className="flex items-center justify-between p-3 border rounded-lg">
                    <span className="font-medium capitalize">
                      {bucket.replace('-', ' ')}
                    </span>
                    <Badge variant="secondary" className="bg-green-50 text-green-700">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Ready
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Technical Details */}
          <Card>
            <CardHeader>
              <CardTitle>Technical Implementation</CardTitle>
              <CardDescription>
                Details about the storage system architecture
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium text-stone-900">Storage Provider</h4>
                  <p className="text-sm text-stone-600">
                    Supabase Storage with Row Level Security (RLS) policies
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-stone-900">Object Naming</h4>
                  <p className="text-sm text-stone-600">
                    {`{org_id}/{resource}/{yyyy}/{mm}/{uuid}.{ext}`}
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-stone-900">Security</h4>
                  <p className="text-sm text-stone-600">
                    Tenant isolation with RLS policies
                  </p>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium text-stone-900">Fallback</h4>
                  <p className="text-sm text-stone-600">
                    Automatic fallback to legacy system if needed
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
