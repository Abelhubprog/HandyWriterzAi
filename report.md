PS D:\HandyWriterzAi> pnpm i
Scope: all 2 workspace projects

   ╭──────────────────────────────────────────╮
   │                                          │
   │   Update available! 10.8.0 → 10.14.0.    │
   │   Changelog: https://pnpm.io/v/10.14.0   │
   │     To update, run: pnpm self-update     │
   │                                          │
   ╰──────────────────────────────────────────╯

frontend                                 |  WARN  deprecated eslint@8.57.1
 WARN  7 deprecated subdependencies found: @humanwhocodes/config-array@0.13.0, @humanwhocodes/object-schema@2.0.3, abab@2.0.6, domexception@4.0.0, glob@7.2.3, inflight@1.0.6, rimraf@3.0.2
Packages: +257
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
Progress: resolved 974, reused 828, downloaded 80, added 257, done
Done in 11m 10.4s using pnpm v10.8.0
PS D:\HandyWriterzAi> pnpm dlx playwright install
Packages: +2
++
Progress: resolved 3, reused 0, downloaded 2, added 2, done
Removing unused browser at C:\Users\USER\AppData\Local\ms-playwright\chromium-1169
Removing unused browser at C:\Users\USER\AppData\Local\ms-playwright\chromium_headless_shell-1169
PS D:\HandyWriterzAi> pnpm test
'test' is not recognized as an internal or external command,
operable program or batch file.
 ERR_PNPM_RECURSIVE_EXEC_FIRST_FAIL  Command "test" not found
PS D:\HandyWriterzAi> pnpm test:e2e
The filename, directory name, or volume label syntax is incorrect.
 ERR_PNPM_RECURSIVE_EXEC_FIRST_FAIL  Command "test:e2e" not found
PS D:\HandyWriterzAi> cd frontend
PS D:\HandyWriterzAi\frontend> npx playwright install
PS D:\HandyWriterzAi\frontend>  pnpm install
Scope: all 2 workspace projects
Done in 7.3s using pnpm v10.8.0
PS D:\HandyWriterzAi\frontend> pnpm test

