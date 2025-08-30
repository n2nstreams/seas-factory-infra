#!/usr/bin/env node

/**
 * WebSocket Testing Script
 * Tests WebSocket functionality and API endpoints
 */

const WebSocket = require('ws')
const fetch = require('node-fetch')

// Configuration
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000'
const WS_URL = process.env.WS_URL || 'ws://localhost:3000/ws'
const TENANT_ID = 'test-tenant-123'
const USER_ID = 'test-user-456'

// Test results
let testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  details: []
}

// Helper functions
function log(message, type = 'info') {
  const timestamp = new Date().toISOString()
  const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️'
  console.log(`${prefix} [${timestamp}] ${message}`)
}

function addTestResult(name, passed, details = '') {
  testResults.total++
  if (passed) {
    testResults.passed++
    log(`PASS: ${name}`, 'success')
  } else {
    testResults.failed++
    log(`FAIL: ${name}`, 'error')
  }
  testResults.details.push({ name, passed, details })
}

// Test WebSocket API endpoints
async function testWebSocketAPI() {
  log('Testing WebSocket API endpoints...')
  
  try {
    // Test GET /api/websocket
    const response = await fetch(`${BASE_URL}/api/websocket`, {
      method: 'GET',
      headers: {
        'X-Tenant-ID': TENANT_ID,
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      addTestResult('GET /api/websocket', true, `Status: ${response.status}`)
      
      // Validate response structure
      if (data.websocket && data.websocket.nextjs) {
        addTestResult('WebSocket API response structure', true, 'Response contains expected fields')
      } else {
        addTestResult('WebSocket API response structure', false, 'Missing expected fields')
      }
    } else {
      addTestResult('GET /api/websocket', false, `Status: ${response.status}`)
    }
  } catch (error) {
    addTestResult('GET /api/websocket', false, error.message)
  }
  
  try {
    // Test POST /api/websocket
    const response = await fetch(`${BASE_URL}/api/websocket`, {
      method: 'POST',
      headers: {
        'X-Tenant-ID': TENANT_ID,
        'X-User-ID': USER_ID,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        channel: `tenant:${TENANT_ID}`,
        event: 'test_event',
        payload: { message: 'Test message from API' },
        source: 'test_script',
        priority: 'normal'
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      addTestResult('POST /api/websocket', true, `Status: ${response.status}`)
      
      // Validate response structure
      if (data.websocket && data.websocket.clients_reached !== undefined) {
        addTestResult('WebSocket POST response structure', true, 'Response contains expected fields')
      } else {
        addTestResult('WebSocket POST response structure', false, 'Missing expected fields')
      }
    } else {
      addTestResult('POST /api/websocket', false, `Status: ${response.status}`)
    }
  } catch (error) {
    addTestResult('POST /api/websocket', false, error.message)
  }
  
  try {
    // Test GET /api/websocket/status
    const response = await fetch(`${BASE_URL}/api/websocket/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      addTestResult('GET /api/websocket/status', true, `Status: ${response.status}`)
      
      // Validate response structure
      if (data.websocket && data.websocket.server_running !== undefined) {
        addTestResult('WebSocket status response structure', true, 'Response contains expected fields')
      } else {
        addTestResult('WebSocket status response structure', false, 'Missing expected fields')
      }
    } else {
      addTestResult('GET /api/websocket/status', false, `Status: ${response.status}`)
    }
  } catch (error) {
    addTestResult('GET /api/websocket/status', false, error.message)
  }
}

// Test WebSocket connection
function testWebSocketConnection() {
  return new Promise((resolve) => {
    log('Testing WebSocket connection...')
    
    const ws = new WebSocket(`${WS_URL}?tenant_id=${TENANT_ID}&user_id=${USER_ID}`)
    let connectionTested = false
    let messageTested = false
    let filterTested = false
    
    const timeout = setTimeout(() => {
      if (!connectionTested) {
        addTestResult('WebSocket connection', false, 'Connection timeout')
      }
      if (!messageTested) {
        addTestResult('WebSocket message handling', false, 'Message timeout')
      }
      if (!filterTested) {
        addTestResult('WebSocket filter update', false, 'Filter timeout')
      }
      ws.close()
      resolve()
    }, 10000)
    
    ws.on('open', () => {
      log('WebSocket connected successfully')
      addTestResult('WebSocket connection', true, 'Connection established')
      connectionTested = true
      
      // Test sending a message
      ws.send(JSON.stringify({
        type: 'ping',
        data: { timestamp: new Date().toISOString() }
      }))
      
      // Test updating filters
      ws.send(JSON.stringify({
        type: 'filters',
        filters: {
          eventTypes: ['test', 'ping'],
          sources: ['test_script']
        }
      }))
    })
    
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString())
        log(`Received message: ${message.eventType}`)
        
        if (message.eventType === 'pong') {
          addTestResult('WebSocket message handling', true, 'Received pong response')
          messageTested = true
        }
        
        if (message.eventType === 'connection') {
          addTestResult('WebSocket welcome message', true, 'Received welcome message')
        }
        
        // Close connection after receiving expected messages
        if (messageTested && connectionTested) {
          clearTimeout(timeout)
          ws.close()
          resolve()
        }
      } catch (error) {
        log(`Failed to parse message: ${error.message}`, 'error')
      }
    })
    
    ws.on('error', (error) => {
      log(`WebSocket error: ${error.message}`, 'error')
      addTestResult('WebSocket connection', false, error.message)
      clearTimeout(timeout)
      resolve()
    })
    
    ws.on('close', () => {
      log('WebSocket connection closed')
      if (!connectionTested) {
        addTestResult('WebSocket connection', false, 'Connection closed unexpectedly')
      }
    })
  })
}

// Test WebSocket with different query parameters
function testWebSocketQueryParams() {
  return new Promise((resolve) => {
    log('Testing WebSocket with query parameters...')
    
    const ws = new WebSocket(`${WS_URL}?tenant_id=${TENANT_ID}&user_id=${USER_ID}&event_types=test,ping`)
    
    const timeout = setTimeout(() => {
      addTestResult('WebSocket query parameters', false, 'Query parameter test timeout')
      ws.close()
      resolve()
    }, 5000)
    
    ws.on('open', () => {
      addTestResult('WebSocket query parameters', true, 'Connection with query parameters established')
      clearTimeout(timeout)
      ws.close()
      resolve()
    })
    
    ws.on('error', (error) => {
      addTestResult('WebSocket query parameters', false, error.message)
      clearTimeout(timeout)
      resolve()
    })
  })
}

// Test WebSocket message broadcasting
async function testWebSocketBroadcasting() {
  log('Testing WebSocket message broadcasting...')
  
  try {
    // Send a test event via API
    const response = await fetch(`${BASE_URL}/api/websocket`, {
      method: 'POST',
      headers: {
        'X-Tenant-ID': TENANT_ID,
        'X-User-ID': USER_ID,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        channel: `tenant:${TENANT_ID}`,
        event: 'broadcast_test',
        payload: { message: 'Broadcast test message' },
        source: 'test_script',
        priority: 'high'
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      addTestResult('WebSocket broadcasting', true, `Message sent, clients reached: ${data.websocket.clients_reached}`)
    } else {
      addTestResult('WebSocket broadcasting', false, `Status: ${response.status}`)
    }
  } catch (error) {
    addTestResult('WebSocket broadcasting', false, error.message)
  }
}

// Main test function
async function runTests() {
  log('Starting WebSocket functionality tests...')
  log(`Base URL: ${BASE_URL}`)
  log(`WebSocket URL: ${WS_URL}`)
  log(`Tenant ID: ${TENANT_ID}`)
  log(`User ID: ${USER_ID}`)
  
  // Run tests
  await testWebSocketAPI()
  await testWebSocketConnection()
  await testWebSocketQueryParams()
  await testWebSocketBroadcasting()
  
  // Print results
  log('\n' + '='.repeat(50))
  log('TEST RESULTS SUMMARY')
  log('='.repeat(50))
  log(`Total Tests: ${testResults.total}`)
  log(`Passed: ${testResults.passed}`)
  log(`Failed: ${testResults.failed}`)
  log(`Success Rate: ${testResults.total > 0 ? Math.round((testResults.passed / testResults.total) * 100) : 0}%`)
  
  if (testResults.failed > 0) {
    log('\nFAILED TESTS:')
    testResults.details
      .filter(test => !test.passed)
      .forEach(test => log(`- ${test.name}: ${test.details}`, 'error'))
  }
  
  if (testResults.passed > 0) {
    log('\nPASSED TESTS:')
    testResults.details
      .filter(test => test.passed)
      .forEach(test => log(`- ${test.name}: ${test.details}`, 'success'))
  }
  
  log('\n' + '='.repeat(50))
  
  // Exit with appropriate code
  process.exit(testResults.failed > 0 ? 1 : 0)
}

// Handle command line arguments
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log(`
WebSocket Testing Script

Usage: node test-websocket.js [options]

Options:
  --base-url <url>     Base URL for API testing (default: http://localhost:3000)
  --ws-url <url>       WebSocket URL for connection testing (default: ws://localhost:3000/ws)
  --tenant-id <id>     Tenant ID for testing (default: test-tenant-123)
  --user-id <id>       User ID for testing (default: test-user-456)
  --help, -h           Show this help message

Environment Variables:
  BASE_URL             Base URL for API testing
  WS_URL               WebSocket URL for connection testing
  TENANT_ID            Tenant ID for testing
  USER_ID              User ID for testing

Examples:
  node test-websocket.js
  node test-websocket.js --base-url http://localhost:3001
  BASE_URL=http://localhost:3001 node test-websocket.js
`)
  process.exit(0)
}

// Parse command line arguments
for (let i = 2; i < process.argv.length; i += 2) {
  const arg = process.argv[i]
  const value = process.argv[i + 1]
  
  switch (arg) {
    case '--base-url':
      process.env.BASE_URL = value
      break
    case '--ws-url':
      process.env.WS_URL = value
      break
    case '--tenant-id':
      process.env.TENANT_ID = value
      break
    case '--user-id':
      process.env.USER_ID = value
      break
  }
}

// Run tests
runTests().catch(error => {
  log(`Test execution failed: ${error.message}`, 'error')
  process.exit(1)
})
