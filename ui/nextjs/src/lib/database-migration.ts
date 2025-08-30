import { supabase } from './supabase'

// Database migration service for Module 3: Database On-Ramp
// Handles dual-write operations between legacy and Supabase databases

export interface MigrationTable {
  name: string
  legacySchema: string
  supabaseSchema: string
  primaryKey: string
  requiredColumns: string[]
  optionalColumns: string[]
  indexes: string[]
  rlsPolicy: string
}

export interface MigrationStatus {
  table: string
  status: 'pending' | 'active' | 'completed' | 'failed'
  recordsMigrated: number
  recordsTotal: number
  lastSync: Date | null
  errors: string[]
}

export interface DualWriteResult {
  success: boolean
  legacyResult?: any
  supabaseResult?: any
  errors: string[]
  migrationStatus: MigrationStatus
}

export class DatabaseMigrationService {
  private static instance: DatabaseMigrationService
  private migrationStatus: Map<string, MigrationStatus> = new Map()
  private isInitialized = false

  // Core tables for migration (in order of dependency)
  private readonly migrationTables: MigrationTable[] = [
    {
      name: 'tenants',
      legacySchema: 'public',
      supabaseSchema: 'public',
      primaryKey: 'id',
      requiredColumns: ['id', 'name', 'slug', 'plan', 'status', 'created_at', 'updated_at'],
      optionalColumns: ['domain', 'isolation_mode', 'settings', 'limits', 'created_by', 'updated_by'],
      indexes: ['slug', 'status'],
      rlsPolicy: 'tenant_isolation'
    },
    {
      name: 'users',
      legacySchema: 'public',
      supabaseSchema: 'public',
      primaryKey: 'id',
      requiredColumns: ['id', 'tenant_id', 'email', 'name', 'role', 'status', 'created_at', 'updated_at'],
      optionalColumns: ['password_hash', 'last_login_at'],
      indexes: ['tenant_id', 'email'],
      rlsPolicy: 'user_tenant_isolation'
    },
    {
      name: 'projects',
      legacySchema: 'public',
      supabaseSchema: 'public',
      primaryKey: 'id',
      requiredColumns: ['id', 'tenant_id', 'name', 'description', 'project_type', 'status', 'created_at', 'updated_at'],
      optionalColumns: ['config', 'tech_stack', 'design_config', 'created_by'],
      indexes: ['tenant_id', 'status'],
      rlsPolicy: 'project_tenant_isolation'
    },
    {
      name: 'ideas',
      legacySchema: 'public',
      supabaseSchema: 'public',
      primaryKey: 'id',
      requiredColumns: ['id', 'tenant_id', 'project_name', 'description', 'problem', 'solution', 'status', 'created_at', 'updated_at'],
      optionalColumns: ['submitted_by', 'target_audience', 'key_features', 'business_model', 'category', 'priority', 'admin_notes', 'reviewed_by', 'reviewed_at', 'timeline', 'budget', 'submission_data', 'approval_data', 'project_id', 'promoted_at'],
      indexes: ['tenant_id', 'status', 'submitted_by', 'priority', 'category'],
      rlsPolicy: 'ideas_tenant_isolation'
    }
  ]

  private constructor() {}

  static getInstance(): DatabaseMigrationService {
    if (!DatabaseMigrationService.instance) {
      DatabaseMigrationService.instance = new DatabaseMigrationService()
    }
    return DatabaseMigrationService.instance
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return

    try {
      // Initialize migration status for all tables
      for (const table of this.migrationTables) {
        this.migrationStatus.set(table.name, {
          table: table.name,
          status: 'pending',
          recordsMigrated: 0,
          recordsTotal: 0,
          lastSync: null,
          errors: []
        })
      }

      // Verify Supabase connection
      const { data, error } = await supabase.from('tenants').select('count').limit(1)
      if (error) {
        throw new Error(`Failed to connect to Supabase: ${error.message}`)
      }

      this.isInitialized = true
      console.log('Database migration service initialized successfully')
    } catch (error) {
      console.error('Failed to initialize database migration service:', error)
      throw error
    }
  }

  async getMigrationStatus(): Promise<MigrationStatus[]> {
    await this.initialize()
    return Array.from(this.migrationStatus.values())
  }

  async getTableMigrationStatus(tableName: string): Promise<MigrationStatus | null> {
    await this.initialize()
    return this.migrationStatus.get(tableName) || null
  }

  async startTableMigration(tableName: string): Promise<MigrationStatus> {
    await this.initialize()
    
    const table = this.migrationTables.find(t => t.name === tableName)
    if (!table) {
      throw new Error(`Table ${tableName} not found in migration configuration`)
    }

    const status = this.migrationStatus.get(tableName)!
    status.status = 'active'
    status.lastSync = new Date()

    console.log(`Started migration for table: ${tableName}`)
    return status
  }

  async stopTableMigration(tableName: string): Promise<MigrationStatus> {
    await this.initialize()
    
    const status = this.migrationStatus.get(tableName)
    if (!status) {
      throw new Error(`Table ${tableName} not found in migration status`)
    }

    status.status = 'pending'
    status.lastSync = new Date()

    console.log(`Stopped migration for table: ${tableName}`)
    return status
  }

