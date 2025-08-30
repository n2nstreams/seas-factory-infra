'use client'

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react'

export interface FeatureFlags {
  ui_shell_v2: boolean
  auth_supabase: boolean
  db_dual_write: boolean
  db_dual_write_tenants: boolean
  db_dual_write_users: boolean
  db_dual_write_projects: boolean
  db_dual_write_ideas: boolean
  storage_supabase: boolean
  jobs_pg: boolean
  billing_v2: boolean
  emails_v2: boolean
  observability_v2: boolean
  sentry_enabled: boolean
  vercel_analytics_enabled: boolean
  health_monitoring_enabled: boolean
  ai_workloads_v2: boolean
  performance_monitoring: boolean
  data_migration_final: boolean
  decommission_legacy: boolean
}

interface FeatureFlagContextType {
  flags: FeatureFlags
  isEnabled: (flag: string) => boolean
  setFlag: (flag: string, enabled: boolean) => { success: boolean; conflicts?: string[]; error?: string }
  refreshFlags: () => void
  getConflicts: (flag: string) => string[]
  getAllConflicts: () => { flagName: string; conflicts: string[] }[]
  validateMigrationSequence: () => { isValid: boolean; issues: string[] }
}

const FeatureFlagContext = createContext<FeatureFlagContextType | undefined>(undefined)

const DEFAULT_FLAGS: FeatureFlags = {
  ui_shell_v2: true, // Enable new UI shell by default
  auth_supabase: true, // TEMPORARILY ENABLED FOR TESTING
  db_dual_write: false,
  db_dual_write_tenants: false,
  db_dual_write_users: false,
  db_dual_write_projects: false,
  db_dual_write_ideas: false,
  storage_supabase: true, // Enable Supabase storage for Module 4
  jobs_pg: true, // Enable Supabase jobs for Module 5
  billing_v2: false,
  emails_v2: false,
  observability_v2: true, // Enable observability for Module 8
  sentry_enabled: true, // Enable Sentry error tracking
  vercel_analytics_enabled: true, // Enable Vercel Analytics
  health_monitoring_enabled: true, // Enable health monitoring
  ai_workloads_v2: false, // Disable AI workloads v2 until ready
  agents_v2: false, // Disable AI agents v2 until Module 6 is complete
  performance_monitoring: true, // Enable performance monitoring for Module 12
  data_migration_final: false,
  decommission_legacy: false,
}

