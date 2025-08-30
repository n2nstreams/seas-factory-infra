import { supabase } from './supabase'
import { databaseMigrationService, MigrationTable } from './database-migration'
import { FeatureFlagService } from '../../../src/lib/featureFlags'

// Module 13: Final Data Migration - Source-of-Truth Cutover
// This service handles the final migration from legacy systems to Supabase as the source of truth

export interface CutoverTable {
  name: string
  status: 'pending' | 'ready' | 'cutover' | 'completed' | 'rolled_back'
  readSource: 'legacy' | 'supabase' | 'dual'
  writeSource: 'legacy' | 'supabase' | 'dual'
  lastValidation: Date | null
  validationStatus: 'pending' | 'passed' | 'failed'
  driftPercentage: number
  recordCount: {
    legacy: number
    supabase: number
    difference: number
  }
  referentialIntegrity: {
    status: 'pending' | 'clean' | 'issues'
    issues: string[]
  }
  cutoverDate: Date | null
  rollbackDate: Date | null
}

export interface CutoverChecklist {
  id: string
  tableName: string
  checklist: {
    dataConsistency: boolean
    referentialIntegrity: boolean
    performanceValidation: boolean
    securityValidation: boolean
    backupComplete: boolean
    freezeWindowScheduled: boolean
    teamNotified: boolean
    rollbackPlanReady: boolean
  }
  completedAt: Date | null
  completedBy: string | null
}

export interface FreezeWindow {
  id: string
  startTime: Date
  endTime: Date
  status: 'scheduled' | 'active' | 'completed' | 'cancelled'
  affectedTables: string[]
  description: string
  createdBy: string
  createdAt: Date
}

export interface CutoverResult {
  success: boolean
  tableName: string
  oldReadSource: string
  newReadSource: string
  cutoverTime: Date
  validationResults: {
    dataConsistency: boolean
    referentialIntegrity: boolean
    performance: boolean
    security: boolean
  }
  errors: string[]
  warnings: string[]
}

export interface ReconciliationJob {
  id: string
  tableName: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  type: 'full' | 'incremental' | 'drift_check'
  startedAt: Date | null
  completedAt: Date | null
  recordsProcessed: number
  recordsTotal: number
  driftDetected: number
  errors: string[]
}

export class FinalDataMigrationService {
  private static instance: FinalDataMigrationService
  private cutoverTables: Map<string, CutoverTable> = new Map()
  private freezeWindows: Map<string, FreezeWindow> = new Map()
  private reconciliationJobs: Map<string, ReconciliationJob> = new Map()
  private featureFlagService: FeatureFlagService
  private isInitialized = false

  private constructor() {
    this.featureFlagService = new FeatureFlagService()
  }

  static getInstance(): FinalDataMigrationService {
    if (!FinalDataMigrationService.instance) {
      FinalDataMigrationService.instance = new FinalDataMigrationService()
    }
    return FinalDataMigrationService.instance
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return

    try {
      // Initialize cutover tables from migration service
      const migrationTables = await databaseMigrationService.getMigrationTables()
      
      for (const table of migrationTables) {
        this.cutoverTables.set(table.name, {
          name: table.name,
          status: 'pending',
          readSource: 'legacy',
          writeSource: 'dual',
          lastValidation: null,
          validationStatus: 'pending',
          driftPercentage: 0,
          recordCount: {
            legacy: 0,
            supabase: 0,
            difference: 0
          },
          referentialIntegrity: {
            status: 'pending',
            issues: []
          },
          cutoverDate: null,
          rollbackDate: null
        })
      }

      this.isInitialized = true
    } catch (error) {
      console.error('Failed to initialize FinalDataMigrationService:', error)
      throw error
    }
  }

