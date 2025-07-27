#!/bin/bash
# ACAT System - Automated Backup Script for Staging

set -e

# Configuration
BACKUP_DIR="/app/backups/staging"
DB_NAME="acat_staging"
DB_USER="acat_staging_user"
DB_HOST="db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

echo "🔄 Starting ACAT Staging Backup - $TIMESTAMP"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "📊 Backing up database..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME --no-password > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
if [ $? -eq 0 ]; then
    echo "✅ Database backup completed: db_backup_$TIMESTAMP.sql"
    gzip "$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
    echo "✅ Database backup compressed"
else
    echo "❌ Database backup failed"
    exit 1
fi

# Media files backup
echo "📁 Backing up media files..."
if [ -d "/app/media" ] && [ "$(ls -A /app/media)" ]; then
    tar -czf "$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz" -C /app media/
    echo "✅ Media files backup completed: media_backup_$TIMESTAMP.tar.gz"
else
    echo "ℹ️  No media files to backup"
fi

# Configuration backup
echo "⚙️  Backing up configuration..."
tar -czf "$BACKUP_DIR/config_backup_$TIMESTAMP.tar.gz" \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    -C /app \
    acat_system/ \
    requirements.txt \
    .env.staging \
    docker-compose.staging.yml \
    Dockerfile.staging
echo "✅ Configuration backup completed: config_backup_$TIMESTAMP.tar.gz"

# Clean old backups
echo "🧹 Cleaning old backups (older than $RETENTION_DAYS days)..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "✅ Old backups cleaned"

# Backup summary
echo "📋 Backup Summary:"
echo "   Database: db_backup_$TIMESTAMP.sql.gz"
if [ -f "$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz" ]; then
    echo "   Media: media_backup_$TIMESTAMP.tar.gz"
fi
echo "   Config: config_backup_$TIMESTAMP.tar.gz"
echo "   Location: $BACKUP_DIR"

# Calculate backup sizes
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
echo "   Total backup size: $TOTAL_SIZE"

echo "✅ Backup completed successfully!"

# Optional: Send notification (uncomment if needed)
# curl -X POST "your-webhook-url" \
#      -H "Content-Type: application/json" \
#      -d "{\"text\":\"ACAT Staging backup completed: $TIMESTAMP\"}"
