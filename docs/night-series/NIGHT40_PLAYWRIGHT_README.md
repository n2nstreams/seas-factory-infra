# Night 40: Playwright Tests Authored by QA Agent

## Overview

Night 40 implements comprehensive **Playwright test generation** by the QA Agent, automatically creating end-to-end, accessibility, performance, and visual regression tests for web applications. This builds on the UIDevAgent from Night 39 to provide complete test coverage for React applications with glassmorphism styling and olive green theming.

## Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Components │    │    QA Agent     │    │ Playwright Tests│
│  (From Night 39)│───▶│   (Port 8084)   │───▶│   Generated     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │ Playwright      │              │
         └──────────────▶│ Generator       │◀─────────────┘
                        │                 │
                        └─────────────────┘
```

### Test Generation Workflow

```
Figma Design → UIDevAgent → React Components → QA Agent → Playwright Tests
     │              │              │              │
     │              │              │              ├─ E2E Tests
     │              │              │              ├─ API Tests  
     │              │              │              ├─ Accessibility Tests
     │              │              │              ├─ Performance Tests
     │              │              │              └─ Visual Regression Tests
```

### Component Architecture

```
QA Agent (Enhanced)
├── Playwright Generator
│   ├── Page Object Model Generator
│   ├── E2E Test Generator
│   ├── API Test Generator
│   ├── Accessibility Test Generator
│   ├── Performance Test Generator
│   └── Visual Regression Test Generator
├── UI Component Parser
│   ├── React Code Analysis
│   ├── Selector Extraction
│   └── Interaction Detection
├── Test Suite Manager
│   ├── Configuration Generation
│   ├── Setup/Teardown Scripts
│   └── Fixture Management
└── Orchestrator Integration
    ├── Workflow Automation
    └── Agent Delegation
```

## Core Features

### 🎭 Playwright Test Generation
- **E2E Tests**: Complete user journey testing
- **API Tests**: Backend endpoint validation with tenant isolation
- **Accessibility Tests**: WCAG compliance and a11y validation
- **Performance Tests**: Core Web Vitals and performance monitoring
- **Visual Regression**: Cross-browser and responsive testing

### 🎨 Glassmorphism & Theme Testing
- **Backdrop Blur Effects**: CSS backdrop-filter validation
- **Transparency Layers**: Glass effect rendering tests
- **Olive Green Theme**: Color palette and contrast testing
- **Responsive Design**: Multi-device and viewport testing

### 🏗️ Page Object Models
- **Maintainable Tests**: Clean separation of concerns
- **Reusable Components**: DRY principle for test code
- **TypeScript Support**: Type-safe test development
- **Selector Management**: Centralized element locators

### 🔧 Configuration & Setup
- **Multi-Browser Testing**: Chrome, Firefox, Safari support
- **CI/CD Integration**: GitHub Actions and test reporting
- **Global Setup/Teardown**: Test environment management
- **Fixture Management**: Shared test utilities

## File Structure

```
agents/qa/
├── main.py                      # Enhanced QA Agent with Playwright
├── playwright_generator.py      # Playwright test generator
├── requirements.txt             # Updated dependencies
└── test_*.py                   # Test files

night40_demo.py                 # Comprehensive demo script
NIGHT40_PLAYWRIGHT_README.md    # This documentation
orchestrator/project_orchestrator.py  # Enhanced with Playwright integration
```

## Installation & Setup

### Prerequisites

```bash
# Python 3.11+
# Node.js 18+
# Playwright browsers
```

### QA Agent Setup

```bash
# Install Python dependencies
cd agents/qa
pip install -r requirements.txt

# Start the QA agent
python main.py
```

### Playwright Setup (Generated Tests)

```bash
# Install Playwright (for generated tests)
npm install -D @playwright/test

# Install browsers
npx playwright install