export function FeatureFlagProvider({ children }: { children: ReactNode }) {
  const [flags, setFlags] = useState<FeatureFlags>(DEFAULT_FLAGS)

  // Load feature flags from localStorage or environment
  useEffect(() => {
    const loadFlags = () => {
      try {
        // Check for feature flags in localStorage (for development/testing)
        const storedFlags = localStorage.getItem('saas-factory-feature-flags')
        if (storedFlags) {
          const parsedFlags = JSON.parse(storedFlags)
          setFlags(prev => ({ ...prev, ...parsedFlags }))
        }

        // Check environment variables for feature flags (both development and production)
        const envFlags: Partial<FeatureFlags> = {}
        Object.keys(DEFAULT_FLAGS).forEach(key => {
          const envKey = `NEXT_PUBLIC_FEATURE_${key.toUpperCase()}`
          if (process.env[envKey]) {
            envFlags[key] = process.env[envKey] === 'true'
            console.log(`🔧 Feature Flag Loaded: ${key} = ${process.env[envKey]} (from ${envKey})`)
          }
        })
        setFlags(prev => ({ ...prev, ...envFlags }))
        
        // Debug: Log final flags state
        console.log('🔧 Feature Flags Final State:', { ...DEFAULT_FLAGS, ...envFlags })
      } catch (error) {
        console.error('Error loading feature flags:', error)
      }
    }

    loadFlags()
  }, [])

  const isEnabled = (flag: string): boolean => {
    return flags[flag] || false
  }

  // Check for flag conflicts before setting
  const checkFlagConflicts = (flagName: string, enabled: boolean): { hasConflict: boolean; conflicts: string[] } => {
    if (!enabled) {
      return { hasConflict: false, conflicts: [] }
    }

    const conflicts: string[] = []

    // Check decommission_legacy conflicts
    if (flagName === 'decommission_legacy') {
      if (flags.db_dual_write) conflicts.push('db_dual_write')
      if (flags.storage_supabase) conflicts.push('storage_supabase')
      if (flags.auth_supabase) conflicts.push('auth_supabase')
    }

    // Check migration flag conflicts with decommission
    if (['db_dual_write', 'storage_supabase', 'auth_supabase'].includes(flagName)) {
      if (flags.decommission_legacy) conflicts.push('decommission_legacy')
    }

    // Check data migration final conflicts
    if (flagName === 'data_migration_final') {
      if (flags.decommission_legacy) conflicts.push('decommission_legacy')
    }

    return {
      hasConflict: conflicts.length > 0,
      conflicts
    }
  }

  const setFlag = (flag: string, enabled: boolean): { success: boolean; conflicts?: string[]; error?: string } => {
    // Check for conflicts
    const conflictCheck = checkFlagConflicts(flag, enabled)
    
    if (conflictCheck.hasConflict) {
      return {
        success: false,
        conflicts: conflictCheck.conflicts,
        error: `Cannot enable ${flag} while conflicting flags are active: ${conflictCheck.conflicts.join(', ')}`
      }
    }

    // Update the flag
    setFlags(prev => {
      const newFlags = { ...prev, [flag]: enabled }
      
      // Store in localStorage for development
      try {
        localStorage.setItem('saas-factory-feature-flags', JSON.stringify(newFlags))
      } catch (error) {
        console.error('Error saving feature flags:', error)
      }
      
      return newFlags
    })

    return { success: true }
  }

  const refreshFlags = () => {
    // Reload flags from storage/environment
    window.location.reload()
  }

  const getConflicts = (flag: string): string[] => {
    const conflictCheck = checkFlagConflicts(flag, true)
    return conflictCheck.conflicts
  }

  const getAllConflicts = (): { flagName: string; conflicts: string[] }[] => {
    const allConflicts: { flagName: string; conflicts: string[] }[] = []
    
    Object.keys(flags).forEach(flagName => {
      const conflicts = getConflicts(flagName)
      if (conflicts.length > 0) {
        allConflicts.push({ flagName, conflicts })
      }
    })

    return allConflicts
  }

  const validateMigrationSequence = (): { isValid: boolean; issues: string[] } => {
    const issues: string[] = []

    // Check if decommission is enabled before migration is complete
    if (flags.decommission_legacy) {
      if (!flags.data_migration_final) {
        issues.push('decommission_legacy cannot be enabled before data_migration_final')
      }
      if (!flags.ui_shell_v2) {
        issues.push('decommission_legacy cannot be enabled before ui_shell_v2')
      }
    }

    // Check if migration flags are enabled without proper sequence
    if (flags.db_dual_write_tenants && !flags.db_dual_write) {
      issues.push('db_dual_write_tenants requires db_dual_write to be enabled first')
    }
    if (flags.db_dual_write_users && !flags.db_dual_write) {
      issues.push('db_dual_write_users requires db_dual_write to be enabled first')
    }
    if (flags.db_dual_write_projects && !flags.db_dual_write) {
      issues.push('db_dual_write_projects requires db_dual_write to be enabled first')
    }
    if (flags.db_dual_write_ideas && !flags.db_dual_write) {
      issues.push('db_dual_write_ideas requires db_dual_write to be enabled first')
    }

    return {
      isValid: issues.length === 0,
      issues
    }
  }

  const value: FeatureFlagContextType = {
    flags,
    isEnabled,
    setFlag,
    refreshFlags,
    getConflicts,
    getAllConflicts,
    validateMigrationSequence,
  }

  return (
    <FeatureFlagContext.Provider value={value}>
      {children}
    </FeatureFlagContext.Provider>
  )
}

export function useFeatureFlags() {
  const context = useContext(FeatureFlagContext)
  if (context === undefined) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagProvider')
  }
  return context
}

// Hook for specific feature flag
export function useFeatureFlag(flag: string): boolean {
  const { isEnabled } = useFeatureFlags()
  return isEnabled(flag)
}
