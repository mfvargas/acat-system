#!/bin/bash

# ACAT System - Staging Environment Health Check Script
# This script performs comprehensive health checks on the staging environment

set -e

echo "🔍 ACAT Staging Environment Health Check"
echo "========================================"
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status with colors
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Function to check HTTP response
check_http() {
    local url=$1
    local expected_code=$2
    local description=$3
    
    echo -n "🌐 Checking $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_code" ]; then
        print_status "OK" "$description: HTTP $response"
    else
        print_status "ERROR" "$description: Expected HTTP $expected_code, got $response"
        return 1
    fi
}

# Function to check SSL certificate
check_ssl() {
    local domain=$1
    
    echo -n "🔒 Checking SSL certificate for $domain... "
    
    cert_info=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        expiry=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
        print_status "OK" "SSL certificate valid until: $expiry"
    else
        print_status "ERROR" "SSL certificate check failed"
        return 1
    fi
}

# Main health checks
echo "🚀 Starting health checks..."
echo

# Check domain resolution
echo -n "🔍 Checking DNS resolution... "
if nslookup staging.acatcr.org >/dev/null 2>&1; then
    ip=$(nslookup staging.acatcr.org | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    print_status "OK" "staging.acatcr.org resolves to $ip"
else
    print_status "ERROR" "DNS resolution failed"
fi

# Check HTTP endpoints
echo
echo "🌐 Testing HTTP endpoints..."
check_http "https://staging.acatcr.org" "200" "Main application"
check_http "https://staging.acatcr.org/staging-info" "200" "Staging info page"
check_http "https://staging.acatcr.org/admin/" "302" "Django admin (redirect to login)"

# Check SSL
echo
echo "🔒 Testing SSL configuration..."
check_ssl "staging.acatcr.org"

# Check headers
echo
echo "📋 Checking security headers..."
headers=$(curl -s -I https://staging.acatcr.org)

if echo "$headers" | grep -q "X-Environment: STAGING"; then
    print_status "OK" "Environment header present"
else
    print_status "WARNING" "Environment header missing"
fi

if echo "$headers" | grep -q "X-Frame-Options"; then
    print_status "OK" "X-Frame-Options header present"
else
    print_status "WARNING" "X-Frame-Options header missing"
fi

if echo "$headers" | grep -q "Content-Security-Policy"; then
    print_status "OK" "Content-Security-Policy header present"
else
    print_status "WARNING" "Content-Security-Policy header missing"
fi

# If SSH key is available, check Docker containers
if [ -f ~/.ssh/acat ]; then
    echo
    echo "🐳 Checking Docker containers..."
    
    container_status=$(ssh -o ConnectTimeout=10 -i ~/.ssh/acat root@staging.acatcr.org "cd /opt/acat-system && docker-compose -f docker-compose.production.yml ps --format table" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "$container_status"
        
        # Count running containers
        running_count=$(echo "$container_status" | grep -c "Up" || echo "0")
        if [ "$running_count" -ge 4 ]; then
            print_status "OK" "All expected containers are running ($running_count/4)"
        else
            print_status "WARNING" "Some containers may not be running ($running_count/4)"
        fi
    else
        print_status "WARNING" "Could not check Docker containers (SSH access required)"
    fi
else
    print_status "WARNING" "SSH key not found - cannot check Docker containers"
fi

echo
echo "========================================"
echo "🎉 Health check completed!"
echo
echo "📊 Summary:"
echo "- Domain: staging.acatcr.org"
echo "- Environment: STAGING"
echo "- HTTPS: Enabled with Let's Encrypt"
echo "- Services: Django, PostgreSQL, Redis, Nginx"
echo
echo "🔗 Access URLs:"
echo "- Main app: https://staging.acatcr.org"
echo "- Admin: https://staging.acatcr.org/admin/"
echo "- Info: https://staging.acatcr.org/staging-info"
echo
