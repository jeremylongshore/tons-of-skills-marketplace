---
name: automating-database-backups
description: 'Automate database backup processes with scheduling, compression, and
  encryption.

  Supports PostgreSQL (pg_dump), MySQL (mysqldump), MongoDB (mongodump), and SQLite.

  Generates production-ready backup scripts with retention policies and restore procedures.

  Trigger: "automate database backups", "schedule backups", "create backup script",
  "disaster recovery". Use when working with automating database backups. Trigger
  with ''automating'', ''database'', ''backups''.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(pg_dump:*), Bash(mysqldump:*),
  Bash(mongodump:*), Bash(cron:*), Bash(gpg:*)
version: 1.27.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- database
- postgresql
- mysql
- mongodb
compatibility: Designed for Claude Code
---
# Database Backup Automation

Generate production-ready backup scripts for PostgreSQL, MySQL, MongoDB, and SQLite with compression, encryption, scheduling, and retention policies.

## Quick Start

### PostgreSQL Backup

```bash
#!/bin/bash
set -euo pipefail
BACKUP_DIR="/var/backups/postgresql"
DB_NAME="mydb"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz"

pg_dump -h localhost -U postgres -d "$DB_NAME" \
  --format=custom \
  --compress=9 \
  --file="$BACKUP_FILE"

# Encrypt with GPG (optional)
gpg --symmetric --cipher-algo AES256 --batch --passphrase-file /etc/backup.key "$BACKUP_FILE"
rm "$BACKUP_FILE"
```

### MySQL Backup

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mysql"
DB_NAME="mydb"
DATE=$(date +%Y%m%d_%H%M%S)

mysqldump -h localhost -u root -p"${MYSQL_PASSWORD}" \
  --single-transaction \
  --routines \
  --triggers \
  "$DB_NAME" | gzip > "${BACKUP_DIR}/${DB_NAME}_${DATE}.sql.gz"
```

### MongoDB Backup

```bash
#!/bin/bash
mongodump --uri="mongodb://localhost:27017" \  # 27017: MongoDB port
  --db=mydb \
  --out=/var/backups/mongodb/$(date +%Y%m%d_%H%M%S) \
  --gzip
```

## Instructions

### Step 1: Gather Requirements

Ask the user for:

- Database type (PostgreSQL, MySQL, MongoDB, SQLite)
- Database connection details (host, port, database name)
- Backup schedule (cron expression or frequency)
- Retention policy (days to keep)
- Encryption requirement (yes/no)
- Backup destination (local path, S3, GCS)

### Step 2: Generate Backup Script

Use `scripts/backup_script_generator.py` to create a customized backup script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/backup_script_generator.py \
  --db-type postgresql \
  --database mydb \
  --output /opt/backup-scripts/mydb-backup.sh \
  --compression gzip \
  --encryption gpg
```

### Step 3: Schedule with Cron

Use `scripts/backup_scheduler.py` to create cron entries:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/backup_scheduler.py \
  --script /opt/backup-scripts/mydb-backup.sh \
  --schedule "0 2 * * *" \
  --user postgres
```

### Step 4: Validate Backup

After backup completes, validate integrity:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/backup_validator.py \
  --backup-file /var/backups/postgresql/mydb_20250115.sql.gz \
  --db-type postgresql
```

### Step 5: Generate Restore Procedure

Create matching restore script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/restore_script_generator.py \
  --db-type postgresql \
  --database mydb \
  --output /opt/backup-scripts/mydb-restore.sh
```

## Cron Schedule Reference

| Schedule | Cron Expression | Description |
|----------|-----------------|-------------|
| Daily 2 AM | `0 2 * * *` | Low-traffic window |
| Every 6 hours | `0 */6 * * *` | Frequent backups |
| Weekly Sunday | `0 2 * * 0` | Weekly full backup |
| Monthly 1st | `0 2 1 * *` | Monthly archive |

## Retention Policy Example

```bash
# Keep daily backups for 7 days
# Keep weekly backups for 4 weeks
# Keep monthly backups for 12 months

find /var/backups -name "*.gz" -mtime +7 -delete  # Daily cleanup
find /var/backups/weekly -mtime +28 -delete       # Weekly cleanup
find /var/backups/monthly -mtime +365 -delete     # 365: Monthly cleanup
```

## Output

- **Backup Scripts**: Database-specific shell scripts with compression and encryption
- **Cron Entries**: Ready-to-install crontab configurations
- **Restore Scripts**: Matching restore procedures for each backup type
- **Validation Reports**: Integrity check results for backup files

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | DB not running | Check service status: `systemctl status postgresql` |
| Permission denied | Wrong credentials | Verify user has backup privileges |
| Disk full | No space | Check space: `df -h`, clean old backups |
| Lock timeout | Active transactions | Use `--single-transaction` for MySQL |

## Resources

- [`references/postgresql_backup_restore.md`](references/postgresql_backup_restore.md) - PostgreSQL backup guide
- [`references/mysql_backup_restore.md`](references/mysql_backup_restore.md) - MySQL backup guide
- [`references/mongodb_backup_restore.md`](references/mongodb_backup_restore.md) - MongoDB backup guide
- [`references/sqlite_backup_restore.md`](references/sqlite_backup_restore.md) - SQLite backup guide
- [`references/backup_best_practices.md`](references/backup_best_practices.md) - Security and storage best practices
- [`references/cron_syntax.md`](references/cron_syntax.md) - Cron scheduling reference

## Overview

Automate database backup processes with scheduling, compression, and encryption.

## Prerequisites

- Access to the PostgreSQL environment or API
- Required CLI tools installed and authenticated
- Familiarity with PostgreSQL concepts and terminology

## Examples

**Basic usage**: Apply automating database backups to a standard project setup with default configuration options.

**Advanced scenario**: Customize automating database backups for production environments with multiple constraints and team-specific requirements.
