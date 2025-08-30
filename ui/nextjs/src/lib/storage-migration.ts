import { supabase } from './supabase'
import { storageManager, STORAGE_BUCKETS, StorageBucket } from './storage'

export interface MigrationStatus {
  id: string
  tenant_id: string
  bucket_id: string
  migration_stage: 'pending' | 'in_progress' | 'completed' | 'failed'
  objects_migrated: number
  total_objects: number
  last_migration_at?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface MigrationProgress {
  current: number
  total: number
  percentage: number
  stage: string
  currentFile?: string
}

export interface MigrationOptions {
  batchSize?: number
  maxConcurrent?: number
  dryRun?: boolean
  onProgress?: (progress: MigrationProgress) => void
}

export class StorageMigrationService {
  private isRunning = false
  private currentMigration: string | null = null

  // Get migration status for a tenant and bucket
  async getMigrationStatus(tenantId: string, bucketId: string): Promise<MigrationStatus | null> {
    try {
      const { data, error } = await supabase
        .from('storage_migration_status')
        .select('*')
        .eq('tenant_id', tenantId)
        .eq('bucket_id', bucketId)
        .single()

      if (error) {
        console.error('Error fetching migration status:', error)
        return null
      }

      return data
    } catch (error) {
      console.error('Error fetching migration status:', error)
      return null
    }
  }

  // Get all migration statuses for a tenant
  async getTenantMigrationStatuses(tenantId: string): Promise<MigrationStatus[]> {
    try {
      const { data, error } = await supabase
        .from('storage_migration_status')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('bucket_id')

      if (error) {
        console.error('Error fetching tenant migration statuses:', error)
        return []
      }

      return data || []
    } catch (error) {
      console.error('Error fetching tenant migration statuses:', error)
      return []
    }
  }

  // Start migration for a specific bucket
  async startMigration(
    tenantId: string, 
    bucketId: string, 
    options: MigrationOptions = {}
  ): Promise<boolean> {
    if (this.isRunning) {
      console.warn('Migration already running')
      return false
    }

    const {
      batchSize = 10,
      maxConcurrent = 3,
      dryRun = false,
      onProgress
    } = options

    try {
      this.isRunning = true
      this.currentMigration = `${tenantId}-${bucketId}`

      // Update migration status to in_progress
      await this.updateMigrationStatus(tenantId, bucketId, {
        migration_stage: 'in_progress',
        last_migration_at: new Date().toISOString()
      })

      // Get total objects to migrate (this would come from legacy system)
      const totalObjects = await this.getLegacyObjectCount(tenantId, bucketId)
      
      if (totalObjects === 0) {
        await this.updateMigrationStatus(tenantId, bucketId, {
          migration_stage: 'completed',
          objects_migrated: 0,
          total_objects: 0
        })
        return true
      }

      // Update total objects count
      await this.updateMigrationStatus(tenantId, bucketId, {
        total_objects: totalObjects
      })

      // Start migration process
      const success = await this.migrateObjects(
        tenantId,
        bucketId,
        totalObjects,
        batchSize,
        maxConcurrent,
        dryRun,
        onProgress
      )

      if (success) {
        await this.updateMigrationStatus(tenantId, bucketId, {
          migration_stage: 'completed',
          objects_migrated: totalObjects,
          last_migration_at: new Date().toISOString()
        })
      } else {
        await this.updateMigrationStatus(tenantId, bucketId, {
          migration_stage: 'failed',
          error_message: 'Migration failed during execution'
        })
      }

      return success
    } catch (error) {
      console.error('Migration failed:', error)
      await this.updateMigrationStatus(tenantId, bucketId, {
        migration_stage: 'failed',
        error_message: error instanceof Error ? error.message : 'Unknown error'
      })
      return false
    } finally {
      this.isRunning = false
      this.currentMigration = null
    }
  }

  // Stop current migration
  async stopMigration(): Promise<boolean> {
    if (!this.isRunning || !this.currentMigration) {
      return false
    }

    try {
      const [tenantId, bucketId] = this.currentMigration.split('-')
      
      await this.updateMigrationStatus(tenantId, bucketId, {
        migration_stage: 'failed',
        error_message: 'Migration stopped by user'
      })

      this.isRunning = false
      this.currentMigration = null
      return true
    } catch (error) {
      console.error('Error stopping migration:', error)
      return false
    }
  }

  // Get migration progress
  async getMigrationProgress(tenantId: string, bucketId: string): Promise<MigrationProgress | null> {
    const status = await this.getMigrationStatus(tenantId, bucketId)
    if (!status) return null

    return {
      current: status.objects_migrated,
      total: status.total_objects,
      percentage: status.total_objects > 0 ? (status.objects_migrated / status.total_objects) * 100 : 0,
      stage: status.migration_stage,
      currentFile: undefined // Would be set during active migration
    }
  }

  // Validate migration readiness
  async validateMigrationReadiness(tenantId: string, bucketId: string): Promise<{
    ready: boolean
    issues: string[]
  }> {
    const issues: string[] = []

    try {
      // Check if bucket exists
      const { data: bucket, error: bucketError } = await supabase.storage
        .getBucket(bucketId)

      if (bucketError || !bucket) {
        issues.push(`Bucket '${bucketId}' does not exist or is not accessible`)
      }

      // Check if migration status table exists
      const { error: tableError } = await supabase
        .from('storage_migration_status')
        .select('id')
        .limit(1)

      if (tableError) {
        issues.push('Migration status table is not accessible')
      }

      // Check if legacy system is accessible (placeholder)
      const legacyAccessible = await this.checkLegacySystemAccess(tenantId, bucketId)
      if (!legacyAccessible) {
        issues.push('Legacy storage system is not accessible')
      }

      // Check storage permissions
      const permissionsOk = await this.checkStoragePermissions(bucketId)
      if (!permissionsOk) {
        issues.push(`Insufficient permissions for bucket '${bucketId}'`)
      }

      return {
        ready: issues.length === 0,
        issues
      }
    } catch (error) {
      issues.push(`Validation error: ${error instanceof Error ? error.message : 'Unknown error'}`)
      return {
        ready: false,
        issues
      }
    }
  }

