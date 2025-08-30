// Supabase Edge Function for Module 5: Jobs & Scheduling
// This function processes jobs from the job queue using a pg-boss pattern
// Handles job execution, retries, and monitoring

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface JobRequest {
  tenant_id: string
  worker_id: string
  job_family?: string
  action: 'get_next' | 'complete' | 'retry' | 'heartbeat'
  job_id?: string
  status?: 'succeeded' | 'failed'
  output_data?: any
  error_data?: any
}

interface JobResponse {
  success: boolean
  data?: any
  error?: string
}

// Initialize Supabase client
const supabaseUrl = Deno.env.get('SUPABASE_URL')!
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const supabase = createClient(supabaseUrl, supabaseServiceKey)

// Job execution handlers for different job types
const jobHandlers: Record<string, (input: any) => Promise<any>> = {
  'security_scan': async (input) => {
    // Simulate security scan execution
    console.log('Executing security scan with input:', input)
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate 2s execution
    
    return {
      vulnerabilities_found: Math.floor(Math.random() * 5),
      risk_score: Math.random() * 10,
      recommendations: ['Update dependencies', 'Fix security headers']
    }
  },
  
  'code_generation': async (input) => {
    // Simulate code generation execution
    console.log('Executing code generation with input:', input)
    await new Promise(resolve => setTimeout(resolve, 5000)) // Simulate 5s execution
    
    return {
      files_generated: Math.floor(Math.random() * 10) + 1,
      lines_of_code: Math.floor(Math.random() * 500) + 100,
      complexity_score: Math.random() * 10
    }
  },
  
  'design_generation': async (input) => {
    // Simulate design generation execution
    console.log('Executing design generation with input:', input)
    await new Promise(resolve => setTimeout(resolve, 8000)) // Simulate 8s execution
    
    return {
      wireframes_created: Math.floor(Math.random() * 5) + 1,
      style_guide_pages: Math.floor(Math.random() * 10) + 3,
      design_system_components: Math.floor(Math.random() * 20) + 5
    }
  },
  
  'data_migration': async (input) => {
    // Simulate data migration execution
    console.log('Executing data migration with input:', input)
    await new Promise(resolve => setTimeout(resolve, 15000)) // Simulate 15s execution
    
    return {
      records_migrated: Math.floor(Math.random() * 10000) + 1000,
      tables_processed: Math.floor(Math.random() * 10) + 1,
      migration_duration: '15s'
    }
  },
  
  'backup_cleanup': async (input) => {
    // Simulate backup cleanup execution
    console.log('Executing backup cleanup with input:', input)
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate 1s execution
    
    return {
      old_backups_removed: Math.floor(Math.random() * 50) + 10,
      space_freed_gb: Math.random() * 10,
      cleanup_duration: '1s'
    }
  },
  
  'health_check': async (input) => {
    // Simulate health check execution
    console.log('Executing health check with input:', input)
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate 0.5s execution
    
    return {
      services_healthy: Math.floor(Math.random() * 10) + 5,
      response_time_avg: Math.random() * 100 + 50,
      uptime_percentage: 99.9
    }
  },
  
  'email_send': async (input) => {
    // Simulate email sending execution
    console.log('Executing email send with input:', input)
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate 1s execution
    
    return {
      emails_sent: 1,
      delivery_status: 'delivered',
      message_id: `msg_${Math.random().toString(36).substr(2, 9)}`
    }
  },
  
  'webhook_process': async (input) => {
    // Simulate webhook processing execution
    console.log('Executing webhook processing with input:', input)
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate 2s execution
    
    return {
      webhook_processed: true,
      events_handled: Math.floor(Math.random() * 5) + 1,
      processing_duration: '2s'
    }
  }
}

