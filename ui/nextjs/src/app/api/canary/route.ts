import { NextRequest, NextResponse } from 'next/server';
import { canaryDeploymentService } from '../../../lib/canary-deployment';

/**
 * GET /api/canary - Get canary deployment status
 */
export async function GET(request: NextRequest) {
  try {
    const status = canaryDeploymentService.getStatus();
    const config = canaryDeploymentService.getConfig();
    
    return NextResponse.json({
      success: true,
      data: {
        status,
        config,
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    console.error('Error getting canary status:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to get canary status' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/canary - Control canary deployment
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, trafficPercentage, rollbackThreshold } = body;
    
    switch (action) {
      case 'start':
        await canaryDeploymentService.startCanary(trafficPercentage || 10);
        break;
        
      case 'increase':
        await canaryDeploymentService.increaseTraffic(trafficPercentage || 10);
        break;
        
      case 'rollback':
        await canaryDeploymentService.triggerRollback();
        break;
        
      case 'update-config':
        if (rollbackThreshold !== undefined) {
          canaryDeploymentService.updateConfig({ rollbackThreshold });
        }
        break;
        
      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action' },
          { status: 400 }
        );
    }
    
    const status = canaryDeploymentService.getStatus();
    
    return NextResponse.json({
      success: true,
      data: {
        action,
        status,
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    console.error('Error controlling canary deployment:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to control canary deployment' },
      { status: 500 }
    );
  }
}
