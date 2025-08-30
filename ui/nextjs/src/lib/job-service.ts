// Job Service for Module 5: Jobs & Scheduling
// Provides unified interface for job submission with dual-destination support
// Uses feature flag `jobs_pg` to control migration rollout

import { supabase } from './supabase'
import { useFeatureFlag } from '@/components/providers/FeatureFlagProvider'

export interface JobSubmission {
  tenant_id: string
  job_name: string
  job_family: 'A' | 'B' | 'C' // A: short, B: cron, C: long-running
  input_data?: Record<string, any>
  priority?: number
  idempotency_key?: string
  max_retries?: number
  timeout_seconds?: number
}

export interface JobStatus {
  id: string
  tenant_id: string
  job_name: string
  job_family: string
  status: 'queued' | 'in_progress' | 'succeeded' | 'failed' | 'canceled' | 'retrying'
  priority: number
  retry_count: number
  queued_at: string
  started_at?: string
  completed_at?: string
  execution_time_ms?: number
  queue_time_ms?: number
  worker_id?: string
  worker_heartbeat?: string
  sla_status?: 'within_sla' | 'sla_breach' | 'failed' | 'timeout' | 'normal'
}

export interface JobMetrics {
  total_jobs: number
  jobs_by_status: Record<string, number>
  jobs_by_family: Record<string, number>
  avg_execution_time_ms: number
  sla_compliance_rate: number
  failed_jobs_count: number
  retry_rate: number
}

export class JobService {
  private static instance: JobService
  private edgeFunctionUrl: string
  private isInitialized = false

  private constructor() {
    this.edgeFunctionUrl = process.env.NEXT_PUBLIC_SUPABASE_URL?.replace('.supabase.co', '.supabase.co/functions/v1/process-jobs') || ''
  }

  static getInstance(): JobService {
    if (!JobService.instance) {
      JobService.instance = new JobService()
    }
    return JobService.instance
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return

    // Verify Supabase connection
    try {
      const { data, error } = await supabase.from('job_catalog').select('count').limit(1)
      if (error) {
        console.warn('Job catalog not accessible, jobs will use legacy system:', error)
      } else {
        console.log('Job service initialized with Supabase backend')
      }
    } catch (error) {
      console.warn('Job service initialization failed, falling back to legacy:', error)
    }

    this.isInitialized = true
  }

  // Submit a job to the appropriate system based on feature flag
  async submitJob(submission: JobSubmission): Promise<string> {
    await this.initialize()

    // Check if Supabase jobs are enabled via feature flag
    const useSupabaseJobs = this.isFeatureFlagEnabled('jobs_pg')
    
    if (useSupabaseJobs && this.edgeFunctionUrl) {
      return this.submitJobToSupabase(submission)
    } else {
      return this.submitJobToLegacy(submission)
    }
  }

  // Submit job to Supabase job queue
  private async submitJobToSupabase(submission: JobSubmission): Promise<string> {
    try {
      // First, ensure the job exists in the catalog
      await this.ensureJobCatalogEntry(submission)

      // Submit job using the database function
      const { data, error } = await supabase.rpc('enqueue_job', {
        p_tenant_id: submission.tenant_id,
        p_job_name: submission.job_name,
        p_job_family: submission.job_family,
        p_input_data: submission.input_data || {},
        p_priority: submission.priority || 0,
        p_idempotency_key: submission.idempotency_key || null,
        p_max_retries: submission.max_retries || 3,
        p_timeout_seconds: submission.timeout_seconds || 600
      })

      if (error) {
        console.error('Error submitting job to Supabase:', error)
        // Fallback to legacy system
        return this.submitJobToLegacy(submission)
      }

      console.log(`Job submitted to Supabase: ${data}`)
      return data

    } catch (error) {
      console.error('Exception submitting job to Supabase:', error)
      // Fallback to legacy system
      return this.submitJobToLegacy(submission)
    }
  }