// Get next available job from the queue
async function getNextJob(tenantId: string, workerId: string, jobFamily?: string): Promise<any> {
  try {
    // Set tenant context for RLS
    await supabase.rpc('set_config', {
      key: 'app.current_tenant_id',
      value: tenantId
    })
    
    // Get next job using the database function
    const { data, error } = await supabase.rpc('get_next_job', {
      p_tenant_id: tenantId,
      p_worker_id: workerId,
      p_job_family: jobFamily || null
    })
    
    if (error) {
      console.error('Error getting next job:', error)
      return null
    }
    
    if (data && data.length > 0) {
      return data[0]
    }
    
    return null
  } catch (error) {
    console.error('Exception getting next job:', error)
    return null
  }
}

// Complete a job (success or failure)
async function completeJob(jobId: string, status: string, outputData?: any, errorData?: any): Promise<boolean> {
  try {
    const { error } = await supabase.rpc('complete_job', {
      p_job_id: jobId,
      p_status: status,
      p_output_data: outputData || {},
      p_error_data: errorData || {}
    })
    
    if (error) {
      console.error('Error completing job:', error)
      return false
    }
    
    return true
  } catch (error) {
    console.error('Exception completing job:', error)
    return false
  }
}

// Retry a failed job
async function retryJob(jobId: string, delaySeconds: number = 60): Promise<boolean> {
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

// Update worker heartbeat
async function updateHeartbeat(jobId: string, workerId: string): Promise<boolean> {
  try {
    const { error } = await supabase
      .from('job_queue')
      .update({ 
        worker_heartbeat: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
      .eq('id', jobId)
      .eq('worker_id', workerId)
    
    if (error) {
      console.error('Error updating heartbeat:', error)
      return false
    }
    
    return true
  } catch (error) {
    console.error('Exception updating heartbeat:', error)
    return false
  }
}

// Execute a job based on its type
async function executeJob(jobName: string, inputData: any): Promise<any> {
  const handler = jobHandlers[jobName]
  
  if (!handler) {
    throw new Error(`No handler found for job type: ${jobName}`)
  }
  
  try {
    const result = await handler(inputData)
    return result
  } catch (error) {
    console.error(`Error executing job ${jobName}:`, error)
    throw error
  }
}

// Main request handler
serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }
  
  try {
    const { tenant_id, worker_id, job_family, action, job_id, status, output_data, error_data }: JobRequest = await req.json()
    
    // Validate required fields
    if (!tenant_id || !worker_id || !action) {
      return new Response(
        JSON.stringify({
          success: false,
          error: 'Missing required fields: tenant_id, worker_id, action'
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }
    
    let response: JobResponse
    
    switch (action) {
      case 'get_next':
        const nextJob = await getNextJob(tenant_id, worker_id, job_family)
        if (nextJob) {
          response = {
            success: true,
            data: nextJob
          }
        } else {
          response = {
            success: true,
            data: null // No jobs available
          }
        }
        break
        
      case 'complete':
        if (!job_id || !status) {
          response = {
            success: false,
            error: 'Missing required fields for complete action: job_id, status'
          }
        } else {
          const success = await completeJob(job_id, status, output_data, error_data)
          response = {
            success,
            data: { job_id, status }
          }
        }
        break
        
      case 'retry':
        if (!job_id) {
          response = {
            success: false,
            error: 'Missing required field for retry action: job_id'
          }
        } else {
          const success = await retryJob(job_id)
          response = {
            success,
            data: { job_id, retry_scheduled: success }
          }
        }
        break
        
      case 'heartbeat':
        if (!job_id) {
          response = {
            success: false,
            error: 'Missing required field for heartbeat action: job_id'
          }
        } else {
          const success = await updateHeartbeat(job_id, worker_id)
          response = {
            success,
            data: { job_id, heartbeat_updated: success }
          }
        }
        break
        
      default:
        response = {
          success: false,
          error: `Unknown action: ${action}`
        }
    }
    
    return new Response(
      JSON.stringify(response),
      { 
        status: response.success ? 200 : 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
    
  } catch (error) {
    console.error('Error processing request:', error)
    
    return new Response(
      JSON.stringify({
        success: false,
        error: 'Internal server error'
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})
