'use client'

import React, { useState, useRef, useCallback } from 'react'
import { Button } from './button'
import { Card, CardContent } from './card'
import { Progress } from './progress'
import { 
  Upload, 
  X, 
  File, 
  Image, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Trash2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { 
  storageManager, 
  STORAGE_BUCKETS, 
  StorageBucket, 
  generateStoragePath,
  validateFileType,
  validateFileSize
} from '@/lib/storage'

export interface FileUploadProps {
  bucket: StorageBucket
  orgId?: string
  resource?: string
  maxFiles?: number
  maxFileSize?: number // in bytes
  allowedTypes?: string[]
  onUploadComplete?: (files: Array<{ path: string; url: string; name: string }>) => void
  onUploadError?: (error: string) => void
  className?: string
  disabled?: boolean
  showPreview?: boolean
  multiple?: boolean
}

export interface UploadedFile {
  id: string
  file: File
  path: string
  url?: string
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
}

export default function FileUpload({
  bucket,
  orgId = 'default',
  resource = 'uploads',
  maxFiles = 5,
  maxFileSize = 10 * 1024 * 1024, // 10MB default
  allowedTypes = ['image/*', 'application/pdf', 'text/*'],
  onUploadComplete,
  onUploadError,
  className,
  disabled = false,
  showPreview = true,
  multiple = true
}: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Handle file selection
  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files) return

    const newFiles: UploadedFile[] = Array.from(files).map(file => {
      // Validate file type
      if (!validateFileType(file, allowedTypes)) {
        onUploadError?.(`File type not allowed: ${file.type}`)
        return null
      }

      // Validate file size
      if (!validateFileSize(file, maxFileSize)) {
        onUploadError?.(`File too large: ${(file.size / 1024 / 1024).toFixed(2)}MB (max: ${(maxFileSize / 1024 / 1024).toFixed(2)}MB)`)
        return null
      }

      // Check if we've reached max files
      if (uploadedFiles.length >= maxFiles) {
        onUploadError?.(`Maximum ${maxFiles} files allowed`)
        return null
      }

      const path = generateStoragePath(orgId, resource, file.name)
      
      return {
        id: crypto.randomUUID(),
        file,
        path,
        progress: 0,
        status: 'pending' as const
      }
    }).filter(Boolean) as UploadedFile[]

    setUploadedFiles(prev => [...prev, ...newFiles])
  }, [allowedTypes, maxFileSize, maxFiles, orgId, resource, uploadedFiles.length, onUploadError])

  // Handle drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }, [handleFileSelect])

  // Upload files
  const uploadFiles = useCallback(async () => {
    if (uploadedFiles.length === 0 || isUploading) return

    setIsUploading(true)
    const filesToUpload = uploadedFiles.filter(f => f.status === 'pending')
    
    const uploadPromises = filesToUpload.map(async (uploadFile) => {
      // Update status to uploading
      setUploadedFiles(prev => prev.map(f => 
        f.id === uploadFile.id 
          ? { ...f, status: 'uploading', progress: 0 }
          : f
      ))

      try {
        // Simulate progress (in real implementation, you'd track actual upload progress)
        const progressInterval = setInterval(() => {
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadFile.id 
              ? { ...f, progress: Math.min(f.progress + Math.random() * 30, 90) }
              : f
          ))
        }, 100)

        // Upload to storage
        const result = await storageManager.upload(
          uploadFile.file,
          bucket,
          uploadFile.path,
          {
            originalName: uploadFile.file.name,
            orgId,
            resource
          }
        )

        clearInterval(progressInterval)

        if (result.success && result.object && result.url) {
          // Update status to completed
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadFile.id 
              ? { 
                  ...f, 
                  status: 'completed', 
                  progress: 100, 
                  url: result.url 
                }
              : f
          ))
        } else {
          // Update status to error
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadFile.id 
              ? { 
                  ...f, 
                  status: 'error', 
                  error: result.error || 'Upload failed' 
                }
              : f
          ))
          onUploadError?.(result.error || 'Upload failed')
        }
      } catch (error) {
        setUploadedFiles(prev => prev.map(f => 
          f.id === uploadFile.id 
            ? { 
                ...f, 
                status: 'error', 
                error: error instanceof Error ? error.message : 'Upload failed' 
              }
            : f
        ))
        onUploadError?.(error instanceof Error ? error.message : 'Upload failed')
      }
    })

    await Promise.all(uploadPromises)
    setIsUploading(false)

    // Call completion callback
    const completedFiles = uploadedFiles.filter(f => f.status === 'completed' && f.url)
    if (completedFiles.length > 0) {
      onUploadComplete?.(completedFiles.map(f => ({
        path: f.path,
        url: f.url!,
        name: f.file.name
      })))
    }
  }, [uploadedFiles, isUploading, bucket, orgId, resource, onUploadComplete, onUploadError])

  // Remove file
  const removeFile = useCallback((id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id))
  }, [])

  // Get file icon based on type
  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <Image className="w-4 h-4" />
    if (file.type === 'application/pdf') return <FileText className="w-4 h-4" />
    return <File className="w-4 h-4" />
  }

  // Get file status icon
  const getStatusIcon = (status: UploadedFile['status'], error?: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" title={error} />
      case 'uploading':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      default:
        return null
    }
  }

  return (
    <div className={cn('w-full', className)}>
      {/* File Drop Zone */}
      <Card 
        className={cn(
          'border-2 border-dashed transition-colors cursor-pointer',
          isDragging 
            ? 'border-green-500 bg-green-50' 
            : 'border-stone-300 hover:border-stone-400',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <CardContent className="p-6 text-center">
          <Upload className="w-8 h-8 text-stone-400 mx-auto mb-2" />
          <p className="text-sm text-stone-600 mb-1">
            {isDragging ? 'Drop files here' : 'Click to upload or drag and drop'}
          </p>
          <p className="text-xs text-stone-500">
            {allowedTypes.join(', ')} • Max {maxFileSize / 1024 / 1024}MB per file
          </p>
        </CardContent>
      </Card>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple={multiple}
        accept={allowedTypes.join(',')}
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
        disabled={disabled}
        aria-label="File upload input"
        title="Select files to upload"
      />

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-stone-700">
              Files ({uploadedFiles.length}/{maxFiles})
            </h4>
            <Button
              onClick={uploadFiles}
              disabled={isUploading || uploadedFiles.every(f => f.status !== 'pending')}
              size="sm"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload All
                </>
              )}
            </Button>
          </div>

          {uploadedFiles.map((uploadFile) => (
            <div
              key={uploadFile.id}
              className="flex items-center space-x-3 p-3 bg-stone-50 rounded-lg border"
            >
              {showPreview && (
                <div className="flex-shrink-0">
                  {getFileIcon(uploadFile.file)}
                </div>
              )}
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-stone-900 truncate">
                    {uploadFile.file.name}
                  </p>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(uploadFile.status, uploadFile.error)}
                    <Button
                      onClick={() => removeFile(uploadFile.id)}
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
                
                <div className="mt-1">
                  <Progress value={uploadFile.progress} className="h-2" />
                  <p className="text-xs text-stone-500 mt-1">
                    {uploadFile.status === 'completed' && 'Upload complete'}
                    {uploadFile.status === 'error' && uploadFile.error}
                    {uploadFile.status === 'uploading' && 'Uploading...'}
                    {uploadFile.status === 'pending' && 'Ready to upload'}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
