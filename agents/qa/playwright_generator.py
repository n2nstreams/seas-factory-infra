#!/usr/bin/env python3
"""
Playwright Test Generator - Night 40 Implementation
Automatically generates comprehensive Playwright tests for web applications
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PlaywrightTestCase(BaseModel):
    """Model for a Playwright test case"""
    name: str
    description: str
    test_type: str  # e2e, api, accessibility, performance
    file_path: str
    code: str
    selectors: List[str] = Field(default_factory=list)
    test_data: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    timeout: int = Field(default=30000)  # milliseconds
    retry_count: int = Field(default=2)

class PlaywrightTestSuite(BaseModel):
    """Model for a complete Playwright test suite"""
    name: str
    project_id: str
    test_cases: List[PlaywrightTestCase]
    config: Dict[str, Any]
    setup_files: Dict[str, str] = Field(default_factory=dict)
    fixtures: Dict[str, str] = Field(default_factory=dict)
    estimated_duration: int  # minutes
    browsers: List[str] = Field(default_factory=lambda: ["chromium", "firefox", "webkit"])

class UIComponent(BaseModel):
    """Model for UI component from UIDevAgent"""
    name: str
    type: str  # page, component
    selectors: Dict[str, str]
    interactions: List[str]
    route: Optional[str] = None

class PlaywrightGenerator:
    """Playwright test generator for comprehensive E2E testing"""
    
    def __init__(self):
        self.glassmorphism_selectors = {
            'glass_container': '.glass, [class*="backdrop-blur"], [class*="bg-white/"]',
            'glass_card': '.glass-card, [class*="rounded-xl"][class*="backdrop-blur"]',
            'glass_button': 'button.glass, [class*="backdrop-blur"][role="button"]',
            'olive_theme': '[class*="olive-theme"], [class*="text-green"], [class*="bg-green"]'
        }
        
        self.common_selectors = {
            'navigation': 'nav, [role="navigation"], .navbar, .nav',
            'header': 'header, [role="banner"], .header',
            'main_content': 'main, [role="main"], .main-content',
            'footer': 'footer, [role="contentinfo"], .footer',
            'form': 'form, [role="form"]',
            'button': 'button, [role="button"], input[type="submit"]',
            'input': 'input, textarea, select, [role="textbox"]',
            'modal': '[role="dialog"], .modal, .overlay',
            'loading': '[data-loading], .loading, .spinner'
        }
    
    def generate_page_object_model(self, component: UIComponent) -> str:
        """Generate Page Object Model class for a UI component"""
        
        class_name = f"{component.name}Page"
        
        page_object = f"""import {{ Page, Locator, expect }} from '@playwright/test';

export class {class_name} {{
    readonly page: Page;
    readonly url: string;"""
        
        # Add selectors as properties
        for selector_name, selector_value in component.selectors.items():
            prop_name = self._to_camel_case(selector_name)
            page_object += f"""
    readonly {prop_name}: Locator;"""
        
        # Constructor
        page_object += f"""

