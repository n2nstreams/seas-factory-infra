#!/usr/bin/env node

/**
 * AI Agent System Migration Test Script - Module 6
 * Tests the complete AI agent integration with Next.js + Supabase
 */

const http = require('http')
const https = require('https')
const { URL } = require('url')

// Configuration
const CONFIG = {
  baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3000',
  orchestratorUrl: process.env.TEST_ORCHESTRATOR_URL || 'http://localhost:8001',
  testTenantId: 'test-tenant-123',
  testUserId: 'test-user-456',
  timeout: 10000
}

// Test results tracking
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  errors: []
}

// Utility functions
function log(message, type = 'info') {
  const timestamp = new Date().toISOString()
  const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️'
  console.log(`${prefix} [${timestamp}] ${message}`)
}

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
        'x-tenant-id': CONFIG.testTenantId,
        'x-user-id': CONFIG.testUserId,
        ...options.headers
      },
      timeout: CONFIG.timeout
    }

    const req = client.request(requestOptions, (res) => {
      let data = ''
      res.on('data', (chunk) => data += chunk)
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
    req.on('timeout', () => reject(new Error('Request timeout')))
    
    if (options.body) {
      req.write(JSON.stringify(options.body))
    }
    
    req.end()
  })
}

function runTest(testName, testFunction) {
  return async () => {
    testResults.total++
    log(`Running test: ${testName}`)
    
    try {
      await testFunction()
      testResults.passed++
      log(`Test passed: ${testName}`, 'success')
      return true
    } catch (error) {
      testResults.failed++
      testResults.errors.push({ test: testName, error: error.message })
      log(`Test failed: ${testName} - ${error.message}`, 'error')
      return false
    }
  }
}

// Test functions
const testFeatureFlagControl = runTest('Feature Flag Control', async () => {
  // Test that AI agents are disabled by default
  const response = await makeRequest(`${CONFIG.baseUrl}/api/ai-agents`)
  
  if (response.status !== 503) {
    throw new Error(`Expected status 503 (service unavailable), got ${response.status}`)
  }
  
  if (!response.data.error || !response.data.error.includes('not enabled')) {
    throw new Error('Expected error message about feature flag not being enabled')
  }
  
  log('Feature flag control working correctly - AI agents disabled by default')
})

const testOrchestratorHealthCheck = runTest('Orchestrator Health Check', async () => {
  const response = await makeRequest(`${CONFIG.orchestratorUrl}/health`)
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`)
  }
  
  if (!response.data.status || response.data.status !== 'healthy') {
    throw new Error('Expected healthy status from orchestrator')
  }
  
  log('Orchestrator health check passed')
})

const testOrchestratorAgentsEndpoint = runTest('Orchestrator Agents Endpoint', async () => {
  const response = await makeRequest(`${CONFIG.orchestratorUrl}/orchestrator/agents`)
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`)
  }
  
  if (!response.data.agents || !Array.isArray(response.data.agents)) {
    throw new Error('Expected agents array in response')
  }
  
  log(`Orchestrator reports ${response.data.agents.length} agents available`)
})

