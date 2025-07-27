#!/bin/bash
set -e

# ACAT System - Staging Entrypoint Script
# Handles initialization for staging environment

echo "🚀 ACAT System - Staging Environment Startup"
echo "============================================="

# Environment validation
echo "📋 Validating staging environment..."
if [ -z "$DB_NAME" ]; then
    echo "❌ ERROR: DB_NAME environment variable not set"
    exit 1
fi

if [ -z "$DB_USER" ]; then
    echo "❌ ERROR: DB_USER environment variable not set"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ ERROR: DB_PASSWORD environment variable not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Wait for PostgreSQL to be ready
echo "🔍 Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "⏳ PostgreSQL is unavailable - sleeping for 2 seconds"
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "🔍 Waiting for Redis to be ready..."
# Extract Redis host from REDIS_URL or use default
REDIS_HOST=${REDIS_HOST:-$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f1)}
REDIS_PORT=${REDIS_PORT:-6379}
echo "🔍 Trying to connect to Redis at $REDIS_HOST:$REDIS_PORT"
while ! python -c "import socket; sock = socket.socket(); sock.settimeout(2); result = sock.connect_ex(('$REDIS_HOST', $REDIS_PORT)); sock.close(); exit(0 if result == 0 else 1)" 2>/dev/null; do
    echo "⏳ Redis is unavailable - sleeping for 1 second"
    sleep 1
done
echo "✅ Redis is ready!"

# Database migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@staging.acat.local', 'staging_admin_2025')
    print('✅ Staging superuser created: admin')
else:
    print('ℹ️  Staging superuser already exists')
"

# Collect static files for staging
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then
    echo "✅ Static files collected"
else
    echo "❌ Static files collection failed"
    exit 1
fi

# Load initial data if specified
if [ "$LOAD_FIXTURES" = "true" ]; then
    echo "📊 Loading initial fixtures..."
    python manage.py loaddata staging_data.json
    echo "✅ Initial data loaded"
fi

# Run system checks
echo "🔍 Running Django system checks..."
python manage.py check --deploy
if [ $? -eq 0 ]; then
    echo "✅ System checks passed"
else
    echo "⚠️  System checks found issues (continuing anyway for staging)"
fi

# Warm up the cache
echo "🔥 Warming up cache..."
python manage.py shell -c "
from django.core.cache import cache
cache.set('staging_startup', 'ok', 300)
print('✅ Cache warmed up')
"

# Log startup completion
echo "📝 Logging startup completion..."
python manage.py shell -c "
import logging
logger = logging.getLogger('django')
logger.info('ACAT Staging environment started successfully')
print('✅ Startup logged')
"

# Create backup directory if needed
mkdir -p /app/backups/staging

# Start cron service for automated backups
if command -v cron > /dev/null; then
    echo "⏰ Starting cron service for automated backups..."
    cron
    echo "✅ Cron service started"
fi

echo "============================================="
echo "🎉 ACAT Staging Environment Ready!"
echo "🌐 Application will start on port 8000"
echo "📊 Database: $DB_NAME on $DB_HOST"
echo "💾 Redis: redis:6379"
echo "📁 Static files: /app/staticfiles"
echo "📷 Media files: /app/media"
echo "============================================="

# Execute the main command
exec "$@"
