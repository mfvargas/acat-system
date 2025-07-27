#!/bin/bash
set -e

echo "🔧 Starting ACAT System setup..."

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "✅ PostgreSQL is up - executing migrations"

# Run migrations
python manage.py migrate --noinput

# Collect static files for production
if [ "$DJANGO_SETTINGS_MODULE" != "acat_system.settings.development" ]; then
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
fi

echo "🚀 Starting Django application..."

# Execute the main command
exec "$@"
