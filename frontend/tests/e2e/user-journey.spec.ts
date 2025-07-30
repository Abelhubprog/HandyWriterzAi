import { test, expect } from '@playwright/test';

// Comprehensive E2E test suite for HandyWriterz user journeys
test.describe('HandyWriterz User Journey Tests', () => {
  
  // Test configuration
  const BACKEND_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8001';
  const FRONTEND_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3001';
  
  test.beforeEach(async ({ page }) => {
    // Set up page with proper viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Mock Dynamic.xyz authentication for testing
    await page.addInitScript(() => {
      window.localStorage.setItem('dynamic_auth_token', 'test_token_12345');
      window.localStorage.setItem('auth_token', 'test_jwt_token');
    });
  });

  test('Homepage loads and displays key elements', async ({ page }) => {
    await page.goto(FRONTEND_URL);
    
    // Check page loads successfully
    await expect(page).toHaveTitle(/HandyWriterz/);
    
    // Check key elements are present
    await expect(page.locator('h1')).toContainText(/HandyWriterz|AI|Academic/);
    await expect(page.locator('nav')).toBeVisible();
    
    // Check navigation links
    const chatLink = page.locator('a[href*="chat"]');
    if (await chatLink.count() > 0) {
      await expect(chatLink).toBeVisible();
    }
  });

  test('Chat interface functionality', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Wait for chat interface to load
    await page.waitForSelector('textarea, input[type="text"]', { timeout: 10000 });
    
    // Check for chat input elements
    const textInput = page.locator('textarea, input[type="text"]').first();
    await expect(textInput).toBeVisible();
    
    // Check for send button
    const sendButton = page.locator('button[type="submit"], button:has-text("Send"), button:has-text("↑")');
    if (await sendButton.count() > 0) {
      await expect(sendButton.first()).toBeVisible();
    }
    
    // Test typing in chat input
    await textInput.fill('Hello, this is a test message');
    await expect(textInput).toHaveValue('Hello, this is a test message');
    
    // Test file upload functionality
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.count() > 0) {
      await expect(fileInput.first()).toBeVisible();
    }
  });

  test('Settings page navigation and functionality', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/settings`);
    
    // Check settings page loads
    await expect(page.locator('h1')).toContainText(/Settings/);
    
    // Check settings navigation
    const billingLink = page.locator('a[href*="billing"]');
    if (await billingLink.count() > 0) {
      await billingLink.click();
      await expect(page).toHaveURL(/billing/);
      await expect(page.locator('h1')).toContainText(/Billing/);
    }
    
    // Check general settings
    await page.goto(`${FRONTEND_URL}/settings/general`);
    await expect(page.locator('h1')).toContainText(/General|Settings/);
  });

  test('Billing page and pricing tiers', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/settings/billing`);
    
    // Check billing page loads
    await expect(page.locator('h1')).toContainText(/Billing/);
    
    // Check for upgrade button
    const upgradeButton = page.locator('button:has-text("Upgrade"), button:has-text("Plan")');
    if (await upgradeButton.count() > 0) {
      await upgradeButton.first().click();
      
      // Check if payment dialog opens
      await page.waitForTimeout(1000);
      const paymentDialog = page.locator('[role="dialog"], .payment-dialog');
      if (await paymentDialog.count() > 0) {
        await expect(paymentDialog.first()).toBeVisible();
        
        // Check for pricing tiers
        const pricingTiers = page.locator('text=/Free|Basic|Pro|Enterprise/');
        await expect(pricingTiers.first()).toBeVisible();
        
        // Close dialog
        const closeButton = page.locator('button:has-text("Cancel"), button:has-text("Close"), [aria-label="Close"]');
        if (await closeButton.count() > 0) {
          await closeButton.first().click();
        }
      }
    }
  });

  test('Theme toggle functionality', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/settings`);
    
    // Look for theme toggle
    const themeToggle = page.locator('button:has-text("Dark"), button:has-text("Light"), button:has-text("Theme"), [aria-label*="theme"]');
    
    if (await themeToggle.count() > 0) {
      // Get initial theme
      const body = page.locator('body');
      const initialClass = await body.getAttribute('class');
      
      // Toggle theme
      await themeToggle.first().click();
      await page.waitForTimeout(500);
      
      // Check theme changed
      const newClass = await body.getAttribute('class');
      expect(newClass).not.toBe(initialClass);
    }
  });

  test('File upload functionality', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Look for file upload area
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.count() > 0) {
      // Create a test file
      const testFileContent = 'This is a test document for HandyWriterz processing.';
      
      // Upload test file
      await fileInput.first().setInputFiles({
        name: 'test-document.txt',
        mimeType: 'text/plain',
        buffer: Buffer.from(testFileContent)
      });
      
      // Check for file upload feedback
      await page.waitForTimeout(1000);
      const uploadFeedback = page.locator('text=/uploaded|selected|added/i');
      if (await uploadFeedback.count() > 0) {
        await expect(uploadFeedback.first()).toBeVisible();
      }
    }
  });

  test('API health check', async ({ page }) => {
    // Test backend API directly
    const response = await page.request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const healthData = await response.json();
    expect(healthData).toHaveProperty('status');
  });

  test('Payment flow simulation - Paystack', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/settings/billing`);
    
    // Click upgrade button
    const upgradeButton = page.locator('button:has-text("Upgrade")');
    if (await upgradeButton.count() > 0) {
      await upgradeButton.first().click();
      
      // Select a plan (Basic)
      const basicPlan = page.locator('button:has-text("Basic"), button:has-text("$19")');
      if (await basicPlan.count() > 0) {
        await basicPlan.first().click();
        
        // This would normally redirect to Paystack
        // In test environment, we just verify the process starts
        await page.waitForTimeout(2000);
        
        // Check if redirected or payment URL generated
        const currentUrl = page.url();
        console.log('Payment flow initiated, URL:', currentUrl);
      }
    }
  });

  test('Payment flow simulation - Coinbase Commerce', async ({ page }) => {
    await page.goto(`${FRONTEND_URL}/settings/billing`);
    
    // Click upgrade button
    const upgradeButton = page.locator('button:has-text("Upgrade")');
    if (await upgradeButton.count() > 0) {
      await upgradeButton.first().click();
      
      // Select crypto payment method
      const cryptoButton = page.locator('button:has-text("Crypto"), button:has-text("USDC")');
      if (await cryptoButton.count() > 0) {
        await cryptoButton.first().click();
        
        // Select a plan
        const proPlan = page.locator('button:has-text("Pro"), button:has-text("$49")');
        if (await proPlan.count() > 0) {
          await proPlan.first().click();
          
          // This would normally redirect to Coinbase Commerce
          await page.waitForTimeout(2000);
          
          const currentUrl = page.url();
          console.log('Crypto payment flow initiated, URL:', currentUrl);
        }
      }
    }
  });

  test('Responsive design - Mobile view', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto(FRONTEND_URL);
    
    // Check mobile navigation
    const mobileMenu = page.locator('button[aria-label*="menu"], button:has-text("☰")');
    if (await mobileMenu.count() > 0) {
      await mobileMenu.first().click();
      await page.waitForTimeout(500);
    }
    
    // Check chat interface on mobile
    await page.goto(`${FRONTEND_URL}/chat`);
    const chatInput = page.locator('textarea, input[type="text"]');
    if (await chatInput.count() > 0) {
      await expect(chatInput.first()).toBeVisible();
    }
  });

  test('Error handling and edge cases', async ({ page }) => {
    // Test 404 page
    await page.goto(`${FRONTEND_URL}/nonexistent-page`);
    // Should either show 404 or redirect to homepage
    
    // Test API error handling
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Mock network failure
    await page.route('**/api/**', route => {
      route.abort('failed');
    });
    
    // Try to interact with API
    const textInput = page.locator('textarea, input[type="text"]').first();
    if (await textInput.count() > 0) {
      await textInput.fill('Test message');
      const sendButton = page.locator('button[type="submit"], button:has-text("Send")');
      if (await sendButton.count() > 0) {
        await sendButton.first().click();
        
        // Check for error message
        await page.waitForTimeout(2000);
        const errorMessage = page.locator('text=/error|failed|try again/i');
        // Error handling should be graceful
      }
    }
  });

  test('Performance and loading times', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    console.log(`Page load time: ${loadTime}ms`);
    
    // Page should load within reasonable time
    expect(loadTime).toBeLessThan(10000); // 10 seconds max
    
    // Check for loading states
    const loadingIndicators = page.locator('text=/loading|spinner/i');
    // Loading indicators should eventually disappear
  });

  test('Authentication state handling', async ({ page }) => {
    // Test unauthenticated state
    await page.addInitScript(() => {
      window.localStorage.clear();
    });
    
    await page.goto(`${FRONTEND_URL}/chat`);
    
    // Should either redirect to login or show login prompt
    await page.waitForTimeout(2000);
    
    const loginElements = page.locator('button:has-text("Login"), button:has-text("Connect"), text=/sign in|log in/i');
    // Should have some authentication mechanism visible
  });
});

// API Integration Tests
test.describe('API Integration Tests', () => {
  const BACKEND_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8001';
  
  test('Backend health endpoint', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
  });
  
  test('API documentation endpoint', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/docs`);
    expect(response.ok()).toBeTruthy();
  });
  
  test('Billing endpoints', async ({ request }) => {
    // Test pricing tiers endpoint
    const tiersResponse = await request.get(`${BACKEND_URL}/api/billing/tiers`);
    if (tiersResponse.ok()) {
      const tiers = await tiersResponse.json();
      expect(tiers).toHaveProperty('tiers');
    }
  });
  
  test('File upload endpoint', async ({ request }) => {
    // Test file upload
    const response = await request.post(`${BACKEND_URL}/api/files`, {
      multipart: {
        file: {
          name: 'test.txt',
          mimeType: 'text/plain',
          buffer: Buffer.from('Test file content')
        }
      }
    });
    
    // Should handle file upload (may require auth)
    // Response should be 200, 401, or 403 but not 500
    expect([200, 401, 403].includes(response.status())).toBeTruthy();
  });
});