#!/bin/bash

echo "🔍 HandyWriterz Deployment Validation"
echo "===================================="

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0

# Test functions
test_service() {
    local service_name="$1"
    local url="$2"
    local expected_response="$3"
    
    echo -n "Testing $service_name... "
    
    if curl -s -f --max-time 10 "$url" | grep -q "$expected_response" 2>/dev/null; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

test_docker_service() {
    local service_name="$1"
    
    echo -n "Checking Docker service $service_name... "
    
    if docker-compose ps "$service_name" | grep -q "healthy\|Up"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}🐳 Docker Services Status:${NC}"
test_docker_service "db"
test_docker_service "redis"
test_docker_service "backend"
test_docker_service "agentic-doc-service"
test_docker_service "frontend"

echo ""
echo -e "${BLUE}🌐 HTTP Endpoint Tests:${NC}"
test_service "Backend Health" "http://localhost:8000/health" "status"
test_service "Backend API Docs" "http://localhost:8000/docs" "FastAPI"
test_service "Agentic-Doc Health" "http://localhost:8001/health" "status"
test_service "Frontend" "http://localhost:3000" "<!DOCTYPE html>"

echo ""
echo -e "${BLUE}🔌 Database Connectivity:${NC}"
echo -n "Testing PostgreSQL connection... "
if docker-compose exec -T db psql -U handywriterz -d handywriterz -c "SELECT 1;" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAILED${NC}"
    ((FAILED++))
fi

echo -n "Testing Redis connection... "
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAILED${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}📊 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo -e "${BLUE}📝 Service Logs (last 10 lines):${NC}"
echo "Backend logs:"
docker-compose logs --tail=5 backend | head -10
echo ""
echo "Frontend logs:"
docker-compose logs --tail=5 frontend | head -10

echo ""
echo "=================================="
echo -e "${BLUE}🎯 VALIDATION RESULTS:${NC}"
echo -e "   Passed: ${GREEN}$PASSED${NC}"
echo -e "   Failed: ${RED}$FAILED${NC}"
echo -e "   Total:  $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🏆 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}🚀 HandyWriterz is ready for YC Demo Day demonstration!${NC}"
    echo ""
    echo -e "${BLUE}🎪 Demo URLs:${NC}"
    echo "   🌟 Main Application: http://localhost:3000"
    echo "   📚 API Documentation: http://localhost:8000/docs"
    echo "   🔧 Backend Health: http://localhost:8000/health"
    echo ""
    echo -e "${BLUE}🧪 Run Demo Test:${NC}"
    echo "   python test_yc_demo_ready.py"
    exit 0
else
    echo ""
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo -e "${YELLOW}🔧 Check service logs:${NC}"
    echo "   docker-compose logs [service-name]"
    echo ""
    echo -e "${YELLOW}🔄 Restart services:${NC}"
    echo "   docker-compose restart"
    exit 1
fi