# Install accessibility testing
npm install -D @axe-core/playwright
```

## API Reference

### Base URL
```
http://localhost:8084  # QA Agent
```

### New Playwright Endpoints

#### Generate Playwright Tests
```http
POST /generate-playwright-tests
```

**Request Body:**
```json
{
  "project_id": "my-project",
  "ui_components": [
    {
      "name": "LandingPage",
      "type": "page",
      "route": "/",
      "content": "React component code..."
    }
  ],
  "api_endpoints": [
    {
      "method": "GET",
      "path": "/api/projects"
    }
  ],
  "test_types": ["e2e", "api", "accessibility", "performance"],
  "browsers": ["chromium", "firefox", "webkit"]
}
```

**Response:**
```json
{
  "name": "my-project_playwright_suite",
  "project_id": "my-project",
  "test_cases": [...],
  "setup_files": {...},
  "config": {...},
  "estimated_duration": 24
}
```

#### Generate UI Component Tests
```http
POST /generate-ui-component-tests
```

**Request Body:**
```json
{
  "project_id": "my-project",
  "figma_pages": [
    {
      "name": "Landing Page",
      "route": "/",
      "content": "Generated React code..."
    }
  ],
  "generate_visual_tests": true,
  "generate_accessibility_tests": true
}
```

#### Generate from UI Scaffold
```http
POST /playwright-tests-from-ui-scaffold?project_id=my-project
```

**Request Body:**
```json
{
  "project_id": "my-project",
  "scaffold_result": {
    "pages": [...],
    "components": [...],
    "styles": {...}
  }
}
```

#### Get Test Templates
```http
GET /playwright-test-templates
```

**Response:**
```json
{
  "test_types": [
    {
      "name": "e2e",
      "description": "End-to-end user journey tests",
      "scenarios": ["user_interaction", "navigation"]
    }
  ],
  "browsers": ["chromium", "firefox", "webkit"],
  "glassmorphism_features": [...],
  "olive_theme_features": [...]
}
```

## Usage Examples

### Basic Playwright Test Generation

```python
import httpx
import json

# UI components from UIDevAgent Night 39
ui_components = [
    {
        "name": "LandingPage",
        "type": "page",
        "route": "/",
        "content": "React component with glassmorphism..."
    }
]

# API endpoints to test
api_endpoints = [
    {"method": "GET", "path": "/api/projects"},
    {"method": "POST", "path": "/api/projects"}
]

# Generate tests
request = {
    "project_id": "my-saas-app",
    "ui_components": ui_components,
    "api_endpoints": api_endpoints,
    "test_types": ["e2e", "api", "accessibility", "performance"],
    "browsers": ["chromium", "firefox", "webkit"]
}

response = httpx.post("http://localhost:8084/generate-playwright-tests", json=request)
test_suite = response.json()

print(f"Generated {len(test_suite['test_cases'])} test cases")
```

### Orchestrator Integration

```python
from orchestrator.project_orchestrator import ProjectOrchestrator

orchestrator = ProjectOrchestrator()

# Generate tests from UI scaffold result
result = orchestrator.invoke(
    "Generate comprehensive Playwright tests for this UI",
    agent_name="playwright_qa_agent",
    project_id="my-app",
    ui_scaffold_result=json.dumps(scaffold_result)
)
```

### Complete Workflow

```python
# 1. Generate UI with UIDevAgent (Night 39)
ui_result = ui_dev_agent.scaffold_ui_from_figma(figma_data)

# 2. Generate tests with QA Agent (Night 40)
test_request = {
    "project_id": "complete-workflow",
    "ui_components": qa_agent.convert_ui_scaffold_to_components(ui_result),
    "test_types": ["e2e", "accessibility", "performance", "visual"]
}

test_suite = await qa_agent.generate_playwright_tests(test_request)

# 3. Deploy generated tests
for file_path, content in test_suite['setup_files'].items():
    with open(file_path, 'w') as f:
        f.write(content)
