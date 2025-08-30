#!/usr/bin/env node

/**
 * Backend Migration Test Script
 * Tests all the new Next.js API routes to ensure they're working correctly
 */

const http = require('http')
const https = require('https')

// Configuration
const config = {
  baseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL || 'http://localhost:3000',
  tenantId: process.env.TEST_TENANT_ID || '550e8400-e29b-41d4-a716-446655440000',
  userId: process.env.TEST_USER_ID || '550e8400-e29b-41d4-a716-446655440001',
  userRole: process.env.TEST_USER_ROLE || 'admin',
  timeout: 10000
}

// Test results
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  details: []
}

// Helper function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url)
    const isHttps = urlObj.protocol === 'https:'
    const client = isHttps ? https : http
    
    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': config.tenantId,
        'X-User-ID': config.userId,
        'X-User-Role': config.userRole,
        ...options.headers
      },
      timeout: config.timeout
    }

    const req = client.request(requestOptions, (res) => {
      let data = ''
      res.on('data', (chunk) => {
        data += chunk
      })
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data)
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: jsonData
          })
        } catch (error) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data
          })
        }
      })
    })

    req.on('error', reject)
    req.on('timeout', () => {
      req.destroy()
      reject(new Error('Request timeout'))
    })

    if (options.body) {
      req.write(JSON.stringify(options.body))
    }
    
    req.end()
  })
}

// Test functions
async function testHealthEndpoint() {
  try {
    const response = await makeRequest(`${config.baseUrl}/api/health`)
    return {
      name: 'Health Endpoint',
      passed: response.status === 200,
      status: response.status,
      data: response.data
    }
  } catch (error) {
    return {
      name: 'Health Endpoint',
      passed: false,
      error: error.message
    }
  }
}

async function testUsersAPI() {
  try {
    // Test GET /api/users
    const getResponse = await makeRequest(`${config.baseUrl}/api/users`)
    const getPassed = getResponse.status === 200

    // Test POST /api/users
    const postResponse = await makeRequest(`${config.baseUrl}/api/users`, {
      method: 'POST',
      body: {
        email: 'test@example.com',
        name: 'Test User',
        role: 'user'
      }
    })
    const postPassed = postResponse.status === 201

    return {
      name: 'Users API',
      passed: getPassed && postPassed,
      details: {
        get: { passed: getPassed, status: getResponse.status },
        post: { passed: postPassed, status: postResponse.status }
      }
    }
  } catch (error) {
    return {
      name: 'Users API',
      passed: false,
      error: error.message
    }
  }
}

async function testPrivacyAPI() {
  try {
    // Test GET /api/privacy
    const getResponse = await makeRequest(`${config.baseUrl}/api/privacy`)
    const getPassed = getResponse.status === 200

    // Test POST /api/privacy
    const postResponse = await makeRequest(`${config.baseUrl}/api/privacy`, {
      method: 'POST',
      body: {
        consent_type: 'gdpr',
        consent_given: true
      }
    })
    const postPassed = postResponse.status === 200

    return {
      name: 'Privacy API',
      passed: getPassed && postPassed,
      details: {
        get: { passed: getPassed, status: getResponse.status },
        post: { passed: postPassed, status: postResponse.status }
      }
    }
  } catch (error) {
    return {
      name: 'Privacy API',
      passed: false,
      error: error.message
    }
  }
}

async function testAdminAPI() {
  try {
    const response = await makeRequest(`${config.baseUrl}/api/admin`)
    return {
      name: 'Admin API',
      passed: response.status === 200,
      status: response.status,
      data: response.data
    }
  } catch (error) {
    return {
      name: 'Admin API',
      passed: false,
      error: error.message
    }
  }
}

