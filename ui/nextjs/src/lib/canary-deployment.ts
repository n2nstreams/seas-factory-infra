/**
 * Canary Deployment Service
 * Manages traffic distribution between legacy and new systems
 */

export interface CanaryConfig {
  enabled: boolean;
  trafficPercentage: number;
  rollbackThreshold: number;
  healthCheckEndpoint: string;
  metricsEndpoint: string;
}

export interface CanaryMetrics {
  errorRate: number;
  responseTime: number;
  uptime: number;
  userSatisfaction: number;
  timestamp: Date;
}

export interface CanaryStatus {
  isActive: boolean;
  currentTrafficPercentage: number;
  healthStatus: 'healthy' | 'degraded' | 'critical';
  lastHealthCheck: Date;
  metrics: CanaryMetrics;
  rollbackTriggered: boolean;
}

export class CanaryDeploymentService {
  private config: CanaryConfig;
  private status: CanaryStatus;
  private healthCheckInterval: NodeJS.Timeout | null = null;

  constructor(config: CanaryConfig) {
    this.config = config;
    this.status = {
      isActive: false,
      currentTrafficPercentage: 0,
      healthStatus: 'healthy',
      lastHealthCheck: new Date(),
      metrics: {
        errorRate: 0,
        responseTime: 0,
        uptime: 1,
        userSatisfaction: 1,
        timestamp: new Date(),
      },
      rollbackTriggered: false,
    };
  }

  /**
   * Start canary deployment
   */
  async startCanary(initialTrafficPercentage: number = 10): Promise<void> {
    if (!this.config.enabled) {
      throw new Error('Canary deployment is not enabled');
    }

    this.status.isActive = true;
    this.status.currentTrafficPercentage = Math.min(initialTrafficPercentage, 100);
    
    // Start health monitoring
    this.startHealthMonitoring();
    
    console.log(`🚀 Canary deployment started with ${this.status.currentTrafficPercentage}% traffic`);
  }

  /**
   * Gradually increase canary traffic
   */
  async increaseTraffic(increment: number = 10): Promise<void> {
    if (!this.status.isActive) {
      throw new Error('Canary deployment is not active');
    }

    const newPercentage = Math.min(
      this.status.currentTrafficPercentage + increment,
      100
    );
    
    this.status.currentTrafficPercentage = newPercentage;
    console.log(`📈 Canary traffic increased to ${newPercentage}%`);
    
    // Check if we should trigger rollback
    await this.checkRollbackConditions();
  }

  /**
   * Trigger immediate rollback
   */
  async triggerRollback(): Promise<void> {
    this.status.isActive = false;
    this.status.currentTrafficPercentage = 0;
    this.status.rollbackTriggered = true;
    this.status.healthStatus = 'critical';
    
    // Stop health monitoring
    this.stopHealthMonitoring();
    
    console.log('🚨 Canary deployment rolled back - all traffic returned to legacy system');
  }

  /**
   * Get current canary status
   */
  getStatus(): CanaryStatus {
    return { ...this.status };
  }

  /**
   * Check if user should be routed to canary
   */
  shouldRouteToCanary(userId?: string): boolean {
    if (!this.status.isActive || this.status.rollbackTriggered) {
      return false;
    }

    // Simple hash-based routing for consistent user experience
    if (userId) {
      const hash = this.hashUserId(userId);
      return hash % 100 < this.status.currentTrafficPercentage;
    }

    // Random routing for anonymous users
    return Math.random() * 100 < this.status.currentTrafficPercentage;
  }

  /**
   * Start health monitoring
   */
  private startHealthMonitoring(): void {
    this.healthCheckInterval = setInterval(async () => {
      await this.performHealthCheck();
    }, 30000); // Check every 30 seconds
  }

  /**
   * Stop health monitoring
   */
  private stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Perform health check
   */
  private async performHealthCheck(): Promise<void> {
    try {
      const response = await fetch(this.config.healthCheckEndpoint, {
        method: 'GET',
        headers: {
          'X-Canary-Version': 'v2',
        },
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }

      const healthData = await response.json();
      this.updateMetrics(healthData);
      this.status.lastHealthCheck = new Date();
      
      // Check rollback conditions
      await this.checkRollbackConditions();
      
    } catch (error) {
      console.error('Health check failed:', error);
      this.status.healthStatus = 'degraded';
      
      // Trigger rollback if health check fails consistently
      if (this.status.healthStatus === 'degraded') {
        await this.triggerRollback();
      }
    }
  }

  /**
   * Update metrics from health check
   */
  private updateMetrics(healthData: any): void {
    this.status.metrics = {
      errorRate: healthData.errorRate || 0,
      responseTime: healthData.responseTime || 0,
      uptime: healthData.uptime || 1,
      userSatisfaction: healthData.userSatisfaction || 1,
      timestamp: new Date(),
    };

    // Update health status based on metrics
    if (this.status.metrics.errorRate > this.config.rollbackThreshold) {
      this.status.healthStatus = 'critical';
    } else if (this.status.metrics.errorRate > this.config.rollbackThreshold * 0.5) {
      this.status.healthStatus = 'degraded';
    } else {
      this.status.healthStatus = 'healthy';
    }
  }

  /**
   * Check if rollback conditions are met
   */
  private async checkRollbackConditions(): Promise<void> {
    if (this.status.rollbackTriggered) {
      return;
    }

    const shouldRollback = 
      this.status.metrics.errorRate > this.config.rollbackThreshold ||
      this.status.metrics.responseTime > 5000 || // 5 second threshold
      this.status.metrics.uptime < 0.95 || // 95% uptime threshold
      this.status.metrics.userSatisfaction < 0.8; // 80% satisfaction threshold

    if (shouldRollback) {
      console.log('🚨 Rollback conditions met - triggering rollback');
      await this.triggerRollback();
    }
  }

  /**
   * Hash user ID for consistent routing
   */
  private hashUserId(userId: string): number {
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      const char = userId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return Math.abs(hash);
  }

  /**
   * Get canary deployment configuration
   */
  getConfig(): CanaryConfig {
    return { ...this.config };
  }

  /**
   * Update canary configuration
   */
  updateConfig(newConfig: Partial<CanaryConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Canary configuration updated:', this.config);
  }
}

// Default canary configuration
export const defaultCanaryConfig: CanaryConfig = {
  enabled: true,
  trafficPercentage: 10,
  rollbackThreshold: 0.05, // 5% error rate
  healthCheckEndpoint: '/api/health',
  metricsEndpoint: '/api/metrics',
};

// Create singleton instance
export const canaryDeploymentService = new CanaryDeploymentService(defaultCanaryConfig);