```

## Generated Code Examples

### Page Object Model
```typescript
import { Page, Locator, expect } from '@playwright/test';

export class LandingPagePage {
    readonly page: Page;
    readonly url: string;
    readonly pageContainer: Locator;
    readonly glassElements: Locator;
    readonly oliveThemeElements: Locator;

    constructor(page: Page) {
        this.page = page;
        this.url = '/';
        this.pageContainer = page.locator('.page-container');
        this.glassElements = page.locator('.glass, [class*="backdrop-blur"]');
        this.oliveThemeElements = page.locator('[class*="text-green"]');
    }

    async goto() {
        await this.page.goto(this.url);
        await this.waitForLoad();
    }

    async verifyGlassmorphismStyles() {
        const glassElements = await this.glassElements.all();
        for (const element of glassElements) {
            await expect(element).toHaveCSS('backdrop-filter', /blur/);
        }
    }

    async verifyOliveTheme() {
        const oliveElements = await this.oliveThemeElements.all();
        expect(oliveElements.length).toBeGreaterThan(0);
    }
}
```

### E2E Test
```typescript
import { test, expect } from '@playwright/test';
import { LandingPagePage } from '../pages/LandingPagePage';

test.describe('LandingPage - User Interaction', () => {
    let landingPage: LandingPagePage;

    test.beforeEach(async ({ page }) => {
        landingPage = new LandingPagePage(page);
        await landingPage.goto();
    });

    test('should verify glassmorphism and olive theme', async ({ page }) => {
        // Verify page loads correctly
        await landingPage.verifyPageLoaded();
        
        // Test glassmorphism styling
        await landingPage.verifyGlassmorphismStyles();
        
        // Test olive theme application
        await landingPage.verifyOliveTheme();
        
        // Test responsive behavior
        await page.setViewportSize({ width: 375, height: 667 }); // Mobile
        await landingPage.verifyPageLoaded();
        
        // Take screenshot for visual regression
        await landingPage.takeScreenshot('mobile-view');
    });
});
```

### Accessibility Test
```typescript
import { test, expect } from '@playwright/test';
import { LandingPagePage } from '../pages/LandingPagePage';
import AxeBuilder from '@axe-core/playwright';

test.describe('LandingPage Accessibility', () => {
    test('should pass WCAG compliance', async ({ page }) => {
        const landingPage = new LandingPagePage(page);
        await landingPage.goto();
        
        // Run axe accessibility tests
        const accessibilityScanResults = await new AxeBuilder({ page })
            .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
            .analyze();
        
        expect(accessibilityScanResults.violations).toEqual([]);
    });

    test('should support keyboard navigation', async ({ page }) => {
        const landingPage = new LandingPagePage(page);
        await landingPage.goto();
        
        // Test keyboard navigation
        await page.keyboard.press('Tab');
        const focusedElement = await page.locator(':focus').first();
        await expect(focusedElement).toBeVisible();
    });
});
```

### Performance Test
```typescript
import { test, expect } from '@playwright/test';
import { LandingPagePage } from '../pages/LandingPagePage';

test.describe('LandingPage Performance', () => {
    test('should meet Core Web Vitals thresholds', async ({ page }) => {
        const landingPage = new LandingPagePage(page);
        
        // Navigate and measure
        const startTime = Date.now();
        await landingPage.goto();
        const loadTime = Date.now() - startTime;
        
        // Verify load time
        expect(loadTime).toBeLessThan(3000); // 3 seconds max
        
        // Test Core Web Vitals
        const vitals = await page.evaluate(() => {
            return new Promise((resolve) => {
                const observer = new PerformanceObserver((list) => {
                    // Collect vitals...
                });
                observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
            });
        });
        
        if (vitals.fcp) expect(vitals.fcp).toBeLessThan(1800); // FCP < 1.8s
        if (vitals.lcp) expect(vitals.lcp).toBeLessThan(2500); // LCP < 2.5s
    });
});
```

### API Test
```typescript
import { test, expect } from '@playwright/test';

