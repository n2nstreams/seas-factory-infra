import { supabase } from '../supabase'

// API service for Module 13: Final Data Migration
// Handles server-side operations and database interactions

export interface CutoverTableAPI {
  name: string
  status: 'pending' | 'ready' | 'cutover' | 'completed' | 'rolled_back'
  read_source: 'legacy' | 'supabase' | 'dual'
  write_source: 'legacy' | 'supabase' | 'dual'
  last_validation: string | null
  validation_status: 'pending' | 'passed' | 'failed'
  drift_percentage: number
  record_count_legacy: number
  record_count_supabase: number
  record_count_difference: number
  referential_integrity_status: 'pending' | 'clean' | 'issues'
  referential_integrity_issues: string[]
  cutover_date: string | null
  rollback_date: string | null
  created_at: string
  updated_at: string
}

export interface CutoverChecklistAPI {
  id: string
  table_name: string
  data_consistency: boolean
  referential_integrity: boolean
  performance_validation: boolean
  security_validation: boolean
  backup_complete: boolean
  freeze_window_scheduled: boolean
  team_notified: boolean
  rollback_plan_ready: boolean
  completed_at: string | null
  completed_by: string | null
  created_at: string
  updated_at: string
}

export interface FreezeWindowAPI {
  id: string
  start_time: string
  end_time: string
  status: 'scheduled' | 'active' | 'completed' | 'cancelled'
  affected_tables: string[]
  description: string
  created_by: string
  created_at: string
  updated_at: string
}

export interface ReconciliationJobAPI {
  id: string
  table_name: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  type: 'full' | 'incremental' | 'drift_check'
  started_at: string | null
  completed_at: string | null
  records_processed: number
  records_total: number
  drift_detected: number
  errors: string[]
  created_at: string
  updated_at: string
}

export interface CutoverResultAPI {
  success: boolean
  table_name: string
  old_read_source: string
  new_read_source: string
  cutover_time: string
  validation_results: {
    data_consistency: boolean
    referential_integrity: boolean
    performance: boolean
    security: boolean
  }
  errors: string[]
  warnings: string[]
}

export class FinalDataMigrationAPI {
  private static instance: FinalDataMigrationAPI

  private constructor() {}

  static getInstance(): FinalDataMigrationAPI {
    if (!FinalDataMigrationAPI.instance) {
      FinalDataMigrationAPI.instance = new FinalDataMigrationAPI()
    }
    return FinalDataMigrationAPI.instance
  }

  // Get all cutover tables
  async getCutoverTables(): Promise<CutoverTableAPI[]> {
    const { data, error } = await supabase
      .from('cutover_tables')
      .select('*')
      .order('name')

    if (error) {
      throw new Error(`Failed to fetch cutover tables: ${error.message}`)
    }

    return data || []
  }

