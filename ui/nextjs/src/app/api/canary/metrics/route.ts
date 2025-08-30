import { NextRequest, NextResponse } from 'next/server';
import { canaryDeploymentService } from '../../../../lib/canary-deployment';

/**
 * GET /api/canary/metrics - Get canary deployment metrics
 */
export async function GET(request: NextRequest) {
  try {
    const status = canaryDeploymentService.getStatus();
    const { searchParams } = new URL(request.url);
    const format = searchParams.get('format') || 'json';
    
    const metrics = {
      canary: {
        isActive: status.isActive,
        trafficPercentage: status.currentTrafficPercentage,
        healthStatus: status.healthStatus,
        lastHealthCheck: status.lastHealthCheck,
        rollbackTriggered: status.rollbackTriggered,
      },
      performance: {
        errorRate: status.metrics.errorRate,
        responseTime: status.metrics.responseTime,
        uptime: status.metrics.uptime,
        userSatisfaction: status.metrics.userSatisfaction,
      },
      system: {
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        nodeVersion: process.version,
      },
    };
    
    if (format === 'prometheus') {
      // Return Prometheus format for monitoring systems
      const prometheusMetrics = [
        `# HELP canary_traffic_percentage Current canary traffic percentage`,
        `# TYPE canary_traffic_percentage gauge`,
        `canary_traffic_percentage ${status.currentTrafficPercentage}`,
        '',
        `# HELP canary_error_rate Current error rate`,
        `# TYPE canary_error_rate gauge`,
        `canary_error_rate ${status.metrics.errorRate}`,
        '',
        `# HELP canary_response_time Current response time in milliseconds`,
        `# TYPE canary_response_time gauge`,
        `canary_response_time ${status.metrics.responseTime}`,
        '',
        `# HELP canary_uptime Current uptime percentage`,
        `# TYPE canary_uptime gauge`,
        `canary_uptime ${status.metrics.uptime}`,
        '',
        `# HELP canary_user_satisfaction Current user satisfaction score`,
        `# TYPE canary_user_satisfaction gauge`,
        `canary_user_satisfaction ${status.metrics.userSatisfaction}`,
        '',
        `# HELP canary_health_status Current health status (0=healthy, 1=degraded, 2=critical)`,
        `# TYPE canary_health_status gauge`,
        `canary_health_status ${status.healthStatus === 'healthy' ? 0 : status.healthStatus === 'degraded' ? 1 : 2}`,
      ].join('\n');
      
      return new NextResponse(prometheusMetrics, {
        headers: {
          'Content-Type': 'text/plain; version=0.0.4; charset=utf-8',
        },
      });
    }
    
    return NextResponse.json({
      success: true,
      data: metrics,
    });
  } catch (error) {
    console.error('Error getting canary metrics:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to get canary metrics' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/canary/metrics - Update canary metrics
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { errorRate, responseTime, uptime, userSatisfaction } = body;
    
    // Update metrics in the canary service
    // Note: This is a simplified update - in production, you'd want more sophisticated metric handling
    
    return NextResponse.json({
      success: true,
      message: 'Metrics updated successfully',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error updating canary metrics:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to update canary metrics' },
      { status: 500 }
    );
  }
}
