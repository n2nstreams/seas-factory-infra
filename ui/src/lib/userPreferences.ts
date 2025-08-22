// User preferences management utility

export interface UserPreferences {
  onboardingCompleted: boolean;
  onboardingCompletedAt?: string;
  theme?: 'light' | 'dark' | 'auto';
  dashboardLayout?: 'grid' | 'list';
  notifications?: {
    buildComplete: boolean;
    projectUpdates: boolean;
    billingAlerts: boolean;
  };
}

const DEFAULT_PREFERENCES: UserPreferences = {
  onboardingCompleted: false,
  theme: 'light',
  dashboardLayout: 'grid',
  notifications: {
    buildComplete: true,
    projectUpdates: true,
    billingAlerts: true
  }
};

const STORAGE_KEY = 'saas-factory-user-preferences';

export class UserPreferencesManager {
  private static instance: UserPreferencesManager;
  private preferences: UserPreferences;

  private constructor() {
    this.preferences = this.loadPreferences();
  }

  static getInstance(): UserPreferencesManager {
    if (!UserPreferencesManager.instance) {
      UserPreferencesManager.instance = new UserPreferencesManager();
    }
    return UserPreferencesManager.instance;
  }

  /**
   * Load preferences from localStorage or return defaults
   */
  private loadPreferences(): UserPreferences {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Merge with defaults to ensure all properties exist
        return { ...DEFAULT_PREFERENCES, ...parsed };
      }
    } catch (error) {
      console.warn('Failed to load user preferences:', error);
    }
    return { ...DEFAULT_PREFERENCES };
  }

  /**
   * Save preferences to localStorage
   */
  private savePreferences(): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.preferences));
    } catch (error) {
      console.error('Failed to save user preferences:', error);
    }
  }

  /**
   * Get all preferences
   */
  getPreferences(): UserPreferences {
    return { ...this.preferences };
  }

  /**
   * Update specific preferences
   */
  updatePreferences(updates: Partial<UserPreferences>): void {
    this.preferences = { ...this.preferences, ...updates };
    this.savePreferences();
  }

  /**
   * Check if onboarding has been completed
   */
  isOnboardingCompleted(): boolean {
    return this.preferences.onboardingCompleted;
  }

  /**
   * Mark onboarding as completed
   */
  completeOnboarding(): void {
    this.preferences.onboardingCompleted = true;
    this.preferences.onboardingCompletedAt = new Date().toISOString();
    this.savePreferences();
  }

  /**
   * Reset onboarding (for testing or support purposes)
   */
  resetOnboarding(): void {
    this.preferences.onboardingCompleted = false;
    delete this.preferences.onboardingCompletedAt;
    this.savePreferences();
  }

  /**
   * Get theme preference
   */
  getTheme(): string {
    return this.preferences.theme || 'light';
  }

  /**
   * Set theme preference
   */
  setTheme(theme: 'light' | 'dark' | 'auto'): void {
    this.updatePreferences({ theme });
  }

  /**
   * Get dashboard layout preference
   */
  getDashboardLayout(): string {
    return this.preferences.dashboardLayout || 'grid';
  }

  /**
   * Set dashboard layout preference
   */
  setDashboardLayout(layout: 'grid' | 'list'): void {
    this.updatePreferences({ dashboardLayout: layout });
  }

  /**
   * Get notification preferences
   */
  getNotificationPreferences() {
    return this.preferences.notifications || DEFAULT_PREFERENCES.notifications;
  }

  /**
   * Update notification preferences
   */
  updateNotificationPreferences(notifications: Partial<UserPreferences['notifications']>): void {
    const currentNotifications = this.preferences.notifications || DEFAULT_PREFERENCES.notifications!;
    this.updatePreferences({
      notifications: {
        ...currentNotifications,
        ...notifications
      }
    });
  }

  /**
   * Reset all preferences to defaults
   */
  resetToDefaults(): void {
    this.preferences = { ...DEFAULT_PREFERENCES };
    this.savePreferences();
  }

  /**
   * Clear all stored preferences
   */
  clearPreferences(): void {
    try {
      localStorage.removeItem(STORAGE_KEY);
      this.preferences = { ...DEFAULT_PREFERENCES };
    } catch (error) {
      console.error('Failed to clear user preferences:', error);
    }
  }
}

// Export singleton instance for easy use
export const userPreferences = UserPreferencesManager.getInstance();

/**
 * Session state management utilities
 */
export const sessionUtils = {
  /**
   * Check if user session is valid
   */
  isValidSession: (): boolean => {
    try {
      const user = localStorage.getItem('user');
      if (!user) return false;

      const parsedUser = JSON.parse(user);
      // Check if user object has required fields
      return !!(parsedUser.id && parsedUser.email && parsedUser.name);
    } catch (error) {
      console.warn('Invalid session data:', error);
      return false;
    }
  },

  /**
   * Get current user from session
   */
  getCurrentUser: (): any => {
    if (!sessionUtils.isValidSession()) return null;

    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },

  /**
   * Clear all session data
   */
  clearSession: (): void => {
    try {
      localStorage.removeItem('user');
      localStorage.removeItem('tenantContext');
      // Clear any other session-related data
      const keysToRemove = Object.keys(localStorage).filter(key =>
        key.startsWith('session_') || key.startsWith('auth_')
      );
      keysToRemove.forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error('Error clearing session:', error);
    }
  },

  /**
   * Initialize session with user data
   */
  initializeSession: (userData: any): void => {
    try {
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Error initializing session:', error);
    }
  }
};

// Export utility functions for common operations
export const onboardingUtils = {
  isCompleted: () => userPreferences.isOnboardingCompleted(),
  complete: () => userPreferences.completeOnboarding(),
  reset: () => userPreferences.resetOnboarding()
};

// Development utilities - only use in development environment
export const devUtils = {
  /**
   * Reset onboarding for testing (logs action for visibility)
   */
  resetOnboardingForTesting: () => {
    console.log('🧪 [DEV] Resetting onboarding for testing...');
    userPreferences.resetOnboarding();
    console.log('✅ [DEV] Onboarding reset complete. Refresh the dashboard to see the wizard.');
  },

  /**
   * Log current user preferences state
   */
  logPreferences: () => {
    console.log('👤 [DEV] Current user preferences:', userPreferences.getPreferences());
  },

  /**
   * Force show onboarding wizard (for testing)
   */
  forceShowOnboarding: () => {
    console.log('🎯 [DEV] Forcing onboarding wizard to show...');
    userPreferences.resetOnboarding();
    window.location.reload();
  }
};

// Make dev utils available globally in development
if (typeof window !== 'undefined' && import.meta.env?.DEV) {
  (window as any).onboardingDevUtils = devUtils;
  console.log('🔧 [DEV] Onboarding dev utils available at: window.onboardingDevUtils');
  console.log('💡 [DEV] Try: window.onboardingDevUtils.forceShowOnboarding()');
} 