import { supabase } from './supabase'
import { databaseMigrationService, MigrationTable } from './database-migration'

// ETL Service for Module 3: Database On-Ramp
// Handles data extraction, transformation, and loading between legacy and Supabase databases

export interface ETLJob {
  id: string
  tableName: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  recordsProcessed: number
  recordsTotal: number
  startedAt: Date | null
  completedAt: Date | null
  error: string | null
  metadata: Record<string, any>
}

export interface ETLResult {
  success: boolean
  recordsProcessed: number
  recordsTotal: number
  errors: string[]
  warnings: string[]
  metadata: Record<string, any>
}

export interface DataMapping {
  legacyColumn: string
  supabaseColumn: string
  transformation?: (value: any) => any
  required: boolean
  defaultValue?: any
}

export class ETLService {
  private static instance: ETLService
  private activeJobs: Map<string, ETLJob> = new Map()
  private isInitialized = false

  // Data mappings for each table
  private readonly dataMappings: Record<string, DataMapping[]> = {
    tenants: [
      { legacyColumn: 'id', supabaseColumn: 'id', required: true },
      { legacyColumn: 'name', supabaseColumn: 'name', required: true },
      { legacyColumn: 'slug', supabaseColumn: 'slug', required: true },
      { legacyColumn: 'domain', supabaseColumn: 'domain', required: false },
      { legacyColumn: 'plan', supabaseColumn: 'plan', required: true, defaultValue: 'starter' },
      { legacyColumn: 'status', supabaseColumn: 'status', required: true, defaultValue: 'active' },
      { legacyColumn: 'isolation_mode', supabaseColumn: 'isolation_mode', required: false, defaultValue: 'shared' },
      { legacyColumn: 'settings', supabaseColumn: 'settings', required: false, defaultValue: {} },
      { legacyColumn: 'limits', supabaseColumn: 'limits', required: false, defaultValue: { max_users: 10, max_projects: 5, max_storage_gb: 1 } },
      { legacyColumn: 'created_at', supabaseColumn: 'created_at', required: true },
      { legacyColumn: 'updated_at', supabaseColumn: 'updated_at', required: true },
      { legacyColumn: 'created_by', supabaseColumn: 'created_by', required: false },
      { legacyColumn: 'updated_by', supabaseColumn: 'updated_by', required: false }
    ],
    users: [
      { legacyColumn: 'id', supabaseColumn: 'id', required: true },
      { legacyColumn: 'tenant_id', supabaseColumn: 'tenant_id', required: true },
      { legacyColumn: 'email', supabaseColumn: 'email', required: true },
      { legacyColumn: 'name', supabaseColumn: 'name', required: true },
      { legacyColumn: 'role', supabaseColumn: 'role', required: true, defaultValue: 'user' },
      { legacyColumn: 'status', supabaseColumn: 'status', required: true, defaultValue: 'active' },
      { legacyColumn: 'password_hash', supabaseColumn: 'password_hash', required: false },
      { legacyColumn: 'last_login_at', supabaseColumn: 'last_login_at', required: false },
      { legacyColumn: 'gdpr_consent_given', supabaseColumn: 'gdpr_consent_given', required: false, defaultValue: false },
      { legacyColumn: 'gdpr_consent_date', supabaseColumn: 'gdpr_consent_date', required: false },
      { legacyColumn: 'gdpr_consent_ip', supabaseColumn: 'gdpr_consent_ip', required: false },
      { legacyColumn: 'privacy_policy_version', supabaseColumn: 'privacy_policy_version', required: false, defaultValue: '1.0' },
      { legacyColumn: 'dpa_version', supabaseColumn: 'dpa_version', required: false, defaultValue: '1.0' },
      { legacyColumn: 'created_at', supabaseColumn: 'created_at', required: true },
      { legacyColumn: 'updated_at', supabaseColumn: 'updated_at', required: true }
    ],
    projects: [
      { legacyColumn: 'id', supabaseColumn: 'id', required: true },
      { legacyColumn: 'tenant_id', supabaseColumn: 'tenant_id', required: true },
      { legacyColumn: 'name', supabaseColumn: 'name', required: true },
      { legacyColumn: 'description', supabaseColumn: 'description', required: false },
      { legacyColumn: 'project_type', supabaseColumn: 'project_type', required: true },
      { legacyColumn: 'status', supabaseColumn: 'status', required: true, defaultValue: 'active' },
      { legacyColumn: 'config', supabaseColumn: 'config', required: false, defaultValue: {} },
      { legacyColumn: 'tech_stack', supabaseColumn: 'tech_stack', required: false, defaultValue: {} },
      { legacyColumn: 'design_config', supabaseColumn: 'design_config', required: false, defaultValue: {} },
      { legacyColumn: 'created_at', supabaseColumn: 'created_at', required: true },
      { legacyColumn: 'updated_at', supabaseColumn: 'updated_at', required: true },
      { legacyColumn: 'created_by', supabaseColumn: 'created_by', required: false }
    ],
    ideas: [
      { legacyColumn: 'id', supabaseColumn: 'id', required: true },
      { legacyColumn: 'tenant_id', supabaseColumn: 'tenant_id', required: true },
      { legacyColumn: 'submitted_by', supabaseColumn: 'submitted_by', required: false },
      { legacyColumn: 'project_name', supabaseColumn: 'project_name', required: true },
      { legacyColumn: 'description', supabaseColumn: 'description', required: true },
      { legacyColumn: 'problem', supabaseColumn: 'problem', required: true },
      { legacyColumn: 'solution', supabaseColumn: 'solution', required: true },
      { legacyColumn: 'target_audience', supabaseColumn: 'target_audience', required: false },
      { legacyColumn: 'key_features', supabaseColumn: 'key_features', required: false },
      { legacyColumn: 'business_model', supabaseColumn: 'business_model', required: false },
      { legacyColumn: 'category', supabaseColumn: 'category', required: false },
      { legacyColumn: 'priority', supabaseColumn: 'priority', required: true, defaultValue: 'medium' },
      { legacyColumn: 'status', supabaseColumn: 'status', required: true, defaultValue: 'pending' },
      { legacyColumn: 'admin_notes', supabaseColumn: 'admin_notes', required: false },
      { legacyColumn: 'reviewed_by', supabaseColumn: 'reviewed_by', required: false },
      { legacyColumn: 'reviewed_at', supabaseColumn: 'reviewed_at', required: false },
      { legacyColumn: 'timeline', supabaseColumn: 'timeline', required: false },
      { legacyColumn: 'budget', supabaseColumn: 'budget', required: false },
      { legacyColumn: 'submission_data', supabaseColumn: 'submission_data', required: false, defaultValue: {} },
      { legacyColumn: 'approval_data', supabaseColumn: 'approval_data', required: false, defaultValue: {} },
      { legacyColumn: 'project_id', supabaseColumn: 'project_id', required: false },
      { legacyColumn: 'promoted_at', supabaseColumn: 'promoted_at', required: false },
      { legacyColumn: 'created_at', supabaseColumn: 'created_at', required: true },
      { legacyColumn: 'updated_at', supabaseColumn: 'updated_at', required: true }
    ]
  }

