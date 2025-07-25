import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestCount = new Counter('request_count');

// Test configuration from environment variables
const BASE_URL = __ENV.BASE_URL || 'https://api-backend-saas-factory.run.app';
const ORCHESTRATOR_URL = __ENV.ORCHESTRATOR_URL || 'https://orchestrator-saas-factory.run.app';
const DASHBOARD_URL = __ENV.DASHBOARD_URL || 'https://dashboard-saas-factory.run.app';

// Test scenarios configuration
export const options = {
  scenarios: {
    // Spike test: Sudden increase in traffic
    spike_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },  // Ramp up to 10 users
        { duration: '1m', target: 50 },   // Spike to 50 users
        { duration: '30s', target: 10 },  // Scale down
        { duration: '1m', target: 0 },    // Ramp down
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'spike' },
    },
    
    // Load test: Sustained traffic
    load_test: {
      executor: 'constant-vus',
      vus: 20,
      duration: '5m',
      tags: { test_type: 'load' },
    },
    
    // Stress test: High traffic to find breaking point
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 20 },   // Ramp up to normal load
        { duration: '5m', target: 20 },   // Stay at normal load
        { duration: '2m', target: 40 },   // Bump to high load
        { duration: '5m', target: 40 },   // Stay at high load
        { duration: '2m', target: 80 },   // Ramp up to stress load
        { duration: '5m', target: 80 },   // Stay at stress load
        { duration: '2m', target: 0 },    // Ramp down
      ],
      gracefulRampDown: '30s',
      tags: { test_type: 'stress' },
    },
    
    // Soak test: Extended duration test
    soak_test: {
      executor: 'constant-vus',
      vus: 15,
      duration: '15m',
      tags: { test_type: 'soak' },
    },
  },
  
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.1'],     // Error rate should be below 10%
    error_rate: ['rate<0.05'],         // Custom error rate should be below 5%
  },
};

// Test data for different endpoints
const testData = {
  healthChecks: [
    '/health',
    '/metrics',
    '/status'
  ],
  
  orchestratorRequests: [
    {
      endpoint: '/orchestrator',
      payload: {
        idea: 'Simple task tracker app',
        features: ['user authentication', 'task creation', 'due dates'],
        tech_stack: 'react,node,postgres'
      }
    },
    {
      endpoint: '/orchestrator/simple',
      payload: {
        idea: 'Blog platform',
        features: ['posts', 'comments', 'user profiles']
      }
    }
  ],
  
  aiopsRequests: [
    {
      endpoint: '/anomalies',
      params: '?limit=50&severity=high'
    },
    {
      endpoint: '/alerts',
      params: ''
    },
    {
      endpoint: '/metrics',
      params: ''
    }
  ]
};

// Utility functions
function makeRequest(url, options = {}) {
  const startTime = new Date().getTime();
  const response = http.get(url, options);
  const endTime = new Date().getTime();
  
  // Record metrics
  requestCount.add(1);
  responseTime.add(endTime - startTime);
  errorRate.add(response.status >= 400);
  
  return response;
}

