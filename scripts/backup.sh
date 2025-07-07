#!/bin/bash
# === NEXTVISION BACKUP SCRIPT ===
# Automated backup for production data

set -e

# Configuration
BACKUP_DIR="/backup"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30
S3_BUCKET="${S3_BACKUP_BUCKET:-}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Backup PostgreSQL
backup_postgres() {
    log "Starting PostgreSQL backup..."
    
    local backup_file="${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz"
    
    if pg_dump -h "${DB_HOST}" -U "${DB_USER}" "${DB_NAME}" | gzip > "$backup_file"; then
        log "PostgreSQL backup completed: $backup_file"
        echo "$backup_file"
    else
        log_error "PostgreSQL backup failed"
        return 1
    fi
}

# Backup Redis
backup_redis() {
    log "Starting Redis backup..."
    
    local backup_file="${BACKUP_DIR}/redis_${TIMESTAMP}.rdb"
    
    if cp /backup/redis/dump.rdb "$backup_file" 2>/dev/null; then
        gzip "$backup_file"
        log "Redis backup completed: ${backup_file}.gz"
        echo "${backup_file}.gz"
    else
        log_error "Redis backup failed"
        return 1
    fi
}

# Backup logs
backup_logs() {
    log "Starting logs backup..."
    
    local backup_file="${BACKUP_DIR}/logs_${TIMESTAMP}.tar.gz"
    
    if tar -czf "$backup_file" -C /backup/logs . 2>/dev/null; then
        log "Logs backup completed: $backup_file"
        echo "$backup_file"
    else
        log_error "Logs backup failed"
        return 1
    fi
}

# Upload to S3
upload_to_s3() {
    local file="$1"
    
    if [[ -n "$S3_BUCKET" ]]; then
        log "Uploading $file to S3..."
        
        if aws s3 cp "$file" "s3://${S3_BUCKET}/nextvision/$(basename "$file")"; then
            log "S3 upload completed"
        else
            log_error "S3 upload failed"
        fi
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.sql" -mtime +$RETENTION_DAYS -delete
    
    log "Cleanup completed"
}

# Main backup function
main() {
    log "=== Nextvision Backup Started ==="
    
    mkdir -p "$BACKUP_DIR"
    
    local backup_files=()
    
    # PostgreSQL backup
    if postgres_file=$(backup_postgres); then
        backup_files+=("$postgres_file")
    fi
    
    # Redis backup
    if redis_file=$(backup_redis); then
        backup_files+=("$redis_file")
    fi
    
    # Logs backup
    if logs_file=$(backup_logs); then
        backup_files+=("$logs_file")
    fi
    
    # Upload to S3
    for file in "${backup_files[@]}"; do
        upload_to_s3 "$file"
    done
    
    # Cleanup
    cleanup_old_backups
    
    log "=== Backup Completed ==="
    log "Files created: ${#backup_files[@]}"
    
    return 0
}

main "$@"
