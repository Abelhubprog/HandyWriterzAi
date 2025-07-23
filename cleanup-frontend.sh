#!/bin/bash

# Frontend Cleanup Script for MultiAgent HandyWriterz
# This script removes conflicting dependencies and optimizes the build process

set -e

echo "🧹 Cleaning up frontend build issues..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[CLEANUP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Step 1: Stop any running dev servers
print_step "Stopping any running development servers..."
pkill -f "next dev" || true
pkill -f "pnpm dev" || true
sleep 2

# Step 2: Remove all node_modules directories
print_step "Removing all node_modules directories..."

# Root level node_modules (conflicting with workspace)
if [ -d "/mnt/d/multiagentwriterz/node_modules" ]; then
    print_status "Removing root node_modules..."
    rm -rf /mnt/d/multiagentwriterz/node_modules
fi

# Frontend node_modules
if [ -d "/mnt/d/multiagentwriterz/frontend/node_modules" ]; then
    print_status "Removing frontend node_modules..."
    rm -rf /mnt/d/multiagentwriterz/frontend/node_modules
fi

# Testing demo node_modules (huge and not needed)
if [ -d "/mnt/d/multiagentwriterz/testing-demo/node_modules" ]; then
    print_status "Removing testing-demo node_modules..."
    rm -rf /mnt/d/multiagentwriterz/testing-demo/node_modules
fi

if [ -d "/mnt/d/multiagentwriterz/testing-demo/frontend/node_modules" ]; then
    print_status "Removing testing-demo/frontend node_modules..."
    rm -rf /mnt/d/multiagentwriterz/testing-demo/frontend/node_modules
fi

if [ -d "/mnt/d/multiagentwriterz/testing-demo/sample-test-app/node_modules" ]; then
    print_status "Removing testing-demo/sample-test-app node_modules..."
    rm -rf /mnt/d/multiagentwriterz/testing-demo/sample-test-app/node_modules
fi

# Step 3: Remove lock files that might be causing conflicts
print_step "Removing conflicting lock files..."

# Remove root pnpm-lock.yaml (workspace conflicts)
if [ -f "/mnt/d/multiagentwriterz/pnpm-lock.yaml" ]; then
    print_status "Removing root pnpm-lock.yaml..."
    rm -f /mnt/d/multiagentwriterz/pnpm-lock.yaml
fi

# Remove any package-lock.json files in favor of pnpm
find /mnt/d/multiagentwriterz -name "package-lock.json" -type f -delete 2>/dev/null || true

# Step 4: Clean pnpm cache
print_step "Cleaning pnpm cache..."
pnpm store prune || true

# Step 5: Remove problematic root package.json configurations
print_step "Cleaning up root package.json conflicts..."

# The root package.json has workspace conflicts, let's simplify it
cat > /mnt/d/multiagentwriterz/package.json << 'EOF'
{
  "private": true,
  "scripts": {
    "dev:frontend": "cd frontend && pnpm dev",
    "build:frontend": "cd frontend && pnpm build",
    "dev:backend": "cd backend && python src/main.py"
  }
}
EOF

print_status "Simplified root package.json"

# Step 6: Remove pnpm workspace config that's causing conflicts
if [ -f "/mnt/d/multiagentwriterz/pnpm-workspace.yaml" ]; then
    print_status "Removing conflicting pnpm-workspace.yaml..."
    rm -f /mnt/d/multiagentwriterz/pnpm-workspace.yaml
fi

# Step 7: Navigate to frontend and install fresh dependencies
print_step "Installing fresh frontend dependencies..."
cd /mnt/d/multiagentwriterz/frontend

# Ensure we have the latest pnpm
npm install -g pnpm@latest

# Install dependencies fresh
print_status "Installing frontend dependencies with pnpm..."
pnpm install --frozen-lockfile=false

print_status "✅ Frontend cleanup completed!"

echo ""
echo "🚀 Next steps:"
echo "1. cd frontend"
echo "2. pnpm dev"
echo ""
echo "The frontend should now compile much faster without conflicts!"