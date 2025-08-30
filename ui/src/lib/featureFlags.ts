// Feature Flags Configuration
// This file manages feature flags for the SaaS Factory platform

export interface FeatureFlag {
  name: string;
  description: string;
  enabled: boolean;
  rolloutPercentage: number; // 0-100, percentage of users who see this feature
  environment: 'development' | 'staging' | 'production';
  createdAt: string;
  updatedAt: string;
}

export interface FeatureFlagConfig {
  [key: string]: FeatureFlag;
}

// Default feature flags configuration
export const defaultFeatureFlags: FeatureFlagConfig = {
  // Module 1: UI Shell Migration
  ui_shell_v2: {
    name: 'UI Shell v2',
    description: 'Next.js + shadcn/ui shell migration',
    enabled: true,
    rolloutPercentage: 100,
    environment: 'production',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 2: Authentication Migration
  auth_supabase: {
    name: 'Supabase Authentication',
    description: 'Supabase Auth integration with dual auth system',
    enabled: true,
    rolloutPercentage: 100,
    environment: 'production',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 3: Database Migration
  db_dual_write: {
    name: 'Database Dual Write',
    description: 'Dual-write system for database migration',
    enabled: true,
    rolloutPercentage: 100,
    environment: 'production',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 4: File/Object Storage
  storage_supabase: {
    name: 'Supabase Storage',
    description: 'Supabase Storage integration with migration system',
    enabled: true,
    rolloutPercentage: 100,
    environment: 'production',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 5: Jobs & Scheduling
  jobs_pg: {
    name: 'PostgreSQL Jobs',
    description: 'pg-boss job scheduling system',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 6: Billing - Stripe Checkout + Customer Portal
  billing_v2: {
    name: 'Billing v2',
    description: 'New Stripe billing system with customer portal',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 7: Email/Notifications
  emails_v2: {
    name: 'Email System v2',
    description: 'Resend email integration',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 8: Observability
  observability_v2: {
    name: 'Observability v2',
    description: 'Sentry + Vercel Analytics integration',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 9: AI Workloads
  ai_workloads_v2: {
    name: 'AI Workloads v2',
    description: 'New AI workload management system with cost controls and latency constraints',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 10: Hosting, Domains, DNS
  hosting_vercel: {
    name: 'Vercel Hosting',
    description: 'Vercel hosting with weighted canaries',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 11: Security & Compliance
  security_compliance_v2: {
    name: 'Security & Compliance v2',
    description: 'Comprehensive security and compliance system with RLS + Least-Privilege + Audits',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 12: Performance & Cost
  performance_monitoring: {
    name: 'Performance Monitoring',
    description: 'Load testing and performance monitoring',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 13: Final Data Migration
  data_migration_final: {
    name: 'Final Data Migration',
    description: 'Source-of-truth cutover to new systems',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },

  // Module 14: Decommission
  decommission_legacy: {
    name: 'Legacy System Decommission',
    description: 'Decommission legacy infrastructure',
    enabled: false,
    rolloutPercentage: 0,
    environment: 'development',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  },
};

// Feature flag service class
export class FeatureFlagService {
  private flags: FeatureFlagConfig;
  private apiBaseUrl: string;

  constructor() {
    this.flags = defaultFeatureFlags;
    this.apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.loadFeatureFlags();
  }

  // Load feature flags from API or localStorage
  private async loadFeatureFlags() {
    try {
      // Try to load from API first
      const response = await fetch(`${this.apiBaseUrl}/feature-flags`);
      if (response.ok) {
        const apiFlags = await response.json();
        this.flags = { ...this.flags, ...apiFlags };
      }
    } catch (error) {
      console.warn('Failed to load feature flags from API, using defaults');
    }

    // Fallback to localStorage
    try {
      const storedFlags = localStorage.getItem('feature_flags');
      if (storedFlags) {
        const parsedFlags = JSON.parse(storedFlags);
        this.flags = { ...this.flags, ...parsedFlags };
      }
    } catch (error) {
      console.warn('Failed to load feature flags from localStorage');
    }
  }

  // Check for flag conflicts before enabling
  private checkFlagConflicts(flagName: string, enabled: boolean): { hasConflict: boolean; conflicts: string[] } {
    if (!enabled) {
      return { hasConflict: false, conflicts: [] };
    }

    const conflicts: string[] = [];

    // Check decommission_legacy conflicts
    if (flagName === 'decommission_legacy') {
      // Cannot decommission legacy while migration flags are active
      if (this.isEnabled('db_dual_write')) {
        conflicts.push('db_dual_write');
      }
      if (this.isEnabled('storage_supabase')) {
        conflicts.push('storage_supabase');
      }
      if (this.isEnabled('auth_supabase')) {
        conflicts.push('auth_supabase');
      }
    }

    // Check migration flag conflicts with decommission
    if (['db_dual_write', 'storage_supabase', 'auth_supabase'].includes(flagName)) {
      if (this.isEnabled('decommission_legacy')) {
        conflicts.push('decommission_legacy');
      }
    }

    // Check data migration final conflicts
    if (flagName === 'data_migration_final') {
      if (this.isEnabled('decommission_legacy')) {
        conflicts.push('decommission_legacy');
      }
    }

    return {
      hasConflict: conflicts.length > 0,
      conflicts
    };
  }

  // Check if a feature flag is enabled
  isEnabled(flagName: string): boolean {
    const flag = this.flags[flagName];
    if (!flag) {
      return false;
    }

    // Check if flag is enabled
    if (!flag.enabled) {
      return false;
    }

    // Check environment
    const currentEnv = import.meta.env.MODE || 'development';
    if (flag.environment !== currentEnv && currentEnv !== 'development') {
      return false;
    }

    // Check rollout percentage
    const userId = this.getUserId();
    if (userId) {
      const hash = this.hashUserId(userId);
      const percentage = hash % 100;
      return percentage < flag.rolloutPercentage;
    }

    // Default to enabled if no user ID
    return true;
  }

  // Set a feature flag with conflict checking
  setFlag(flagName: string, enabled: boolean): { success: boolean; conflicts?: string[]; error?: string } {
    // Check for conflicts
    const conflictCheck = this.checkFlagConflicts(flagName, enabled);
    
    if (conflictCheck.hasConflict) {
      return {
        success: false,
        conflicts: conflictCheck.conflicts,
        error: `Cannot enable ${flagName} while conflicting flags are active: ${conflictCheck.conflicts.join(', ')}`
      };
    }

    // Update the flag
    if (this.flags[flagName]) {
      this.flags[flagName].enabled = enabled;
      this.flags[flagName].updatedAt = new Date().toISOString();
      
      // Save to localStorage
      try {
        localStorage.setItem('feature_flags', JSON.stringify(this.flags));
      } catch (error) {
        console.warn('Failed to save feature flags to localStorage');
      }

      return { success: true };
    }

    return {
      success: false,
      error: `Feature flag ${flagName} not found`
    };
  }

  // Get feature flag configuration
  getFlag(flagName: string): FeatureFlag | null {
    return this.flags[flagName] || null;
  }

  // Get all feature flags
  getAllFlags(): FeatureFlagConfig {
    return { ...this.flags };
  }

  // Get flag conflicts for a specific flag
  getFlagConflicts(flagName: string): string[] {
    const conflictCheck = this.checkFlagConflicts(flagName, true);
    return conflictCheck.conflicts;
  }

  // Get all potential conflicts in the system
  getAllConflicts(): { flagName: string; conflicts: string[] }[] {
    const allConflicts: { flagName: string; conflicts: string[] }[] = [];
    
    Object.keys(this.flags).forEach(flagName => {
      const conflicts = this.getFlagConflicts(flagName);
      if (conflicts.length > 0) {
        allConflicts.push({ flagName, conflicts });
      }
    });

    return allConflicts;
  }

  // Validate flag sequence for migration
  validateMigrationSequence(): { isValid: boolean; issues: string[] } {
    const issues: string[] = [];

    // Check if decommission is enabled before migration is complete
    if (this.isEnabled('decommission_legacy')) {
      if (!this.isEnabled('data_migration_final')) {
        issues.push('decommission_legacy cannot be enabled before data_migration_final');
      }
      if (!this.isEnabled('ui_shell_v2')) {
        issues.push('decommission_legacy cannot be enabled before ui_shell_v2');
      }
    }

    // Check if migration flags are enabled without proper sequence
    if (this.isEnabled('db_dual_write_tenants') && !this.isEnabled('db_dual_write')) {
      issues.push('db_dual_write_tenants requires db_dual_write to be enabled first');
    }
    if (this.isEnabled('db_dual_write_users') && !this.isEnabled('db_dual_write')) {
      issues.push('db_dual_write_users requires db_dual_write to be enabled first');
    }
    if (this.isEnabled('db_dual_write_projects') && !this.isEnabled('db_dual_write')) {
      issues.push('db_dual_write_projects requires db_dual_write to be enabled first');
    }
    if (this.isEnabled('db_dual_write_ideas') && !this.isEnabled('db_dual_write')) {
      issues.push('db_dual_write_ideas requires db_dual_write to be enabled first');
    }

    return {
      isValid: issues.length === 0,
      issues
    };
  }

  // Private helper methods
  private getUserId(): string | null {
    // Get user ID from your auth system
    return localStorage.getItem('user_id') || null;
  }

  private getAuthToken(): string {
    // Get auth token from your auth system
    return localStorage.getItem('auth_token') || '';
  }

  private hashUserId(userId: string): number {
    // Simple hash function for consistent user assignment
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      const char = userId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }
}

// Export singleton instance
export const featureFlagService = new FeatureFlagService();

// Export convenience functions
export const isFeatureEnabled = (flagName: string): boolean => 
  featureFlagService.isEnabled(flagName);

export const shouldShowFeature = (flagName: string): boolean => 
  featureFlagService.shouldShowFeature(flagName);

export const getFeatureFlag = (flagName: string): FeatureFlag | null => 
  featureFlagService.getFlag(flagName);

export const getAllFeatureFlags = (): FeatureFlagConfig => 
  featureFlagService.getAllFlags();