  // Get cutover table by name
  async getCutoverTable(tableName: string): Promise<CutoverTableAPI | null> {
    const { data, error } = await supabase
      .from('cutover_tables')
      .select('*')
      .eq('name', tableName)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        return null // No rows returned
      }
      throw new Error(`Failed to fetch cutover table: ${error.message}`)
    }

    return data
  }

  // Create or update cutover table
  async upsertCutoverTable(table: Partial<CutoverTableAPI>): Promise<CutoverTableAPI> {
    const { data, error } = await supabase
      .from('cutover_tables')
      .upsert(table, { onConflict: 'name' })
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to upsert cutover table: ${error.message}`)
    }

    return data
  }

  // Update cutover table status
  async updateCutoverTableStatus(
    tableName: string, 
    status: CutoverTableAPI['status'],
    updates: Partial<CutoverTableAPI> = {}
  ): Promise<CutoverTableAPI> {
    const { data, error } = await supabase
      .from('cutover_tables')
      .update({ 
        status, 
        updated_at: new Date().toISOString(),
        ...updates 
      })
      .eq('name', tableName)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to update cutover table status: ${error.message}`)
    }

    return data
  }

  // Get cutover checklists
  async getCutoverChecklists(tableName?: string): Promise<CutoverChecklistAPI[]> {
    let query = supabase
      .from('cutover_checklists')
      .select('*')
      .order('created_at', { ascending: false })

    if (tableName) {
      query = query.eq('table_name', tableName)
    }

    const { data, error } = await query

    if (error) {
      throw new Error(`Failed to fetch cutover checklists: ${error.message}`)
    }

    return data || []
  }

  // Create cutover checklist
  async createCutoverChecklist(checklist: Partial<CutoverChecklistAPI>): Promise<CutoverChecklistAPI> {
    const { data, error } = await supabase
      .from('cutover_checklists')
      .insert(checklist)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to create cutover checklist: ${error.message}`)
    }

    return data
  }

  // Update cutover checklist
  async updateCutoverChecklist(
    id: string, 
    updates: Partial<CutoverChecklistAPI>
  ): Promise<CutoverChecklistAPI> {
    const { data, error } = await supabase
      .from('cutover_checklists')
      .update({ 
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to update cutover checklist: ${error.message}`)
    }

    return data
  }

  // Get freeze windows
  async getFreezeWindows(): Promise<FreezeWindowAPI[]> {
    const { data, error } = await supabase
      .from('freeze_windows')
      .select('*')
      .order('start_time', { ascending: false })

    if (error) {
      throw new Error(`Failed to fetch freeze windows: ${error.message}`)
    }

    return data || []
  }

  // Create freeze window
  async createFreezeWindow(freezeWindow: Partial<FreezeWindowAPI>): Promise<FreezeWindowAPI> {
    const { data, error } = await supabase
      .from('freeze_windows')
      .insert(freezeWindow)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to create freeze window: ${error.message}`)
    }

    return data
  }

  // Update freeze window status
  async updateFreezeWindowStatus(
    id: string, 
    status: FreezeWindowAPI['status']
  ): Promise<FreezeWindowAPI> {
    const { data, error } = await supabase
      .from('freeze_windows')
      .update({ 
        status,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to update freeze window status: ${error.message}`)
    }

    return data
  }

  // Get reconciliation jobs
  async getReconciliationJobs(tableName?: string): Promise<ReconciliationJobAPI[]> {
    let query = supabase
      .from('reconciliation_jobs')
      .select('*')
      .order('created_at', { ascending: false })

    if (tableName) {
      query = query.eq('table_name', tableName)
    }

    const { data, error } = await query

    if (error) {
      throw new Error(`Failed to fetch reconciliation jobs: ${error.message}`)
    }

    return data || []
  }

  // Create reconciliation job
  async createReconciliationJob(job: Partial<ReconciliationJobAPI>): Promise<ReconciliationJobAPI> {
    const { data, error } = await supabase
      .from('reconciliation_jobs')
      .insert(job)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to create reconciliation job: ${error.message}`)
    }

    return data
  }

  // Update reconciliation job
  async updateReconciliationJob(
    id: string, 
    updates: Partial<ReconciliationJobAPI>
  ): Promise<ReconciliationJobAPI> {
    const { data, error } = await supabase
      .from('reconciliation_jobs')
      .update({ 
        ...updates,
        updated_at: new Date().toISOString()
      })
      .eq('id', id)
      .select()
      .single()

    if (error) {
      throw new Error(`Failed to update reconciliation job: ${error.message}`)
    }

    return data
  }

  // Execute table cutover
  async executeTableCutover(tableName: string, userId: string): Promise<CutoverResultAPI> {
    // This would be a complex operation that coordinates multiple steps
    // For now, we'll simulate the process
    
    try {
      // 1. Validate table is ready for cutover
      const table = await this.getCutoverTable(tableName)
      if (!table) {
        throw new Error(`Table ${tableName} not found`)
      }

      if (table.status !== 'ready') {
        throw new Error(`Table ${tableName} is not ready for cutover. Status: ${table.status}`)
      }

      // 2. Create freeze window
      const freezeWindow = await this.createFreezeWindow({
        start_time: new Date().toISOString(),
        end_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours
        status: 'active',
        affected_tables: [tableName],
        description: `Cutover execution for table ${tableName}`,
        created_by: userId
      })

      // 3. Update table status to cutover
      await this.updateCutoverTableStatus(tableName, 'cutover', {
        read_source: 'supabase',
        cutover_date: new Date().toISOString()
      })

      // 4. Create reconciliation job
      await this.createReconciliationJob({
        table_name: tableName,
        status: 'running',
        type: 'incremental',
        started_at: new Date().toISOString(),
        records_processed: 0,
        records_total: table.record_count_supabase,
        drift_detected: 0,
        errors: []
      })

      // 5. Update freeze window to completed
      await this.updateFreezeWindowStatus(freezeWindow.id, 'completed')

      return {
        success: true,
        table_name: tableName,
        old_read_source: table.read_source,
        new_read_source: 'supabase',
        cutover_time: new Date().toISOString(),
        validation_results: {
          data_consistency: true,
          referential_integrity: true,
          performance: true,
          security: true
        },
        errors: [],
        warnings: []
      }

    } catch (error) {
      // Rollback on failure
      await this.rollbackTableCutover(tableName, userId, 'Cutover execution failed')
      
      throw error
    }
  }

  // Rollback table cutover
  async rollbackTableCutover(tableName: string, userId: string, reason: string): Promise<void> {
    try {
      // 1. Update table status to rolled_back
      await this.updateCutoverTableStatus(tableName, 'rolled_back', {
        read_source: 'legacy',
        rollback_date: new Date().toISOString()
      })

      // 2. Stop any active reconciliation jobs
      const activeJobs = await this.getReconciliationJobs(tableName)
      for (const job of activeJobs.filter(j => j.status === 'running')) {
        await this.updateReconciliationJob(job.id, {
          status: 'completed',
          completed_at: new Date().toISOString()
        })
      }

      // 3. Create audit log entry (this would go to an audit table)
      console.log(`Rollback logged: ${tableName} by ${userId} - ${reason}`)

    } catch (error) {
      console.error(`Rollback failed for table ${tableName}:`, error)
      throw error
    }
  }

  // Validate data consistency for a table
  async validateDataConsistency(tableName: string): Promise<{
    isConsistent: boolean
    driftPercentage: number
    recordCounts: {
      legacy: number
      supabase: number
      difference: number
    }
    issues: string[]
  }> {
    try {
      // This would implement actual data consistency validation
      // For now, return mock data
      const mockData = {
        isConsistent: true,
        driftPercentage: 0.02,
        recordCounts: {
          legacy: 1000,
          supabase: 1000,
          difference: 0
        },
        issues: []
      }

      // Update the table with validation results
      await this.updateCutoverTableStatus(tableName, 'pending', {
        validation_status: mockData.isConsistent ? 'passed' : 'failed',
        last_validation: new Date().toISOString(),
        drift_percentage: mockData.driftPercentage,
        record_count_legacy: mockData.recordCounts.legacy,
        record_count_supabase: mockData.recordCounts.supabase,
        record_count_difference: mockData.recordCounts.difference
      })

      return mockData

    } catch (error) {
      throw new Error(`Failed to validate data consistency: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // Check referential integrity for a table
  async checkReferentialIntegrity(tableName: string): Promise<{
    status: 'pending' | 'clean' | 'issues'
    issues: string[]
  }> {
    try {
      // This would implement actual referential integrity checking
      // For now, return mock data
      const result = {
        status: 'clean' as const,
        issues: []
      }

      // Update the table with integrity results
      await this.updateCutoverTableStatus(tableName, 'pending', {
        referential_integrity_status: result.status,
        referential_integrity_issues: result.issues
      })

      return result

    } catch (error) {
      throw new Error(`Failed to check referential integrity: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // Get migration statistics
  async getMigrationStatistics(): Promise<{
    totalTables: number
    readyForCutover: number
    inProgress: number
    completed: number
    rolledBack: number
    overallProgress: number
  }> {
    try {
      const tables = await this.getCutoverTables()
      
      const stats = {
        totalTables: tables.length,
        readyForCutover: tables.filter(t => t.status === 'ready').length,
        inProgress: tables.filter(t => t.status === 'cutover').length,
        completed: tables.filter(t => t.status === 'completed').length,
        rolledBack: tables.filter(t => t.status === 'rolled_back').length,
        overallProgress: 0
      }

      stats.overallProgress = (stats.completed / stats.totalTables) * 100

      return stats

    } catch (error) {
      throw new Error(`Failed to get migration statistics: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
}

// Export singleton instance
export const finalDataMigrationAPI = FinalDataMigrationAPI.getInstance()
