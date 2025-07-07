#!/bin/bash
# 🏥 Nextvision Health Check Script
# Validation santé application pour Docker/K8s

set -e

# Configuration
HOST=${HOST:-localhost}
PORT=${PORT:-8000}
TIMEOUT=${TIMEOUT:-10}

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏥 Starting Nextvision Health Check..."

# Function: Test endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=${2:-200}
    local description=$3
    
    echo -n "  Testing $description... "
    
    response=$(curl -s -w "%{http_code}" -o /dev/null \
        --max-time $TIMEOUT \
        "http://$HOST:$PORT$endpoint" || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $response)${NC}"
        return 1
    fi
}

# Function: Test avec timeout
test_with_timeout() {
    local test_name=$1
    shift
    
    if timeout $TIMEOUT "$@"; then
        echo -e "  $test_name: ${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "  $test_name: ${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Variables pour tracking
failed_tests=0
total_tests=0

# ==============================================
# 🎯 CORE API HEALTH CHECKS
# ==============================================

echo "\n🎯 Core API Health Checks:"

# Test 1: Basic health endpoint
((total_tests++))
if test_endpoint "/api/v1/health" 200 "Basic Health"; then
    : # Success
else
    ((failed_tests++))
fi

# Test 2: Root endpoint
((total_tests++))
if test_endpoint "/" 200 "Root Endpoint"; then
    : # Success
else
    ((failed_tests++))
fi

# Test 3: Google Maps health
((total_tests++))
if test_endpoint "/api/v2/maps/health" 200 "Google Maps Intelligence"; then
    : # Success
else
    ((failed_tests++))
fi

# ==============================================
# 💾 DATABASE & CACHE CHECKS
# ==============================================

echo "\n💾 Infrastructure Health Checks:"

# Test 4: Database connection (via API)
((total_tests++))
echo -n "  Testing Database Connection... "
db_response=$(curl -s --max-time $TIMEOUT \
    "http://$HOST:$PORT/api/v1/health" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('features', {}).get('database', 'false'))" 2>/dev/null || echo "false")

if [ "$db_response" = "true" ] || [ "$db_response" = "True" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}"
    ((failed_tests++))
fi

# Test 5: Cache availability
((total_tests++))
echo -n "  Testing Cache System... "
cache_response=$(curl -s --max-time $TIMEOUT \
    "http://$HOST:$PORT/api/v2/performance/stats" | \
    python3 -c "import sys, json; data=json.load(sys.stdin); print('cache_layers' in data)" 2>/dev/null || echo "False")

if [ "$cache_response" = "True" ]; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING${NC}"
    ((failed_tests++))
fi

# ==============================================
# ⚡ PERFORMANCE CHECKS
# ==============================================

echo "\n⚡ Performance Health Checks:"

# Test 6: Response time check
((total_tests++))
echo -n "  Testing Response Time... "
start_time=$(date +%s.%N)
test_endpoint "/api/v1/health" 200 "" > /dev/null 2>&1
end_time=$(date +%s.%N)
response_time=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "999")
response_time_ms=$(echo "$response_time * 1000" | bc 2>/dev/null || echo "999")

if (( $(echo "$response_time_ms < 1000" | bc -l 2>/dev/null || echo 0) )); then
    echo -e "${GREEN}✅ OK (${response_time_ms%.*}ms)${NC}"
else
    echo -e "${YELLOW}⚠️  SLOW (${response_time_ms%.*}ms)${NC}"
    # Don't fail for slow response, just warn
fi

# Test 7: Memory usage
((total_tests++))
echo -n "  Testing Memory Usage... "
memory_percent=$(ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep -v grep | grep python | head -n1 | awk '{print $4}' || echo "0")

if (( $(echo "$memory_percent < 80" | bc -l 2>/dev/null || echo 1) )); then
    echo -e "${GREEN}✅ OK (${memory_percent%.*}%)${NC}"
else
    echo -e "${YELLOW}⚠️  HIGH (${memory_percent%.*}%)${NC}"
fi

# ==============================================
# 🔒 SECURITY CHECKS
# ==============================================

echo "\n🔒 Security Health Checks:"

# Test 8: Non-root user
((total_tests++))
echo -n "  Testing Non-root User... "
current_user=$(whoami)
if [ "$current_user" != "root" ]; then
    echo -e "${GREEN}✅ OK (running as $current_user)${NC}"
else
    echo -e "${RED}❌ SECURITY RISK (running as root)${NC}"
    ((failed_tests++))
fi

# Test 9: SSL redirect (si en production)
((total_tests++))
if [ "$ENVIRONMENT" = "production" ]; then
    echo -n "  Testing SSL Configuration... "
    # Test si port 443 répond
    if curl -s --max-time 5 -k "https://$HOST" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${YELLOW}⚠️  SSL not configured${NC}"
    fi
else
    echo "  SSL Check: ${YELLOW}SKIPPED (non-production)${NC}"
fi

# ==============================================
# 📊 FINAL RESULTS
# ==============================================

echo "\n📊 Health Check Results:"
echo "  Total Tests: $total_tests"
echo "  Failed Tests: $failed_tests"
echo "  Success Rate: $(( (total_tests - failed_tests) * 100 / total_tests ))%"

# Verdict final
if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}🏆 ALL HEALTH CHECKS PASSED!${NC}"
    echo "✅ Nextvision is healthy and ready for production"
    exit 0
elif [ $failed_tests -le 2 ]; then
    echo -e "\n${YELLOW}⚠️  SOME HEALTH CHECKS FAILED${NC}"
    echo "🔧 Service degraded but operational"
    exit 0  # Still return 0 for Docker health check
else
    echo -e "\n${RED}💥 CRITICAL HEALTH CHECK FAILURES${NC}"
    echo "🚨 Service requires immediate attention"
    exit 1
fi
