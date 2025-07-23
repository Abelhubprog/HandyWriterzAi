#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting fast development mode...');

// Clear Next.js cache
const nextDir = path.join(__dirname, '.next');
if (fs.existsSync(nextDir)) {
  console.log('🧹 Clearing .next cache...');
  fs.rmSync(nextDir, { recursive: true, force: true });
}

// Clear node_modules/.cache if it exists
const cacheDir = path.join(__dirname, 'node_modules', '.cache');
if (fs.existsSync(cacheDir)) {
  console.log('🧹 Clearing node_modules cache...');
  fs.rmSync(cacheDir, { recursive: true, force: true });
}

console.log('✅ Cache cleared! Starting dev server with Turbopack...');

// Start with turbopack
try {
  execSync('pnpm run dev:turbo', { stdio: 'inherit' });
} catch (error) {
  console.log('⚠️  Turbopack failed, falling back to regular dev...');
  execSync('pnpm run dev', { stdio: 'inherit' });
}
