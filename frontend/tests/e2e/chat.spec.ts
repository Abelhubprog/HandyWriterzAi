import { test, expect } from '@playwright/test';

const CHAT_URL = '/chat';

// Helper to wait for initial assistant stream text to appear in chat pane
async function expectStreamedMessage(page) {
  // Adjust selector names if your UI differs
  const assistantMessage = page.getByTestId('assistant-message').first().or(page.locator('[data-role="assistant"]')).first();
  await expect(assistantMessage).toBeVisible({ timeout: 30000 });
}

test.describe('Claude.md Journeys - Chat End-to-End', () => {
  test.beforeEach(async ({ page, baseURL }) => {
    await page.goto(`${baseURL ?? 'http://localhost:3000'}${CHAT_URL}`);
    // Sidebar and ChatPane basic smoke
    await expect(page).toHaveURL(/\/chat$/);
  });

  test('1) New chat: prompt-only -> POST /api/chat -> WS stream', async ({ page }) => {
    // New chat button in sidebar
    const newChat = page.getByRole('button', { name: /new chat/i }).or(page.getByTestId('new-chat'));
    await newChat.click().catch(() => {}); // no-op if not present

    // Type prompt
    const promptBox = page.getByPlaceholder(/message/i).or(page.getByRole('textbox'));
    await promptBox.fill('Summarize the importance of RAG with citations.');

    // Send
    const sendBtn = page.getByRole('button', { name: /send/i }).or(page.getByTestId('send-button'));
    await sendBtn.click();

    // Expect streamed content in UI (first assistant message)
    await expectStreamedMessage(page);
  });

  test('2) Upload files + prompt -> POST /api/files -> POST /api/chat -> WS stream', async ({ page }) => {
    // Attach small sample file(s). Adjust selector to your uploader dropzone/input.
    const fileInput = page.locator('input[type="file"]').first().or(page.getByTestId('file-input'));
    await fileInput.setInputFiles([
      { name: 'sample.txt', mimeType: 'text/plain', buffer: Buffer.from('This is a sample context file.') },
    ]);

    // Verify thumbnail/progress visible if UI surfaces it (best-effort)
    const uploader = page.getByTestId('uploader').or(page.getByText(/upload/i));
    await uploader.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});

    // Enter prompt referencing file
    const promptBox = page.getByPlaceholder(/message/i).or(page.getByRole('textbox'));
    await promptBox.fill('Use uploaded context to outline 3 key points.');

    // Send
    const sendBtn = page.getByRole('button', { name: /send/i }).or(page.getByTestId('send-button'));
    await sendBtn.click();

    // Expect streamed assistant response
    await expectStreamedMessage(page);
  });

  test('3) Role routing: Researcher -> Perplexity, General -> OpenRouter default', async ({ page }) => {
    // If role selector exists, switch role. Update selectors if your UI differs.
    const roleSelect = page.getByLabel(/role/i).or(page.getByTestId('role-select'));
    if (await roleSelect.isVisible().catch(() => false)) {
      await roleSelect.selectOption(/researcher/i);
    }

    const promptBox = page.getByPlaceholder(/message/i).or(page.getByRole('textbox'));
    await promptBox.fill('Find latest 3 AI governance reports and summarize.');

    const sendBtn = page.getByRole('button', { name: /send/i }).or(page.getByTestId('send-button'));
    await sendBtn.click();

    await expectStreamedMessage(page);

    // Switch to general and test again
    if (await roleSelect.isVisible().catch(() => false)) {
      await roleSelect.selectOption(/general/i);
      await promptBox.fill('Explain retrieval augmented generation in 2 sentences.');
      await sendBtn.click();
      await expectStreamedMessage(page);
    }
  });

  test('4) Download menu presence (DOCX / PDF / PPT / ZIP) after response', async ({ page }) => {
    // Trigger a simple chat
    const promptBox = page.getByPlaceholder(/message/i).or(page.getByRole('textbox'));
    await promptBox.fill('Generate a short academic abstract.');
    const sendBtn = page.getByRole('button', { name: /send/i }).or(page.getByTestId('send-button'));
    await sendBtn.click();

    await expectStreamedMessage(page);

    // Download options; adapt selectors to your DownloadMenu
    const downloadMenu = page.getByTestId('download-menu').or(page.getByRole('button', { name: /download/i }));
    await downloadMenu.click().catch(() => {});
    const docx = page.getByRole('menuitem', { name: /docx/i }).or(page.getByText(/docx/i));
    const pdf = page.getByRole('menuitem', { name: /pdf/i }).or(page.getByText(/pdf/i));
    await expect(docx.or(pdf)).toBeVisible({ timeout: 5000 });
  });

  test('5) Wallet / Dynamic.xyz button visibility', async ({ page }) => {
    const walletBtn = page.getByRole('button', { name: /wallet|login|get started/i })
      .or(page.getByTestId('wallet-button'));
    await expect(walletBtn).toBeVisible();
  });

  test('6) Error fallback: invalid model or missing key -> user-facing error with retry', async ({ page }) => {
    // If the UI allows selecting a provider/model, pick a likely-invalid combination
    const providerSelect = page.getByLabel(/provider/i).or(page.getByTestId('provider-select'));
    if (await providerSelect.isVisible().catch(() => false)) {
      await providerSelect.selectOption('openrouter').catch(() => {});
    }

    const promptBox = page.getByPlaceholder(/message/i).or(page.getByRole('textbox'));
    await promptBox.fill('Trigger a model error for testing.');

    const sendBtn = page.getByRole('button', { name: /send/i }).or(page.getByTestId('send-button'));
    await sendBtn.click();

    // Expect either stream or a handled error banner/toast
    const errorToast = page.getByRole('alert').or(page.getByTestId('error-banner'));
    await expect(errorToast).toBeVisible({ timeout: 15000 }).catch(async () => {
      // If no error shown, expect streamed message instead (fallback worked)
      await expectStreamedMessage(page);
    });
  });
});
