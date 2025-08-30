'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { useFeatureFlags } from '@/components/providers/FeatureFlagProvider'
import Navigation from '@/components/Navigation'
import { 
  databaseMigrationService, 
  MigrationStatus, 
  MigrationTable,
  DualWriteResult 
} from '@/lib/database-migration'

export default function DatabaseMigrationPage() {
  const { user, isLoading } = useAuth()
  const { flags, setFlag } = useFeatureFlags()
  const router = useRouter()
  
  const [migrationStatus, setMigrationStatus] = useState<MigrationStatus[]>([])
  const [migrationTables, setMigrationTables] = useState<MigrationTable[]>([])
  const [isPageLoading, setIsPageLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [consistencyResults, setConsistencyResults] = useState<Record<string, any>>({})

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
      loadMigrationData()
    }
  }, [user])

  const loadMigrationData = async () => {
    try {
      setIsPageLoading(true)
      setError(null)
      
      const [status, tables] = await Promise.all([
        databaseMigrationService.getMigrationStatus(),
        databaseMigrationService.getMigrationTables()
      ])
      
      setMigrationStatus(status)
      setMigrationTables(tables)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load migration data')
    } finally {
      setIsPageLoading(false)
    }
  }

  const handleStartMigration = async (tableName: string) => {
    try {
      setError(null)
      const status = await databaseMigrationService.startTableMigration(tableName)
      setMigrationStatus(prev => 
        prev.map(s => s.table === tableName ? status : s)
      )
      
      // Enable the corresponding feature flag
      const flagName = `db_dual_write_${tableName}` as keyof typeof flags
      if (flagName in flags) {
        setFlag(flagName, true)
      }
      
      // Enable the main db_dual_write flag if not already enabled
      if (!flags.db_dual_write) {
        setFlag('db_dual_write', true)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start migration')
    }
  }

  const handleStopMigration = async (tableName: string) => {
    try {
      setError(null)
      const status = await databaseMigrationService.stopTableMigration(tableName)
      setMigrationStatus(prev => 
        prev.map(s => s.table === tableName ? status : s)
      )
      
      // Disable the corresponding feature flag
      const flagName = `db_dual_write_${tableName}` as keyof typeof flags
      if (flagName in flags) {
        setFlag(flagName, false)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop migration')
    }
  }

  const handleValidateConsistency = async (tableName: string) => {
    try {
      setError(null)
      const result = await databaseMigrationService.validateDataConsistency(tableName)
      setConsistencyResults(prev => ({
        ...prev,
        [tableName]: result
      }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to validate consistency')
    }
  }

  const handleResetMigration = async (tableName?: string) => {
    try {
      setError(null)
      await databaseMigrationService.resetMigrationStatus(tableName)
      await loadMigrationData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset migration')
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
            Database Migration Management
          </h1>
          <p className="text-primary-600">
            Module 3: Database On-Ramp - Manage dual-write operations between legacy and Supabase databases.
          </p>
        </div>

        {/* Feature Flags Status */}
        <div className="glass-card mb-8">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Migration Feature Flags</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="font-medium">Main Dual-Write</span>
              <span className={`px-2 py-1 rounded text-sm ${flags.db_dual_write ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {flags.db_dual_write ? 'Active' : 'Inactive'}
              </span>
            </div>
            {migrationTables.map(table => {
              const flagName = `db_dual_write_${table.name}` as keyof typeof flags
              const isEnabled = flags[flagName] || false
              return (
                <div key={table.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="font-medium">{table.name} Table</span>
                  <span className={`px-2 py-1 rounded text-sm ${isEnabled ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {isEnabled ? 'Active' : 'Inactive'}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Migration Tables */}
        <div className="glass-card mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-primary-800">Migration Tables</h2>
            <button
              onClick={() => loadMigrationData()}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Refresh
            </button>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left p-3 font-semibold text-primary-800">Table</th>
                  <th className="text-left p-3 font-semibold text-primary-800">Status</th>
                  <th className="text-left p-3 font-semibold text-primary-800">Records</th>
                  <th className="text-left p-3 font-semibold text-primary-800">Last Sync</th>
                  <th className="text-left p-3 font-semibold text-primary-800">Actions</th>
                </tr>
              </thead>
              <tbody>
                {migrationStatus.map((status) => (
                  <tr key={status.table} className="border-b border-gray-100">
                    <td className="p-3">
                      <div>
                        <div className="font-medium text-primary-800">{status.table}</div>
                        <div className="text-sm text-primary-600">
                          {migrationTables.find(t => t.name === status.table)?.rlsPolicy || 'No RLS'}
                        </div>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        status.status === 'active' ? 'bg-green-100 text-green-800' :
                        status.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                        status.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {status.status}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="text-sm">
                        <div>Migrated: {status.recordsMigrated}</div>
                        <div>Total: {status.recordsTotal}</div>
                      </div>
                    </td>
                    <td className="p-3 text-sm text-primary-600">
                      {status.lastSync ? new Date(status.lastSync).toLocaleString() : 'Never'}
                    </td>
                    <td className="p-3">
                      <div className="flex space-x-2">
                        {status.status === 'pending' ? (
                          <button
                            onClick={() => handleStartMigration(status.table)}
                            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                          >
                            Start
                          </button>
                        ) : (
                          <button
                            onClick={() => handleStopMigration(status.table)}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                          >
                            Stop
                          </button>
                        )}
                        <button
                          onClick={() => handleValidateConsistency(status.table)}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                        >
                          Validate
                        </button>
                        <button
                          onClick={() => handleResetMigration(status.table)}
                          className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
                        >
                          Reset
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Data Consistency Results */}
        {Object.keys(consistencyResults).length > 0 && (
          <div className="glass-card mb-8">
            <h2 className="text-xl font-semibold text-primary-800 mb-4">Data Consistency Validation</h2>
            <div className="space-y-4">
              {Object.entries(consistencyResults).map(([tableName, result]) => (
                <div key={tableName} className="p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-primary-800 mb-2">{tableName} Table</h3>
                  <div className="grid md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="font-medium">Legacy Count:</span> {result.legacyCount}
                    </div>
                    <div>
                      <span className="font-medium">Supabase Count:</span> {result.supabaseCount}
                    </div>
                    <div>
                      <span className="font-medium">Status:</span>
                      <span className={`ml-2 px-2 py-1 rounded text-xs ${
                        result.consistent ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {result.consistent ? 'Consistent' : 'Inconsistent'}
                      </span>
                    </div>
                  </div>
                  {result.differences.length > 0 && (
                    <div className="mt-2">
                      <span className="font-medium text-red-700">Differences:</span>
                      <ul className="mt-1 text-sm text-red-600">
                        {result.differences.map((diff, index) => (
                          <li key={index}>• {diff}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Migration Actions */}
        <div className="glass-card">
          <h2 className="text-xl font-semibold text-primary-800 mb-4">Bulk Actions</h2>
          <div className="flex space-x-4">
            <button
              onClick={() => handleResetMigration()}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Reset All Migrations
            </button>
            <button
              onClick={loadMigrationData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Refresh All Data
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