function makePostRequest(url, payload, options = {}) {
  const startTime = new Date().getTime();
  const response = http.post(url, JSON.stringify(payload), {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  const endTime = new Date().getTime();
  
  // Record metrics
  requestCount.add(1);
  responseTime.add(endTime - startTime);
  errorRate.add(response.status >= 400);
  
  return response;
}

// Main test function
export default function() {
  // Health check tests
  group('Health Checks', () => {
    testData.healthChecks.forEach(endpoint => {
      const response = makeRequest(`${BASE_URL}${endpoint}`);
      
      check(response, {
        [`${endpoint} status is 200`]: (r) => r.status === 200,
        [`${endpoint} response time < 1s`]: (r) => r.timings.duration < 1000,
        [`${endpoint} has valid response`]: (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.status === 'healthy' || body.status === 'success';
          } catch (e) {
            return false;
          }
        },
      });
    });
  });
  
  // Orchestrator tests
  group('Orchestrator API', () => {
    testData.orchestratorRequests.forEach(req => {
      const response = makePostRequest(`${ORCHESTRATOR_URL}${req.endpoint}`, req.payload);
      
      check(response, {
        [`${req.endpoint} status is 200`]: (r) => r.status === 200,
        [`${req.endpoint} response time < 5s`]: (r) => r.timings.duration < 5000,
        [`${req.endpoint} returns success`]: (r) => {
          try {
            const body = JSON.parse(r.body);
            return body.status === 'success';
          } catch (e) {
            return false;
          }
        },
      });
      
      // Add some thinking time between orchestrator requests
      sleep(1);
    });
  });
  
  // AIOps Agent tests
  group('AIOps Agent API', () => {
    testData.aiopsRequests.forEach(req => {
      const response = makeRequest(`${BASE_URL}${req.endpoint}${req.params}`);
      
      check(response, {
        [`${req.endpoint} status is 200`]: (r) => r.status === 200,
        [`${req.endpoint} response time < 2s`]: (r) => r.timings.duration < 2000,
        [`${req.endpoint} returns valid JSON`]: (r) => {
          try {
            JSON.parse(r.body);
            return true;
          } catch (e) {
            return false;
          }
        },
      });
    });
  });
  
  // Dashboard tests
  group('Dashboard', () => {
    const response = makeRequest(`${DASHBOARD_URL}/`);
    
    check(response, {
      'Dashboard loads successfully': (r) => r.status === 200,
      'Dashboard response time < 3s': (r) => r.timings.duration < 3000,
    });
  });
  
  // Random sleep between 1-3 seconds to simulate real user behavior
  sleep(Math.random() * 2 + 1);
}

// Setup function (runs once per VU at the beginning)
export function setup() {
  console.log('Starting load test...');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Orchestrator URL: ${ORCHESTRATOR_URL}`);
  console.log(`Dashboard URL: ${DASHBOARD_URL}`);
  
  // Verify services are accessible
  const healthCheck = http.get(`${BASE_URL}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`Base service not accessible: ${healthCheck.status}`);
  }
  
  return {
    startTime: new Date().toISOString(),
    baseUrl: BASE_URL,
    orchestratorUrl: ORCHESTRATOR_URL,
    dashboardUrl: DASHBOARD_URL
  };
}

// Teardown function (runs once at the end)
export function teardown(data) {
  console.log('Load test completed');
  console.log(`Started at: ${data.startTime}`);
  console.log(`Finished at: ${new Date().toISOString()}`);
}

// Handle summary for custom reporting
export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data, null, 2),
    'summary.html': htmlReport(data),
  };
}

// Generate HTML report
function htmlReport(data) {
  const date = new Date().toISOString();
  
  return `
<!DOCTYPE html>
<html>
<head>
    <title>Load Test Report - ${date}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2d3748; color: white; padding: 20px; border-radius: 8px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #f7fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #4299e1; }
        .pass { color: #38a169; }
        .fail { color: #e53e3e; }
        .threshold { margin: 10px 0; }
        pre { background: #1a202c; color: #cbd5e0; padding: 15px; border-radius: 8px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 SaaS Factory Load Test Report</h1>
        <p>Generated: ${date}</p>
        <p>Duration: ${data.state.testRunDurationMs / 1000}s</p>
    </div>
    
    <div class="metrics">
        <div class="metric-card">
            <h3>📊 HTTP Metrics</h3>
            <p><strong>Requests:</strong> ${data.metrics.http_reqs.values.count}</p>
            <p><strong>Failed:</strong> ${data.metrics.http_req_failed.values.rate * 100}%</p>
            <p><strong>Avg Duration:</strong> ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms</p>
            <p><strong>95th Percentile:</strong> ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms</p>
        </div>
        
        <div class="metric-card">
            <h3>🎯 Thresholds</h3>
            ${Object.entries(data.thresholds).map(([metric, result]) => 
              `<div class="threshold ${result.ok ? 'pass' : 'fail'}">
                ${metric}: ${result.ok ? '✅ PASS' : '❌ FAIL'}
              </div>`
            ).join('')}
        </div>
        
        <div class="metric-card">
            <h3>⚡ Performance</h3>
            <p><strong>Data Received:</strong> ${(data.metrics.data_received.values.count / 1024 / 1024).toFixed(2)} MB</p>
            <p><strong>Data Sent:</strong> ${(data.metrics.data_sent.values.count / 1024).toFixed(2)} KB</p>
            <p><strong>Iterations:</strong> ${data.metrics.iterations.values.count}</p>
            <p><strong>VUs Max:</strong> ${data.metrics.vus_max.values.max}</p>
        </div>
    </div>
    
    <h3>📋 Raw Data</h3>
    <pre>${JSON.stringify(data, null, 2)}</pre>
</body>
</html>
  `;
} 