> handywriterz@0.1.0 test D:\HandyWriterzAi\frontend
> jest

 FAIL  tests/e2e/user-journey.spec.ts
  ● Test suite failed to run

    Playwright Test needs to be invoked via 'pnpm exec playwright test' and excluded from Jest test runs.
    Creating one directory for Playwright tests and one for Jest is the recommended way of doing it. 
    See https://playwright.dev/docs/intro for more information about Playwright Test.

      2 |
      3 | // Comprehensive E2E test suite for HandyWriterz user journeys
    > 4 | test.describe('HandyWriterz User Journey Tests', () => {
        |      ^
      5 |
      6 |   // Test configuration
      7 |   const BACKEND_URL = process.env.PLAYWRIGHT_API_URL || 'http://localhost:8001';

      at throwIfRunningInsideJest (../node_modules/.pnpm/playwright@1.54.2/node_modules/playwright/lib/common/testType.js:272:11)
      at TestTypeImpl._describe (../node_modules/.pnpm/playwright@1.54.2/node_modules/playwright/lib/common/testType.js:113:5)
      at Function.describe (../node_modules/.pnpm/playwright@1.54.2/node_modules/playwright/lib/transform/transform.js:275:12)
      at Object.describe (tests/e2e/user-journey.spec.ts:4:6)

 FAIL  tests/e2e/chat.spec.ts
  ● Test suite failed to run

    Playwright Test needs to be invoked via 'pnpm exec playwright test' and excluded from Jest test runs.
    Creating one directory for Playwright tests and one for Jest is the recommended way of doing it. 
    See https://playwright.dev/docs/intro for more information about Playwright Test.

      10 | }
      11 |
    > 12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
         |      ^
      13 |   test.beforeEach(async ({ page, baseURL }) => {
      14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
      15 |     // Sidebar and ChatPane basic smoke

      at throwIfRunningInsideJest (../node_modules/.pnpm/playwright@1.54.2/node_modules/playwright/lib/common/testType.js:272:11)
      at TestTypeImpl._describe (../node_modules/.pnpm/playwright@1.54.2/node_modules/playwright/lib/common/testType.js:113:5)
      at Function.describe (../node_modules/.pnpm/playwright@1.54.2/node_modules/playwright/lib/transform/transform.js:275:12)
      at Object.describe (tests/e2e/chat.spec.ts:12:6)

 PASS  src/__tests__/smoke.test.tsx (34.335 s)

Test Suites: 2 failed, 1 passed, 3 total
Tests:       1 passed, 1 total
Snapshots:   0 total
Time:        55.608 s
Ran all test suites.
 ELIFECYCLE  Test failed. See above for more details.
PS D:\HandyWriterzAi\frontend> pnpm test:e2e

> handywriterz@0.1.0 test:e2e D:\HandyWriterzAi\frontend
> playwright test


Running 69 tests using 2 workers

  ✘  1 …nd-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream (9.1s)  ✘  2 …d Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream (9.1s)  ✘  3 … - Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response (4.8s)  ✘  4 … End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default (4.3s)  ✘  5 …0:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility (4.3s)  ✘  6 …-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry (4.3s)  ✘  7 …-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality (4.1s)  ✘  8 …c.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements (3.9s)  ✘  9 …ts:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality (3.8s)  ✘  10 …urney.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers (3.9s)  ✘  11 …-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality (3.8s)  ✘  12 …r-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality (3.8s)  ✘  13 …s\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check (1.1s)  ✘  14 …193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce (3.9s)  ✘  15 ….spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack (3.6s)  ✘  16 …ney.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view (4.8s)  ✘  17 …urney.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases (4.4s)  ✘  18 …urney.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times (4.1s)  ✘  19 …urney.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling (3.9s)  ✘  20 …sts\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint (544ms)  ✘  21 …] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints (771ms)  ✘  22 …\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint (603ms)  ✘  23 … tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint (680ms)  ✘  24 … Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream (9.3s)  ✘  25 …-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream (12.1s)  ✘  26 …End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default (7.0s)  ✘  27 …- Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response (7.2s)  ✘  28 …:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility (6.8s)  ✘  29 …End › 6) Error fallback: invalid model or missing key -> user-facing error with retry (7.0s)  ✘  30 ….ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements (6.6s)  ✘  31 …journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality (6.5s)  ✘  32 …s:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality (6.2s)  ✘  33 …urney.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers (6.0s)  ✘  34 …-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality (6.4s)  ✘  35 …r-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality (6.5s)  ✘  36 …s\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check (4.1s)  ✘  37 ….spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack (6.3s)  ✘  38 …193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce (6.2s)  ✘  39 …ney.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view (7.2s)  ✘  40 …urney.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases (7.0s)  ✘  41 …urney.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times (6.5s)  ✘  42 …urney.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling (7.3s)  ✘  43 …sts\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint (767ms)  ✘  44 …\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint (526ms)  ✘  45 … tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint (633ms)  ✘  46 …] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints (583ms)  ✘  47 … Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream (5.3s)  ✘  48 …d-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream (5.5s)  ✘  49 …End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default (4.9s)  ✘  50 …- Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response (4.6s)  ✘  51 …:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility (4.6s)  ✘  52 …End › 6) Error fallback: invalid model or missing key -> user-facing error with retry (4.6s)  ✘  53 ….ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements (4.8s)  ✘  54 …journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality (4.4s)  ✘  55 …s:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality (4.8s)  ✘  56 …urney.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers (4.6s)  ✘  57 …-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality (4.9s)  ✘  58 …r-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality (5.6s)  ✘  59 …s\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check (2.5s)  ✘  60 ….spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack (4.9s)  ✘  61 …193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce (5.2s)  ✘  62 …ney.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view (5.2s)  ✘  63 …urney.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases (5.7s)  ✘  64 …urney.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling (4.3s)  ✘  65 …urney.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times (4.7s)
  ✘  66 …sts\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint (554ms)  ✘  67 …\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint (716ms)  ✘  68 …] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints (647ms)  ✘  69 … tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint (507ms)

  1) [chromium] › tests\e2e\chat.spec.ts:19:7 › Claude.md Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/chat
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  2) [chromium] › tests\e2e\chat.spec.ts:36:7 › Claude.md Journeys - Chat End-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/chat
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  3) [chromium] › tests\e2e\chat.spec.ts:59:7 › Claude.md Journeys - Chat End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/chat
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  4) [chromium] › tests\e2e\chat.spec.ts:83:7 › Claude.md Journeys - Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/chat
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  5) [chromium] › tests\e2e\chat.spec.ts:100:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/chat
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  6) [chromium] › tests\e2e\chat.spec.ts:106:7 › Claude.md Journeys - Chat End-to-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3000/chat
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  7) [chromium] › tests\e2e\user-journey.spec.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      20 |
      21 |   test('Homepage loads and displays key elements', async ({ page }) => {
    > 22 |     await page.goto(FRONTEND_URL);
         |                ^
      23 |
      24 |     // Check page loads successfully
      25 |     await expect(page).toHaveTitle(/HandyWriterz/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:22:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  8) [chromium] › tests\e2e\user-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/chat
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      37 |
      38 |   test('Chat interface functionality', async ({ page }) => {
    > 39 |     await page.goto(`${FRONTEND_URL}/chat`);
         |                ^
      40 |
      41 |     // Wait for chat interface to load
      42 |     await page.waitForSelector('textarea, input[type="text"]', { timeout: 10000 });       
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:39:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  9) [chromium] › tests\e2e\user-journey.spec.ts:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/settings
    Call log:
      - navigating to "http://localhost:3001/settings", waiting until "load"


      64 |
      65 |   test('Settings page navigation and functionality', async ({ page }) => {
    > 66 |     await page.goto(`${FRONTEND_URL}/settings`);
         |                ^
      67 |
      68 |     // Check settings page loads
      69 |     await expect(page.locator('h1')).toContainText(/Settings/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:66:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  10) [chromium] › tests\e2e\user-journey.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/settings/billing
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      83 |
      84 |   test('Billing page and pricing tiers', async ({ page }) => {
    > 85 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
         |                ^
      86 |
      87 |     // Check billing page loads
      88 |     await expect(page.locator('h1')).toContainText(/Billing/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:85:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  11) [chromium] › tests\e2e\user-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/settings
    Call log:
      - navigating to "http://localhost:3001/settings", waiting until "load"


      113 |
      114 |   test('Theme toggle functionality', async ({ page }) => {
    > 115 |     await page.goto(`${FRONTEND_URL}/settings`);
          |                ^
      116 |
      117 |     // Look for theme toggle
      118 |     const themeToggle = page.locator('button:has-text("Dark"), button:has-text("Light"), 
button:has-text("Theme"), [aria-label*="theme"]');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:115:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  12) [chromium] › tests\e2e\user-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/chat
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      134 |
      135 |   test('File upload functionality', async ({ page }) => {
    > 136 |     await page.goto(`${FRONTEND_URL}/chat`);
          |                ^
      137 |
      138 |     // Look for file upload area
      139 |     const fileInput = page.locator('input[type="file"]');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:136:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  13) [chromium] › tests\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/health
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.5 Safari/537.36
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:162:41

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  14) [chromium] › tests\e2e\user-journey.spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/settings/billing
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      168 |
      169 |   test('Payment flow simulation - Paystack', async ({ page }) => {
    > 170 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
          |                ^
      171 |
      172 |     // Click upgrade button
      173 |     const upgradeButton = page.locator('button:has-text("Upgrade")');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:170:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  15) [chromium] › tests\e2e\user-journey.spec.ts:193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/settings/billing
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      192 |
      193 |   test('Payment flow simulation - Coinbase Commerce', async ({ page }) => {
    > 194 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
          |                ^
      195 |
      196 |     // Click upgrade button
      197 |     const upgradeButton = page.locator('button:has-text("Upgrade")');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:194:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  16) [chromium] › tests\e2e\user-journey.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      223 |     await page.setViewportSize({ width: 375, height: 667 });
      224 |
    > 225 |     await page.goto(FRONTEND_URL);
          |                ^
      226 |
      227 |     // Check mobile navigation
      228 |     const mobileMenu = page.locator('button[aria-label*="menu"], button:has-text("☰")'); 
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:225:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  17) [chromium] › tests\e2e\user-journey.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/nonexistent-page
    Call log:
      - navigating to "http://localhost:3001/nonexistent-page", waiting until "load"


      242 |   test('Error handling and edge cases', async ({ page }) => {
      243 |     // Test 404 page
    > 244 |     await page.goto(`${FRONTEND_URL}/nonexistent-page`);
          |                ^
      245 |     // Should either show 404 or redirect to homepage
      246 |
      247 |     // Test API error handling
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:244:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  18) [chromium] › tests\e2e\user-journey.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      272 |     const startTime = Date.now();
      273 |
    > 274 |     await page.goto(FRONTEND_URL);
          |                ^
      275 |     await page.waitForLoadState('networkidle');
      276 |
      277 |     const loadTime = Date.now() - startTime;
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:274:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  19) [chromium] › tests\e2e\user-journey.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling

    Error: page.goto: net::ERR_CONNECTION_REFUSED at http://localhost:3001/chat
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      292 |     });
      293 |
    > 294 |     await page.goto(`${FRONTEND_URL}/chat`);
          |                ^
      295 |
      296 |     // Should either redirect to login or show login prompt
      297 |     await page.waitForTimeout(2000);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:294:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-chromium\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-chromium\video.webm    
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--31711-thentication-state-handling-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  20) [chromium] › tests\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/health
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.5 Safari/537.36
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:309:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-Backend-health-endpoint-chromium\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-Backend-health-endpoint-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  21) [chromium] › tests\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/docs
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.5 Safari/537.36
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:317:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integrati-12a6e--API-documentation-endpoint-chromium\trace.zip     
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integrati-12a6e--API-documentation-endpoint-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  22) [chromium] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints 

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/api/billing/tiers
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.5 Safari/537.36
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:323:41

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-Billing-endpoints-chromium\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-Billing-endpoints-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  23) [chromium] › tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint

    Error: apiRequestContext.post: connect ECONNREFUSED ::1:8001
    Call log:
      - → POST http://localhost:8001/api/files
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.5 Safari/537.36
        - accept: */*
        - accept-encoding: gzip,deflate,br
        - content-type: multipart/form-data; boundary=----WebKitFormBoundaryPpgdYkbkEHhiHyCw
        - content-length: 199

        at apiRequestContext.post: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:332:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-File-upload-endpoint-chromium\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-File-upload-endpoint-chromium\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  24) [firefox] › tests\e2e\chat.spec.ts:19:7 › Claude.md Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  25) [firefox] › tests\e2e\chat.spec.ts:36:7 › Claude.md Journeys - Chat End-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  26) [firefox] › tests\e2e\chat.spec.ts:59:7 › Claude.md Journeys - Chat End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  27) [firefox] › tests\e2e\chat.spec.ts:83:7 › Claude.md Journeys - Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  28) [firefox] › tests\e2e\chat.spec.ts:100:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  29) [firefox] › tests\e2e\chat.spec.ts:106:7 › Claude.md Journeys - Chat End-to-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  30) [firefox] › tests\e2e\user-journey.spec.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      20 |
      21 |   test('Homepage loads and displays key elements', async ({ page }) => {
    > 22 |     await page.goto(FRONTEND_URL);
         |                ^
      23 |
      24 |     // Check page loads successfully
      25 |     await expect(page).toHaveTitle(/HandyWriterz/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:22:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  31) [firefox] › tests\e2e\user-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      37 |
      38 |   test('Chat interface functionality', async ({ page }) => {
    > 39 |     await page.goto(`${FRONTEND_URL}/chat`);
         |                ^
      40 |
      41 |     // Wait for chat interface to load
      42 |     await page.waitForSelector('textarea, input[type="text"]', { timeout: 10000 });       
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:39:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  32) [firefox] › tests\e2e\user-journey.spec.ts:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/settings", waiting until "load"


      64 |
      65 |   test('Settings page navigation and functionality', async ({ page }) => {
    > 66 |     await page.goto(`${FRONTEND_URL}/settings`);
         |                ^
      67 |
      68 |     // Check settings page loads
      69 |     await expect(page.locator('h1')).toContainText(/Settings/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:66:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  33) [firefox] › tests\e2e\user-journey.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      83 |
      84 |   test('Billing page and pricing tiers', async ({ page }) => {
    > 85 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
         |                ^
      86 |
      87 |     // Check billing page loads
      88 |     await expect(page.locator('h1')).toContainText(/Billing/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:85:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  34) [firefox] › tests\e2e\user-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/settings", waiting until "load"


      113 |
      114 |   test('Theme toggle functionality', async ({ page }) => {
    > 115 |     await page.goto(`${FRONTEND_URL}/settings`);
          |                ^
      116 |
      117 |     // Look for theme toggle
      118 |     const themeToggle = page.locator('button:has-text("Dark"), button:has-text("Light"), 
button:has-text("Theme"), [aria-label*="theme"]');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:115:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  35) [firefox] › tests\e2e\user-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      134 |
      135 |   test('File upload functionality', async ({ page }) => {
    > 136 |     await page.goto(`${FRONTEND_URL}/chat`);
          |                ^
      137 |
      138 |     // Look for file upload area
      139 |     const fileInput = page.locator('input[type="file"]');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:136:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  36) [firefox] › tests\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/health
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0.2) Gecko/20100101 Firefox/140.0.2
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:162:41

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  37) [firefox] › tests\e2e\user-journey.spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      168 |
      169 |   test('Payment flow simulation - Paystack', async ({ page }) => {
    > 170 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
          |                ^
      171 |
      172 |     // Click upgrade button
      173 |     const upgradeButton = page.locator('button:has-text("Upgrade")');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:170:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  38) [firefox] › tests\e2e\user-journey.spec.ts:193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      192 |
      193 |   test('Payment flow simulation - Coinbase Commerce', async ({ page }) => {
    > 194 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
          |                ^
      195 |
      196 |     // Click upgrade button
      197 |     const upgradeButton = page.locator('button:has-text("Upgrade")');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:194:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  39) [firefox] › tests\e2e\user-journey.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      223 |     await page.setViewportSize({ width: 375, height: 667 });
      224 |
    > 225 |     await page.goto(FRONTEND_URL);
          |                ^
      226 |
      227 |     // Check mobile navigation
      228 |     const mobileMenu = page.locator('button[aria-label*="menu"], button:has-text("☰")'); 
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:225:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  40) [firefox] › tests\e2e\user-journey.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/nonexistent-page", waiting until "load"


      242 |   test('Error handling and edge cases', async ({ page }) => {
      243 |     // Test 404 page
    > 244 |     await page.goto(`${FRONTEND_URL}/nonexistent-page`);
          |                ^
      245 |     // Should either show 404 or redirect to homepage
      246 |
      247 |     // Test API error handling
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:244:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  41) [firefox] › tests\e2e\user-journey.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      272 |     const startTime = Date.now();
      273 |
    > 274 |     await page.goto(FRONTEND_URL);
          |                ^
      275 |     await page.waitForLoadState('networkidle');
      276 |
      277 |     const loadTime = Date.now() - startTime;
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:274:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  42) [firefox] › tests\e2e\user-journey.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling

    Error: page.goto: NS_ERROR_CONNECTION_REFUSED
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      292 |     });
      293 |
    > 294 |     await page.goto(`${FRONTEND_URL}/chat`);
          |                ^
      295 |
      296 |     // Should either redirect to login or show login prompt
      297 |     await page.waitForTimeout(2000);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:294:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-firefox\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-firefox\video.webm     
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    Error Context: test-results\user-journey-HandyWriterz--31711-thentication-state-handling-firefox\error-context.md

    attachment #4: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--31711-thentication-state-handling-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  43) [firefox] › tests\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/health
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0.2) Gecko/20100101 Firefox/140.0.2
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:309:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-Backend-health-endpoint-firefox\trace.zip        
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-Backend-health-endpoint-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  44) [firefox] › tests\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/docs
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0.2) Gecko/20100101 Firefox/140.0.2
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:317:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integrati-12a6e--API-documentation-endpoint-firefox\trace.zip      
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integrati-12a6e--API-documentation-endpoint-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  45) [firefox] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints ─ 

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/api/billing/tiers
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0.2) Gecko/20100101 Firefox/140.0.2
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:323:41

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-Billing-endpoints-firefox\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-Billing-endpoints-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  46) [firefox] › tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint

    Error: apiRequestContext.post: connect ECONNREFUSED ::1:8001
    Call log:
      - → POST http://localhost:8001/api/files
        - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0.2) Gecko/20100101 Firefox/140.0.2
        - accept: */*
        - accept-encoding: gzip,deflate,br
        - content-type: multipart/form-data; boundary=----WebKitFormBoundaryHNg3LiZNN1AmOnJB
        - content-length: 199

        at apiRequestContext.post: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:332:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-File-upload-endpoint-firefox\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-File-upload-endpoint-firefox\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  47) [webkit] › tests\e2e\chat.spec.ts:19:7 › Claude.md Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----4d347---POST-api-chat---WS-stream-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  48) [webkit] › tests\e2e\chat.spec.ts:36:7 › Claude.md Journeys - Chat End-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----e547b---POST-api-chat---WS-stream-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  49) [webkit] › tests\e2e\chat.spec.ts:59:7 › Claude.md Journeys - Chat End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----1533f-eneral---OpenRouter-default-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  50) [webkit] › tests\e2e\chat.spec.ts:83:7 › Claude.md Journeys - Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----a3d26--PDF-PPT-ZIP-after-response-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  51) [webkit] › tests\e2e\chat.spec.ts:100:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----dfcb4-namic-xyz-button-visibility-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  52) [webkit] › tests\e2e\chat.spec.ts:106:7 › Claude.md Journeys - Chat End-to-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3000/chat", waiting until "load"


      12 | test.describe('Claude.md Journeys - Chat End-to-End', () => {
      13 |   test.beforeEach(async ({ page, baseURL }) => {
    > 14 |     await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
         |                ^
      15 |     // Sidebar and ChatPane basic smoke
      16 |     await expect(page).toHaveURL(/\/chat$/);
      17 |   });
        at D:\HandyWriterzAi\frontend\tests\e2e\chat.spec.ts:14:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\chat-Claude-md-Journeys----37551-ser-facing-error-with-retry-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  53) [webkit] › tests\e2e\user-journey.spec.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      20 |
      21 |   test('Homepage loads and displays key elements', async ({ page }) => {
    > 22 |     await page.goto(FRONTEND_URL);
         |                ^
      23 |
      24 |     // Check page loads successfully
      25 |     await expect(page).toHaveTitle(/HandyWriterz/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:22:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--52cc4-s-and-displays-key-elements-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  54) [webkit] › tests\e2e\user-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      37 |
      38 |   test('Chat interface functionality', async ({ page }) => {
    > 39 |     await page.goto(`${FRONTEND_URL}/chat`);
         |                ^
      40 |
      41 |     // Wait for chat interface to load
      42 |     await page.waitForSelector('textarea, input[type="text"]', { timeout: 10000 });       
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:39:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--01e6d-hat-interface-functionality-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  55) [webkit] › tests\e2e\user-journey.spec.ts:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/settings", waiting until "load"


      64 |
      65 |   test('Settings page navigation and functionality', async ({ page }) => {
    > 66 |     await page.goto(`${FRONTEND_URL}/settings`);
         |                ^
      67 |
      68 |     // Check settings page loads
      69 |     await expect(page.locator('h1')).toContainText(/Settings/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:66:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--51755-avigation-and-functionality-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  56) [webkit] › tests\e2e\user-journey.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      83 |
      84 |   test('Billing page and pricing tiers', async ({ page }) => {
    > 85 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
         |                ^
      86 |
      87 |     // Check billing page loads
      88 |     await expect(page.locator('h1')).toContainText(/Billing/);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:85:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--fb373-ling-page-and-pricing-tiers-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  57) [webkit] › tests\e2e\user-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/settings", waiting until "load"


      113 |
      114 |   test('Theme toggle functionality', async ({ page }) => {
    > 115 |     await page.goto(`${FRONTEND_URL}/settings`);
          |                ^
      116 |
      117 |     // Look for theme toggle
      118 |     const themeToggle = page.locator('button:has-text("Dark"), button:has-text("Light"), 
button:has-text("Theme"), [aria-label*="theme"]');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:115:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--6d8c0--Theme-toggle-functionality-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  58) [webkit] › tests\e2e\user-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      134 |
      135 |   test('File upload functionality', async ({ page }) => {
    > 136 |     await page.goto(`${FRONTEND_URL}/chat`);
          |                ^
      137 |
      138 |     // Look for file upload area
      139 |     const fileInput = page.locator('input[type="file"]');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:136:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--07580-s-File-upload-functionality-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  59) [webkit] › tests\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health 
check

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/health
        - user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:162:41

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--8eb58-rney-Tests-API-health-check-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  60) [webkit] › tests\e2e\user-journey.spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      168 |
      169 |   test('Payment flow simulation - Paystack', async ({ page }) => {
    > 170 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
          |                ^
      171 |
      172 |     // Click upgrade button
      173 |     const upgradeButton = page.locator('button:has-text("Upgrade")');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:170:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--8b2b2--flow-simulation---Paystack-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  61) [webkit] › tests\e2e\user-journey.spec.ts:193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/settings/billing", waiting until "load"


      192 |
      193 |   test('Payment flow simulation - Coinbase Commerce', async ({ page }) => {
    > 194 |     await page.goto(`${FRONTEND_URL}/settings/billing`);
          |                ^
      195 |
      196 |     // Click upgrade button
      197 |     const upgradeButton = page.locator('button:has-text("Upgrade")');
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:194:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--14e85-ulation---Coinbase-Commerce-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  62) [webkit] › tests\e2e\user-journey.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive 
design - Mobile view

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      223 |     await page.setViewportSize({ width: 375, height: 667 });
      224 |
    > 225 |     await page.goto(FRONTEND_URL);
          |                ^
      226 |
      227 |     // Check mobile navigation
      228 |     const mobileMenu = page.locator('button[aria-label*="menu"], button:has-text("☰")'); 
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:225:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--289e9-onsive-design---Mobile-view-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  63) [webkit] › tests\e2e\user-journey.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/nonexistent-page", waiting until "load"


      242 |   test('Error handling and edge cases', async ({ page }) => {
      243 |     // Test 404 page
    > 244 |     await page.goto(`${FRONTEND_URL}/nonexistent-page`);
          |                ^
      245 |     // Should either show 404 or redirect to homepage
      246 |
      247 |     // Test API error handling
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:244:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--1cc19-ror-handling-and-edge-cases-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  64) [webkit] › tests\e2e\user-journey.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/", waiting until "load"


      272 |     const startTime = Date.now();
      273 |
    > 274 |     await page.goto(FRONTEND_URL);
          |                ^
      275 |     await page.waitForLoadState('networkidle');
      276 |
      277 |     const loadTime = Date.now() - startTime;
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:274:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--9c75d-rformance-and-loading-times-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  65) [webkit] › tests\e2e\user-journey.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling

    Error: page.goto: Could not connect to server
    Call log:
      - navigating to "http://localhost:3001/chat", waiting until "load"


      292 |     });
      293 |
    > 294 |     await page.goto(`${FRONTEND_URL}/chat`);
          |                ^
      295 |
      296 |     // Should either redirect to login or show login prompt
      297 |     await page.waitForTimeout(2000);
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:294:16

    attachment #1: screenshot (image/png) ────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-webkit\test-failed-1.png
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #2: video (video/webm) ────────────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-webkit\video.webm      
    ──────────────────────────────────────────────────────────────────────────────────────────────── 

    attachment #3: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-HandyWriterz--31711-thentication-state-handling-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-HandyWriterz--31711-thentication-state-handling-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  66) [webkit] › tests\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/health
        - user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:309:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-Backend-health-endpoint-webkit\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-Backend-health-endpoint-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  67) [webkit] › tests\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/docs
        - user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:317:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integrati-12a6e--API-documentation-endpoint-webkit\trace.zip       
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integrati-12a6e--API-documentation-endpoint-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  68) [webkit] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints ── 

    Error: apiRequestContext.get: connect ECONNREFUSED ::1:8001
    Call log:
      - → GET http://localhost:8001/api/billing/tiers
        - user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15
        - accept: */*
        - accept-encoding: gzip,deflate,br

        at apiRequestContext.get: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:323:41

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-Billing-endpoints-webkit\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-Billing-endpoints-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  69) [webkit] › tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint 

    Error: apiRequestContext.post: connect ECONNREFUSED ::1:8001
    Call log:
      - → POST http://localhost:8001/api/files
        - user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15
        - accept: */*
        - accept-encoding: gzip,deflate,br
        - content-type: multipart/form-data; boundary=----WebKitFormBoundaryVfJ6H59p06k96fEB
        - content-length: 199

        at apiRequestContext.post: connect ECONNREFUSED ::1:8001
        at D:\HandyWriterzAi\frontend\tests\e2e\user-journey.spec.ts:332:36

    attachment #1: trace (application/zip) ───────────────────────────────────────────────────────── 
    test-results\user-journey-API-Integration-Tests-File-upload-endpoint-webkit\trace.zip
    Usage:

        pnpm exec playwright show-trace test-results\user-journey-API-Integration-Tests-File-upload-endpoint-webkit\trace.zip

    ──────────────────────────────────────────────────────────────────────────────────────────────── 

  69 failed
    [chromium] › tests\e2e\chat.spec.ts:19:7 › Claude.md Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream
    [chromium] › tests\e2e\chat.spec.ts:36:7 › Claude.md Journeys - Chat End-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream
    [chromium] › tests\e2e\chat.spec.ts:59:7 › Claude.md Journeys - Chat End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default
    [chromium] › tests\e2e\chat.spec.ts:83:7 › Claude.md Journeys - Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response
    [chromium] › tests\e2e\chat.spec.ts:100:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility
    [chromium] › tests\e2e\chat.spec.ts:106:7 › Claude.md Journeys - Chat End-to-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry
    [chromium] › tests\e2e\user-journey.spec.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements
    [chromium] › tests\e2e\user-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality
    [chromium] › tests\e2e\user-journey.spec.ts:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality
    [chromium] › tests\e2e\user-journey.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers
    [chromium] › tests\e2e\user-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality
    [chromium] › tests\e2e\user-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality
    [chromium] › tests\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health 
check
    [chromium] › tests\e2e\user-journey.spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack
    [chromium] › tests\e2e\user-journey.spec.ts:193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce
    [chromium] › tests\e2e\user-journey.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive 
design - Mobile view
    [chromium] › tests\e2e\user-journey.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases
    [chromium] › tests\e2e\user-journey.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times
    [chromium] › tests\e2e\user-journey.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling
    [chromium] › tests\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint
    [chromium] › tests\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint
    [chromium] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints ── 
    [chromium] › tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint 
    [firefox] › tests\e2e\chat.spec.ts:19:7 › Claude.md Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream
    [firefox] › tests\e2e\chat.spec.ts:36:7 › Claude.md Journeys - Chat End-to-End › 2) Upload files 
+ prompt -> POST /api/files -> POST /api/chat -> WS stream
    [firefox] › tests\e2e\chat.spec.ts:59:7 › Claude.md Journeys - Chat End-to-End › 3) Role routing: Researcher -> Perplexity, General -> OpenRouter default
    [firefox] › tests\e2e\chat.spec.ts:83:7 › Claude.md Journeys - Chat End-to-End › 4) Download menu presence (DOCX / PDF / PPT / ZIP) after response
    [firefox] › tests\e2e\chat.spec.ts:100:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility
    [firefox] › tests\e2e\chat.spec.ts:106:7 › Claude.md Journeys - Chat End-to-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry
    [firefox] › tests\e2e\user-journey.spec.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements
    [firefox] › tests\e2e\user-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality
    [firefox] › tests\e2e\user-journey.spec.ts:65:7 › HandyWriterz User Journey Tests › Settings page navigation and functionality
    [firefox] › tests\e2e\user-journey.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page 
and pricing tiers
    [firefox] › tests\e2e\user-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle functionality
    [firefox] › tests\e2e\user-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload 
functionality
    [firefox] › tests\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check
    [firefox] › tests\e2e\user-journey.spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow simulation - Paystack
    [firefox] › tests\e2e\user-journey.spec.ts:193:7 › HandyWriterz User Journey Tests › Payment flow simulation - Coinbase Commerce
    [firefox] › tests\e2e\user-journey.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view
    [firefox] › tests\e2e\user-journey.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases
    [firefox] › tests\e2e\user-journey.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance 
and loading times
    [firefox] › tests\e2e\user-journey.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling
    [firefox] › tests\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint
    [firefox] › tests\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint
    [firefox] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints ─── 
    [firefox] › tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint  
    [webkit] › tests\e2e\chat.spec.ts:19:7 › Claude.md Journeys - Chat End-to-End › 1) New chat: prompt-only -> POST /api/chat -> WS stream
    [webkit] › tests\e2e\chat.spec.ts:36:7 › Claude.md Journeys - Chat End-to-End › 2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream
    [webkit] › tests\e2e\chat.spec.ts:59:7 › Claude.md Journeys - Chat End-to-End › 3) Role routing: 
Researcher -> Perplexity, General -> OpenRouter default
    [webkit] › tests\e2e\chat.spec.ts:83:7 › Claude.md Journeys - Chat End-to-End › 4) Download menu 
presence (DOCX / PDF / PPT / ZIP) after response
    [webkit] › tests\e2e\chat.spec.ts:100:7 › Claude.md Journeys - Chat End-to-End › 5) Wallet / Dynamic.xyz button visibility
    [webkit] › tests\e2e\chat.spec.ts:106:7 › Claude.md Journeys - Chat End-to-End › 6) Error fallback: invalid model or missing key -> user-facing error with retry
    [webkit] › tests\e2e\user-journey.spec.ts:21:7 › HandyWriterz User Journey Tests › Homepage loads and displays key elements
    [webkit] › tests\e2e\user-journey.spec.ts:38:7 › HandyWriterz User Journey Tests › Chat interface functionality
    [webkit] › tests\e2e\user-journey.spec.ts:65:7 › HandyWriterz User Journey Tests › Settings page 