  private constructor() {}

  static getInstance(): ETLService {
    if (!ETLService.instance) {
      ETLService.instance = new ETLService()
    }
    return ETLService.instance
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return

    try {
      // Verify Supabase connection
      const { data, error } = await supabase.from('tenants').select('count').limit(1)
      if (error) {
        throw new Error(`Failed to connect to Supabase: ${error.message}`)
      }

      this.isInitialized = true
      console.log('ETL service initialized successfully')
    } catch (error) {
      console.error('Failed to initialize ETL service:', error)
      throw error
    }
  }

  async startETLJob(tableName: string, batchSize: number = 100): Promise<ETLJob> {
    await this.initialize()

    const jobId = `etl_${tableName}_${Date.now()}`
    const job: ETLJob = {
      id: jobId,
      tableName,
      status: 'pending',
      progress: 0,
      recordsProcessed: 0,
      recordsTotal: 0,
      startedAt: null,
      completedAt: null,
      error: null,
      metadata: { batchSize }
    }

    this.activeJobs.set(jobId, job)

    // Start the ETL job asynchronously
    this.runETLJob(jobId, batchSize).catch(error => {
      const job = this.activeJobs.get(jobId)
      if (job) {
        job.status = 'failed'
        job.error = error instanceof Error ? error.message : 'Unknown error'
        job.completedAt = new Date()
      }
    })

    return job
  }

