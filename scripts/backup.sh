#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups"
DB_NAME="${DB_NAME:-todoapp}"
DB_USER="${DB_USER:-todo_user}"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/todo_${TIMESTAMP}.sql

# Compress backup
gzip $BACKUP_DIR/todo_${TIMESTAMP}.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "todo_*.sql.gz" -mtime +30 -delete

echo "Backup completed: todo_${TIMESTAMP}.sql.gz"