  // Pre-cutover validation and preparation
  async prepareTableForCutover(tableName: string): Promise<CutoverChecklist> {
    await this.initialize()

    const table = this.cutoverTables.get(tableName)
    if (!table) {
      throw new Error(`Table ${tableName} not found in cutover configuration`)
    }

    // Run comprehensive validation
    const validationResults = await this.runPreCutoverValidation(tableName)
    
    const checklist: CutoverChecklist = {
      id: `checklist_${tableName}_${Date.now()}`,
      tableName,
      checklist: validationResults,
      completedAt: null,
      completedBy: null
    }

    // Mark table as ready if all checks pass
    if (Object.values(validationResults).every(check => check)) {
      table.status = 'ready'
      table.lastValidation = new Date()
      table.validationStatus = 'passed'
    } else {
      table.validationStatus = 'failed'
    }

    return checklist
  }

  private async runPreCutoverValidation(tableName: string): Promise<CutoverChecklist['checklist']> {
    const results = {
      dataConsistency: false,
      referentialIntegrity: false,
      performanceValidation: false,
      securityValidation: false,
      backupComplete: false,
      freezeWindowScheduled: false,
      teamNotified: false,
      rollbackPlanReady: false
    }

    try {
      // 1. Data Consistency Check
      const consistencyResult = await databaseMigrationService.validateDataConsistency(tableName)
      results.dataConsistency = consistencyResult.isConsistent && consistencyResult.driftPercentage < 0.05

      // 2. Referential Integrity Check
      const integrityResult = await this.checkReferentialIntegrity(tableName)
      results.referentialIntegrity = integrityResult.status === 'clean'

      // 3. Performance Validation
      const performanceResult = await this.validatePerformance(tableName)
      results.performanceValidation = performanceResult.success

      // 4. Security Validation
      const securityResult = await this.validateSecurity(tableName)
      results.securityValidation = securityResult.success

      // 5. Backup Complete
      results.backupComplete = await this.verifyBackup(tableName)

      // 6. Freeze Window Scheduled
      results.freezeWindowScheduled = await this.scheduleFreezeWindow(tableName)

      // 7. Team Notification
      results.teamNotified = await this.notifyTeam(tableName, 'cutover_preparation')

      // 8. Rollback Plan Ready
      results.rollbackPlanReady = await this.prepareRollbackPlan(tableName)

    } catch (error) {
      console.error(`Validation failed for table ${tableName}:`, error)
    }

    return results
  }

  // Execute cutover for a specific table
  async executeTableCutover(tableName: string, userId: string): Promise<CutoverResult> {
    await this.initialize()

    const table = this.cutoverTables.get(tableName)
    if (!table) {
      throw new Error(`Table ${tableName} not found in cutover configuration`)
    }

    if (table.status !== 'ready') {
      throw new Error(`Table ${tableName} is not ready for cutover. Status: ${table.status}`)
    }

    // Check if feature flag is enabled
    if (!this.featureFlagService.isFeatureEnabled('data_migration_final')) {
      throw new Error('Final data migration feature flag is not enabled')
    }

    const result: CutoverResult = {
      success: false,
      tableName,
      oldReadSource: table.readSource,
      newReadSource: 'supabase',
      cutoverTime: new Date(),
      validationResults: {
        dataConsistency: false,
        referentialIntegrity: false,
        performance: false,
        security: false
      },
      errors: [],
      warnings: []
    }

    try {
      // 1. Activate freeze window
      await this.activateFreezeWindow(tableName)

      // 2. Final validation
      const finalValidation = await this.runPreCutoverValidation(tableName)
      result.validationResults = {
        dataConsistency: finalValidation.dataConsistency,
        referentialIntegrity: finalValidation.referentialIntegrity,
        performance: finalValidation.performanceValidation,
        security: finalValidation.securityValidation
      }

      if (!Object.values(finalValidation).every(check => check)) {
        throw new Error('Final validation failed - cannot proceed with cutover')
      }

      // 3. Switch read source to Supabase
      await this.switchReadSource(tableName, 'supabase')

      // 4. Update table status
      table.status = 'cutover'
      table.readSource = 'supabase'
      table.cutoverDate = new Date()

      // 5. Start reconciliation monitoring
      await this.startReconciliationMonitoring(tableName)

      result.success = true

      // 6. Notify team of successful cutover
      await this.notifyTeam(tableName, 'cutover_success')

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      result.errors.push(errorMessage)
      
      // Attempt rollback
      await this.rollbackTableCutover(tableName, userId, errorMessage)
      
      throw error
    }

    return result
  }

