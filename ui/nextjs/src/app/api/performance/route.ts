import { NextRequest, NextResponse } from 'next/server'
import { performanceMonitoring } from '@/lib/performance-monitoring'

export async function GET(request: NextRequest) {
  try {
    // Get performance summary
    const summary = performanceMonitoring.getPerformanceSummary()
    
    return NextResponse.json({
      success: true,
      data: summary
    })
  } catch (error) {
    console.error('Error fetching performance data:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch performance data' 
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, ...params } = body

    switch (action) {
      case 'start_monitoring':
        await performanceMonitoring.startMonitoring()
        return NextResponse.json({ success: true, message: 'Monitoring started' })

      case 'stop_monitoring':
        performanceMonitoring.stopMonitoring()
        return NextResponse.json({ success: true, message: 'Monitoring stopped' })

      case 'start_load_test':
        const testId = await performanceMonitoring.startLoadTest(params)
        return NextResponse.json({ success: true, testId })

      case 'cancel_load_test':
        const cancelled = performanceMonitoring.cancelLoadTest(params.testId)
        return NextResponse.json({ 
          success: true, 
          cancelled,
          message: cancelled ? 'Test cancelled' : 'Test not found or already completed'
        })

      case 'acknowledge_alert':
        const acknowledged = performanceMonitoring.acknowledgeCostAlert(params.alertId)
        return NextResponse.json({ 
          success: true, 
          acknowledged,
          message: acknowledged ? 'Alert acknowledged' : 'Alert not found'
        })

      case 'update_cost_data':
        performanceMonitoring.updateCostData(params.service, params.spend)
        return NextResponse.json({ success: true, message: 'Cost data updated' })

      case 'update_config':
        performanceMonitoring.updateConfig(params.config)
        return NextResponse.json({ success: true, message: 'Configuration updated' })

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Error processing performance action:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to process performance action' 
      },
      { status: 500 }
    )
  }
}
