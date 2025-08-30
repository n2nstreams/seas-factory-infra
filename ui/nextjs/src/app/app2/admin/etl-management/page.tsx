'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import Navigation from '@/components/Navigation'
import { 
  etlService, 
  ETLJob, 
  DataMapping 
} from '@/lib/etl-service'

export default function ETLManagementPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  
  const [etlJobs, setEtlJobs] = useState<ETLJob[]>([])
  const [dataMappings, setDataMappings] = useState<Record<string, DataMapping[]>>({})
  const [isPageLoading, setIsPageLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTable, setSelectedTable] = useState<string>('tenants')
  const [batchSize, setBatchSize] = useState<number>(100)
  const [validationResults, setValidationResults] = useState<Record<string, any>>({})

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/app2/signin')
    }
    // Only allow admin users
    if (!isLoading && user && user.plan !== 'growth') {
      router.push('/app2/dashboard')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user?.plan === 'growth') {
      loadETLData()
    }
  }, [user])

  const loadETLData = async () => {
    try {
      setIsPageLoading(true)
      setError(null)
      
      const [jobs, mappings] = await Promise.all([
        etlService.getAllETLJobs(),
        etlService.getDataMappings()
      ])
      
      setEtlJobs(jobs)
      setDataMappings(mappings)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load ETL data')
    } finally {
      setIsPageLoading(false)
    }
  }

  const handleStartETLJob = async () => {
    try {
      setError(null)
      const job = await etlService.startETLJob(selectedTable, batchSize)
      setEtlJobs(prev => [...prev, job])
      
      // Refresh jobs list after a short delay
      setTimeout(() => {
        loadETLData()
      }, 1000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start ETL job')
    }
  }

  const handleCancelETLJob = async (jobId: string) => {
    try {
      setError(null)
      const cancelled = await etlService.cancelETLJob(jobId)
      if (cancelled) {
        setEtlJobs(prev => 
          prev.map(job => 
            job.id === jobId 
              ? { ...job, status: 'failed', error: 'Job cancelled by user', completedAt: new Date() }
              : job
          )
        )
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel ETL job')
    }
  }

  const handleValidateMapping = async (tableName: string) => {
    try {
      setError(null)
      const result = await etlService.validateDataMapping(tableName)
      setValidationResults(prev => ({
        ...prev,
        [tableName]: result
      }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate data mapping')
    }
  }

  const handleClearCompletedJobs = async () => {
    try {
      setError(null)
      await etlService.clearCompletedJobs()
      setEtlJobs(prev => prev.filter(job => 
        job.status === 'pending' || job.status === 'running'
      ))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear completed jobs')
    }
  }

  const getJobStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center">
        <div className="glass-card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-primary-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user || user.plan !== 'growth') {
    return null // Will redirect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary-900 mb-2">
            ETL Management
          </h1>
          <p className="text-primary-600">
            Module 3: Database On-Ramp - Manage data extraction, transformation, and loading jobs.
          </p>
        </div>

        {/* Start New ETL Job */}
        <div className="glass-card mb-8">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Start New ETL Job</h2>
          <div className="grid md:grid-cols-3 gap-4 items-end">
            <div>
              <label htmlFor="table-select" className="block text-sm font-medium text-primary-700 mb-2">
                Select Table
              </label>
              <select
                id="table-select"
                value={selectedTable}
                onChange={(e) => setSelectedTable(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Select table for ETL job"
              >
                {Object.keys(dataMappings).map(table => (
                  <option key={table} value={table}>
                    {table.charAt(0).toUpperCase() + table.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="batch-size" className="block text-sm font-medium text-primary-700 mb-2">
                Batch Size
              </label>
              <input
                id="batch-size"
                type="number"
                value={batchSize}
                onChange={(e) => setBatchSize(Number(e.target.value))}
                min="10"
                max="1000"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                aria-label="Batch size for ETL processing"
              />
            </div>
            <div>
              <button
                onClick={handleStartETLJob}
                className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                aria-label="Start ETL job for selected table"
              >
                Start ETL Job
              </button>
            </div>
          </div>
        </div>

        {/* Data Mapping Validation */}
        <div className="glass-card mb-8">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Data Mapping Validation</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.keys(dataMappings).map(table => (
              <div key={table} className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium text-primary-800 mb-2">
                  {table.charAt(0).toUpperCase() + table.slice(1)} Table
                </h3>
                <button
                  onClick={() => handleValidateMapping(table)}
                  className="w-full px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                  aria-label={`Validate data mapping for ${table} table`}
                >
                  Validate Mapping
                </button>
                {validationResults[table] && (
                  <div className="mt-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      validationResults[table].valid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {validationResults[table].valid ? 'Valid' : 'Invalid'}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* ETL Jobs */}
        <div className="glass-card mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-primary-800">ETL Jobs</h2>
            <div className="flex space-x-2">
              <button
                onClick={loadETLData}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                aria-label="Refresh ETL jobs list"
              >
                Refresh
              </button>
              <button
                onClick={handleClearCompletedJobs}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                aria-label="Clear completed ETL jobs"
              >
                Clear Completed
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {etlJobs.length === 0 ? (
            <div className="text-center py-8 text-primary-600">
              No ETL jobs found. Start a new job to begin data migration.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left p-3 font-semibold text-primary-800">Job ID</th>
                    <th className="text-left p-3 font-semibold text-primary-800">Table</th>
                    <th className="text-left p-3 font-semibold text-primary-800">Status</th>
                    <th className="text-left p-3 font-semibold text-primary-800">Progress</th>
                    <th className="text-left p-3 font-semibold text-primary-800">Records</th>
                    <th className="text-left p-3 font-semibold text-primary-800">Timing</th>
                    <th className="text-left p-3 font-semibold text-primary-800">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {etlJobs.map((job) => (
                    <tr key={job.id} className="border-b border-gray-100">
                      <td className="p-3">
                        <div className="text-sm font-mono text-primary-600">
                          {job.id.substring(0, 20)}...
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="font-medium text-primary-800">{job.tableName}</div>
                        <div className="text-sm text-primary-600">
                          Batch: {job.metadata.batchSize}
                        </div>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getJobStatusColor(job.status)}`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="p-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress}%` }}
                          ></div>
                        </div>
                        <div className="text-sm text-primary-600 mt-1">
                          {job.progress}%
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="text-sm">
                          <div>Processed: {job.recordsProcessed}</div>
                          <div>Total: {job.recordsTotal}</div>
                        </div>
                      </td>
                      <td className="p-3 text-sm text-primary-600">
                        {job.startedAt && (
                          <div>Started: {new Date(job.startedAt).toLocaleTimeString()}</div>
                        )}
                        {job.completedAt && (
                          <div>Completed: {new Date(job.completedAt).toLocaleTimeString()}</div>
                        )}
                      </td>
                      <td className="p-3">
                        <div className="flex space-x-2">
                          {job.status === 'running' && (
                            <button
                              onClick={() => handleCancelETLJob(job.id)}
                              className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                              aria-label={`Cancel ETL job ${job.id}`}
                            >
                              Cancel
                            </button>
                          )}
                          {job.error && (
                            <div className="text-xs text-red-600 max-w-xs">
                              {job.error}
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Data Mappings Details */}
        <div className="glass-card">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Data Mappings</h2>
          <div className="space-y-6">
            {Object.entries(dataMappings).map(([tableName, mappings]) => (
              <div key={tableName} className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-primary-800 mb-3">
                  {tableName.charAt(0).toUpperCase() + tableName.slice(1)} Table
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left p-2 font-medium text-primary-700">Legacy Column</th>
                        <th className="text-left p-2 font-medium text-primary-700">Supabase Column</th>
                        <th className="text-left p-2 font-medium text-primary-700">Required</th>
                        <th className="text-left p-2 font-medium text-primary-700">Default Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mappings.map((mapping, index) => (
                        <tr key={index} className="border-b border-gray-100">
                          <td className="p-2 font-mono text-primary-600">{mapping.legacyColumn}</td>
                          <td className="p-2 font-mono text-primary-600">{mapping.supabaseColumn}</td>
                          <td className="p-2">
                            <span className={`px-2 py-1 rounded text-xs ${
                              mapping.required ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {mapping.required ? 'Required' : 'Optional'}
                            </span>
                          </td>
                          <td className="p-2 text-primary-600">
                            {mapping.defaultValue !== undefined ? 
                              JSON.stringify(mapping.defaultValue) : 
                              'None'
                            }
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