  // Rollback cutover for a specific table
  async rollbackTableCutover(tableName: string, userId: string, reason: string): Promise<void> {
    const table = this.cutoverTables.get(tableName)
    if (!table) {
      throw new Error(`Table ${tableName} not found in cutover configuration`)
    }

    try {
      // 1. Switch read source back to legacy
      await this.switchReadSource(tableName, 'legacy')

      // 2. Update table status
      table.status = 'rolled_back'
      table.readSource = 'legacy'
      table.rollbackDate = new Date()

      // 3. Stop reconciliation monitoring
      await this.stopReconciliationMonitoring(tableName)

      // 4. Deactivate freeze window
      await this.deactivateFreezeWindow(tableName)

      // 5. Notify team of rollback
      await this.notifyTeam(tableName, 'cutover_rollback', reason)

      // 6. Log rollback for audit
      await this.logRollback(tableName, userId, reason)

    } catch (error) {
      console.error(`Rollback failed for table ${tableName}:`, error)
      throw error
    }
  }

  // Switch read source for a table
  private async switchReadSource(tableName: string, source: 'legacy' | 'supabase' | 'dual'): Promise<void> {
    // This would integrate with your routing layer to switch read sources
    // For now, we'll update the internal state
    
    const table = this.cutoverTables.get(tableName)
    if (table) {
      table.readSource = source
    }

    // Update feature flags for per-table read control
    const flagName = `db_read_source_${tableName}`
    // await this.featureFlagService.setFeatureFlag(flagName, source === 'supabase')
  }

  // Start reconciliation monitoring for a table
  private async startReconciliationMonitoring(tableName: string): Promise<void> {
    const job: ReconciliationJob = {
      id: `reconciliation_${tableName}_${Date.now()}`,
      tableName,
      status: 'running',
      type: 'incremental',
      startedAt: new Date(),
      completedAt: null,
      recordsProcessed: 0,
      recordsTotal: 0,
      driftDetected: 0,
      errors: []
    }

    this.reconciliationJobs.set(job.id, job)

    // Start the reconciliation process
    this.runReconciliationJob(job.id)
  }

  // Stop reconciliation monitoring for a table
  private async stopReconciliationMonitoring(tableName: string): Promise<void> {
    for (const [jobId, job] of this.reconciliationJobs.entries()) {
      if (job.tableName === tableName && job.status === 'running') {
        job.status = 'completed'
        job.completedAt = new Date()
      }
    }
  }

  // Run reconciliation job
  private async runReconciliationJob(jobId: string): Promise<void> {
    const job = this.reconciliationJobs.get(jobId)
    if (!job) return

    try {
      // Run reconciliation logic
      const result = await this.performReconciliation(job.tableName)
      
      job.recordsProcessed = result.recordsProcessed
      job.recordsTotal = result.recordsTotal
      job.driftDetected = result.driftDetected
      job.status = 'completed'
      job.completedAt = new Date()

    } catch (error) {
      job.status = 'failed'
      job.completedAt = new Date()
      job.errors.push(error instanceof Error ? error.message : 'Unknown error')
    }
  }

  // Perform reconciliation for a table
  private async performReconciliation(tableName: string): Promise<{
    recordsProcessed: number
    recordsTotal: number
    driftDetected: number
  }> {
    // This would implement the actual reconciliation logic
    // For now, return mock data
    return {
      recordsProcessed: 1000,
      recordsTotal: 1000,
      driftDetected: 0
    }
  }

  // Check referential integrity for a table
  private async checkReferentialIntegrity(tableName: string): Promise<{
    status: 'pending' | 'clean' | 'issues'
    issues: string[]
  }> {
    // This would implement referential integrity checking
    // For now, return mock data
    return {
      status: 'clean',
      issues: []
    }
  }