test.describe('API /api/projects', () => {
    test('should handle GET request with tenant isolation', async ({ request }) => {
        const response = await request.get('/api/projects', {
            headers: {
                'X-Tenant-ID': 'test-tenant'
            }
        });
        
        expect(response.status()).toBe(200);
        const projects = await response.json();
        
        // Verify tenant isolation
        for (const project of projects) {
            expect(project.tenant_id).toBe('test-tenant');
        }
    });

    test('should enforce authentication', async ({ request }) => {
        // Test without auth
        const unauthResponse = await request.get('/api/projects');
        expect(unauthResponse.status()).toBe(401);
        
        // Test with auth
        const authResponse = await request.get('/api/projects', {
            headers: {
                'Authorization': 'Bearer valid-token',
                'X-Tenant-ID': 'test-tenant'
            }
        });
        expect(authResponse.status()).toBe(200);
    });
});
```

### Visual Regression Test
```typescript
import { test, expect } from '@playwright/test';
import { LandingPagePage } from '../pages/LandingPagePage';

test.describe('LandingPage Visual Regression', () => {
    test('should match visual snapshots', async ({ page }) => {
        const landingPage = new LandingPagePage(page);
        await landingPage.goto();
        
        // Wait for glassmorphism effects
        await page.waitForTimeout(1000);
        
        // Test desktop view
        await page.setViewportSize({ width: 1920, height: 1080 });
        await expect(page).toHaveScreenshot('landing-desktop.png', {
            fullPage: true,
            threshold: 0.2
        });
        
        // Test mobile view
        await page.setViewportSize({ width: 375, height: 667 });
        await expect(page).toHaveScreenshot('landing-mobile.png', {
            fullPage: true,
            threshold: 0.2
        });
    });

    test('should handle glassmorphism hover effects', async ({ page }) => {
        const landingPage = new LandingPagePage(page);
        await landingPage.goto();
        
        // Test hover states
        const glassElements = await landingPage.glassElements.all();
        if (glassElements.length > 0) {
            await glassElements[0].hover();
            await page.waitForTimeout(300);
            await expect(page).toHaveScreenshot('glass-hover.png');
        }
    });
});
```

## Playwright Configuration

### Generated Configuration
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './tests',
    timeout: 60 * 1000,
    expect: {
        timeout: 10000,
        threshold: 0.2, // Visual regression threshold
    },
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 1,
    workers: process.env.CI ? 1 : undefined,
    
    reporter: [
        ['html'],
        ['json', { outputFile: 'test-results/results.json' }],
        ['junit', { outputFile: 'test-results/junit.xml' }]
    ],
    
    use: {
        baseURL: process.env.BASE_URL || 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        video: 'retain-on-failure',
    },

    projects: [
        { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
        { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
        { name: 'webkit', use: { ...devices['Desktop Safari'] } },
        { name: 'Mobile Chrome', use: { ...devices['Pixel 5'] } },
        { name: 'Mobile Safari', use: { ...devices['iPhone 12'] } },
    ],

    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
    },
});
```

## Test Categories

### E2E Tests
- **User Journeys**: Complete workflows from start to finish
- **Navigation**: Inter-page navigation and routing
- **Form Interactions**: Input validation and submission
- **Responsive Behavior**: Cross-device functionality
- **Glassmorphism Effects**: Visual effect interactions

### API Tests
- **CRUD Operations**: Create, Read, Update, Delete testing
- **Authentication**: Token validation and authorization
- **Tenant Isolation**: Multi-tenant data segregation
- **Error Handling**: Invalid request processing
- **Rate Limiting**: API throttling compliance

### Accessibility Tests
- **WCAG Compliance**: 2.1 AA standard verification
- **Keyboard Navigation**: Tab order and focus management
- **Screen Reader**: ARIA attributes and semantic HTML
- **Color Contrast**: Accessibility color requirements
- **Form Labels**: Proper label-input associations

