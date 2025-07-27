#!/bin/bash
# ACAT System - Staging Deployment Script

set -e

echo "🚀 ACAT System - Staging Deployment"
echo "===================================="

# Configuration
COMPOSE_FILE="docker-compose.staging.yml"
ENV_FILE=".env.staging"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found."
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file $COMPOSE_FILE not found."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Environment validation
validate_environment() {
    log_info "Validating staging environment configuration..."
    
    # Check required environment variables
    source $ENV_FILE
    
    if [ -z "$DB_PASSWORD" ]; then
        log_error "DB_PASSWORD not set in $ENV_FILE"
        exit 1
    fi
    
    if [ "$SECRET_KEY" = "your-staging-secret-key-here-change-in-production" ]; then
        log_warning "SECRET_KEY should be changed for staging"
    fi
    
    log_success "Environment validation passed"
}

# Pre-deployment backup
backup_existing() {
    log_info "Creating backup of existing staging environment..."
    
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_info "Creating database backup before deployment..."
        docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U acat_staging_user acat_staging > "backup_pre_deploy_$(date +%Y%m%d_%H%M%S).sql"
        log_success "Database backup created"
    else
        log_info "No running staging environment found, skipping backup"
    fi
}

# Build and deploy
deploy() {
    log_info "Building staging images..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    log_success "Images built successfully"
    
    log_info "Starting staging services..."
    docker-compose -f $COMPOSE_FILE up -d
    log_success "Services started"
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    log_info "Running health checks..."
    max_attempts=12
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:8001/health/ > /dev/null 2>&1; then
            log_success "Health check passed"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                log_error "Health check failed after $max_attempts attempts"
                exit 1
            fi
            log_info "Health check attempt $attempt/$max_attempts failed, retrying in 10s..."
            sleep 10
            ((attempt++))
        fi
    done
}

# Post-deployment tasks
post_deploy() {
    log_info "Running post-deployment tasks..."
    
    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f $COMPOSE_FILE exec web python manage.py migrate --noinput
    log_success "Database migrations completed"
    
    # Collect static files
    log_info "Collecting static files..."
    docker-compose -f $COMPOSE_FILE exec web python manage.py collectstatic --noinput --clear
    log_success "Static files collected"
    
    # Create superuser if needed
    log_info "Ensuring superuser exists..."
    docker-compose -f $COMPOSE_FILE exec web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@staging.acat.local', 'staging_admin_2025')
    print('Staging superuser created')
else:
    print('Staging superuser already exists')
"
    log_success "Superuser check completed"
    
    # Load sample data
    log_info "Loading sample data..."
    docker-compose -f $COMPOSE_FILE exec web python test_system.py
    log_success "Sample data loaded"
}

# Show deployment summary
show_summary() {
    echo ""
    echo "🎉 STAGING DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo "============================================="
    echo ""
    echo "📊 Services Status:"
    docker-compose -f $COMPOSE_FILE ps
    echo ""
    echo "🌐 Access URLs:"
    echo "   • Main Application: http://localhost:8001"
    echo "   • Django Admin: http://localhost:8001/admin/"
    echo "   • API Root: http://localhost:8001/api/"
    echo "   • Nginx Proxy: http://localhost:8080"
    echo "   • Staging Info: http://localhost:8080/staging-info"
    echo ""
    echo "🔐 Credentials:"
    echo "   • Admin User: admin"
    echo "   • Admin Password: staging_admin_2025"
    echo ""
    echo "📊 Database:"
    echo "   • Host: localhost:5433"
    echo "   • Database: acat_staging"
    echo "   • User: acat_staging_user"
    echo ""
    echo "📁 Important Locations:"
    echo "   • Logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "   • Backups: ./backups/staging/"
    echo "   • Static Files: static_staging_volume"
    echo ""
    echo "🔧 Management Commands:"
    echo "   • View logs: docker-compose -f $COMPOSE_FILE logs -f [service]"
    echo "   • Shell access: docker-compose -f $COMPOSE_FILE exec web bash"
    echo "   • Django shell: docker-compose -f $COMPOSE_FILE exec web python manage.py shell"
    echo "   • Stop services: docker-compose -f $COMPOSE_FILE down"
    echo ""
    log_success "Staging environment is ready for testing!"
}

# Main deployment flow
main() {
    echo ""
    log_info "Starting ACAT System staging deployment..."
    echo ""
    
    check_prerequisites
    validate_environment
    backup_existing
    deploy
    post_deploy
    show_summary
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping staging services..."
        docker-compose -f $COMPOSE_FILE down
        log_success "Staging services stopped"
        ;;
    "restart")
        log_info "Restarting staging services..."
        docker-compose -f $COMPOSE_FILE restart
        log_success "Staging services restarted"
        ;;
    "logs")
        docker-compose -f $COMPOSE_FILE logs -f "${2:-}"
        ;;
    "status")
        echo "📊 Staging Services Status:"
        docker-compose -f $COMPOSE_FILE ps
        ;;
    "backup")
        log_info "Creating manual backup..."
        ./scripts/backup.sh
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|backup}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy staging environment (default)"
        echo "  stop    - Stop all staging services"
        echo "  restart - Restart all staging services"  
        echo "  logs    - Show logs (optionally specify service)"
        echo "  status  - Show service status"
        echo "  backup  - Create manual backup"
        exit 1
        ;;
esac
