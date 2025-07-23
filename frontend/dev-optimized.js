#!/usr/bin/env node

// Optimized development server for faster compilation
// Use this instead of 'next dev' for much faster builds

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting optimized Next.js development server...');

// Set environment variables for faster builds
process.env.NODE_ENV = 'development';
process.env.NEXT_TELEMETRY_DISABLED = '1';
process.env.DISABLE_ESM = '1';

// Reduce Node.js memory pressure
process.env.NODE_OPTIONS = '--max-old-space-size=4096 --no-experimental-fetch';

// Start Next.js with Turbopack if available (Next.js 14+)
const usesTurbo = true; // Enable Turbopack for faster builds

const nextCommand = 'next';
const args = ['dev'];

// Add Turbopack flag for much faster compilation
if (usesTurbo) {
  args.push('--turbopack');
  console.log('⚡ Using Turbopack for faster builds...');
}

// Add port and hostname
args.push('--port', '3000');
args.push('--hostname', '0.0.0.0');

console.log(`📦 Running: ${nextCommand} ${args.join(' ')}`);

// Spawn the Next.js process
const nextProcess = spawn(nextCommand, args, {
  stdio: 'inherit',
  cwd: process.cwd(),
  env: process.env,
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down development server...');
  nextProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down development server...');
  nextProcess.kill('SIGTERM');
});

nextProcess.on('close', (code) => {
  console.log(`\n📱 Development server exited with code ${code}`);
  process.exit(code);
});

nextProcess.on('error', (error) => {
  console.error('❌ Failed to start development server:', error);
  process.exit(1);
});