  async performDualWrite<T>(
    tableName: string,
    operation: 'INSERT' | 'UPDATE' | 'DELETE',
    data: T,
    where?: Record<string, any>
  ): Promise<DualWriteResult> {
    await this.initialize()

    const table = this.migrationTables.find(t => t.name === tableName)
    if (!table) {
      throw new Error(`Table ${tableName} not found in migration configuration`)
    }

    const status = this.migrationStatus.get(tableName)!
    const result: DualWriteResult = {
      success: false,
      errors: [],
      migrationStatus: status
    }

    try {
      // Perform legacy operation (this would call your existing FastAPI backend)
      // For now, we'll simulate this
      const legacyResult = await this.performLegacyOperation(tableName, operation, data, where)
      result.legacyResult = legacyResult

      // Perform Supabase operation if migration is active
      if (status.status === 'active') {
        const supabaseResult = await this.performSupabaseOperation(tableName, operation, data, where)
        result.supabaseResult = supabaseResult
        
        if (supabaseResult.success) {
          status.recordsMigrated++
          result.success = true
        } else {
          result.errors.push(`Supabase operation failed: ${supabaseResult.error}`)
        }
      } else {
        result.success = true // Only legacy operation
      }

      status.lastSync = new Date()
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      result.errors.push(errorMessage)
      status.errors.push(errorMessage)
    }

    return result
  }

  private async performLegacyOperation<T>(
    tableName: string,
    operation: 'INSERT' | 'UPDATE' | 'DELETE',
    data: T,
    where?: Record<string, any>
  ): Promise<any> {
    // This would make an API call to your existing FastAPI backend
    // For now, we'll simulate a successful operation
    console.log(`Legacy ${operation} operation on ${tableName}:`, { data, where })
    
    return {
      success: true,
      operation,
      table: tableName,
      timestamp: new Date().toISOString()
    }
  }

  private async performSupabaseOperation<T>(
    tableName: string,
    operation: 'INSERT' | 'UPDATE' | 'DELETE',
    data: T,
    where?: Record<string, any>
  ): Promise<{ success: boolean; error?: string; result?: any }> {
    try {
      let result

      switch (operation) {
        case 'INSERT':
          const { data: insertData, error: insertError } = await supabase
            .from(tableName)
            .insert(data)
            .select()
          
          if (insertError) throw insertError
          result = insertData
          break

        case 'UPDATE':
          const { data: updateData, error: updateError } = await supabase
            .from(tableName)
            .update(data)
            .match(where || {})
            .select()
          
          if (updateError) throw updateError
          result = updateData
          break

        case 'DELETE':
          const { data: deleteData, error: deleteError } = await supabase
            .from(tableName)
            .delete()
            .match(where || {})
            .select()
          
          if (deleteError) throw deleteError
          result = deleteData
          break

        default:
          throw new Error(`Unsupported operation: ${operation}`)
      }

      return { success: true, result }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      return { success: false, error: errorMessage }
    }
  }

  async validateDataConsistency(tableName: string): Promise<{
    consistent: boolean
    legacyCount: number
    supabaseCount: number
    differences: string[]
  }> {
    await this.initialize()

    const table = this.migrationTables.find(t => t.name === tableName)
    if (!table) {
      throw new Error(`Table ${tableName} not found in migration configuration`)
    }

    try {
      // Get legacy count (this would call your existing FastAPI backend)
      const legacyCount = await this.getLegacyRecordCount(tableName)
      
      // Get Supabase count
      const { count: supabaseCount, error } = await supabase
        .from(tableName)
        .select('*', { count: 'exact', head: true })

      if (error) {
        throw new Error(`Failed to get Supabase count: ${error.message}`)
      }

      const consistent = legacyCount === supabaseCount
      const differences = consistent ? [] : [
        `Record count mismatch: Legacy=${legacyCount}, Supabase=${supabaseCount}`
      ]

      return {
        consistent,
        legacyCount,
        supabaseCount: supabaseCount || 0,
        differences
      }
    } catch (error) {
      throw new Error(`Data consistency validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  private async getLegacyRecordCount(tableName: string): Promise<number> {
    // This would make an API call to your existing FastAPI backend
    // For now, we'll simulate a count
    console.log(`Getting legacy record count for table: ${tableName}`)
    return Math.floor(Math.random() * 100) + 10 // Simulated count
  }

  async getMigrationTables(): Promise<MigrationTable[]> {
    await this.initialize()
    return this.migrationTables
  }

  async resetMigrationStatus(tableName?: string): Promise<void> {
    await this.initialize()

    if (tableName) {
      const status = this.migrationStatus.get(tableName)
      if (status) {
        status.status = 'pending'
        status.recordsMigrated = 0
        status.errors = []
        status.lastSync = null
      }
    } else {
      // Reset all tables
      for (const status of this.migrationStatus.values()) {
        status.status = 'pending'
        status.recordsMigrated = 0
        status.errors = []
        status.lastSync = null
      }
    }
  }
}

// Export singleton instance
export const databaseMigrationService = DatabaseMigrationService.getInstance()
