#!/usr/bin/env node

/**
 * Module 5: Health Monitoring & Environment Configuration Cleanup
 * Comprehensive testing script to validate the module implementation
 */

const https = require('https');
const http = require('http');

// Configuration
const CONFIG = {
  baseUrl: process.env.TEST_BASE_URL || 'http://localhost:3000',
  timeout: 10000,
  retries: 3,
  testTenantId: 'test-tenant-module5'
};

// Test results tracking
const testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  errors: [],
  startTime: new Date(),
  endTime: null
};

// Utility functions
function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : type === 'warning' ? '⚠️' : 'ℹ️';
  console.log(`[${timestamp}] ${prefix} ${message}`);
}

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const isHttps = url.startsWith('https://');
    const client = isHttps ? https : http;
    
    const requestOptions = {
      timeout: CONFIG.timeout,
      ...options
    };

    const req = client.request(url, requestOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: jsonData,
            rawData: data
          });
        } catch (error) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: null,
            rawData: data
          });
        }
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

async function testWithRetry(testFn, testName, maxRetries = CONFIG.retries) {
  testResults.total++;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      await testFn();
      testResults.passed++;
      log(`PASS: ${testName}`, 'success');
      return true;
    } catch (error) {
      if (attempt === maxRetries) {
        testResults.failed++;
        testResults.errors.push({
          test: testName,
          error: error.message,
          attempt
        });
        log(`FAIL: ${testName} - ${error.message}`, 'error');
        return false;
      }
      log(`Attempt ${attempt} failed for ${testName}, retrying...`, 'warning');
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

// Test functions
async function testHealthEndpoint() {
  const response = await makeRequest(`${CONFIG.baseUrl}/api/health`);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!response.data || typeof response.data !== 'object') {
    throw new Error('Response data is not a valid JSON object');
  }
  
  // Validate required fields
  const requiredFields = ['status', 'timestamp', 'checks', 'summary'];
  for (const field of requiredFields) {
    if (!(field in response.data)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  // Validate health check structure
  if (!response.data.checks || typeof response.data.checks !== 'object') {
    throw new Error('Health checks object is missing or invalid');
  }
  
  // Validate summary structure
  if (!response.data.summary || typeof response.data.summary !== 'object') {
    throw new Error('Health summary object is missing or invalid');
  }
  
  log(`Health endpoint response: ${JSON.stringify(response.data, null, 2)}`);
}

async function testHealthEndpointHeaders() {
  const response = await makeRequest(`${CONFIG.baseUrl}/api/health`, {
    method: 'HEAD'
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200 for HEAD request, got ${response.status}`);
  }
  
  // Check for health status header
  const healthStatus = response.headers['x-health-status'];
  if (!healthStatus) {
    throw new Error('Missing X-Health-Status header');
  }
  
  log(`Health HEAD response headers: ${JSON.stringify(response.headers, null, 2)}`);
}

async function testMigrationStatusEndpoint() {
  const response = await makeRequest(`${CONFIG.baseUrl}/api/migration/status`, {
    method: 'GET',
    headers: {
      'X-Tenant-ID': CONFIG.testTenantId
    }
  });
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`);
  }
  
  if (!response.data || !response.data.success) {
    throw new Error('Migration status response indicates failure');
  }
  
  // Validate required fields
  const requiredFields = ['migration', 'infrastructure', 'api_endpoints', 'recommendations'];
  for (const field of requiredFields) {
    if (!(field in response.data)) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  // Check that legacy backend is permanently disabled
  if (response.data.infrastructure.legacy_backend !== 'permanently_disabled') {
    throw new Error(`Expected legacy_backend to be 'permanently_disabled', got '${response.data.infrastructure.legacy_backend}'`);
  }
  
  // Check Module 5 status
  if (response.data.infrastructure.module_5_status !== 'implementing') {
    throw new Error(`Expected module_5_status to be 'implementing', got '${response.data.infrastructure.module_5_status}'`);
  }
  
  log(`Migration status response: ${JSON.stringify(response.data, null, 2)}`);
}

async function testHealthDashboardPage() {
  const response = await makeRequest(`${CONFIG.baseUrl}/app2/health`);
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200 for health dashboard page, got ${response.status}`);
  }
  
  // Check if the page contains expected content
  if (!response.rawData.includes('Health Monitoring Dashboard')) {
    throw new Error('Health dashboard page does not contain expected content');
  }
  
  if (!response.rawData.includes('Module 5: Health Monitoring & Environment Configuration Cleanup')) {
    throw new Error('Health dashboard page does not contain Module 5 information');
  }
  
  log('Health dashboard page loads successfully');
}

async function testNoLegacyReferences() {
  // Test that health endpoint doesn't reference legacy systems
  const response = await makeRequest(`${CONFIG.baseUrl}/api/health`);
  
  if (response.data) {
    const responseStr = JSON.stringify(response.data);
    
    // Check for legacy references
    const legacyPatterns = [
      'localhost:8000',
      'legacy',
      'fastapi',
      'postgresql'
    ];
    
    for (const pattern of legacyPatterns) {
      if (responseStr.toLowerCase().includes(pattern.toLowerCase())) {
        throw new Error(`Found legacy reference in health response: ${pattern}`);
      }
    }
  }
  
  log('No legacy references found in health endpoint');
}

async function testEnvironmentConfiguration() {
  // Test that environment variables are properly configured
  const response = await makeRequest(`${CONFIG.baseUrl}/api/health`);
  
  if (response.status !== 200) {
    throw new Error('Health endpoint not accessible for environment testing');
  }
  
  // Check that the response indicates proper configuration
  if (response.data && response.data.checks) {
    const checks = response.data.checks;
    
    // Verify that health checks are using local endpoints
    for (const [name, check] of Object.entries(checks)) {
      if (name === 'backend-api' && check.status === 'fail') {
        throw new Error('Backend API health check is failing - environment may not be properly configured');
      }
    }
  }
  
  log('Environment configuration appears correct');
}

async function testFeatureFlags() {
  // Test that feature flags are working
  const response = await makeRequest(`${CONFIG.baseUrl}/api/migration/status`, {
    method: 'GET',
    headers: {
      'X-Tenant-ID': CONFIG.testTenantId
    }
  });
  
  if (response.status !== 200 || !response.data.success) {
    throw new Error('Cannot test feature flags - migration status endpoint not accessible');
  }
  
  // Check that feature flags are present
  if (!response.data.migration || !response.data.migration.feature_flags) {
    throw new Error('Feature flags not found in migration status response');
  }
  
  const featureFlags = response.data.migration.feature_flags;
  
  // Log feature flag status
  log(`Feature flags status: ${JSON.stringify(featureFlags, null, 2)}`);
  
  log('Feature flags are properly configured');
}

async function testPerformanceMetrics() {
  const startTime = Date.now();
  const response = await makeRequest(`${CONFIG.baseUrl}/api/health`);
  const endTime = Date.now();
  
  const responseTime = endTime - startTime;
  
  if (responseTime > 5000) {
    throw new Error(`Health endpoint response time too slow: ${responseTime}ms`);
  }
  
  if (response.data && response.data.responseTime) {
    log(`Health endpoint response time: ${response.data.responseTime}ms (measured: ${responseTime}ms)`);
  } else {
    log(`Health endpoint response time: ${responseTime}ms`);
  }
  
  log('Performance metrics are acceptable');
}

// Main test execution
async function runTests() {
  log('🚀 Starting Module 5: Health Monitoring & Environment Configuration Cleanup Tests');
  log(`Testing against: ${CONFIG.baseUrl}`);
  log(`Test tenant ID: ${CONFIG.testTenantId}`);
  log('');
  
  const tests = [
    { name: 'Health Endpoint Basic Functionality', fn: testHealthEndpoint },
    { name: 'Health Endpoint Headers', fn: testHealthEndpointHeaders },
    { name: 'Migration Status Endpoint', fn: testMigrationStatusEndpoint },
    { name: 'Health Dashboard Page', fn: testHealthDashboardPage },
    { name: 'No Legacy References', fn: testNoLegacyReferences },
    { name: 'Environment Configuration', fn: testEnvironmentConfiguration },
    { name: 'Feature Flags Configuration', fn: testFeatureFlags },
    { name: 'Performance Metrics', fn: testPerformanceMetrics }
  ];
  
  for (const test of tests) {
    await testWithRetry(test.fn, test.name);
    log(''); // Add spacing between tests
  }
  
  // Generate test report
  testResults.endTime = new Date();
  const duration = testResults.endTime - testResults.startTime;
  
  log('📊 Test Results Summary');
  log('='.repeat(50));
  log(`Total Tests: ${testResults.total}`);
  log(`Passed: ${testResults.passed} ✅`);
  log(`Failed: ${testResults.failed} ❌`);
  log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);
  log(`Duration: ${duration}ms`);
  
  if (testResults.errors.length > 0) {
    log('');
    log('❌ Failed Tests:');
    testResults.errors.forEach(error => {
      log(`  - ${error.test}: ${error.error}`, 'error');
    });
  }
  
  if (testResults.failed === 0) {
    log('');
    log('🎉 All tests passed! Module 5 is ready for production.', 'success');
    process.exit(0);
  } else {
    log('');
    log('⚠️  Some tests failed. Please review and fix the issues.', 'warning');
    process.exit(1);
  }
}

// Error handling
process.on('unhandledRejection', (reason, promise) => {
  log(`Unhandled Rejection at: ${promise}, reason: ${reason}`, 'error');
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  log(`Uncaught Exception: ${error.message}`, 'error');
  process.exit(1);
});

// Run tests if this script is executed directly
if (require.main === module) {
  runTests().catch(error => {
    log(`Test execution failed: ${error.message}`, 'error');
    process.exit(1);
  });
}

module.exports = {
  runTests,
  testResults,
  CONFIG
};
