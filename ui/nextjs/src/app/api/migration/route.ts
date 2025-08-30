import { NextRequest, NextResponse } from 'next/server'
import { databaseMigrationService } from '@/lib/database-migration'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action')

    switch (action) {
      case 'status':
        const status = await databaseMigrationService.getMigrationStatus()
        return NextResponse.json({ success: true, data: status })

      case 'progress':
        const progress = await databaseMigrationService.getMigrationProgress()
        return NextResponse.json({ success: true, data: progress })

      case 'tables':
        const tables = await databaseMigrationService.getMigrationTables()
        return NextResponse.json({ success: true, data: tables })

      case 'validate':
        const tableName = searchParams.get('table')
        if (!tableName) {
          return NextResponse.json(
            { success: false, error: 'Table name is required for validation' },
            { status: 400 }
          )
        }
        const validation = await databaseMigrationService.validateDataConsistency(tableName)
        return NextResponse.json({ success: true, data: validation })

      case 'validate-all':
        const allValidations = await databaseMigrationService.validateAllTables()
        return NextResponse.json({ success: true, data: allValidations })

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action specified' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Migration API error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action')
    const body = await request.json()

    switch (action) {
      case 'start':
        const { tableName: startTable } = body
        if (!startTable) {
          return NextResponse.json(
            { success: false, error: 'Table name is required' },
            { status: 400 }
          )
        }
        const startStatus = await databaseMigrationService.startTableMigration(startTable)
        return NextResponse.json({ success: true, data: startStatus })

      case 'stop':
        const { tableName: stopTable } = body
        if (!stopTable) {
          return NextResponse.json(
            { success: false, error: 'Table name is required' },
            { status: 400 }
          )
        }
        const stopStatus = await databaseMigrationService.stopTableMigration(stopTable)
        return NextResponse.json({ success: true, data: stopStatus })

      case 'complete':
        const { tableName: completeTable } = body
        if (!completeTable) {
          return NextResponse.json(
            { success: false, error: 'Table name is required' },
            { status: 400 }
          )
        }
        const completeStatus = await databaseMigrationService.completeTableMigration(completeTable)
        return NextResponse.json({ success: true, data: completeStatus })

      case 'reset':
        const { tableName: resetTable } = body
        await databaseMigrationService.resetMigrationStatus(resetTable)
        return NextResponse.json({ success: true, message: 'Migration status reset successfully' })

      case 'dual-write':
        const { tableName, operation, data, where } = body
        if (!tableName || !operation || !data) {
          return NextResponse.json(
            { success: false, error: 'Table name, operation, and data are required' },
            { status: 400 }
          )
        }
        const dualWriteResult = await databaseMigrationService.performDualWrite(
          tableName,
          operation,
          data,
          where
        )
        return NextResponse.json({ success: true, data: dualWriteResult })

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action specified' },
          { status: 400 }
        )
    }
  } catch (error) {
    console.error('Migration API error:', error)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
