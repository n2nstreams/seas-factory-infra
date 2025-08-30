#!/usr/bin/env node

/**
 * Module 4: Functionality Parity Validation Test Script
 * 
 * This script runs comprehensive functionality parity validation tests
 * to ensure 100% feature parity between legacy and new systems before decommission.
 * 
 * Usage:
 *   node scripts/test-parity-validation.js [options]
 * 
 * Options:
 *   --module <name>     Run specific test module only
 *   --tenant <id>       Specify tenant ID for testing
 *   --user <id>         Specify user ID for testing
 *   --role <role>       Specify user role for testing
 *   --verbose           Enable verbose output
 *   --report            Generate detailed report
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000',
  tenantId: process.env.TEST_TENANT_ID || 'test-tenant-001',
  userId: process.env.TEST_USER_ID || 'test-user-001',
  userRole: process.env.TEST_USER_ROLE || 'admin',
  timeout: 30000,
  retries: 3
};

// Test results storage
let testResults = {
  summary: {
    totalTests: 0,
    passedTests: 0,
    failedTests: 0,
    skippedTests: 0,
    successRate: 0,
    executionTime: 0
  },
  modules: [],
  timestamp: new Date().toISOString(),
  errors: []
};

// Utility functions
function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level}]`;
  console.log(`${prefix} ${message}`);
}

function logError(message, error = null) {
  log(message, 'ERROR');
  if (error) {
    console.error(error);
    testResults.errors.push({
      message,
      error: error instanceof Error ? error.message : String(error),
      timestamp: new Date().toISOString()
    });
  }
}

function logSuccess(message) {
  log(message, 'SUCCESS');
}

function logWarning(message) {
  log(message, 'WARN');
}

// HTTP request helper
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const isHttps = url.startsWith('https://');
    const client = isHttps ? https : http;
    
    const requestOptions = {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Tenant-ID': CONFIG.tenantId,
        'X-User-ID': CONFIG.userId,
        'X-User-Role': CONFIG.userRole,
        ...options.headers
      },
      timeout: CONFIG.timeout
    };

    if (options.body) {
      requestOptions.headers['Content-Length'] = Buffer.byteLength(options.body);
    }

    const req = client.request(url, requestOptions, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: jsonData
          });
        } catch (error) {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            data: data
          });
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

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

// Test runner
class ParityTestRunner {
  constructor() {
    this.startTime = Date.now();
  }

  async runAllTests() {
    log('🚀 Starting comprehensive functionality parity validation...');
    log(`📊 Testing tenant: ${CONFIG.tenantId}`);
    log(`👤 Testing user: ${CONFIG.userId} (${CONFIG.userRole})`);
    log(`🌐 Base URL: ${CONFIG.baseUrl}`);

    try {
      // Run comprehensive parity validation
      const results = await this.runComprehensiveValidation();
      
      // Calculate summary
      this.calculateSummary(results);
      
      // Display results
      this.displayResults();
      
      // Generate report if requested
      if (process.argv.includes('--report')) {
        this.generateReport();
      }
      
      // Return exit code
      return testResults.summary.failedTests === 0 ? 0 : 1;
      
    } catch (error) {
      logError('❌ Parity validation failed', error);
      return 1;
    }
  }

  async runComprehensiveValidation() {
    try {
      log('🔍 Running comprehensive parity validation...');
      
      const response = await makeRequest(`${CONFIG.baseUrl}/api/parity-validation`);
      
      if (response.statusCode === 200 && response.data.success) {
        logSuccess('✅ Comprehensive parity validation completed');
        return response.data.results;
      } else {
        throw new Error(`Parity validation failed: ${response.data.error || 'Unknown error'}`);
      }
      
    } catch (error) {
      logError('❌ Comprehensive parity validation failed', error);
      throw error;
    }
  }

  async runSpecificModule(moduleName) {
    try {
      log(`🔍 Running ${moduleName} test module...`);
      
      const response = await makeRequest(`${CONFIG.baseUrl}/api/parity-validation`, {
        method: 'POST',
        body: JSON.stringify({ module: moduleName })
      });
      
      if (response.statusCode === 200 && response.data.success) {
        logSuccess(`✅ ${moduleName} test module completed`);
        return response.data.results;
      } else {
        throw new Error(`${moduleName} test failed: ${response.data.error || 'Unknown error'}`);
      }
      
    } catch (error) {
      logError(`❌ ${moduleName} test module failed`, error);
      throw error;
    }
  }

  calculateSummary(results) {
    testResults.modules = results.modules || [];
    testResults.summary = results.summary || {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      skippedTests: 0,
      successRate: 0,
      executionTime: 0
    };
    testResults.executionTime = Date.now() - this.startTime;
  }

  displayResults() {
    console.log('\n' + '='.repeat(80));
    console.log('🎯 FUNCTIONALITY PARITY VALIDATION RESULTS');
    console.log('='.repeat(80));
    
    // Summary
    console.log('\n📊 SUMMARY');
    console.log(`   Total Tests: ${testResults.summary.totalTests}`);
    console.log(`   Passed: ${testResults.summary.passedTests} ✅`);
    console.log(`   Failed: ${testResults.summary.failedTests} ❌`);
    console.log(`   Skipped: ${testResults.summary.skippedTests} ⏭️`);
    console.log(`   Success Rate: ${testResults.summary.successRate}%`);
    console.log(`   Execution Time: ${testResults.executionTime}ms`);
    
    // Module results
    if (testResults.modules.length > 0) {
      console.log('\n🔧 MODULE RESULTS');
      testResults.modules.forEach(module => {
        const status = module.failed === 0 ? '✅' : '❌';
        console.log(`   ${status} ${module.name}: ${module.passed}/${module.total} passed`);
        
        if (process.argv.includes('--verbose') && module.tests.length > 0) {
          module.tests.forEach(test => {
            const testStatus = test.status === 'PASSED' ? '✅' : 
                             test.status === 'FAILED' ? '❌' : 
                             test.status === 'SKIPPED' ? '⏭️' : '⚠️';
            console.log(`     ${testStatus} ${test.test}`);
            if (test.status === 'FAILED' && test.error) {
              console.log(`       Error: ${test.error}`);
            }
          });
        }
      });
    }
    
    // Errors
    if (testResults.errors.length > 0) {
      console.log('\n❌ ERRORS');
      testResults.errors.forEach(error => {
        console.log(`   ${error.timestamp}: ${error.message}`);
        if (error.error) {
          console.log(`     ${error.error}`);
        }
      });
    }
    
    // Final status
    console.log('\n' + '='.repeat(80));
    if (testResults.summary.failedTests === 0) {
      console.log('🎉 ALL TESTS PASSED - FUNCTIONALITY PARITY ACHIEVED!');
      console.log('✅ Ready to proceed with legacy stack decommission');
    } else {
      console.log('⚠️  SOME TESTS FAILED - FUNCTIONALITY PARITY NOT ACHIEVED');
      console.log('❌ Legacy stack decommission not recommended until issues resolved');
    }
    console.log('='.repeat(80));
  }

  generateReport() {
    try {
      const reportPath = path.join(__dirname, 'parity-validation-report.json');
      const reportData = {
        ...testResults,
        config: CONFIG,
        commandLine: process.argv.join(' '),
        environment: {
          nodeVersion: process.version,
          platform: process.platform,
          arch: process.arch
        }
      };
      
      fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
      logSuccess(`📄 Detailed report generated: ${reportPath}`);
      
    } catch (error) {
      logError('Failed to generate report', error);
    }
  }
}

// Main execution
async function main() {
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    
    // Help
    if (args.includes('--help') || args.includes('-h')) {
      console.log(`
Module 4: Functionality Parity Validation Test Script

Usage:
  node scripts/test-parity-validation.js [options]

Options:
  --module <name>     Run specific test module only
  --tenant <id>       Specify tenant ID for testing
  --user <id>         Specify user ID for testing
  --role <role>       Specify user role for testing
  --verbose           Enable verbose output
  --report            Generate detailed report
  --help, -h         Show this help message

Examples:
  # Run all tests
  node scripts/test-parity-validation.js
  
  # Run specific module
  node scripts/test-parity-validation.js --module user-management
  
  # Run with custom tenant/user
  node scripts/test-parity-validation.js --tenant my-tenant --user my-user --role admin
  
  # Run with verbose output and generate report
  node scripts/test-parity-validation.js --verbose --report

Environment Variables:
  NEXT_PUBLIC_API_URL     Base URL for API (default: http://localhost:3000)
  TEST_TENANT_ID         Default tenant ID for testing
  TEST_USER_ID           Default user ID for testing
  TEST_USER_ROLE         Default user role for testing
`);
      return 0;
    }
    
    // Update config from command line arguments
    const moduleIndex = args.indexOf('--module');
    if (moduleIndex !== -1 && args[moduleIndex + 1]) {
      CONFIG.module = args[moduleIndex + 1];
    }
    
    const tenantIndex = args.indexOf('--tenant');
    if (tenantIndex !== -1 && args[tenantIndex + 1]) {
      CONFIG.tenantId = args[tenantIndex + 1];
    }
    
    const userIndex = args.indexOf('--user');
    if (userIndex !== -1 && args[userIndex + 1]) {
      CONFIG.userId = args[userIndex + 1];
    }
    
    const roleIndex = args.indexOf('--role');
    if (roleIndex !== -1 && args[roleIndex + 1]) {
      CONFIG.userRole = args[roleIndex + 1];
    }
    
    // Run tests
    const runner = new ParityTestRunner();
    
          if (CONFIG.module) {
        // Run specific module
        const results = await runner.runSpecificModule(CONFIG.module);
      testResults.modules = [results];
      testResults.summary = {
        totalTests: results.total,
        passedTests: results.passed,
        failedTests: results.failed,
        skippedTests: 0,
        successRate: results.total > 0 ? Math.round((results.passed / results.total) * 100) : 0,
        executionTime: Date.now() - runner.startTime
      };
      runner.displayResults();
    } else {
      // Run all tests
      await runner.runAllTests();
    }
    
    // Return appropriate exit code
    return testResults.summary.failedTests === 0 ? 0 : 1;
    
  } catch (error) {
    logError('❌ Test execution failed', error);
    return 1;
  }
}

// Run if called directly
if (require.main === module) {
  main().then(exitCode => {
    process.exit(exitCode);
  }).catch(error => {
    logError('❌ Unhandled error', error);
    process.exit(1);
  });
}

module.exports = { ParityTestRunner, makeRequest, CONFIG };