### Performance Tests
- **Core Web Vitals**: FCP, LCP, CLS measurements
- **Load Times**: Page loading performance
- **Memory Usage**: JavaScript heap monitoring
- **Interaction Timing**: Response time validation
- **Network Performance**: Resource loading optimization

### Visual Regression Tests
- **Multi-Viewport**: Desktop, tablet, mobile views
- **Browser Compatibility**: Cross-browser rendering
- **Theme Variations**: Light/dark mode testing
- **Hover States**: Interactive element styling
- **Animation Testing**: CSS transitions and effects

## Glassmorphism Testing Features

### Backdrop Blur Validation
```typescript
// Verify backdrop-filter CSS property
await expect(element).toHaveCSS('backdrop-filter', /blur/);

// Test blur intensity
const blurValue = await element.evaluate(el => 
    getComputedStyle(el).backdropFilter
);
expect(blurValue).toMatch(/blur\(\d+px\)/);
```

### Transparency Effects
```typescript
// Verify transparency layers
await expect(element).toHaveCSS('background-color', /rgba.*0\.\d+\)/);

// Test glass container visibility
const glassElements = await page.locator('.glass').all();
for (const glass of glassElements) {
    await expect(glass).toBeVisible();
    await expect(glass).toHaveCSS('border', /rgba.*0\.\d+/);
}
```

### Olive Theme Validation
```typescript
// Test olive color palette
const oliveElements = await page.locator('[class*="text-green"]').all();
expect(oliveElements.length).toBeGreaterThan(0);

// Verify color contrast
for (const element of oliveElements) {
    const textColor = await element.evaluate(el => 
        getComputedStyle(el).color
    );
    const bgColor = await element.evaluate(el => 
        getComputedStyle(el).backgroundColor
    );
    
    // Ensure sufficient contrast
    expect(calculateContrast(textColor, bgColor)).toBeGreaterThan(4.5);
}
```

## Integration with Night 39

### Workflow Integration
```
Night 39 (UIDevAgent) → Night 40 (QA Agent)
     │                        │
Figma JSON ────────────────▶ UI Components
     │                        │
React Pages ─────────────▶ Page Object Models
     │                        │
Styling Info ─────────────▶ Visual Tests
     │                        │
Routing Config ───────────▶ Navigation Tests
```

### Data Flow
```python
# From Night 39 UIDevAgent
ui_scaffold_result = {
    "pages": [...],      # → E2E and Visual Tests
    "components": [...], # → Component Tests
    "styles": {...},     # → Visual Regression
    "routing_config": "" # → Navigation Tests
}

# To Night 40 QA Agent
playwright_tests = qa_agent.generate_playwright_tests({
    "project_id": "my-project",
    "ui_components": convert_scaffold_to_components(ui_scaffold_result),
    "test_types": ["e2e", "accessibility", "performance", "visual"]
})
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Playwright Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Run Playwright tests
        run: npx playwright test
        
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

### Test Reporting
```typescript
// Generated reporter configuration
reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['github'] // GitHub Actions integration
]
```

## Best Practices

### Test Organization
```
tests/
├── e2e/                    # End-to-end tests
│   ├── landing.spec.ts
│   └── dashboard.spec.ts
├── api/                    # API tests
│   ├── projects.spec.ts
│   └── users.spec.ts
├── accessibility/          # A11y tests
│   ├── forms.spec.ts
│   └── navigation.spec.ts
├── performance/           # Performance tests
│   └── core-vitals.spec.ts
├── visual/               # Visual regression
│   └── snapshots.spec.ts
└── pages/               # Page Object Models
    ├── LandingPage.ts
    └── DashboardPage.ts
```

### Selector Strategy
```typescript
// Prefer data-testid for test stability
page.locator('[data-testid="submit-button"]')

// Use semantic selectors for accessibility
page.locator('button[type="submit"]')