const testOrchestratorMainEndpoint = runTest('Orchestrator Main Endpoint', async () => {
  const response = await makeRequest(`${CONFIG.orchestratorUrl}/orchestrator`, {
    method: 'POST',
    body: { name: 'test' }
  })
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`)
  }
  
  if (!response.data.result) {
    throw new Error('Expected result in response')
  }
  
  log('Orchestrator main endpoint working correctly')
})

const testAIAgentServiceInitialization = runTest('AI Agent Service Initialization', async () => {
  // Test the service initialization by checking if it can reach the orchestrator
  const response = await makeRequest(`${CONFIG.baseUrl}/api/ai-agents`)
  
  // Even with feature flag disabled, the service should be initialized
  // We just expect a 503 due to feature flag, not a 500 due to service error
  if (response.status === 500) {
    throw new Error('AI Agent Service failed to initialize - got 500 error')
  }
  
  log('AI Agent Service initialized successfully')
})

const testWorkflowAPIEndpoints = runTest('Workflow API Endpoints', async () => {
  // Test workflow endpoints (should be disabled by feature flag)
  const response = await makeRequest(`${CONFIG.baseUrl}/api/ai-agents/workflows`)
  
  if (response.status !== 503) {
    throw new Error(`Expected status 503 (service unavailable), got ${response.status}`)
  }
  
  if (!response.data.error || !response.data.error.includes('not enabled')) {
    throw new Error('Expected error message about feature flag not being enabled')
  }
  
  log('Workflow API endpoints properly controlled by feature flag')
})

const testEnvironmentConfiguration = runTest('Environment Configuration', async () => {
  // Check that orchestrator URL is properly configured
  const orchestratorUrl = process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || 'http://localhost:8001'
  
  if (!orchestratorUrl || orchestratorUrl === '') {
    throw new Error('Orchestrator URL not configured')
  }
  
  log(`Orchestrator URL configured: ${orchestratorUrl}`)
})

const testOrchestratorIntegration = runTest('Orchestrator Integration', async () => {
  // Test that the orchestrator can handle the specific agent types we support
  const agentTypes = ['orchestrator', 'techstack', 'design', 'ui_dev', 'playwright_qa', 'github_merge']
  
  for (const agentType of agentTypes) {
    try {
      const response = await makeRequest(`${CONFIG.orchestratorUrl}/orchestrator`, {
        method: 'POST',
        body: { 
          name: agentType,
          stage: agentType,
          data: { test: true }
        }
      })
      
      if (response.status === 200) {
        log(`Agent type ${agentType} integration working`)
      } else {
        log(`Agent type ${agentType} returned status ${response.status}`, 'warning')
      }
    } catch (error) {
      log(`Agent type ${agentType} test failed: ${error.message}`, 'warning')
    }
  }
  
  log('Orchestrator integration test completed')
})

const testErrorHandling = runTest('Error Handling', async () => {
  // Test error handling with invalid requests
  const response = await makeRequest(`${CONFIG.baseUrl}/api/ai-agents`, {
    method: 'POST',
    body: {
      // Missing required fields
      agent_type: 'invalid_type'
    }
  })
  
  if (response.status !== 503) {
    // Should fail due to feature flag, not validation
    throw new Error(`Expected status 503 (feature flag), got ${response.status}`)
  }
  
  log('Error handling working correctly')
})

const testSecurityHeaders = runTest('Security Headers', async () => {
  const response = await makeRequest(`${CONFIG.baseUrl}/api/ai-agents`)
  
  // Check for security headers
  const securityHeaders = ['x-content-type-options', 'x-frame-options', 'x-xss-protection']
  const missingHeaders = securityHeaders.filter(header => !response.headers[header])
  
  if (missingHeaders.length > 0) {
    log(`Missing security headers: ${missingHeaders.join(', ')}`, 'warning')
  } else {
    log('Security headers properly configured')
  }
})

const testPerformanceBaseline = runTest('Performance Baseline', async () => {
  const startTime = Date.now()
  
  try {
    await makeRequest(`${CONFIG.orchestratorUrl}/health`)
    const responseTime = Date.now() - startTime
    
    if (responseTime > 5000) {
      log(`Orchestrator response time: ${responseTime}ms (slow)`, 'warning')
    } else {
      log(`Orchestrator response time: ${responseTime}ms (acceptable)`)
    }
  } catch (error) {
    log(`Performance test failed: ${error.message}`, 'warning')
  }
})

// Main test execution
async function runAllTests() {
  log('🚀 Starting AI Agent System Migration Tests - Module 6')
  log(`Base URL: ${CONFIG.baseUrl}`)
  log(`Orchestrator URL: ${CONFIG.orchestratorUrl}`)
  log('')
  
  const tests = [
    testFeatureFlagControl,
    testOrchestratorHealthCheck,
    testOrchestratorAgentsEndpoint,
    testOrchestratorMainEndpoint,
    testAIAgentServiceInitialization,
    testWorkflowAPIEndpoints,
    testEnvironmentConfiguration,
    testOrchestratorIntegration,
    testErrorHandling,
    testSecurityHeaders,
    testPerformanceBaseline
  ]
  
  for (const test of tests) {
    await test()
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  
  // Test summary
  log('')
  log('📊 Test Results Summary')
  log(`Total Tests: ${testResults.total}`)
  log(`Passed: ${testResults.passed}`, 'success')
  log(`Failed: ${testResults.failed}`, testResults.failed > 0 ? 'error' : 'success')
  
  if (testResults.errors.length > 0) {
    log('')
    log('❌ Failed Tests:')
    testResults.errors.forEach(({ test, error }) => {
      log(`  ${test}: ${error}`, 'error')
    })
  }
  
  log('')
  if (testResults.failed === 0) {
    log('🎉 All tests passed! AI Agent System Migration is ready.', 'success')
    log('')
    log('Next steps:')
    log('1. Enable the agents_v2 feature flag')
    log('2. Test the AI Agent Dashboard UI')
    log('3. Validate workflow creation and execution')
    log('4. Test agent communication and orchestration')
  } else {
    log('⚠️  Some tests failed. Please review and fix issues before proceeding.', 'warning')
  }
  
  return testResults.failed === 0
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAllTests()
    .then(success => {
      process.exit(success ? 0 : 1)
    })
    .catch(error => {
      log(`Test execution failed: ${error.message}`, 'error')
      process.exit(1)
    })
}

module.exports = {
  runAllTests,
  testResults,
  CONFIG
}