  // Private methods

  private async updateMigrationStatus(
    tenantId: string, 
    bucketId: string, 
    updates: Partial<MigrationStatus>
  ): Promise<void> {
    try {
      const { error } = await supabase
        .from('storage_migration_status')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('tenant_id', tenantId)
        .eq('bucket_id', bucketId)

      if (error) {
        console.error('Error updating migration status:', error)
      }
    } catch (error) {
      console.error('Error updating migration status:', error)
    }
  }

  private async migrateObjects(
    tenantId: string,
    bucketId: string,
    totalObjects: number,
    batchSize: number,
    maxConcurrent: number,
    dryRun: boolean,
    onProgress?: (progress: MigrationProgress) => void
  ): Promise<boolean> {
    let migratedCount = 0
    let failedCount = 0

    try {
      // Get objects to migrate in batches
      for (let offset = 0; offset < totalObjects; offset += batchSize) {
        if (!this.isRunning) {
          console.log('Migration stopped')
          break
        }

        const batch = await this.getLegacyObjectsBatch(tenantId, bucketId, offset, batchSize)
        
        if (batch.length === 0) break

        // Process batch with concurrency control
        const batchPromises = batch.map(async (object, index) => {
          if (!this.isRunning) return false

          try {
            if (!dryRun) {
              const success = await this.migrateSingleObject(tenantId, bucketId, object)
              if (success) {
                migratedCount++
              } else {
                failedCount++
              }
            } else {
              // Simulate migration for dry run
              await new Promise(resolve => setTimeout(resolve, 100))
              migratedCount++
            }

            // Update progress
            const progress: MigrationProgress = {
              current: migratedCount + failedCount,
              total: totalObjects,
              percentage: ((migratedCount + failedCount) / totalObjects) * 100,
              stage: dryRun ? 'dry_run' : 'migrating',
              currentFile: object.name
            }

            onProgress?.(progress)

            // Update migration status
            await this.updateMigrationStatus(tenantId, bucketId, {
              objects_migrated: migratedCount
            })

            return true
          } catch (error) {
            console.error(`Error migrating object ${object.name}:`, error)
            failedCount++
            return false
          }
        })

        // Wait for batch to complete
        await Promise.all(batchPromises)

        // Small delay between batches
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      console.log(`Migration completed: ${migratedCount} migrated, ${failedCount} failed`)
      return failedCount === 0 || (migratedCount / totalObjects) > 0.95 // 95% success threshold
    } catch (error) {
      console.error('Error during migration:', error)
      return false
    }
  }

  private async migrateSingleObject(
    tenantId: string, 
    bucketId: string, 
    object: any
  ): Promise<boolean> {
    try {
      // Download from legacy system
      const legacyData = await this.downloadFromLegacy(tenantId, bucketId, object.path)
      if (!legacyData) {
        console.warn(`Could not download ${object.path} from legacy system`)
        return false
      }

      // Upload to Supabase
      const result = await storageManager.upload(
        legacyData,
        bucketId as StorageBucket,
        object.path,
        {
          originalName: object.name,
          orgId: tenantId,
          resource: bucketId,
          migratedFrom: 'legacy',
          migratedAt: new Date().toISOString()
        }
      )

      return result.success
    } catch (error) {
      console.error(`Error migrating object ${object.path}:`, error)
      return false
    }
  }

  // Placeholder methods for legacy system integration
  private async getLegacyObjectCount(tenantId: string, bucketId: string): Promise<number> {
    // TODO: Implement actual legacy system integration
    // This would query the existing file storage system
    console.log(`Getting legacy object count for tenant ${tenantId}, bucket ${bucketId}`)
    return 0 // Placeholder
  }

  private async getLegacyObjectsBatch(
    tenantId: string, 
    bucketId: string, 
    offset: number, 
    limit: number
  ): Promise<any[]> {
    // TODO: Implement actual legacy system integration
    // This would query the existing file storage system
    console.log(`Getting legacy objects batch for tenant ${tenantId}, bucket ${bucketId}, offset ${offset}, limit ${limit}`)
    return [] // Placeholder
  }

  private async downloadFromLegacy(tenantId: string, bucketId: string, path: string): Promise<File | null> {
    // TODO: Implement actual legacy system integration
    // This would download from the existing file storage system
    console.log(`Downloading from legacy: tenant ${tenantId}, bucket ${bucketId}, path ${path}`)
    return null // Placeholder
  }

  private async checkLegacySystemAccess(tenantId: string, bucketId: string): Promise<boolean> {
    // TODO: Implement actual legacy system access check
    console.log(`Checking legacy system access for tenant ${tenantId}, bucket ${bucketId}`)
    return true // Placeholder
  }

  private async checkStoragePermissions(bucketId: string): Promise<boolean> {
    try {
      // Test upload permissions
      const testFile = new File(['test'], 'test.txt', { type: 'text/plain' })
      const testPath = `test-${Date.now()}.txt`
      
      const result = await storageManager.upload(
        testFile,
        bucketId as StorageBucket,
        testPath,
        { test: true }
      )

      if (result.success) {
        // Clean up test file
        await storageManager.delete(testPath, bucketId as StorageBucket)
        return true
      }

      return false
    } catch (error) {
      console.error('Error checking storage permissions:', error)
      return false
    }
  }
}

// Export singleton instance
export const storageMigrationService = new StorageMigrationService()
