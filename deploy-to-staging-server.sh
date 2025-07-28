#!/bin/bash

# ACAT System - Deploy to Staging Server Script
# This script deploys the staging environment to a remote Ubuntu server

set -e

# Configuration
STAGING_SERVER="159.65.122.13"
STAGING_USER="root"
SSH_KEY="$HOME/.ssh/acat"
PROJECT_NAME="acat-system"
DOMAIN="staging.acatcr.org"

echo "🚀 ACAT System - Deploy to Staging Server"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if server IP is configured
if [ "$STAGING_SERVER" = "YOUR_STAGING_SERVER_IP" ]; then
    log_error "Please configure STAGING_SERVER variable with your server IP"
    echo "Edit this script and set: STAGING_SERVER=\"YOUR.SERVER.IP\""
    exit 1
fi

# Check if SSH key is configured
log_info "Testing SSH connection: ssh -i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=5 $STAGING_USER@$STAGING_SERVER"
if ! ssh -i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=5 $STAGING_USER@$STAGING_SERVER echo "SSH connection test" 2>/dev/null; then
    log_error "Cannot connect to staging server. Please ensure:"
    echo "1. SSH key is added to the server"
    echo "2. Server IP is correct: $STAGING_SERVER"
    echo "3. User can connect: ssh $STAGING_USER@$STAGING_SERVER"
    exit 1
fi

log_info "SSH connection to staging server successful"

# Create deployment package
log_info "Creating deployment package..."
tar -czf acat-system-staging.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='logs/*' \
    --exclude='media/*' \
    --exclude='*.sqlite3' \
    .

log_info "Deployment package created: acat-system-staging.tar.gz"

# Transfer files to server
log_info "Transferring files to staging server..."
scp -i $SSH_KEY acat-system-staging.tar.gz $STAGING_USER@$STAGING_SERVER:/tmp/

# Run deployment on server
log_info "Running deployment on staging server..."
ssh -i $SSH_KEY $STAGING_USER@$STAGING_SERVER << 'ENDSSH'
set -e

# Update system
sudo apt update
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx

# Add user to docker group (root doesn't need this)
# Root user already has docker access

# Create project directory
mkdir -p /opt/acat-system

# Extract project files
cd /opt/acat-system
tar -xzf /tmp/acat-system-staging.tar.gz
rm /tmp/acat-system-staging.tar.gz

echo "✅ Files deployed to /opt/acat-system"
ENDSSH

log_info "Creating staging environment file on server..."
ssh -i $SSH_KEY $STAGING_USER@$STAGING_SERVER << ENDSSH
cat > /opt/acat-system/.env.staging << 'EOF'
# ACAT System - Staging Environment Variables
DEBUG=False
DJANGO_SETTINGS_MODULE=acat_system.settings.staging

# Database Configuration
DB_NAME=acat_staging
DB_USER=acat_staging_user
DB_PASSWORD=StAgInG_SecUre_P@ssw0rd_2025
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=staging-ultra-secure-secret-key-change-for-production-2025
ALLOWED_HOSTS=staging.acatcr.org,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://staging.acatcr.org,http://staging.acatcr.org
CSRF_TRUSTED_ORIGINS=https://staging.acatcr.org,http://staging.acatcr.org

# Email Configuration (for staging - using console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Static and Media Files
STATIC_ROOT=/var/www/acat-system/static/
MEDIA_ROOT=/var/www/acat-system/media/
EOF

echo "✅ Environment file created"
ENDSSH

log_info "Creating production docker-compose file..."
ssh -i $SSH_KEY $STAGING_USER@$STAGING_SERVER << 'ENDSSH'
cat > /opt/acat-system/docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    container_name: acat_postgres_staging
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      PGUSER: ${DB_USER}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - acat_network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: acat_redis_staging
    volumes:
      - redis_data:/data
    networks:
      - acat_network
    restart: unless-stopped

  web:
    build:
      context: .
      dockerfile: Dockerfile.staging
    container_name: acat_web_staging
    env_file:
      - .env.staging
    volumes:
      - static_files:/var/www/acat-system/static
      - media_files:/var/www/acat-system/media
      - ./logs:/app/logs
    networks:
      - acat_network
    depends_on:
      - db
      - redis
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: acat_nginx_staging
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/conf.d/default.conf
      - static_files:/var/www/acat-system/static:ro
      - media_files:/var/www/acat-system/media:ro
      - ./ssl:/etc/ssl/certs:ro
    networks:
      - acat_network
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_files:
  media_files:

networks:
  acat_network:
    driver: bridge
EOF

echo "✅ Production docker-compose file created"
ENDSSH

# Clean up local tar file
rm acat-system-staging.tar.gz

log_info "✅ Staging deployment preparation complete!"
echo ""
echo "🔧 Next steps to complete staging setup:"
echo "1. Configure DNS: staging.acatcr.org → $STAGING_SERVER"
echo "2. SSH to server: ssh $STAGING_USER@$STAGING_SERVER"
echo "3. Go to project: cd /opt/acat-system"
echo "4. Create Nginx config: ./create-nginx-config.sh"
echo "5. Deploy: docker-compose -f docker-compose.production.yml up -d"
echo "6. Setup SSL: sudo certbot --nginx -d staging.acatcr.org"
echo ""
echo "📋 Server access:"
echo "   ssh -i $SSH_KEY $STAGING_USER@$STAGING_SERVER"
echo "   Project location: /opt/acat-system"