async function testIdeasAPI() {
  try {
    // Test GET /api/ideas
    const getResponse = await makeRequest(`${config.baseUrl}/api/ideas`)
    const getPassed = getResponse.status === 200

    // Test POST /api/ideas
    const postResponse = await makeRequest(`${config.baseUrl}/api/ideas`, {
      method: 'POST',
      body: {
        project_name: 'Test Project',
        description: 'Test Description',
        problem: 'Test Problem',
        solution: 'Test Solution'
      }
    })
    const postPassed = postResponse.status === 201

    return {
      name: 'Ideas API',
      passed: getPassed && postPassed,
      details: {
        get: { passed: getPassed, status: getResponse.status },
        post: { passed: postPassed, status: postResponse.status }
      }
    }
  } catch (error) {
    return {
      name: 'Ideas API',
      passed: false,
      error: error.message
    }
  }
}

async function testProjectsAPI() {
  try {
    // Test GET /api/projects
    const getResponse = await makeRequest(`${config.baseUrl}/api/projects`)
    const getPassed = getResponse.status === 200

    // Test POST /api/projects
    const postResponse = await makeRequest(`${config.baseUrl}/api/projects`, {
      method: 'POST',
      body: {
        name: 'Test Project',
        description: 'Test Description',
        project_type: 'web'
      }
    })
    const postPassed = postResponse.status === 201

    return {
      name: 'Projects API',
      passed: getPassed && postPassed,
      details: {
        get: { passed: getPassed, status: getResponse.status },
        post: { passed: postPassed, status: postResponse.status }
      }
    }
  } catch (error) {
    return {
      name: 'Projects API',
      passed: false,
      error: error.message
    }
  }
}

async function testWebSocketAPI() {
  try {
    const response = await makeRequest(`${config.baseUrl}/api/websocket`)
    return {
      name: 'WebSocket API',
      passed: response.status === 200,
      status: response.status,
      data: response.data
    }
  } catch (error) {
    return {
      name: 'WebSocket API',
      passed: false,
      error: error.message
    }
  }
}

async function testMigrationStatus() {
  try {
    const response = await makeRequest(`${config.baseUrl}/api/migration/status`)
    return {
      name: 'Migration Status API',
      passed: response.status === 200,
      status: response.status,
      data: response.data
    }
  } catch (error) {
    return {
      name: 'Migration Status API',
      passed: false,
      error: error.message
    }
  }
}

// Main test runner
async function runTests() {
  console.log('🚀 Starting Backend Migration Tests...\n')
  console.log(`Base URL: ${config.baseUrl}`)
  console.log(`Tenant ID: ${config.tenantId}`)
  console.log(`User ID: ${config.userId}`)
  console.log(`User Role: ${config.userRole}\n`)

  const tests = [
    testHealthEndpoint,
    testUsersAPI,
    testPrivacyAPI,
    testAdminAPI,
    testIdeasAPI,
    testProjectsAPI,
    testWebSocketAPI,
    testMigrationStatus
  ]

  for (const test of tests) {
    try {
      const result = await test()
      testResults.total++
      
      if (result.passed) {
        testResults.passed++
        console.log(`✅ ${result.name}: PASSED`)
      } else {
        testResults.failed++
        console.log(`❌ ${result.name}: FAILED`)
        if (result.error) {
          console.log(`   Error: ${result.error}`)
        }
        if (result.details) {
          Object.entries(result.details).forEach(([key, value]) => {
            console.log(`   ${key}: ${value.passed ? 'PASSED' : 'FAILED'} (${value.status})`)
          })
        }
      }
      
      testResults.details.push(result)
    } catch (error) {
      testResults.total++
      testResults.failed++
      console.log(`❌ ${test.name}: ERROR - ${error.message}`)
    }
  }

  // Print summary
  console.log('\n📊 Test Results Summary')
  console.log('========================')
  console.log(`Total Tests: ${testResults.total}`)
  console.log(`Passed: ${testResults.passed}`)
  console.log(`Failed: ${testResults.failed}`)
  console.log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`)

  if (testResults.failed > 0) {
    console.log('\n❌ Failed Tests:')
    testResults.details
      .filter(result => !result.passed)
      .forEach(result => {
        console.log(`   - ${result.name}`)
      })
    process.exit(1)
  } else {
    console.log('\n🎉 All tests passed! Backend migration is working correctly.')
    process.exit(0)
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  runTests().catch(error => {
    console.error('Test runner error:', error)
    process.exit(1)
  })
}

module.exports = {
  runTests,
  testResults
}