// Glassmorphism-specific selectors
page.locator('.glass, [class*="backdrop-blur"]')

// Olive theme selectors
page.locator('[class*="text-green"], [class*="bg-green"]')
```

### Error Handling
```typescript
test('should handle network failures gracefully', async ({ page }) => {
    // Simulate network failure
    await page.route('**/api/**', route => route.abort());
    
    await page.goto('/dashboard');
    
    // Verify error state
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
});
```

## Production Deployment

### Docker Integration
```dockerfile
FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
CMD ["npx", "playwright", "test"]
```

### Environment Configuration
```bash
# Test environment variables
BASE_URL=https://staging.myapp.com
API_BASE_URL=https://api.staging.myapp.com
TEST_TENANT_ID=staging-tenant

# Playwright configuration
PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
CI=true
```

### Monitoring & Alerts
```typescript
// Performance monitoring
test.afterEach(async ({ page }, testInfo) => {
    const metrics = await page.evaluate(() => ({
        loadTime: performance.now(),
        memory: (performance as any).memory?.usedJSHeapSize
    }));
    
    if (metrics.loadTime > 3000) {
        console.warn(`Slow test: ${testInfo.title} took ${metrics.loadTime}ms`);
    }
});
```

## Troubleshooting

### Common Issues

#### Browser Installation
```bash
# Install browsers manually
npx playwright install chromium firefox webkit

# Verify installation
npx playwright --version
```

#### Flaky Tests
```typescript
// Add explicit waits
await page.waitForLoadState('networkidle');
await page.waitForTimeout(500); // For animations

// Use better selectors
await page.locator('button:has-text("Submit")').click();
```

#### Visual Regression Failures
```bash
# Update snapshots
npx playwright test --update-snapshots

# Update specific test
npx playwright test landing.spec.ts --update-snapshots
```

#### Accessibility Test Failures
```typescript
// Exclude specific rules
const accessibilityScanResults = await new AxeBuilder({ page })
    .exclude('[data-testid="third-party-widget"]')
    .disableRules(['color-contrast']) // Temporary exclusion
    .analyze();
```

### Debug Mode
```bash
# Run tests in debug mode
npx playwright test --debug

# Run specific test with trace
npx playwright test landing.spec.ts --trace on
```

## Future Enhancements

### Planned Features
- **AI-Powered Test Generation**: LLM-based test case creation
- **Smart Selector Generation**: ML-based element identification
- **Cross-Platform Testing**: Mobile app testing support
- **Performance Budgets**: Automated performance regression detection
- **Test Maintenance**: Auto-healing for broken selectors

### Extension Points
- **Custom Test Types**: Plugin system for specialized tests
- **Reporting Integration**: Custom reporter development
- **Test Data Management**: Dynamic test data generation
- **Multi-Language Support**: Tests in multiple programming languages

## Contributing

### Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/seas-factory-infra.git
cd seas-factory-infra

# Install QA agent dependencies
cd agents/qa
pip install -r requirements.txt

# Install Playwright
npm install -D @playwright/test
npx playwright install

# Run tests
python -m pytest test_*.py
```

### Adding New Test Types
```python
# Extend PlaywrightGenerator
class CustomTestGenerator(PlaywrightGenerator):
    def generate_custom_test(self, component: UIComponent) -> PlaywrightTestCase:
        # Implement custom test logic
        pass

# Register in QA Agent
qa_agent.playwright_generator.register_test_type('custom', CustomTestGenerator)
```

## License

This project is part of the AI SaaS Factory and is licensed under the MIT License.

## Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/your-org/seas-factory-infra/issues)
- **Documentation**: This README and inline documentation
- **Examples**: See `night40_demo.py` for comprehensive examples

---

**Night 40 QA Agent** - Transforming UI components into comprehensive, production-ready Playwright test suites with AI-powered automation and specialized glassmorphism & accessibility testing. 