    constructor(page: Page) {{
        this.page = page;
        this.url = '{component.route or f"/{component.name.lower()}"}';"""
        
        for selector_name, selector_value in component.selectors.items():
            prop_name = self._to_camel_case(selector_name)
            page_object += f"""
        this.{prop_name} = page.locator('{selector_value}');"""
        
        page_object += """
    }

    async goto() {
        await this.page.goto(this.url);
        await this.waitForLoad();
    }

    async waitForLoad() {
        await this.page.waitForLoadState('networkidle');
        // Wait for glassmorphism effects to render
        await this.page.waitForTimeout(500);
    }"""
        
        # Add interaction methods
        for interaction in component.interactions:
            method_name = self._to_camel_case(interaction.replace(' ', '_'))
            page_object += f"""

    async {method_name}() {{
        // TODO: Implement {interaction}
        await this.page.waitForTimeout(100);
    }}"""
        
        # Add verification methods
        page_object += f"""

    async verifyPageLoaded() {{
        await expect(this.page).toHaveTitle(/{component.name}/i);
        await expect(this.page.locator('body')).toBeVisible();
    }}

    async verifyGlassmorphismStyles() {{
        const glassElements = await this.page.locator('{self.glassmorphism_selectors["glass_container"]}').all();
        for (const element of glassElements) {{
            await expect(element).toHaveCSS('backdrop-filter', /blur/);
        }}
    }}

    async verifyOliveTheme() {{
        const oliveElements = await this.page.locator('{self.glassmorphism_selectors["olive_theme"]}').all();
        expect(oliveElements.length).toBeGreaterThan(0);
    }}

    async takeScreenshot(name?: string) {{
        const screenshotName = name || '{component.name.lower()}-page';
        await this.page.screenshot({{ 
            path: `screenshots/${{screenshotName}}-${{Date.now()}}.png`,
            fullPage: true
        }});
    }}
}}"""
        
        return page_object
    
    def generate_e2e_test_case(self, component: UIComponent, test_scenario: str) -> PlaywrightTestCase:
        """Generate comprehensive E2E test case"""
        
        test_name = f"test_{component.name.lower()}_{test_scenario.replace(' ', '_')}"
        file_path = f"tests/e2e/{component.name.lower()}.spec.ts"
        
        # Generate test code
        test_code = f"""import {{ test, expect }} from '@playwright/test';
import {{ {component.name}Page }} from '../pages/{component.name}Page';

test.describe('{component.name} - {test_scenario}', () => {{
    let {component.name.lower()}Page: {component.name}Page;

    test.beforeEach(async ({{ page }}) => {{
        {component.name.lower()}Page = new {component.name}Page(page);
        await {component.name.lower()}Page.goto();
    }});

    test('{test_name}', async ({{ page }}) => {{
        // Verify page loads correctly
        await {component.name.lower()}Page.verifyPageLoaded();
        
        // Test glassmorphism styling
        await {component.name.lower()}Page.verifyGlassmorphismStyles();
        
        // Test olive theme application
        await {component.name.lower()}Page.verifyOliveTheme();
        
        // Test responsive behavior
        await page.setViewportSize({{ width: 375, height: 667 }}); // Mobile
        await {component.name.lower()}Page.verifyPageLoaded();
        
        await page.setViewportSize({{ width: 768, height: 1024 }}); // Tablet
        await {component.name.lower()}Page.verifyPageLoaded();
        
        await page.setViewportSize({{ width: 1920, height: 1080 }}); // Desktop
        await {component.name.lower()}Page.verifyPageLoaded();
        
        // Take screenshot for visual regression
        await {component.name.lower()}Page.takeScreenshot('{test_scenario}');"""
        
        if test_scenario == "user_interaction":
            test_code += """
        
        // Test user interactions
        const buttons = await page.locator('button, [role="button"]').all();
        for (const button of buttons) {
            if (await button.isVisible()) {
                await button.hover();
                await page.waitForTimeout(200); // Wait for hover effects
            }
        }
        
        // Test form interactions if present
        const forms = await page.locator('form').all();
        for (const form of forms) {
            const inputs = await form.locator('input, textarea, select').all();
            for (const input of inputs) {
                if (await input.isVisible() && await input.isEnabled()) {
                    await input.focus();
                    await page.waitForTimeout(100);
                }
            }
        }"""
        
        elif test_scenario == "navigation":
            test_code += """
        
        // Test navigation functionality
        const navLinks = await page.locator('nav a, [role="navigation"] a').all();
        for (const link of navLinks) {
            if (await link.isVisible()) {
                const href = await link.getAttribute('href');
                if (href && !href.startsWith('http') && !href.startsWith('mailto:')) {
                    await link.click();
                    await page.waitForLoadState('networkidle');
                    await page.goBack();
                    await page.waitForLoadState('networkidle');
                }
            }
        }"""
        
        elif test_scenario == "accessibility":
            test_code += """
        
        // Test accessibility features
        await expect(page.locator('h1, h2, h3')).toHaveCount({ min: 1 });
        
        // Check for alt text on images
        const images = await page.locator('img').all();
        for (const img of images) {
            await expect(img).toHaveAttribute('alt');
        }
        
        // Check for proper form labels
        const inputs = await page.locator('input[type="text"], input[type="email"], textarea').all();
        for (const input of inputs) {
            const id = await input.getAttribute('id');
            if (id) {
                await expect(page.locator(`label[for="${id}"]`)).toBeVisible();
            }
        }
        
        // Test keyboard navigation
        await page.keyboard.press('Tab');
        await expect(page.locator(':focus')).toBeVisible();"""
        
        test_code += """
    });
});"""
        
        return PlaywrightTestCase(
            name=test_name,
            description=f"{test_scenario} test for {component.name} component",
            test_type="e2e",
            file_path=file_path,
            code=test_code,
            selectors=list(component.selectors.values()),
            tags=[test_scenario, component.type, "glassmorphism", "olive-theme"],
            timeout=60000 if test_scenario == "accessibility" else 30000
        )
    
    def generate_api_test_case(self, api_endpoint: str, method: str, test_scenario: str) -> PlaywrightTestCase:
        """Generate API test case using Playwright's request context"""
        
        test_name = f"test_api_{api_endpoint.replace('/', '_')}_{method.lower()}_{test_scenario}"
        file_path = f"tests/api/{api_endpoint.replace('/', '_')}.spec.ts"
        
        test_code = f"""import {{ test, expect }} from '@playwright/test';

test.describe('API {api_endpoint} - {method}', () => {{
    test('{test_name}', async ({{ request }}) => {{
        const baseUrl = process.env.API_BASE_URL || 'http://localhost:8000';
        
        // Test {test_scenario}
        const response = await request.{method.lower()}(`${{baseUrl}}{api_endpoint}`"""
        
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            test_code += """, {
            data: {
                // Test data
            },
            headers: {
                'Content-Type': 'application/json',
                'X-Tenant-ID': process.env.TEST_TENANT_ID || 'test-tenant'
            }
        }"""
        else:
            test_code += """, {
            headers: {
                'X-Tenant-ID': process.env.TEST_TENANT_ID || 'test-tenant'
            }
        }"""
        
        test_code += """);
        
        // Verify response"""
        
        if test_scenario == "success":
            test_code += f"""
        expect(response.status()).toBe({200 if method == 'GET' else 201 if method == 'POST' else 200});
        
        const responseBody = await response.json();
        expect(responseBody).toBeDefined();
        
        // Verify response structure
        if (Array.isArray(responseBody)) {{
            expect(responseBody.length).toBeGreaterThanOrEqual(0);
        }} else {{
            expect(responseBody).toHaveProperty('id');
        }}"""
        
        elif test_scenario == "authentication":
            test_code += """
        // Test without authentication
        const unauthResponse = await request.{method.lower()}(`${baseUrl}{api_endpoint}`);
        expect(unauthResponse.status()).toBe(401);
        
        // Test with valid authentication
        const authResponse = await request.{method.lower()}(`${baseUrl}{api_endpoint}`, {
            headers: {
                'Authorization': 'Bearer valid-token',
                'X-Tenant-ID': process.env.TEST_TENANT_ID || 'test-tenant'
            }
        });
        expect([200, 201, 204]).toContain(authResponse.status());""".format(method=method.lower(), api_endpoint=api_endpoint)
        
        elif test_scenario == "validation":
            test_code += f"""
        // Test with invalid data
        const invalidResponse = await request.{method.lower()}(`${{baseUrl}}{api_endpoint}`, {{
            data: {{}}, // Empty data
            headers: {{
                'Content-Type': 'application/json',
                'X-Tenant-ID': process.env.TEST_TENANT_ID || 'test-tenant'
            }}
        }});
        expect([400, 422]).toContain(invalidResponse.status());"""
        
        test_code += """
    });
});"""
        
        return PlaywrightTestCase(
            name=test_name,
            description=f"API test for {method} {api_endpoint} - {test_scenario}",
            test_type="api",
            file_path=file_path,
            code=test_code,
            tags=["api", test_scenario, method.lower()],
            timeout=15000
        )
    
    def generate_performance_test_case(self, component: UIComponent) -> PlaywrightTestCase:
        """Generate performance test case"""
        
        test_name = f"test_{component.name.lower()}_performance"
        file_path = f"tests/performance/{component.name.lower()}.spec.ts"
        
        test_code = f"""import {{ test, expect }} from '@playwright/test';
import {{ {component.name}Page }} from '../pages/{component.name}Page';

test.describe('{component.name} Performance Tests', () => {{
    test('{test_name}', async ({{ page }}) => {{
        const {component.name.lower()}Page = new {component.name}Page(page);
        
        // Enable performance monitoring
        await page.goto('about:blank');
        await page.addInitScript(() => {{
            window.performance.mark('test-start');
        }});
        
        // Navigate and measure page load
        const startTime = Date.now();
        await {component.name.lower()}Page.goto();
        const loadTime = Date.now() - startTime;
        
        // Verify page loads within acceptable time
        expect(loadTime).toBeLessThan(3000); // 3 seconds max
        
        // Test Core Web Vitals
        const vitals = await page.evaluate(() => {{
            return new Promise((resolve) => {{
                const observer = new PerformanceObserver((list) => {{
                    const entries = list.getEntries();
                    const vitals = {{}};
                    
                    entries.forEach((entry) => {{
                        if (entry.name === 'first-contentful-paint') {{
                            vitals.fcp = entry.startTime;
                        }}
                        if (entry.entryType === 'largest-contentful-paint') {{
                            vitals.lcp = entry.startTime;
                        }}
                        if (entry.entryType === 'layout-shift') {{
                            vitals.cls = (vitals.cls || 0) + entry.value;
                        }}
                    }});
                    
                    setTimeout(() => resolve(vitals), 2000);
                }});
                
                observer.observe({{ entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift'] }});
            }});
        }});
        
        // Verify Core Web Vitals thresholds
        if (vitals.fcp) expect(vitals.fcp).toBeLessThan(1800); // FCP < 1.8s
        if (vitals.lcp) expect(vitals.lcp).toBeLessThan(2500); // LCP < 2.5s
        if (vitals.cls) expect(vitals.cls).toBeLessThan(0.1);   // CLS < 0.1
        
        // Test memory usage
        const memoryInfo = await page.evaluate(() => {{
            return (performance as any).memory ? {{
                usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
                totalJSHeapSize: (performance as any).memory.totalJSHeapSize
            }} : null;
        }});
        
        if (memoryInfo) {{
            const memoryUsageMB = memoryInfo.usedJSHeapSize / 1024 / 1024;
            expect(memoryUsageMB).toBeLessThan(50); // Less than 50MB
        }}
        
        // Test glassmorphism effect performance
        await page.locator('{self.glassmorphism_selectors["glass_container"]}').first().hover();
        await page.waitForTimeout(100);
        
        // Measure interaction responsiveness
        const interactionStart = Date.now();
        await page.locator('button, [role="button"]').first().click();
        await page.waitForTimeout(100);
        const interactionTime = Date.now() - interactionStart;
        
        expect(interactionTime).toBeLessThan(100); // Interactions < 100ms
        
        console.log('Performance Metrics:', {{
            loadTime,
            vitals,
            memoryUsageMB: memoryInfo ? memoryInfo.usedJSHeapSize / 1024 / 1024 : 'N/A',
            interactionTime
        }});
    }});
}});"""
        
        return PlaywrightTestCase(
            name=test_name,
            description=f"Performance test for {component.name}",
            test_type="performance",
            file_path=file_path,
            code=test_code,
            tags=["performance", "core-web-vitals", "memory"],
            timeout=60000
        )
    
    def generate_accessibility_test_case(self, component: UIComponent) -> PlaywrightTestCase:
        """Generate accessibility test case"""
        
        test_name = f"test_{component.name.lower()}_accessibility"
        file_path = f"tests/accessibility/{component.name.lower()}.spec.ts"
        
        test_code = f"""import {{ test, expect }} from '@playwright/test';
import {{ {component.name}Page }} from '../pages/{component.name}Page';
import AxeBuilder from '@axe-core/playwright';

test.describe('{component.name} Accessibility Tests', () => {{
    test('{test_name}', async ({{ page }}) => {{
        const {component.name.lower()}Page = new {component.name}Page(page);
        await {component.name.lower()}Page.goto();
        
        // Run axe accessibility tests
        const accessibilityScanResults = await new AxeBuilder({{ page }})
            .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
            .analyze();
        
        expect(accessibilityScanResults.violations).toEqual([]);
        
        // Test keyboard navigation
        await page.keyboard.press('Tab');
        let focusedElement = await page.locator(':focus').first();
        await expect(focusedElement).toBeVisible();
        
        // Navigate through all focusable elements
        const focusableElements = await page.locator('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])').all();
        
        for (let i = 0; i < Math.min(focusableElements.length, 10); i++) {{
            await page.keyboard.press('Tab');
            focusedElement = await page.locator(':focus').first();
            await expect(focusedElement).toBeVisible();
        }}
        
        // Test ARIA attributes
        const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
        expect(headings.length).toBeGreaterThan(0);
        
        // Verify proper heading hierarchy
        if (headings.length > 0) {{
            const h1Count = await page.locator('h1').count();
            expect(h1Count).toBe(1); // Should have exactly one h1
        }}
        
        // Test color contrast for olive theme
        const oliveElements = await page.locator('{self.glassmorphism_selectors["olive_theme"]}').all();
        for (const element of oliveElements) {{
            const styles = await element.evaluate((el) => {{
                const computed = window.getComputedStyle(el);
                return {{
                    color: computed.color,
                    backgroundColor: computed.backgroundColor
                }};
            }});
            
            // Basic contrast check (simplified)
            expect(styles.color).not.toBe(styles.backgroundColor);
        }}
        
        // Test screen reader compatibility
        const landmarks = await page.locator('[role="main"], [role="banner"], [role="navigation"], [role="contentinfo"]').all();
        expect(landmarks.length).toBeGreaterThan(0);
        
        // Test form accessibility
        const forms = await page.locator('form').all();
        for (const form of forms) {{
            const inputs = await form.locator('input, textarea, select').all();
            for (const input of inputs) {{
                const inputId = await input.getAttribute('id');
                const ariaLabel = await input.getAttribute('aria-label');
                const ariaLabelledBy = await input.getAttribute('aria-labelledby');
                
                // Input should have label, aria-label, or aria-labelledby
                const hasLabel = inputId ? await page.locator(`label[for="${{inputId}}"]`).count() > 0 : false;
                expect(hasLabel || ariaLabel || ariaLabelledBy).toBeTruthy();
            }}
        }}
        
        console.log('Accessibility scan passed for {component.name}');
    }});
}});"""
        
        return PlaywrightTestCase(
            name=test_name,
            description=f"Accessibility test for {component.name}",
            test_type="accessibility",
            file_path=file_path,
            code=test_code,
            tags=["accessibility", "wcag", "a11y", "keyboard-navigation"],
            timeout=45000,
            dependencies=["@axe-core/playwright"]
        )
    
    def generate_visual_regression_test_case(self, component: UIComponent) -> PlaywrightTestCase:
        """Generate visual regression test case"""
        
        test_name = f"test_{component.name.lower()}_visual_regression"
        file_path = f"tests/visual/{component.name.lower()}.spec.ts"
        
        test_code = f"""import {{ test, expect }} from '@playwright/test';
import {{ {component.name}Page }} from '../pages/{component.name}Page';

test.describe('{component.name} Visual Regression Tests', () => {{
    test('{test_name}', async ({{ page }}) => {{
        const {component.name.lower()}Page = new {component.name}Page(page);
        await {component.name.lower()}Page.goto();
        
        // Wait for glassmorphism effects to settle
        await page.waitForTimeout(1000);
        
        // Test desktop view
        await page.setViewportSize({{ width: 1920, height: 1080 }});
        await expect(page).toHaveScreenshot('{component.name.lower()}-desktop.png', {{
            fullPage: true,
            threshold: 0.2
        }});
        
        // Test tablet view
        await page.setViewportSize({{ width: 768, height: 1024 }});
        await expect(page).toHaveScreenshot('{component.name.lower()}-tablet.png', {{
            fullPage: true,
            threshold: 0.2
        }});
        
        // Test mobile view
        await page.setViewportSize({{ width: 375, height: 667 }});
        await expect(page).toHaveScreenshot('{component.name.lower()}-mobile.png', {{
            fullPage: true,
            threshold: 0.2
        }});
        
        // Test glassmorphism hover effects
        await page.setViewportSize({{ width: 1920, height: 1080 }});
        const glassElements = await page.locator('{self.glassmorphism_selectors["glass_container"]}').all();
        
        if (glassElements.length > 0) {{
            await glassElements[0].hover();
            await page.waitForTimeout(300); // Wait for hover animations
            await expect(page).toHaveScreenshot('{component.name.lower()}-hover-state.png', {{
                threshold: 0.3
            }});
        }}
        
        // Test dark mode if available
        await page.emulateMedia({{ colorScheme: 'dark' }});
        await page.waitForTimeout(500);
        await expect(page).toHaveScreenshot('{component.name.lower()}-dark-mode.png', {{
            fullPage: true,
            threshold: 0.3
        }});
        
        // Test high contrast mode
        await page.emulateMedia({{ colorScheme: 'light' }});
        await page.addStyleTag({{
            content: `
                * {{
                    filter: contrast(150%) !important;
                }}
            `
        }});
        await page.waitForTimeout(500);
        await expect(page).toHaveScreenshot('{component.name.lower()}-high-contrast.png', {{
            fullPage: true,
            threshold: 0.4
        }});
    }});
}});"""
        
        return PlaywrightTestCase(
            name=test_name,
            description=f"Visual regression test for {component.name}",
            test_type="visual",
            file_path=file_path,
            code=test_code,
            tags=["visual-regression", "responsive", "glassmorphism"],
            timeout=90000
        )
    
    def generate_playwright_config(self, project_id: str, test_suite: PlaywrightTestSuite) -> str:
        """Generate Playwright configuration file"""
        
        config = f"""import {{ defineConfig, devices }} from '@playwright/test';

/**
 * Playwright Configuration for {project_id}
 * Generated by QA Agent - Night 40
 */
export default defineConfig({{
    testDir: './tests',
    /* Maximum time one test can run for */
    timeout: 60 * 1000,
    expect: {{
        /* Maximum time expect() should wait for the condition to be met */
        timeout: 10000,
        /* Threshold for visual regression tests */
        threshold: 0.2,
    }},
    /* Run tests in files in parallel */
    fullyParallel: true,
    /* Fail the build on CI if you accidentally left test.only in the source code */
    forbidOnly: !!process.env.CI,
    /* Retry on CI only */
    retries: process.env.CI ? 2 : 1,
    /* Opt out of parallel tests on CI */
    workers: process.env.CI ? 1 : undefined,
    /* Reporter to use */
    reporter: [
        ['html'],
        ['json', {{ outputFile: 'test-results/results.json' }}],
        ['junit', {{ outputFile: 'test-results/junit.xml' }}]
    ],
    /* Shared settings for all the projects below */
    use: {{
        /* Base URL to use in actions like `await page.goto('/')` */
        baseURL: process.env.BASE_URL || 'http://localhost:3000',
        /* Collect trace when retrying the failed test */
        trace: 'on-first-retry',
        /* Take screenshot on failure */
        screenshot: 'only-on-failure',
        /* Record video on failure */
        video: 'retain-on-failure',
        /* Global timeout for all actions */
        actionTimeout: 10000,
        /* Global timeout for navigation */
        navigationTimeout: 30000,
    }},

    /* Configure projects for major browsers */
    projects: ["""
        
        for browser in test_suite.browsers:
            browser_config = {
                'chromium': 'Desktop Chrome',
                'firefox': 'Desktop Firefox', 
                'webkit': 'Desktop Safari'
            }.get(browser, browser)
            
            config += f"""
        {{
            name: '{browser}',
            use: {{ ...devices['{browser_config}'] }},
        }},"""
        
        config += """
        /* Mobile browsers */
        {
            name: 'Mobile Chrome',
            use: { ...devices['Pixel 5'] },
        },
        {
            name: 'Mobile Safari',
            use: { ...devices['iPhone 12'] },
        },
        
        /* Tablet browsers */
        {
            name: 'Tablet',
            use: { ...devices['iPad Pro'] },
        },
    ],

    /* Global setup and teardown */
    globalSetup: require.resolve('./tests/global-setup'),
    globalTeardown: require.resolve('./tests/global-teardown'),
    
    /* Test output directories */
    outputDir: 'test-results/',
    
    /* Configure local dev server */
    webServer: {
        command: 'npm run dev',
        url: 'http://localhost:3000',
        reuseExistingServer: !process.env.CI,
        timeout: 120 * 1000,
    },
});"""
        
        return config
    
    def generate_global_setup(self) -> str:
        """Generate global setup file"""
        
        return """import { chromium, FullConfig } from '@playwright/test';
import { TenantDatabase } from '../agents/shared/tenant_db';

async function globalSetup(config: FullConfig) {
    console.log('🚀 Starting Playwright global setup...');
    
    // Set up test database
    const tenantDb = new TenantDatabase();
    await tenantDb.createTestTenant('playwright-test-tenant');
    
    // Launch browser for authentication
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Perform any global authentication
    await page.goto(process.env.BASE_URL || 'http://localhost:3000');
    
    // Store authentication state if needed
    await page.context().storageState({ path: 'tests/auth.json' });
    
    await browser.close();
    
    console.log('✅ Playwright global setup completed');
}

export default globalSetup;"""
    
    def generate_global_teardown(self) -> str:
        """Generate global teardown file"""
        
        return """import { FullConfig } from '@playwright/test';
import { TenantDatabase } from '../agents/shared/tenant_db';

async function globalTeardown(config: FullConfig) {
    console.log('🧹 Starting Playwright global teardown...');
    
    // Clean up test data
    const tenantDb = new TenantDatabase();
    await tenantDb.cleanupTestTenant('playwright-test-tenant');
    
    console.log('✅ Playwright global teardown completed');
}

export default globalTeardown;"""
    
    def generate_fixtures(self) -> Dict[str, str]:
        """Generate common test fixtures"""
        
        fixtures = {}
        
        # Base test fixture
        fixtures['base-test.ts'] = """import { test as base, Page } from '@playwright/test';
import { TenantContext } from '../agents/shared/tenant_db';

export type TestFixtures = {
    tenantContext: TenantContext;
    authenticatedPage: Page;
};

export const test = base.extend<TestFixtures>({
    tenantContext: async ({}, use) => {
        const context = {
            tenant_id: 'playwright-test-tenant',
            user_id: 'test-user'
        };
        await use(context);
    },
    
    authenticatedPage: async ({ page, tenantContext }, use) => {
        // Set tenant context headers
        await page.setExtraHTTPHeaders({
            'X-Tenant-ID': tenantContext.tenant_id,
            'X-User-ID': tenantContext.user_id
        });
        
        // Load authentication state if available
        try {
            await page.context().addInitScript(() => {
                localStorage.setItem('tenant_id', 'playwright-test-tenant');
            });
        } catch (error) {
            console.warn('Could not load auth state:', error);
        }
        
        await use(page);
    }
});

export { expect } from '@playwright/test';"""
        
        # API testing helper
        fixtures['api-helper.ts'] = """import { APIRequestContext, expect } from '@playwright/test';

export class ApiHelper {
    constructor(private request: APIRequestContext) {}
    
    async get(endpoint: string, tenantId: string = 'playwright-test-tenant') {
        return await this.request.get(endpoint, {
            headers: {
                'X-Tenant-ID': tenantId
            }
        });
    }
    
    async post(endpoint: string, data: any, tenantId: string = 'playwright-test-tenant') {
        return await this.request.post(endpoint, {
            data,
            headers: {
                'Content-Type': 'application/json',
                'X-Tenant-ID': tenantId
            }
        });
    }
    
    async expectSuccess(response: any) {
        expect([200, 201, 204]).toContain(response.status());
        return await response.json();
    }
    
    async expectError(response: any, expectedStatus: number) {
        expect(response.status()).toBe(expectedStatus);
    }
}"""
        
        return fixtures
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.capitalize() for x in components[1:])
    
    def generate_complete_test_suite(self, 
                                   project_id: str, 
                                   ui_components: List[UIComponent],
                                   api_endpoints: List[Dict[str, str]]) -> PlaywrightTestSuite:
        """Generate a complete Playwright test suite"""
        
        test_cases = []
        setup_files = {}
        fixtures = self.generate_fixtures()
        
        # Generate Page Object Models
        for component in ui_components:
            page_object = self.generate_page_object_model(component)
            setup_files[f"pages/{component.name}Page.ts"] = page_object
        
        # Generate E2E tests for each component
        for component in ui_components:
            # Core functionality tests
            test_cases.append(self.generate_e2e_test_case(component, "user_interaction"))
            test_cases.append(self.generate_e2e_test_case(component, "navigation"))
            
            # Quality tests
            test_cases.append(self.generate_performance_test_case(component))
            test_cases.append(self.generate_accessibility_test_case(component))
            test_cases.append(self.generate_visual_regression_test_case(component))
        
        # Generate API tests
        for endpoint in api_endpoints:
            for scenario in ["success", "authentication", "validation"]:
                test_cases.append(self.generate_api_test_case(
                    endpoint["path"], 
                    endpoint["method"], 
                    scenario
                ))
        
        # Generate configuration
        test_suite = PlaywrightTestSuite(
            name=f"{project_id}_playwright_suite",
            project_id=project_id,
            test_cases=test_cases,
            config={
                "browsers": ["chromium", "firefox", "webkit"],
                "retries": 2,
                "timeout": 60000,
                "workers": 4
            },
            setup_files=setup_files,
            fixtures=fixtures,
            estimated_duration=len(test_cases) * 2  # 2 minutes per test
        )
        
        # Add configuration files
        setup_files["playwright.config.ts"] = self.generate_playwright_config(project_id, test_suite)
        setup_files["tests/global-setup.ts"] = self.generate_global_setup()
        setup_files["tests/global-teardown.ts"] = self.generate_global_teardown()
        
        return test_suite 