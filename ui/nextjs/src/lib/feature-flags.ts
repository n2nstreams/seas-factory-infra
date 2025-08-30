// Feature flag service for controlling backend migration
export interface BackendFeatureFlags {
  backend_nextjs: boolean
  users_api_nextjs: boolean
  privacy_api_nextjs: boolean
  admin_api_nextjs: boolean
  ideas_api_nextjs: boolean
  projects_api_nextjs: boolean
  websocket_nextjs: boolean
}

// Default feature flags for backend migration
export const DEFAULT_BACKEND_FLAGS: BackendFeatureFlags = {
  backend_nextjs: false,        // Master flag for backend migration
  users_api_nextjs: false,      // User management API
  privacy_api_nextjs: false,    // Privacy and GDPR API
  admin_api_nextjs: false,      // Admin functions API
  ideas_api_nextjs: false,      // Ideas management API
  projects_api_nextjs: false,   // Projects management API
  websocket_nextjs: false,      // WebSocket support
}

// Feature flag service
export class BackendFeatureFlagService {
  private static instance: BackendFeatureFlagService
  private flags: BackendFeatureFlags

  private constructor() {
    this.flags = { ...DEFAULT_BACKEND_FLAGS }
    this.loadFlags()
  }

  public static getInstance(): BackendFeatureFlagService {
    if (!BackendFeatureFlagService.instance) {
      BackendFeatureFlagService.instance = new BackendFeatureFlagService()
    }
    return BackendFeatureFlagService.instance
  }

  // Load feature flags from environment and localStorage
  private loadFlags(): void {
    try {
      // Load from environment variables
      Object.keys(this.flags).forEach(key => {
        const envKey = `NEXT_PUBLIC_FEATURE_${key.toUpperCase()}`
        if (process.env[envKey]) {
          this.flags[key as keyof BackendFeatureFlags] = process.env[envKey] === 'true'
        }
      })

      // Load from localStorage (for development/testing)
      if (typeof window !== 'undefined') {
        const storedFlags = localStorage.getItem('saas-factory-backend-flags')
        if (storedFlags) {
          const parsedFlags = JSON.parse(storedFlags)
          this.flags = { ...this.flags, ...parsedFlags }
        }
      }
    } catch (error) {
      console.error('Error loading backend feature flags:', error)
    }
  }

  // Check if a specific feature flag is enabled
  public isEnabled(flag: keyof BackendFeatureFlags): boolean {
    return this.flags[flag] || false
  }

  // Check if backend migration is enabled
  public isBackendMigrationEnabled(): boolean {
    return this.flags.backend_nextjs
  }

  // Check if a specific API is migrated
  public isApiMigrated(api: keyof Omit<BackendFeatureFlags, 'backend_nextjs'>): boolean {
    return this.flags.backend_nextjs && this.flags[api]
  }

  // Get all flags
  public getAllFlags(): BackendFeatureFlags {
    return { ...this.flags }
  }

  // Set a feature flag (for development/testing)
  public setFlag(flag: keyof BackendFeatureFlags, enabled: boolean): void {
    this.flags[flag] = enabled
    
    // Store in localStorage for development
    if (typeof window !== 'undefined') {
      try {
        localStorage.setItem('saas-factory-backend-flags', JSON.stringify(this.flags))
      } catch (error) {
        console.error('Error saving backend feature flags:', error)
      }
    }
  }

  // Validate migration sequence
  public validateMigrationSequence(): { isValid: boolean; issues: string[] } {
    const issues: string[] = []

    // Check if individual APIs are enabled without master flag
    const apiFlags = ['users_api_nextjs', 'privacy_api_nextjs', 'admin_api_nextjs', 'ideas_api_nextjs', 'projects_api_nextjs', 'websocket_nextjs']
    
    apiFlags.forEach(apiFlag => {
      if (this.flags[apiFlag as keyof BackendFeatureFlags] && !this.flags.backend_nextjs) {
        issues.push(`${apiFlag} cannot be enabled without backend_nextjs`)
      }
    })

    return {
      isValid: issues.length === 0,
      issues
    }
  }

  // Get migration status
  public getMigrationStatus(): {
    overall: 'not_started' | 'in_progress' | 'completed'
    progress: number
    migratedApis: string[]
    pendingApis: string[]
  } {
    const apiFlags = ['users_api_nextjs', 'privacy_api_nextjs', 'admin_api_nextjs', 'ideas_api_nextjs', 'projects_api_nextjs', 'websocket_nextjs']
    
    const migratedApis = apiFlags.filter(api => this.flags[api as keyof BackendFeatureFlags])
    const pendingApis = apiFlags.filter(api => !this.flags[api as keyof BackendFeatureFlags])
    const progress = (migratedApis.length / apiFlags.length) * 100

    let overall: 'not_started' | 'in_progress' | 'completed'
    if (progress === 0) {
      overall = 'not_started'
    } else if (progress === 100) {
      overall = 'completed'
    } else {
      overall = 'in_progress'
    }

    return {
      overall,
      progress: Math.round(progress),
      migratedApis,
      pendingApis
    }
  }
}

// Export singleton instance
export const backendFeatureFlags = BackendFeatureFlagService.getInstance()

// Helper functions
export const isBackendApiEnabled = (api: keyof Omit<BackendFeatureFlags, 'backend_nextjs'>): boolean => {
  return backendFeatureFlags.isApiMigrated(api)
}

export const getBackendMigrationStatus = () => {
  return backendFeatureFlags.getMigrationStatus()
}