  private async runETLJob(jobId: string, batchSize: number): Promise<void> {
    const job = this.activeJobs.get(jobId)
    if (!job) return

    try {
      job.status = 'running'
      job.startedAt = new Date()

      // Get total record count from legacy system
      const totalRecords = await this.getLegacyRecordCount(job.tableName)
      job.recordsTotal = totalRecords

      if (totalRecords === 0) {
        job.status = 'completed'
        job.progress = 100
        job.completedAt = new Date()
        return
      }

      // Process records in batches
      let processedRecords = 0
      let offset = 0

      while (processedRecords < totalRecords) {
        // Extract batch from legacy system
        const legacyData = await this.extractLegacyData(job.tableName, offset, batchSize)
        
        if (legacyData.length === 0) break

        // Transform data
        const transformedData = legacyData.map(record => 
          this.transformRecord(job.tableName, record)
        )

        // Load data to Supabase
        const loadResult = await this.loadToSupabase(job.tableName, transformedData)
        
        if (!loadResult.success) {
          throw new Error(`Failed to load batch to Supabase: ${loadResult.errors.join(', ')}`)
        }

        processedRecords += legacyData.length
        offset += batchSize

        // Update job progress
        job.recordsProcessed = processedRecords
        job.progress = Math.round((processedRecords / totalRecords) * 100)

        // Small delay to prevent overwhelming the system
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      job.status = 'completed'
      job.progress = 100
      job.completedAt = new Date()

    } catch (error) {
      job.status = 'failed'
      job.error = error instanceof Error ? error.message : 'Unknown error'
      job.completedAt = new Date()
      throw error
    }
  }

  // Legacy data extraction - REMOVED - No longer needed for Module 4
  // All data now comes from Supabase directly

  private transformRecord(tableName: string, legacyRecord: any): any {
    const mappings = this.dataMappings[tableName]
    if (!mappings) {
      throw new Error(`No data mappings found for table: ${tableName}`)
    }

    const transformedRecord: any = {}

    for (const mapping of mappings) {
      const legacyValue = legacyRecord[mapping.legacyColumn]
      
      if (legacyValue !== undefined && legacyValue !== null) {
        // Apply transformation if specified
        if (mapping.transformation) {
          transformedRecord[mapping.supabaseColumn] = mapping.transformation(legacyValue)
        } else {
          transformedRecord[mapping.supabaseColumn] = legacyValue
        }
      } else if (mapping.required) {
        // Use default value for required fields
        transformedRecord[mapping.supabaseColumn] = mapping.defaultValue
      }
      // Skip optional fields that don't have values
    }

    return transformedRecord
  }

  private async loadToSupabase(tableName: string, data: any[]): Promise<ETLResult> {
    try {
      const { data: result, error } = await supabase
        .from(tableName)
        .upsert(data, { onConflict: 'id' })
        .select()

      if (error) {
        throw new Error(`Supabase upsert failed: ${error.message}`)
      }

      return {
        success: true,
        recordsProcessed: data.length,
        recordsTotal: data.length,
        errors: [],
        warnings: [],
        metadata: { result }
      }

    } catch (error) {
      return {
        success: false,
        recordsProcessed: 0,
        recordsTotal: data.length,
        errors: [error instanceof Error ? error.message : 'Unknown error'],
        warnings: [],
        metadata: {}
      }
    }
  }

  private async getLegacyRecordCount(tableName: string): Promise<number> {
    // This would make an API call to your existing FastAPI backend
    // For now, we'll simulate a count
    console.log(`Getting legacy record count for table: ${tableName}`)
    return Math.floor(Math.random() * 1000) + 100 // Simulated count
  }

  async getETLJob(jobId: string): Promise<ETLJob | null> {
    return this.activeJobs.get(jobId) || null
  }

  async getAllETLJobs(): Promise<ETLJob[]> {
    return Array.from(this.activeJobs.values())
  }

  async getActiveETLJobs(): Promise<ETLJob[]> {
    return Array.from(this.activeJobs.values()).filter(job => 
      job.status === 'running' || job.status === 'pending'
    )
  }

  async cancelETLJob(jobId: string): Promise<boolean> {
    const job = this.activeJobs.get(jobId)
    if (!job || job.status !== 'running') {
      return false
    }

    job.status = 'failed'
    job.error = 'Job cancelled by user'
    job.completedAt = new Date()
    return true
  }

  async validateDataMapping(tableName: string): Promise<{
    valid: boolean
    issues: string[]
    mappings: DataMapping[]
  }> {
    await this.initialize()

    const mappings = this.dataMappings[tableName]
    if (!mappings) {
      return {
        valid: false,
        issues: [`No data mappings found for table: ${tableName}`],
        mappings: []
      }
    }

    const issues: string[] = []
    
    // Check for required mappings
    const requiredMappings = mappings.filter(m => m.required)
    for (const mapping of requiredMappings) {
      if (!mapping.defaultValue && mapping.required) {
        issues.push(`Required mapping for ${mapping.legacyColumn} has no default value`)
      }
    }

    // Check for duplicate column mappings
    const supabaseColumns = mappings.map(m => m.supabaseColumn)
    const duplicateColumns = supabaseColumns.filter((col, index) => 
      supabaseColumns.indexOf(col) !== index
    )
    
    if (duplicateColumns.length > 0) {
      issues.push(`Duplicate Supabase columns found: ${duplicateColumns.join(', ')}`)
    }

    return {
      valid: issues.length === 0,
      issues,
      mappings
    }
  }

  async getDataMappings(tableName?: string): Promise<Record<string, DataMapping[]> | DataMapping[]> {
    await this.initialize()

    if (tableName) {
      return this.dataMappings[tableName] || []
    }
    return this.dataMappings
  }

  async clearCompletedJobs(): Promise<void> {
    const completedJobs = Array.from(this.activeJobs.values()).filter(job => 
      job.status === 'completed' || job.status === 'failed'
    )
    
    for (const job of completedJobs) {
      this.activeJobs.delete(job.id)
    }
  }
}

// Export singleton instance
export const etlService = ETLService.getInstance()
