#!/bin/bash

# ACAT System - Simple Staging Entrypoint for Testing
# This is a simplified version for initial testing

set -e

echo "🚀 ACAT System - Simple Staging Environment Startup"
echo "============================================="

# Basic environment validation
echo "📋 Validating basic environment..."
if [ -z "$DB_NAME" ] || [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ ERROR: Database environment variables not properly set"
    echo "Required: DB_NAME, DB_HOST, DB_USER, DB_PASSWORD"
    exit 1
fi
echo "✅ Basic environment validation passed"

# Wait for PostgreSQL to be ready
echo "🔍 Waiting for PostgreSQL to be ready..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "⏳ PostgreSQL is unavailable - sleeping for 2 seconds"
    sleep 2
done
echo "✅ PostgreSQL is ready!"

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
echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@staging.acat.local', 'staging_admin_2025')
    print('✅ Superuser created: admin / staging_admin_2025')
else:
    print('ℹ️ Superuser already exists')
" 2>/dev/null || echo "⚠️ Superuser creation skipped"

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"

# Run system checks
echo "🔧 Running Django system checks..."
python manage.py check --deploy
if [ $? -eq 0 ]; then
    echo "✅ System checks passed"
else
    echo "⚠️ System checks completed with warnings"
fi

echo "🎉 Staging environment ready!"
echo "🌐 Starting application server..."

# Execute the main command
exec "$@"
