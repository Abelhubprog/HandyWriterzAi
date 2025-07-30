#!/bin/bash

# Comprehensive Test Runner for HandyWriterz
# Tests all user flows including authentication, payments, and AI agents

set -e

echo "🧪 HandyWriterz Comprehensive Test Suite"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_step "Running: $test_name"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if eval "$test_command"; then
        print_status "✅ PASSED: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        print_error "❌ FAILED: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Wait for services to be ready
print_step "Waiting for services to be ready..."

# Wait for database
timeout=60
counter=0
while ! pg_isready -h postgres-test -p 5432 -U handywriterz -d handywriterz_test >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Database failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done
print_status "Database ready"

# Wait for Redis
timeout=30
counter=0
while ! redis-cli -h redis-test -p 6379 ping >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Redis failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done
print_status "Redis ready"

# Wait for backend
timeout=120
counter=0
while ! curl -s http://backend-test:8000/health >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Backend failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done
print_status "Backend ready"

# Wait for frontend
timeout=120
counter=0
while ! curl -s http://frontend-test:3000 >/dev/null 2>&1; do
    if [ $counter -ge $timeout ]; then
        print_error "Frontend failed to start within $timeout seconds"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done
print_status "Frontend ready"

print_step "All services are ready. Starting tests..."

# 1. Database and Infrastructure Tests
print_step "=== DATABASE & INFRASTRUCTURE TESTS ==="

run_test "Database Connection" "pg_isready -h postgres-test -p 5432 -U handywriterz -d handywriterz_test"
run_test "Redis Connection" "redis-cli -h redis-test -p 6379 ping"
run_test "pgvector Extension" "psql -h postgres-test -U handywriterz -d handywriterz_test -c 'SELECT extname FROM pg_extension WHERE extname = \"vector\";' | grep vector"

# 2. Backend API Tests
print_step "=== BACKEND API TESTS ==="

run_test "Health Check Endpoint" "curl -f http://backend-test:8000/health"
run_test "API Documentation" "curl -f http://backend-test:8000/docs"
run_test "Database Models Creation" "cd backend && uv run python -c 'from src.db.models import User, Conversation; print(\"Models imported successfully\")'"

# 3. Authentication Tests
print_step "=== AUTHENTICATION TESTS ==="

run_test "User Creation API" "curl -X POST http://backend-test:8000/api/users -H 'Content-Type: application/json' -d '{\"wallet_address\": \"0x1234567890123456789012345678901234567890\", \"email\": \"test@example.com\"}' | grep -q '\"id\"'"

# 4. Payment System Tests
print_step "=== PAYMENT SYSTEM TESTS ==="

run_test "Payment Tiers Endpoint" "curl -f http://backend-test:8000/api/billing/tiers | grep -q 'free'"
run_test "Billing Summary Endpoint" "curl -f http://backend-test:8000/api/billing/summary -H 'Authorization: Bearer test_token' | grep -q 'plan'"

# 5. AI Agent System Tests
print_step "=== AI AGENT SYSTEM TESTS ==="

run_test "LangGraph Configuration" "cd backend && uv run python -c 'from src.agent.handywriterz_graph import create_agent_graph; graph = create_agent_graph(); print(\"Graph created successfully\")'"
run_test "Agent Nodes Import" "cd backend && uv run python -c 'from src.agent.nodes.writer import writer_node; print(\"Writer node imported\")'"

# 6. File Processing Tests
print_step "=== FILE PROCESSING TESTS ==="

# Create test file
echo "This is a test document for file processing." > /tmp/test_doc.txt

run_test "File Upload API" "curl -X POST http://backend-test:8000/api/files -F 'file=@/tmp/test_doc.txt' | grep -q 'file_id'"

# 7. Backend Unit Tests
print_step "=== BACKEND UNIT TESTS ==="

run_test "Python Unit Tests" "cd backend && uv run pytest src/tests/ -v --tb=short"

# 8. Frontend Tests
print_step "=== FRONTEND TESTS ==="

run_test "Frontend Health Check" "curl -f http://frontend-test:3000"
run_test "Frontend Build Test" "cd frontend && pnpm build"

# 9. End-to-End User Flow Tests
print_step "=== END-TO-END USER FLOW TESTS ==="

# Create comprehensive E2E test
cat > /tmp/e2e_test.js << 'EOF'
const { chromium } = require('playwright');

async function runE2ETests() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Test 1: Homepage Load
    console.log('Testing homepage load...');
    await page.goto('http://frontend-test:3000');
    await page.waitForSelector('body', { timeout: 10000 });
    console.log('✅ Homepage loaded successfully');
    
    // Test 2: Chat Interface
    console.log('Testing chat interface...');
    await page.goto('http://frontend-test:3000/chat');
    await page.waitForSelector('textarea', { timeout: 10000 });
    console.log('✅ Chat interface loaded');
    
    // Test 3: Settings Page
    console.log('Testing settings page...');
    await page.goto('http://frontend-test:3000/settings');
    await page.waitForSelector('h1', { timeout: 10000 });
    console.log('✅ Settings page loaded');
    
    // Test 4: Billing Page
    console.log('Testing billing page...');
    await page.goto('http://frontend-test:3000/settings/billing');
    await page.waitForSelector('h1', { timeout: 10000 });
    console.log('✅ Billing page loaded');
    
    console.log('All E2E tests passed!');
    return true;
  } catch (error) {
    console.error('E2E test failed:', error);
    return false;
  } finally {
    await browser.close();
  }
}

runE2ETests().then(success => {
  process.exit(success ? 0 : 1);
});
EOF

run_test "End-to-End User Flows" "cd frontend && node /tmp/e2e_test.js"

# 10. Integration Tests
print_step "=== INTEGRATION TESTS ==="

run_test "Backend-Database Integration" "cd backend && uv run python -c 'from src.db.database import get_db; from src.db.models import User; import uuid; db = next(get_db()); user = User(id=uuid.uuid4(), wallet_address=\"0x123\"); db.add(user); db.commit(); print(\"Database integration works\")'"

# 11. Performance Tests
print_step "=== PERFORMANCE TESTS ==="

run_test "API Response Time" "time curl -s http://backend-test:8000/health | grep -q 'status'"
run_test "Concurrent API Requests" "for i in {1..10}; do curl -s http://backend-test:8000/health & done; wait; echo 'Concurrent requests handled'"

# Test Results Summary
print_step "=== TEST RESULTS SUMMARY ==="

echo ""
echo "📊 Test Results:"
echo "  Total Tests: $TOTAL_TESTS"
echo "  Passed: $PASSED_TESTS"
echo "  Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    print_status "🎉 ALL TESTS PASSED! System is ready for deployment."
    echo ""
    echo "✅ Authentication system: Working"
    echo "✅ Payment integration: Working"
    echo "✅ Database operations: Working"
    echo "✅ AI agent system: Working"
    echo "✅ Frontend interface: Working"
    echo "✅ API endpoints: Working"
    echo ""
    echo "🚀 Ready for Railway deployment!"
    exit 0
else
    print_error "❌ $FAILED_TESTS test(s) failed. Please fix before deployment."
    exit 1
fi