#!/bin/bash
# ACAT System - Health Check Script for Staging

set -e

# Configuration
DJANGO_URL="http://localhost:8000"
MAX_RESPONSE_TIME=30

echo "🏥 ACAT Staging Health Check"

# Check if Django is responding
echo "🔍 Checking Django application..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}:%{time_total}" --max-time $MAX_RESPONSE_TIME "$DJANGO_URL/health/" || echo "000:999")
HTTP_CODE=$(echo $RESPONSE | cut -d: -f1)
RESPONSE_TIME=$(echo $RESPONSE | cut -d: -f2)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Django application is healthy (${RESPONSE_TIME}s)"
else
    echo "❌ Django application is unhealthy (HTTP: $HTTP_CODE)"
    exit 1
fi

# Check database connectivity
echo "🔍 Checking database connectivity..."
python manage.py shell -c "
from django.db import connection
try:
    cursor = connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    if result[0] == 1:
        print('✅ Database connection is healthy')
    else:
        print('❌ Database query failed')
        exit(1)
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Database health check failed"
    exit 1
fi

# Check Redis connectivity
echo "🔍 Checking Redis connectivity..."
python manage.py shell -c "
from django.core.cache import cache
try:
    cache.set('health_check', 'ok', 60)
    result = cache.get('health_check')
    if result == 'ok':
        print('✅ Redis connection is healthy')
    else:
        print('❌ Redis operation failed')
        exit(1)
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Redis health check failed"
    exit 1
fi

# Check disk space
echo "🔍 Checking disk space..."
DISK_USAGE=$(df /app | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "⚠️  High disk usage: ${DISK_USAGE}%"
    exit 1
else
    echo "✅ Disk space is adequate (${DISK_USAGE}% used)"
fi

# Check memory usage
echo "🔍 Checking memory usage..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 90 ]; then
    echo "⚠️  High memory usage: ${MEMORY_USAGE}%"
    exit 1
else
    echo "✅ Memory usage is normal (${MEMORY_USAGE}% used)"
fi

echo "🎉 All health checks passed!"
exit 0
