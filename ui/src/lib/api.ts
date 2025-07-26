// API client with tenant context support

interface TenantContext {
  tenantId: string;
  userId?: string;
}

interface ApiRequestOptions extends RequestInit {
  tenantContext?: TenantContext;
  skipTenantHeaders?: boolean;
}

class ApiClient {
  private baseUrl: string;
  private defaultTenantContext: TenantContext | null = null;

  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * Set default tenant context for all requests
   */
  setDefaultTenantContext(context: TenantContext) {
    this.defaultTenantContext = context;
  }

  /**
   * Get current tenant context
   */
  getTenantContext(): TenantContext | null {
    return this.defaultTenantContext;
  }

  /**
   * Create headers with tenant context
   */
  private createHeaders(options: ApiRequestOptions = {}): Headers {
    const headers = new Headers(options.headers);
    
    // Add default Content-Type if not set
    if (!headers.has('Content-Type') && options.body && typeof options.body === 'string') {
      headers.set('Content-Type', 'application/json');
    }

    // Add tenant context headers unless explicitly skipped
    if (!options.skipTenantHeaders) {
      const tenantContext = options.tenantContext || this.defaultTenantContext;
      
      if (tenantContext) {
        headers.set('X-Tenant-ID', tenantContext.tenantId);
        
        if (tenantContext.userId) {
          headers.set('X-User-ID', tenantContext.userId);
        }
      }
    }

    return headers;
  }

  /**
   * Generic request method
   */
  private async request<T = any>(
    endpoint: string, 
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = this.createHeaders(options);
    
    const requestOptions: RequestInit = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, requestOptions);
      
      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      let data: any;
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        throw new ApiError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          data
        );
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Network or parsing errors
      throw new ApiError(
        `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0,
        null
      );
    }
  }

  /**
   * GET request
   */
  async get<T = any>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T = any>(
    endpoint: string, 
    data?: any, 
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const body = data ? JSON.stringify(data) : undefined;
    return this.request<T>(endpoint, { 
      ...options, 
      method: 'POST', 
      body 
    });
  }

  /**
   * PUT request
   */
  async put<T = any>(
    endpoint: string, 
    data?: any, 
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const body = data ? JSON.stringify(data) : undefined;
    return this.request<T>(endpoint, { 
      ...options, 
      method: 'PUT', 
      body 
    });
  }

  /**
   * DELETE request
   */
  async delete<T = any>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  /**
   * PATCH request
   */
  async patch<T = any>(
    endpoint: string, 
    data?: any, 
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const body = data ? JSON.stringify(data) : undefined;
    return this.request<T>(endpoint, { 
      ...options, 
      method: 'PATCH', 
      body 
    });
  }
}

/**
 * Custom API Error class
 */
export class ApiError extends Error {
  public status: number;
  public data: any;

  constructor(message: string, status: number, data: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

/**
 * API Base URL configuration
 */
const getApiBaseUrl = (): string => {
  // Check if we're in development mode
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    return 'http://localhost:8000'; // Development API Gateway
  }
  
  // Production API domain
  return 'https://api.launch24.com';
};

/**
 * Default API client instance
 */
export const apiClient = new ApiClient(getApiBaseUrl());

/**
 * Orchestrator API methods
 */
export const orchestratorApi = {
  /**
   * Submit an idea to the orchestrator
   */
  async submitIdea(ideaData: any, tenantContext?: TenantContext) {
    return apiClient.post('/api/orchestrate', {
      stage: 'idea_validation',
      payload: {
        ...ideaData,
        submission_type: 'user_idea',
        submitted_at: new Date().toISOString()
      }
    }, { tenantContext });
  },

  /**
   * Get orchestrator status
   */
  async getStatus(tenantContext?: TenantContext) {
    return apiClient.get('/api/orchestrate/status', { tenantContext });
  }
};

/**
 * Design API methods
 */
export const designApi = {
  /**
   * Generate design recommendations
   */
  async generateDesign(designRequest: any, tenantContext?: TenantContext) {
    return apiClient.post('/api/design/generate', designRequest, { tenantContext });
  }
};

/**
 * Tech Stack API methods
 */
export const techStackApi = {
  /**
   * Get tech stack recommendations
   */
  async getRecommendations(request: any, tenantContext?: TenantContext) {
    return apiClient.post('/api/techstack/recommend', request, { tenantContext });
  }
};

/**
 * Development API methods
 */
export const devApi = {
  /**
   * Get active tasks
   */
  async getActiveTasks(tenantContext?: TenantContext) {
    return apiClient.get('/api/dev/active-tasks', { tenantContext });
  },

  /**
   * Get pull requests
   */
  async getPullRequests(params: any = {}, tenantContext?: TenantContext) {
    const queryParams = new URLSearchParams(params);
    return apiClient.get(`/api/dev/pull-requests?${queryParams}`, { tenantContext });
  }
};

/**
 * Billing API methods
 */
export const billingApi = {
  /**
   * Create checkout session
   */
  async createCheckoutSession(sessionData: any, tenantContext?: TenantContext) {
    return apiClient.post('/api/billing/create-checkout-session', sessionData, { tenantContext });
  }
};

/**
 * Utility functions for tenant context management
 */
export const tenantUtils = {
  /**
   * Set default tenant context for the session
   */
  setTenantContext(tenantId: string, userId?: string) {
    const context: TenantContext = { tenantId, userId };
    apiClient.setDefaultTenantContext(context);
    
    // Store in localStorage for persistence
    localStorage.setItem('tenantContext', JSON.stringify(context));
  },

  /**
   * Get current tenant context
   */
  getTenantContext(): TenantContext | null {
    return apiClient.getTenantContext();
  },

  /**
   * Load tenant context from localStorage
   */
  loadTenantContextFromStorage(): TenantContext | null {
    try {
      const stored = localStorage.getItem('tenantContext');
      if (stored) {
        const context = JSON.parse(stored);
        apiClient.setDefaultTenantContext(context);
        return context;
      }
    } catch (error) {
      console.warn('Failed to load tenant context from storage:', error);
    }
    return null;
  },

  /**
   * Clear tenant context
   */
  clearTenantContext() {
    apiClient.setDefaultTenantContext({ tenantId: 'default' });
    localStorage.removeItem('tenantContext');
  },

  /**
   * Initialize tenant context with defaults
   */
  initializeTenantContext() {
    // Try to load from storage first
    const storedContext = this.loadTenantContextFromStorage();
    
    if (!storedContext) {
      // Set default context
      this.setTenantContext('default', 'default-user');
    }
    
    return apiClient.getTenantContext();
  }
};

export type { TenantContext, ApiRequestOptions }; 