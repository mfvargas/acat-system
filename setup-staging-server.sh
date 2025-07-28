#!/bin/bash

# ACAT System - Setup Staging Server (Run this ON the staging server)
# This script should be run on the staging server after files are deployed

set -e

echo "🔧 ACAT System - Staging Server Setup"
echo "====================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on server
if [ ! -d "/opt/acat-system" ]; then
    log_error "This script should be run on the staging server where files are deployed"
    log_error "Expected directory: /opt/acat-system"
    exit 1
fi

cd /opt/acat-system

# Make scripts executable
log_info "Making scripts executable..."
chmod +x *.sh
chmod +x deploy-to-staging-server.sh setup-staging-server.sh

# Update system packages
log_info "Updating system packages..."
apt update
apt upgrade -y

# Install required packages
log_info "Installing Docker, Docker Compose, Nginx, and Certbot..."
apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban

# Start and enable services
log_info "Starting and enabling services..."
systemctl start docker
systemctl enable docker
systemctl start nginx
systemctl enable nginx

# Root user already has docker access
log_info "Root user - Docker access already available"

# Create required directories
log_info "Creating required directories..."
mkdir -p /var/www/acat-system/static
mkdir -p /var/www/acat-system/media
mkdir -p /var/log/acat-system

# Configure firewall
log_info "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# Verify Docker installation
log_info "Verifying Docker installation..."
if command -v docker &> /dev/null; then
    log_info "✅ Docker installed successfully"
    docker --version
else
    log_error "❌ Docker installation failed"
    exit 1
fi

# Verify Docker Compose installation
if command -v docker-compose &> /dev/null; then
    log_info "✅ Docker Compose installed successfully"
    docker-compose --version
else
    log_error "❌ Docker Compose installation failed"
    exit 1
fi

# Build Docker images
log_info "Building Docker images..."
docker-compose -f docker-compose.production.yml build

# Create initial Nginx configuration (before SSL)
log_info "Creating initial Nginx configuration..."
cp nginx/staging.conf /etc/nginx/sites-available/acat-staging
ln -sf /etc/nginx/sites-available/acat-staging /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
log_info "Testing Nginx configuration..."
nginx -t

# Reload Nginx
systemctl reload nginx

log_info "✅ Staging server setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Ensure DNS is configured: staging.acatcr.org → $(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
echo "2. Start the application: docker-compose -f docker-compose.production.yml up -d"
echo "3. Setup SSL certificate: certbot --nginx -d staging.acatcr.org"
echo "4. Check application status: docker-compose -f docker-compose.production.yml ps"
echo ""
echo "📋 Useful commands:"
echo "   - View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "   - Restart services: docker-compose -f docker-compose.production.yml restart"
echo "   - Update application: docker-compose -f docker-compose.production.yml pull && docker-compose -f docker-compose.production.yml up -d"
echo ""
echo "🌐 Application will be available at:"
echo "   - http://staging.acatcr.org (before SSL)"
echo "   - https://staging.acatcr.org (after SSL setup)"