  // Validate performance for a table
  private async validatePerformance(tableName: string): Promise<{
    success: boolean
    metrics: Record<string, number>
  }> {
    // This would implement performance validation
    // For now, return mock data
    return {
      success: true,
      metrics: {
        avgResponseTime: 150,
        p95ResponseTime: 300,
        throughput: 1000
      }
    }
  }

  // Validate security for a table
  private async validateSecurity(tableName: string): Promise<{
    success: boolean
    issues: string[]
  }> {
    // This would implement security validation
    // For now, return mock data
    return {
      success: true,
      issues: []
    }
  }

  // Verify backup for a table
  private async verifyBackup(tableName: string): Promise<boolean> {
    // This would implement backup verification
    // For now, return true
    return true
  }

  // Schedule freeze window for a table
  private async scheduleFreezeWindow(tableName: string): Promise<boolean> {
    // This would implement freeze window scheduling
    // For now, return true
    return true
  }

  // Activate freeze window for a table
  private async activateFreezeWindow(tableName: string): Promise<void> {
    // This would implement freeze window activation
    // For now, just log
    console.log(`Freeze window activated for table ${tableName}`)
  }

  // Deactivate freeze window for a table
  private async deactivateFreezeWindow(tableName: string): Promise<void> {
    // This would implement freeze window deactivation
    // For now, just log
    console.log(`Freeze window deactivated for table ${tableName}`)
  }

  // Notify team of events
  private async notifyTeam(tableName: string, event: string, details?: string): Promise<boolean> {
    // This would implement team notification
    // For now, just log
    console.log(`Team notification: ${event} for table ${tableName}`, details)
    return true
  }

  // Prepare rollback plan for a table
  private async prepareRollbackPlan(tableName: string): Promise<boolean> {
    // This would implement rollback plan preparation
    // For now, return true
    return true
  }

  // Log rollback for audit
  private async logRollback(tableName: string, userId: string, reason: string): Promise<void> {
    // This would implement rollback logging
    // For now, just log
    console.log(`Rollback logged: ${tableName} by ${userId} - ${reason}`)
  }

  // Get cutover status for all tables
  async getCutoverStatus(): Promise<CutoverTable[]> {
    await this.initialize()
    return Array.from(this.cutoverTables.values())
  }

  // Get cutover status for a specific table
  async getTableCutoverStatus(tableName: string): Promise<CutoverTable | null> {
    await this.initialize()
    return this.cutoverTables.get(tableName) || null
  }

  // Get active reconciliation jobs
  async getActiveReconciliationJobs(): Promise<ReconciliationJob[]> {
    return Array.from(this.reconciliationJobs.values()).filter(job => job.status === 'running')
  }

  // Get freeze windows
  async getFreezeWindows(): Promise<FreezeWindow[]> {
    return Array.from(this.freezeWindows.values())
  }

  // Schedule a freeze window
  async scheduleFreezeWindow(
    startTime: Date,
    endTime: Date,
    affectedTables: string[],
    description: string,
    createdBy: string
  ): Promise<FreezeWindow> {
    const freezeWindow: FreezeWindow = {
      id: `freeze_${Date.now()}`,
      startTime,
      endTime,
      status: 'scheduled',
      affectedTables,
      description,
      createdBy,
      createdAt: new Date()
    }

    this.freezeWindows.set(freezeWindow.id, freezeWindow)
    return freezeWindow
  }

  // Check if a table is in freeze window
  async isTableInFreezeWindow(tableName: string): Promise<boolean> {
    const now = new Date()
    
    for (const freezeWindow of this.freezeWindows.values()) {
      if (freezeWindow.status === 'active' && 
          freezeWindow.affectedTables.includes(tableName) &&
          now >= freezeWindow.startTime && 
          now <= freezeWindow.endTime) {
        return true
      }
    }
    
    return false
  }
}

// Export singleton instance
export const finalDataMigrationService = FinalDataMigrationService.getInstance()
