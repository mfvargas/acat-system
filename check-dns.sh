#!/bin/bash

# ACAT System - DNS Checker Script

echo "🔍 ACAT System DNS Status Checker"
echo "================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_dns() {
    local domain=$1
    local expected_ip=$2
    
    echo -n "Checking $domain... "
    
    # Get IP from DNS
    local resolved_ip=$(dig +short $domain A)
    
    if [ -z "$resolved_ip" ]; then
        echo -e "${RED}❌ NOT RESOLVED${NC}"
        return 1
    elif [ "$expected_ip" != "any" ] && [ "$resolved_ip" != "$expected_ip" ]; then
        echo -e "${YELLOW}⚠️  RESOLVED to $resolved_ip (expected: $expected_ip)${NC}"
        return 2
    else
        echo -e "${GREEN}✅ RESOLVED to $resolved_ip${NC}"
        return 0
    fi
}

test_connectivity() {
    local domain=$1
    local port=${2:-80}
    
    echo -n "Testing connectivity to $domain:$port... "
    
    if timeout 5 bash -c "</dev/tcp/$domain/$port" 2>/dev/null; then
        echo -e "${GREEN}✅ CONNECTED${NC}"
        return 0
    else
        echo -e "${RED}❌ NO CONNECTION${NC}"
        return 1
    fi
}

echo ""
echo "📋 DNS Resolution Check:"
echo "------------------------"

# Check main domain
check_dns "acatcr.org" "any"

# Check staging domain
check_dns "staging.acatcr.org" "any"

# Check www domain
check_dns "www.acatcr.org" "any"

echo ""
echo "🌐 Connectivity Check:"
echo "----------------------"

# Test connectivity if DNS resolves
if dig +short staging.acatcr.org A > /dev/null 2>&1; then
    STAGING_IP=$(dig +short staging.acatcr.org A)
    if [ ! -z "$STAGING_IP" ]; then
        test_connectivity "staging.acatcr.org" 80
        test_connectivity "staging.acatcr.org" 443
        test_connectivity "$STAGING_IP" 22
        
        echo ""
        echo "📊 Additional Info:"
        echo "   Staging IP: $STAGING_IP"
        echo "   SSH Command: ssh ubuntu@$STAGING_IP"
    fi
fi

echo ""
echo "🔧 Useful Commands:"
echo "-------------------"
echo "   nslookup staging.acatcr.org"
echo "   dig staging.acatcr.org"
echo "   curl -I http://staging.acatcr.org"
echo "   ping staging.acatcr.org"

# Check if ready for deployment
echo ""
if dig +short staging.acatcr.org A > /dev/null 2>&1; then
    STAGING_IP=$(dig +short staging.acatcr.org A)
    if [ ! -z "$STAGING_IP" ]; then
        echo -e "${GREEN}🚀 DNS is ready! You can now deploy to staging.${NC}"
        echo -e "${GREEN}   Update deploy-to-staging-server.sh with IP: $STAGING_IP${NC}"
    fi
else
    echo -e "${YELLOW}⏳ Waiting for DNS configuration...${NC}"
    echo -e "${YELLOW}   Add A record: staging.acatcr.org → YOUR_DROPLET_IP${NC}"
fi