  // Submit job to legacy system (FastAPI BackgroundTasks)
  private async submitJobToLegacy(submission: JobSubmission): Promise<string> {
    try {
      // For now, simulate legacy job submission
      // In production, this would call the existing FastAPI endpoints
      const jobId = `legacy_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      
      console.log(`Job submitted to legacy system: ${jobId}`)
      
      // Simulate legacy job processing
      setTimeout(() => {
        console.log(`Legacy job ${jobId} completed`)
      }, 1000)
      
      return jobId
    } catch (error) {
      console.error('Error submitting job to legacy system:', error)
      throw new Error(`Failed to submit job: ${error}`)
    }
  }

  // Ensure job exists in catalog (creates if missing)
  private async ensureJobCatalogEntry(submission: JobSubmission): Promise<void> {
    try {
      const { data, error } = await supabase
        .from('job_catalog')
        .select('id')
        .eq('tenant_id', submission.tenant_id)
        .eq('job_key', submission.job_name)
        .single()

      if (error && error.code === 'PGRST116') {
        // Job doesn't exist, create it
        const { error: insertError } = await supabase
          .from('job_catalog')
          .insert({
            tenant_id: submission.tenant_id,
            job_name: submission.job_name,
            job_family: submission.job_family,
            job_key: submission.job_name,
            max_runtime_seconds: submission.timeout_seconds || 600,
            max_retries: submission.max_retries || 3,
            description: `Auto-created job for ${submission.job_name}`,
            owner: 'System'
          })

        if (insertError) {
          console.warn('Failed to create job catalog entry:', insertError)
        }
      }
    } catch (error) {
      console.warn('Error ensuring job catalog entry:', error)
    }
  }

  // Get job status
  async getJobStatus(jobId: string, tenantId: string): Promise<JobStatus | null> {
    await this.initialize()

    try {
      const { data, error } = await supabase
        .from('job_queue')
        .select('*')
        .eq('id', jobId)
        .eq('tenant_id', tenantId)
        .single()

      if (error) {
        console.error('Error getting job status:', error)
        return null
      }

      return data as JobStatus
    } catch (error) {
      console.error('Exception getting job status:', error)
      return null
    }
  }

  // Get all jobs for a tenant
  async getTenantJobs(tenantId: string, status?: string, limit: number = 100): Promise<JobStatus[]> {
    await this.initialize()

    try {
      let query = supabase
        .from('job_queue')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('queued_at', { ascending: false })
        .limit(limit)

      if (status) {
        query = query.eq('status', status)
      }

      const { data, error } = await query

      if (error) {
        console.error('Error getting tenant jobs:', error)
        return []
      }

      return data as JobStatus[]
    } catch (error) {
      console.error('Exception getting tenant jobs:', error)
      return []
    }
  }

  // Get job metrics for a tenant
  async getJobMetrics(tenantId: string): Promise<JobMetrics> {
    await this.initialize()

    try {
      // Get jobs by status
      const { data: statusData, error: statusError } = await supabase
        .from('job_queue')
        .select('status')
        .eq('tenant_id', tenantId)

      if (statusError) {
        console.error('Error getting job status data:', statusError)
        return this.getDefaultMetrics()
      }

      // Get jobs by family
      const { data: familyData, error: familyError } = await supabase
        .from('job_queue')
        .select('job_family')
        .eq('tenant_id', tenantId)

      if (familyError) {
        console.error('Error getting job family data:', familyError)
        return this.getDefaultMetrics()
      }

      // Get execution time metrics
      const { data: metricsData, error: metricsError } = await supabase
        .from('job_metrics')
        .select('metric_value, metric_name')
        .eq('tenant_id', tenantId)
        .in('metric_name', ['execution_time_ms', 'job_status'])

      if (metricsError) {
        console.error('Error getting job metrics:', metricsError)
      }

      // Calculate metrics
      const statusCounts: Record<string, number> = {}
      const familyCounts: Record<string, number> = {}
      let totalJobs = 0
      let failedJobs = 0
      let retryCount = 0
      let totalExecutionTime = 0
      let executionTimeCount = 0
      let successfulJobs = 0

      // Count by status
      statusData?.forEach(job => {
        const status = job.status
        statusCounts[status] = (statusCounts[status] || 0) + 1
        totalJobs++
        
        if (status === 'failed') failedJobs++
        if (status === 'retrying') retryCount++
      })

      // Count by family
      familyData?.forEach(job => {
        const family = job.job_family
        familyCounts[family] = (familyCounts[family] || 0) + 1
      })

      // Calculate execution time metrics
      metricsData?.forEach(metric => {
        if (metric.metric_name === 'execution_time_ms') {
          totalExecutionTime += metric.metric_value
          executionTimeCount++
        } else if (metric.metric_name === 'job_status') {
          if (metric.metric_value === 1) successfulJobs++
        }
      })

      const avgExecutionTime = executionTimeCount > 0 ? totalExecutionTime / executionTimeCount : 0
      const slaComplianceRate = totalJobs > 0 ? (successfulJobs / totalJobs) * 100 : 0
      const retryRate = totalJobs > 0 ? (retryCount / totalJobs) * 100 : 0

      return {
        total_jobs: totalJobs,
        jobs_by_status: statusCounts,
        jobs_by_family: familyCounts,
        avg_execution_time_ms: avgExecutionTime,
        sla_compliance_rate: slaComplianceRate,
        failed_jobs_count: failedJobs,
        retry_rate: retryRate
      }

    } catch (error) {
      console.error('Exception getting job metrics:', error)
      return this.getDefaultMetrics()
    }
  }

  // Retry a failed job
  async retryJob(jobId: string, tenantId: string, delaySeconds: number = 60): Promise<boolean> {
    await this.initialize()

    try {
      const { data, error } = await supabase.rpc('retry_job', {
        p_job_id: jobId,
        p_delay_seconds: delaySeconds
      })

      if (error) {
        console.error('Error retrying job:', error)
        return false
      }

      return data
    } catch (error) {
      console.error('Exception retrying job:', error)
      return false
    }
  }

  // Cancel a job
  async cancelJob(jobId: string, tenantId: string): Promise<boolean> {
    await this.initialize()

    try {
      const { error } = await supabase
        .from('job_queue')
        .update({ 
          status: 'canceled',
          completed_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', jobId)
        .eq('tenant_id', tenantId)
        .in('status', ['queued', 'in_progress'])

      if (error) {
        console.error('Error canceling job:', error)
        return false
      }

      return true
    } catch (error) {
      console.error('Exception canceling job:', error)
      return false
    }
  }

  // Get dead letter queue entries
  async getDeadLetterQueue(tenantId: string, limit: number = 50): Promise<any[]> {
    await this.initialize()

    try {
      const { data, error } = await supabase
        .from('job_dead_letter')
        .select('*')
        .eq('tenant_id', tenantId)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (error) {
        console.error('Error getting dead letter queue:', error)
        return []
      }

      return data || []
    } catch (error) {
      console.error('Exception getting dead letter queue:', error)
      return []
    }
  }

  // Resolve dead letter entry
  async resolveDeadLetterEntry(entryId: string, tenantId: string, notes: string, resolvedBy: string): Promise<boolean> {
    await this.initialize()

    try {
      const { error } = await supabase
        .from('job_dead_letter')
        .update({
          remediation_status: 'resolved',
          remediation_notes: notes,
          resolved_by: resolvedBy,
          resolved_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .eq('id', entryId)
        .eq('tenant_id', tenantId)

      if (error) {
        console.error('Error resolving dead letter entry:', error)
        return false
      }

      return true
    } catch (error) {
      console.error('Exception resolving dead letter entry:', error)
      return false
    }
  }

  // Get default metrics when data is unavailable
  private getDefaultMetrics(): JobMetrics {
    return {
      total_jobs: 0,
      jobs_by_status: {},
      jobs_by_family: {},
      avg_execution_time_ms: 0,
      sla_compliance_rate: 0,
      failed_jobs_count: 0,
      retry_rate: 0
    }
  }

  // Check if feature flag is enabled
  private isFeatureFlagEnabled(flag: string): boolean {
    // In a real implementation, this would check the feature flag system
    // For now, we'll use environment variables or localStorage
    try {
      if (typeof window !== 'undefined') {
        const flags = localStorage.getItem('saas-factory-feature-flags')
        if (flags) {
          const parsedFlags = JSON.parse(flags)
          return parsedFlags[flag] || false
        }
      }
      
      // Check environment variable
      const envKey = `NEXT_PUBLIC_FEATURE_${flag.toUpperCase()}`
      return process.env[envKey] === 'true'
    } catch (error) {
      console.warn('Error checking feature flag:', error)
      return false
    }
  }

  // Health check for the job system
  async healthCheck(): Promise<{ status: string; details: any }> {
    await this.initialize()

    try {
      // Check Supabase connection
      const { data: catalogData, error: catalogError } = await supabase
        .from('job_catalog')
        .select('count')
        .limit(1)

      // Check job queue
      const { data: queueData, error: queueError } = await supabase
        .from('job_queue')
        .select('count')
        .limit(1)

      // Check Edge Function
      let edgeFunctionStatus = 'unknown'
      try {
        const response = await fetch(`${this.edgeFunctionUrl}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tenant_id: '00000000-0000-0000-0000-000000000000',
            worker_id: 'health-check',
            action: 'get_next'
          })
        })
        edgeFunctionStatus = response.ok ? 'healthy' : 'unhealthy'
      } catch (error) {
        edgeFunctionStatus = 'unreachable'
      }

      const status = catalogError || queueError ? 'degraded' : 'healthy'

      return {
        status,
        details: {
          supabase_catalog: catalogError ? 'error' : 'healthy',
          supabase_queue: queueError ? 'error' : 'healthy',
          edge_function: edgeFunctionStatus,
          timestamp: new Date().toISOString()
        }
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        details: {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        }
      }
    }
  }
}

// Export singleton instance
export const jobService = JobService.getInstance()

// Export hook for React components
export function useJobService() {
  return jobService
}