navigation and functionality
    [webkit] › tests\e2e\user-journey.spec.ts:84:7 › HandyWriterz User Journey Tests › Billing page and pricing tiers
    [webkit] › tests\e2e\user-journey.spec.ts:114:7 › HandyWriterz User Journey Tests › Theme toggle 
functionality
    [webkit] › tests\e2e\user-journey.spec.ts:135:7 › HandyWriterz User Journey Tests › File upload functionality
    [webkit] › tests\e2e\user-journey.spec.ts:160:7 › HandyWriterz User Journey Tests › API health check
    [webkit] › tests\e2e\user-journey.spec.ts:169:7 › HandyWriterz User Journey Tests › Payment flow 
simulation - Paystack
    [webkit] › tests\e2e\user-journey.spec.ts:193:7 › HandyWriterz User Journey Tests › Payment flow 
simulation - Coinbase Commerce
    [webkit] › tests\e2e\user-journey.spec.ts:221:7 › HandyWriterz User Journey Tests › Responsive design - Mobile view
    [webkit] › tests\e2e\user-journey.spec.ts:242:7 › HandyWriterz User Journey Tests › Error handling and edge cases
    [webkit] › tests\e2e\user-journey.spec.ts:271:7 › HandyWriterz User Journey Tests › Performance and loading times
    [webkit] › tests\e2e\user-journey.spec.ts:288:7 › HandyWriterz User Journey Tests › Authentication state handling
    [webkit] › tests\e2e\user-journey.spec.ts:308:7 › API Integration Tests › Backend health endpoint
    [webkit] › tests\e2e\user-journey.spec.ts:316:7 › API Integration Tests › API documentation endpoint
    [webkit] › tests\e2e\user-journey.spec.ts:321:7 › API Integration Tests › Billing endpoints ──── 
    [webkit] › tests\e2e\user-journey.spec.ts:330:7 › API Integration Tests › File upload endpoint ─ 

To open last HTML report run:

  pnpm exec playwright show-report

 ELIFECYCLE  Command failed with exit code 1.
PS D:\HandyWriterzAi\frontend> 
PS D:\HandyWriterzAi\frontend>  pnpm exec playwright show-report

  Serving HTML report at http://localhost:9323. Press Ctrl+C to quit.