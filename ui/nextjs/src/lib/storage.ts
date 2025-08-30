import { supabase } from './supabase'

// Feature flag for storage migration
const STORAGE_SUPABASE_ENABLED = process.env.NEXT_PUBLIC_STORAGE_SUPABASE === 'true'

// Storage bucket configuration
export const STORAGE_BUCKETS = {
  USER_UPLOADS: 'user-uploads',
  PROJECT_ASSETS: 'project-assets',
  TEMP_FILES: 'temp-files',
  PUBLIC_ASSETS: 'public-assets'
} as const

export type StorageBucket = typeof STORAGE_BUCKETS[keyof typeof STORAGE_BUCKETS]

// Object naming scheme: {org_id}/{resource}/{yyyy}/{mm}/{uuid}.{ext}
export interface StorageObject {
  id: string
  name: string
  bucket: StorageBucket
  path: string
  size: number
  mimeType: string
  metadata?: Record<string, any>
  createdAt: Date
  updatedAt: Date
}

// Upload result interface
export interface UploadResult {
  success: boolean
  object?: StorageObject
  url?: string
  error?: string
  provider: 'supabase' | 'legacy'
}

// Storage provider interface
export interface StorageProvider {
  upload(
    file: File,
    bucket: StorageBucket,
    path: string,
    metadata?: Record<string, any>
  ): Promise<UploadResult>
  
  download(path: string, bucket: StorageBucket): Promise<Blob | null>
  
  delete(path: string, bucket: StorageBucket): Promise<boolean>
  
  getSignedUrl(path: string, bucket: StorageBucket, expiresIn?: number): Promise<string | null>
  
  listObjects(bucket: StorageBucket, prefix?: string): Promise<StorageObject[]>
}

// Supabase Storage Provider Implementation
export class SupabaseStorageProvider implements StorageProvider {
  async upload(
    file: File,
    bucket: StorageBucket,
    path: string,
    metadata?: Record<string, any>
  ): Promise<UploadResult> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .upload(path, file, {
          cacheControl: '3600',
          upsert: false,
          metadata: {
            ...metadata,
            originalName: file.name,
            size: file.size,
            mimeType: file.type,
            uploadedAt: new Date().toISOString()
          }
        })

      if (error) {
        console.error('Supabase upload error:', error)
        return {
          success: false,
          error: error.message,
          provider: 'supabase'
        }
      }

      // Get public URL
      const { data: urlData } = supabase.storage
        .from(bucket)
        .getPublicUrl(path)

      const storageObject: StorageObject = {
        id: data.id,
        name: file.name,
        bucket,
        path,
        size: file.size,
        mimeType: file.type,
        metadata,
        createdAt: new Date(),
        updatedAt: new Date()
      }

      return {
        success: true,
        object: storageObject,
        url: urlData.publicUrl,
        provider: 'supabase'
      }
    } catch (error) {
      console.error('Supabase upload exception:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        provider: 'supabase'
      }
    }
  }

  async download(path: string, bucket: StorageBucket): Promise<Blob | null> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .download(path)

      if (error) {
        console.error('Supabase download error:', error)
        return null
      }

      return data
    } catch (error) {
      console.error('Supabase download exception:', error)
      return null
    }
  }

  async delete(path: string, bucket: StorageBucket): Promise<boolean> {
    try {
      const { error } = await supabase.storage
        .from(bucket)
        .remove([path])

      if (error) {
        console.error('Supabase delete error:', error)
        return false
      }

      return true
    } catch (error) {
      console.error('Supabase delete exception:', error)
      return false
    }
  }

  async getSignedUrl(path: string, bucket: StorageBucket, expiresIn: number = 3600): Promise<string | null> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .createSignedUrl(path, expiresIn)

      if (error) {
        console.error('Supabase signed URL error:', error)
        return null
      }

      return data.signedUrl
    } catch (error) {
      console.error('Supabase signed URL exception:', error)
      return null
    }
  }

  async listObjects(bucket: StorageBucket, prefix?: string): Promise<StorageObject[]> {
    try {
      const { data, error } = await supabase.storage
        .from(bucket)
        .list(prefix || '')

      if (error) {
        console.error('Supabase list objects error:', error)
        return []
      }

      return data.map(item => ({
        id: item.id,
        name: item.name,
        bucket,
        path: prefix ? `${prefix}/${item.name}` : item.name,
        size: item.metadata?.size || 0,
        mimeType: item.metadata?.mimetype || 'application/octet-stream',
        metadata: item.metadata,
        createdAt: new Date(item.created_at),
        updatedAt: new Date(item.updated_at)
      }))
    } catch (error) {
      console.error('Supabase list objects exception:', error)
      return []
    }
  }
}

// Legacy Storage Provider - REMOVED - No longer needed for Module 4
// All storage operations now use Supabase directly

// Storage Manager - Main interface for file operations
export class StorageManager {
  private supabaseProvider: SupabaseStorageProvider

  constructor() {
    this.supabaseProvider = new SupabaseStorageProvider()
  }

  // Get the storage provider (Supabase only for Module 4)
  private getProvider(): StorageProvider {
    return this.supabaseProvider
  }

  // Upload file with automatic provider selection
  async upload(
    file: File,
    bucket: StorageBucket,
    path: string,
    metadata?: Record<string, any>
  ): Promise<UploadResult> {
    const provider = this.getProvider()
    return provider.upload(file, bucket, path, metadata)
  }

  // Download file from Supabase
  async download(path: string, bucket: StorageBucket): Promise<Blob | null> {
    return this.supabaseProvider.download(path, bucket)
  }

  // Delete file
  async delete(path: string, bucket: StorageBucket): Promise<boolean> {
    const provider = this.getProvider()
    return provider.delete(path, bucket)
  }

  // Get signed URL
  async getSignedUrl(path: string, bucket: StorageBucket, expiresIn?: number): Promise<string | null> {
    const provider = this.getProvider()
    return provider.getSignedUrl(path, bucket, expiresIn)
  }

  // List objects
  async listObjects(bucket: StorageBucket, prefix?: string): Promise<StorageObject[]> {
    const provider = this.getProvider()
    return provider.listObjects(bucket, prefix)
  }

  // Dual-write upload (for migration period)
  async dualWriteUpload(
    file: File,
    bucket: StorageBucket,
    path: string,
    metadata?: Record<string, any>
  ): Promise<{ supabase: UploadResult; legacy: UploadResult }> {
    const [supabaseResult, legacyResult] = await Promise.allSettled([
      this.supabaseProvider.upload(file, bucket, path, metadata),
      this.legacyProvider.upload(file, bucket, path, metadata)
    ])

    return {
      supabase: supabaseResult.status === 'fulfilled' ? supabaseResult.value : {
        success: false,
        error: 'Supabase upload failed',
        provider: 'supabase'
      },
      legacy: legacyResult.status === 'fulfilled' ? legacyResult.value : {
        success: false,
        error: 'Legacy upload failed',
        provider: 'legacy'
      }
    }
  }
}

// Export singleton instance
export const storageManager = new StorageManager()

// Utility functions
export const generateStoragePath = (
  orgId: string,
  resource: string,
  filename: string
): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const uuid = crypto.randomUUID()
  const extension = filename.split('.').pop() || 'bin'
  
  return `${orgId}/${resource}/${year}/${month}/${uuid}.${extension}`
}

export const validateFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(file.type)
}

export const validateFileSize = (file: File, maxSizeBytes: number): boolean => {
  return file.size <= maxSizeBytes
}
