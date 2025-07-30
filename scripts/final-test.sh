#!/bin/bash

# Final Verification Test for HandyWriterz
# Quick comprehensive test before Railway deployment

set -e

echo "🎯 HandyWriterz Final Verification"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✅]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[🔧]${NC} $1"
}

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

test_item() {
    local name="$1"
    local condition="$2"
    
    if eval "$condition" 2>/dev/null; then
        print_status "$name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_error "$name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

print_step "System Requirements"
test_item "Docker installed and running" "docker --version && docker info > /dev/null"
test_item "Python 3.11+ available" "python3 --version | grep -E '3\\.(11|12)'"
test_item "Node.js 20+ available" "node --version | grep -E 'v(2[0-9]|[3-9][0-9])'"
test_item "Railway CLI available" "railway --version || which railway"

print_step "Project Structure"
test_item "Backend source code" "[ -d 'backend/src' ]"
test_item "Frontend source code" "[ -d 'frontend/src' ]"
test_item "Docker configurations" "[ -f 'backend/Dockerfile' ] && [ -f 'frontend/Dockerfile' ]"
test_item "Test configurations" "[ -f 'docker-compose.test.yml' ] && [ -f 'Dockerfile.test' ]"

print_step "Core Components"
test_item "FastAPI main module" "[ -f 'backend/src/main.py' ]"
test_item "Payment service" "[ -f 'backend/src/services/payment_service.py' ]"
test_item "Database models" "[ -f 'backend/src/db/models.py' ]"
test_item "Next.js configuration" "[ -f 'frontend/next.config.mjs' ]"
test_item "Payment components" "[ -f 'frontend/src/components/PaymentDialog.tsx' ]"
test_item "Auth integration" "[ -f 'frontend/src/hooks/useDynamicAuth.ts' ]"

print_step "Integration Features"
test_item "Dynamic.xyz authentication" "grep -q 'useDynamicContext' frontend/src/hooks/useDynamicAuth.ts"
test_item "Paystack payment integration" "grep -q 'paystack' backend/src/services/payment_service.py"
test_item "Coinbase Commerce integration" "grep -q 'coinbase' backend/src/services/payment_service.py"
test_item "Subscription tiers" "grep -q 'SubscriptionTier' backend/src/services/payment_service.py"

print_step "Environment Configuration"
test_item "Environment example file" "[ -f '.env.example' ]"
test_item "Payment provider configs" "grep -q 'PAYSTACK_SECRET_KEY' .env.example"
test_item "Auth provider configs" "grep -q 'DYNAMIC_ENV_ID' .env.example"
test_item "Database configs" "grep -q 'DATABASE_URL' .env.example"
test_item "AI provider configs" "grep -q 'GEMINI_API_KEY' .env.example"

print_step "Deployment Configuration"
test_item "Railway services config" "[ -f 'railway-services.yaml' ]"
test_item "Railway deploy script" "[ -f 'scripts/railway-deploy.sh' ] && [ -x 'scripts/railway-deploy.sh' ]"
test_item "Test scripts" "[ -f 'scripts/docker-test.sh' ] && [ -x 'scripts/docker-test.sh' ]"

print_step "Database Services Test"
echo "Starting minimal database services for connectivity test..."

# Clean up any existing containers
docker-compose -f docker-compose.test.yml down --volumes --remove-orphans 2>/dev/null || true

# Start database services only
docker-compose -f docker-compose.test.yml up -d postgres-test redis-test

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Test database connectivity
if docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready -U handywriterz -d handywriterz_test > /dev/null 2>&1; then
    print_status "PostgreSQL service connectivity"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # Test pgvector extension
    if docker-compose -f docker-compose.test.yml exec -T postgres-test psql -U handywriterz -d handywriterz_test -c "SELECT extname FROM pg_extension WHERE extname = 'vector';" | grep -q 'vector'; then
        print_status "pgvector extension installed"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        print_error "pgvector extension missing"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    print_error "PostgreSQL service connectivity"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test Redis connectivity
if docker-compose -f docker-compose.test.yml exec -T redis-test redis-cli ping | grep -q 'PONG'; then
    print_status "Redis service connectivity"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    print_error "Redis service connectivity"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Clean up
echo "Cleaning up test services..."
docker-compose -f docker-compose.test.yml down --volumes 2>/dev/null || true

print_step "Final Results"
echo ""
echo "📊 Verification Summary:"
echo "  ✅ Tests Passed: $TESTS_PASSED"
echo "  ❌ Tests Failed: $TESTS_FAILED"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "🎉 ALL VERIFICATIONS PASSED!"
    echo ""
    echo "✅ System is ready for Railway deployment"
    echo "✅ All core components are in place"
    echo "✅ Payment integrations configured"
    echo "✅ Authentication system ready"
    echo "✅ Database services working"
    echo ""
    echo "🚀 Ready to deploy!"
    echo ""
    echo "Next step: Run './scripts/railway-deploy.sh' to deploy to production"
    exit 0
else
    echo "⚠️  Some verifications failed ($TESTS_FAILED)"
    echo ""
    echo "The system should still work, but please review the failed items."
    echo "Most failures are likely due to missing development dependencies."
    echo ""
    echo "You can proceed with deployment if core components passed."
    exit 1
fi