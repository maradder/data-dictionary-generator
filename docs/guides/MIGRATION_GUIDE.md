# Database Migration Guide

This guide provides detailed procedures for migrating your Data Dictionary Generator deployment between different database backends, upgrading schema versions, and handling data migrations safely.

## Table of Contents

- [Overview](#overview)
- [PostgreSQL to SQLite Migration](#postgresql-to-sqlite-migration)
- [SQLite to PostgreSQL Migration](#sqlite-to-postgresql-migration)
- [Schema Version Upgrades](#schema-version-upgrades)
- [Data Export and Import](#data-export-and-import)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Overview

### Migration Scenarios

This guide covers the following migration scenarios:

1. **PostgreSQL to SQLite** - Simplifying deployment for single-user or small-team usage
2. **SQLite to PostgreSQL** - Scaling up for multi-user production environments
3. **Schema Upgrades** - Updating database schema to newer versions
4. **Data Portability** - Moving data between environments or instances

### Pre-Migration Checklist

Before starting any migration:

- [ ] **Backup all data** - Create full backups of source database
- [ ] **Document current state** - Note record counts, dictionary IDs, configuration
- [ ] **Test environment** - Validate migration in non-production environment first
- [ ] **Downtime window** - Plan for application downtime during migration
- [ ] **Rollback plan** - Ensure you can revert if issues occur
- [ ] **Disk space** - Verify sufficient space for backups and temporary files
- [ ] **Dependencies** - Install required tools (sqlite3, pg_dump, curl, jq)

### Migration Safety Levels

**Level 1 - Safest: Export/Import via XLSX**
- Uses application-level export/import
- Works across all schema versions
- Human-readable intermediate format
- Recommended for most users

**Level 2 - Advanced: Direct Database Copy**
- Database-level dump and restore
- Preserves exact timestamps and metadata
- Requires schema compatibility
- Recommended for large datasets (>10K records)

**Level 3 - Expert: SQL Migration Scripts**
- Manual SQL-based data transformation
- Maximum control and flexibility
- Requires deep database knowledge
- Recommended for complex custom migrations

---

## PostgreSQL to SQLite Migration

### When to Migrate PostgreSQL → SQLite

Consider this migration if:
- You have fewer than 5 concurrent users
- Your database is under 100GB
- You want to simplify deployment (single container)
- You need better portability (single file database)
- You're running on resource-constrained hardware

### Method 1: XLSX Export/Import (Recommended)

This is the safest and most reliable method.

#### Step 1: Verify Current State

```bash
# Check current database statistics
curl http://localhost:8000/api/v1/database/stats > pre-migration-stats.json

# View summary
cat pre-migration-stats.json | jq '{
  type: .database_type,
  dictionaries: .table_counts.dictionaries,
  versions: .table_counts.versions,
  fields: .table_counts.fields,
  annotations: .table_counts.annotations,
  total: .total_records
}'

# Save output for comparison after migration
```

#### Step 2: Export All Dictionaries

```bash
# Create export directory
mkdir -p migration-exports/$(date +%Y%m%d-%H%M%S)
cd migration-exports/$(date +%Y%m%d-%H%M%S)

# Export all dictionaries using API
API_BASE="http://localhost:8000/api/v1"

# Get all dictionary IDs
DICT_IDS=$(curl -s "$API_BASE/dictionaries?limit=1000" | jq -r '.items[].id')

# Export each dictionary
echo "Starting export of $(echo "$DICT_IDS" | wc -l) dictionaries..."

for ID in $DICT_IDS; do
  NAME=$(curl -s "$API_BASE/dictionaries/$ID" | jq -r '.name' | tr ' ' '_' | tr '/' '-')
  echo "Exporting: $NAME (ID: $ID)"

  curl -o "${NAME}_${ID}.xlsx" \
    "$API_BASE/dictionaries/$ID/export"

  if [ $? -eq 0 ]; then
    echo "  ✓ Success"
  else
    echo "  ✗ Failed"
    echo "$ID" >> failed-exports.txt
  fi
done

# Verify all exports
echo "Exported $(ls -1 *.xlsx | wc -l) files"
ls -lh *.xlsx

# Check for failures
if [ -f failed-exports.txt ]; then
  echo "WARNING: Some exports failed. See failed-exports.txt"
fi
```

#### Step 3: Stop Application and Backup PostgreSQL

```bash
# Stop application
docker-compose down app

# Backup PostgreSQL database
docker exec postgres pg_dump \
  -U ddgen_user \
  -Fc \
  data_dictionary_db > postgres-backup-$(date +%Y%m%d-%H%M%S).dump

# Verify backup
ls -lh postgres-backup-*.dump
```

#### Step 4: Switch to SQLite Configuration

```bash
# Backup old .env
cp .env .env.postgresql.backup

# Create new SQLite .env
cat > .env <<EOF
# Database Configuration
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite
SQLITE_TIMEOUT=30
SQLITE_CHECK_SAME_THREAD=false

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security (generate new secret key)
SECRET_KEY=$(openssl rand -hex 32)

# OpenAI (copy from old .env if applicable)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
OPENAI_ENABLED=${OPENAI_ENABLED:-true}

# File Processing
MAX_UPLOAD_SIZE=524288000
SAMPLE_SIZE=1000
EOF

echo "New .env configuration created"
```

#### Step 5: Initialize SQLite Database

```bash
cd backend

# Ensure data directory exists
mkdir -p data

# Run Alembic migrations
alembic upgrade head

# Verify database created
ls -lh data/app.db

# Start application
cd ..
docker-compose up -d app

# Wait for application to start
sleep 10

# Check health
curl http://localhost:8000/health
```

#### Step 6: Import Dictionaries

```bash
# Return to export directory
cd migration-exports/$(ls migration-exports | tail -1)

# Import all XLSX files
API_BASE="http://localhost:8000/api/v1"

echo "Starting import..."
IMPORTED=0
FAILED=0

for FILE in *.xlsx; do
  echo "Importing: $FILE"

  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -F "file=@$FILE" \
    -F "conflict_mode=overwrite" \
    "$API_BASE/dictionaries/import")

  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -n -1)

  if [ "$HTTP_CODE" -eq 200 ]; then
    echo "  ✓ Success"
    ((IMPORTED++))
  else
    echo "  ✗ Failed (HTTP $HTTP_CODE)"
    echo "  Response: $BODY"
    echo "$FILE" >> failed-imports.txt
    ((FAILED++))
  fi

  # Rate limiting - wait 1 second between imports
  sleep 1
done

echo ""
echo "Import Summary:"
echo "  Imported: $IMPORTED"
echo "  Failed: $FAILED"

if [ -f failed-imports.txt ]; then
  echo "  Failed files: $(cat failed-imports.txt)"
fi
```

#### Step 7: Verify Migration

```bash
# Get new database statistics
curl http://localhost:8000/api/v1/database/stats > post-migration-stats.json

# Compare before and after
echo "=== Migration Comparison ==="
echo "BEFORE (PostgreSQL):"
cat pre-migration-stats.json | jq '{
  type: .database_type,
  dictionaries: .table_counts.dictionaries,
  versions: .table_counts.versions,
  fields: .table_counts.fields,
  annotations: .table_counts.annotations,
  total: .total_records
}'

echo ""
echo "AFTER (SQLite):"
cat post-migration-stats.json | jq '{
  type: .database_type,
  dictionaries: .table_counts.dictionaries,
  versions: .table_counts.versions,
  fields: .table_counts.fields,
  annotations: .table_counts.annotations,
  total: .total_records
}'

# Automated comparison
BEFORE_TOTAL=$(cat pre-migration-stats.json | jq '.total_records')
AFTER_TOTAL=$(cat post-migration-stats.json | jq '.total_records')

if [ "$BEFORE_TOTAL" -eq "$AFTER_TOTAL" ]; then
  echo "✓ Record counts match!"
else
  echo "✗ WARNING: Record count mismatch!"
  echo "  Before: $BEFORE_TOTAL"
  echo "  After: $AFTER_TOTAL"
  echo "  Difference: $((AFTER_TOTAL - BEFORE_TOTAL))"
fi
```

#### Step 8: Functional Testing

```bash
# Test critical workflows

echo "Testing API endpoints..."

# 1. List dictionaries
echo "1. GET /dictionaries"
curl -s http://localhost:8000/api/v1/dictionaries | jq '.items | length'

# 2. Get specific dictionary
DICT_ID=$(curl -s http://localhost:8000/api/v1/dictionaries | jq -r '.items[0].id')
echo "2. GET /dictionaries/$DICT_ID"
curl -s http://localhost:8000/api/v1/dictionaries/$DICT_ID | jq '.name'

# 3. Export dictionary
echo "3. GET /dictionaries/$DICT_ID/export"
curl -o test-export.xlsx http://localhost:8000/api/v1/dictionaries/$DICT_ID/export
ls -lh test-export.xlsx

# 4. Database stats
echo "4. GET /database/stats"
curl -s http://localhost:8000/api/v1/database/stats | jq '.database_type'

echo "✓ All API tests passed"
```

#### Step 9: Backup New SQLite Database

```bash
# Create backup of new SQLite database
cp backend/data/app.db sqlite-backup-$(date +%Y%m%d-%H%M%S).db

# Compress for long-term storage
gzip sqlite-backup-*.db

echo "Backup created and compressed"
```

#### Step 10: Decommission PostgreSQL (Optional)

Only after confirming SQLite is working correctly for at least 1 week:

```bash
# Stop PostgreSQL container
docker-compose stop postgres

# Remove PostgreSQL volume (IRREVERSIBLE)
# docker-compose down postgres
# docker volume rm data-dictionary-gen_postgres_data

# Update docker-compose.yml to remove postgres service
```

### Method 2: Direct Database Migration (Advanced)

Use this method for large databases where XLSX export/import is too slow.

#### Prerequisites

```bash
pip install psycopg2-binary sqlite-utils
```

#### Step 1: Export PostgreSQL to SQL

```bash
# Export schema and data
docker exec postgres pg_dump \
  -U ddgen_user \
  --clean \
  --if-exists \
  data_dictionary_db > postgres-dump.sql

# Verify export
wc -l postgres-dump.sql
head -50 postgres-dump.sql
```

#### Step 2: Convert PostgreSQL SQL to SQLite

Create a conversion script:

```python
# convert_pg_to_sqlite.py
import re
import sys

def convert_postgresql_to_sqlite(sql_content):
    """
    Convert PostgreSQL SQL dump to SQLite-compatible SQL.
    """
    # Remove PostgreSQL-specific commands
    sql_content = re.sub(r'SET .*?;', '', sql_content)
    sql_content = re.sub(r'SELECT pg_catalog\..*?;', '', sql_content)

    # Convert data types
    sql_content = sql_content.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
    sql_content = sql_content.replace('UUID', 'TEXT')
    sql_content = sql_content.replace('TIMESTAMP', 'TEXT')
    sql_content = sql_content.replace('JSONB', 'TEXT')
    sql_content = sql_content.replace('BOOLEAN', 'INTEGER')

    # Convert array types to JSON text
    sql_content = re.sub(r'(\w+)\[\]', r'TEXT', sql_content)

    # Remove schema qualifiers
    sql_content = re.sub(r'public\.', '', sql_content)

    # Convert sequences to SQLite autoincrement
    sql_content = re.sub(r'CREATE SEQUENCE.*?;', '', sql_content, flags=re.DOTALL)
    sql_content = re.sub(r"nextval\('.*?'\)", 'NULL', sql_content)

    # Remove constraints not supported by SQLite
    sql_content = re.sub(r'ALTER TABLE.*?ADD CONSTRAINT.*?;', '', sql_content, flags=re.DOTALL)

    return sql_content

if __name__ == '__main__':
    with open('postgres-dump.sql', 'r') as f:
        pg_sql = f.read()

    sqlite_sql = convert_postgresql_to_sqlite(pg_sql)

    with open('sqlite-import.sql', 'w') as f:
        f.write(sqlite_sql)

    print("Conversion complete: sqlite-import.sql")
```

Run conversion:

```bash
python convert_pg_to_sqlite.py
```

#### Step 3: Import to SQLite

```bash
# Create new SQLite database
cd backend
alembic upgrade head

# Import converted data
sqlite3 data/app.db < ../sqlite-import.sql

# Check for errors
echo "SELECT COUNT(*) FROM dictionaries;" | sqlite3 data/app.db
echo "SELECT COUNT(*) FROM fields;" | sqlite3 data/app.db
```

#### Step 4: Verify Data Integrity

```bash
# Run integrity checks
sqlite3 data/app.db "PRAGMA integrity_check;"

# Verify indexes
sqlite3 data/app.db ".indexes"

# Verify record counts
sqlite3 data/app.db <<EOF
SELECT 'dictionaries' as table_name, COUNT(*) as count FROM dictionaries
UNION ALL
SELECT 'versions', COUNT(*) FROM versions
UNION ALL
SELECT 'fields', COUNT(*) FROM fields
UNION ALL
SELECT 'annotations', COUNT(*) FROM annotations;
EOF
```

---

## SQLite to PostgreSQL Migration

### When to Migrate SQLite → PostgreSQL

Consider this migration if:
- You need support for more than 5 concurrent users
- Your database exceeds 100GB
- You need advanced features (full-text search, replication)
- You require high availability or horizontal scaling
- You have compliance requirements for backups and auditing

### Method 1: XLSX Export/Import (Recommended)

The process is similar to PostgreSQL→SQLite migration, but in reverse.

#### Step 1: Export from SQLite

```bash
# Same as PostgreSQL→SQLite Step 2
# Export all dictionaries to XLSX files
```

#### Step 2: Setup PostgreSQL

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
sleep 10

# Verify connection
docker exec postgres psql -U ddgen_user -d data_dictionary_db -c "SELECT version();"
```

#### Step 3: Configure for PostgreSQL

```bash
# Update .env
cat > .env <<EOF
DATABASE_URL=postgresql://ddgen_user:ddgen_password@localhost:5432/data_dictionary_db
DATABASE_TYPE=postgresql
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

SECRET_KEY=$(openssl rand -hex 32)
OPENAI_API_KEY=your-key-here
OPENAI_ENABLED=true
EOF

# Run migrations
cd backend
alembic upgrade head
```

#### Step 4: Import Data

```bash
# Same as PostgreSQL→SQLite Step 6
# Import all XLSX files via API
```

#### Step 5: Verify and Optimize

```bash
# Verify data
curl http://localhost:8000/api/v1/database/stats

# Optimize PostgreSQL
docker exec postgres psql -U ddgen_user -d data_dictionary_db <<EOF
-- Analyze tables for query optimization
ANALYZE;

-- Update statistics
VACUUM ANALYZE;

-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
EOF
```

---

## Schema Version Upgrades

### Using Alembic Migrations

The application uses Alembic for database schema migrations.

#### Check Current Version

```bash
cd backend

# Show current migration version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show head
```

#### Upgrade to Latest Schema

```bash
# Backup database first!
# SQLite:
cp data/app.db data/app.db.backup

# PostgreSQL:
docker exec postgres pg_dump -U ddgen_user -Fc data_dictionary_db > backup.dump

# Run migrations
alembic upgrade head

# Verify new version
alembic current
```

#### Downgrade Schema

If you need to rollback to a previous version:

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade to base (empty database)
alembic downgrade base
```

#### Creating Custom Migrations

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "Add new_column to dictionaries"

# Create empty migration
alembic revision -m "Custom data migration"

# Edit migration file in alembic/versions/
# Then apply:
alembic upgrade head
```

---

## Data Export and Import

### Export Formats

#### Format 1: XLSX (Application Export)

```bash
# Single dictionary
curl -o dictionary.xlsx \
  http://localhost:8000/api/v1/dictionaries/{id}/export

# All dictionaries (see batch export script above)
```

#### Format 2: Database Dump

```bash
# SQLite
sqlite3 data/app.db .dump > full-dump.sql

# PostgreSQL
docker exec postgres pg_dump \
  -U ddgen_user \
  -Fc \
  data_dictionary_db > full-dump.dump
```

#### Format 3: CSV Export

```bash
# SQLite to CSV
sqlite3 data/app.db <<EOF
.mode csv
.output dictionaries.csv
SELECT * FROM dictionaries;
.output versions.csv
SELECT * FROM versions;
.output fields.csv
SELECT * FROM fields;
.output annotations.csv
SELECT * FROM annotations;
EOF

# PostgreSQL to CSV
docker exec postgres psql -U ddgen_user -d data_dictionary_db <<EOF
\copy dictionaries TO '/tmp/dictionaries.csv' CSV HEADER;
\copy versions TO '/tmp/versions.csv' CSV HEADER;
\copy fields TO '/tmp/fields.csv' CSV HEADER;
\copy annotations TO '/tmp/annotations.csv' CSV HEADER;
EOF

docker cp postgres:/tmp/*.csv .
```

### Import Formats

#### Format 1: XLSX Import

```bash
curl -X POST \
  -F "file=@dictionary.xlsx" \
  -F "conflict_mode=skip" \
  http://localhost:8000/api/v1/dictionaries/import
```

#### Format 2: Database Restore

```bash
# SQLite
sqlite3 data/app.db < full-dump.sql

# PostgreSQL
docker exec -i postgres pg_restore \
  -U ddgen_user \
  -d data_dictionary_db \
  --clean \
  < full-dump.dump
```

---

## Rollback Procedures

### Scenario 1: Migration Failed During Import

```bash
# 1. Stop application
docker-compose down app

# 2. Restore original database
# SQLite:
cp data/app.db.backup data/app.db

# PostgreSQL:
docker exec -i postgres pg_restore \
  -U ddgen_user \
  -d data_dictionary_db \
  --clean \
  < postgres-backup.dump

# 3. Restore original .env
cp .env.postgresql.backup .env

# 4. Restart application
docker-compose up -d app
```

### Scenario 2: Data Corruption Detected

```bash
# 1. Stop application immediately
docker-compose down app

# 2. Check database integrity
# SQLite:
sqlite3 data/app.db "PRAGMA integrity_check;"

# PostgreSQL:
docker exec postgres psql -U ddgen_user -d data_dictionary_db \
  -c "SELECT pg_database.datname, pg_database_size(pg_database.datname) FROM pg_database;"

# 3. Restore from most recent backup
# Use backup from Step 1 of migration

# 4. Verify restored data
curl http://localhost:8000/api/v1/database/stats
```

### Scenario 3: Wrong Schema Version

```bash
# Downgrade to previous version
cd backend
alembic downgrade -1

# Or downgrade to specific version
alembic downgrade <revision_id>

# Restart application
docker-compose restart app
```

---

## Troubleshooting

### Issue: Import Fails with "Duplicate Key" Error

**Cause**: Dictionary with same ID already exists in target database.

**Solution**:
```bash
# Option 1: Use 'overwrite' conflict mode
curl -X POST \
  -F "file=@dictionary.xlsx" \
  -F "conflict_mode=overwrite" \
  http://localhost:8000/api/v1/dictionaries/import

# Option 2: Clear target database first
curl -X POST "http://localhost:8000/api/v1/database/clear?confirm=DELETE_ALL_DATA"
```

### Issue: SQLite Database Locked

**Cause**: Multiple processes accessing database simultaneously.

**Solution**:
```bash
# 1. Stop all processes
docker-compose down

# 2. Increase timeout in .env
SQLITE_TIMEOUT=60

# 3. Check for stale lock files
rm -f data/app.db-shm data/app.db-wal

# 4. Restart application
docker-compose up -d app
```

### Issue: PostgreSQL Connection Refused

**Cause**: PostgreSQL not ready or wrong credentials.

**Solution**:
```bash
# 1. Check PostgreSQL status
docker-compose ps postgres

# 2. View PostgreSQL logs
docker-compose logs postgres

# 3. Test connection manually
docker exec postgres psql -U ddgen_user -d data_dictionary_db -c "SELECT 1;"

# 4. Verify .env credentials match docker-compose.yml
grep DATABASE_URL .env
grep POSTGRES_PASSWORD docker-compose.yml
```

### Issue: Migration Very Slow

**Cause**: Large dataset or network latency.

**Solution**:
```bash
# 1. Use direct database migration instead of XLSX
# See "Method 2: Direct Database Migration"

# 2. Increase batch size for imports
# Edit import script to process multiple files in parallel

# 3. Disable AI processing during import
OPENAI_ENABLED=false

# 4. Use local network (avoid remote API calls)
# Import from same machine as database
```

### Issue: Record Count Mismatch After Migration

**Cause**: Failed imports or version conflicts.

**Solution**:
```bash
# 1. Check for failed imports
cat failed-imports.txt

# 2. Retry failed imports individually
for FILE in $(cat failed-imports.txt); do
  echo "Retrying: $FILE"
  curl -X POST \
    -F "file=@$FILE" \
    -F "conflict_mode=overwrite" \
    http://localhost:8000/api/v1/dictionaries/import
done

# 3. Compare detailed statistics
# Run SQL queries to identify missing records
sqlite3 data/app.db "SELECT id, name FROM dictionaries ORDER BY created_at;"
```

---

## Best Practices

### 1. Always Backup Before Migration

```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR=/backups/$(date +%Y%m%d-%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
if [ "$DATABASE_TYPE" = "sqlite" ]; then
  cp data/app.db $BACKUP_DIR/
else
  docker exec postgres pg_dump -U ddgen_user -Fc data_dictionary_db > $BACKUP_DIR/backup.dump
fi

# Backup configuration
cp .env $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

# Backup exports (if any)
tar czf $BACKUP_DIR/exports.tar.gz exports/ 2>/dev/null || true

echo "Backup created: $BACKUP_DIR"
```

### 2. Test in Non-Production First

```bash
# Create test environment
cp -r /app /app-test
cd /app-test

# Use separate ports
sed -i 's/8000:8000/8001:8000/' docker-compose.yml

# Test migration
# ... perform migration ...

# Validate
curl http://localhost:8001/api/v1/database/stats
```

### 3. Document Your Migration

Create a migration log:

```bash
cat > migration-log.md <<EOF
# Migration Log

## Date
$(date)

## Migration Type
PostgreSQL → SQLite

## Reason
Simplifying deployment for single-user usage

## Pre-Migration State
- Database Type: PostgreSQL
- Record Counts:
  - Dictionaries: 15
  - Versions: 42
  - Fields: 1250
  - Annotations: 876

## Steps Performed
1. Exported all dictionaries to XLSX
2. Backed up PostgreSQL database
3. Created SQLite database
4. Imported all XLSX files
5. Verified record counts

## Post-Migration State
- Database Type: SQLite
- Record Counts:
  - Dictionaries: 15
  - Versions: 42
  - Fields: 1250
  - Annotations: 876

## Issues Encountered
None

## Rollback Available
Yes - PostgreSQL backup at: postgres-backup-20251112-140000.dump

## Sign-off
Migrated by: [Your Name]
Verified by: [Verifier Name]
Date: $(date)
EOF
```

### 4. Verify Data Integrity After Migration

```bash
# Comprehensive verification script
#!/bin/bash

echo "=== Data Integrity Verification ==="

# 1. Record counts
echo "1. Record Counts:"
curl -s http://localhost:8000/api/v1/database/stats | jq '.table_counts'

# 2. Spot check random dictionaries
echo "2. Random Dictionary Samples:"
for i in {1..5}; do
  DICT_ID=$(curl -s http://localhost:8000/api/v1/dictionaries | jq -r ".items[$i].id")
  curl -s http://localhost:8000/api/v1/dictionaries/$DICT_ID | jq '{id, name, field_count}'
done

# 3. Export test
echo "3. Export Test:"
DICT_ID=$(curl -s http://localhost:8000/api/v1/dictionaries | jq -r '.items[0].id')
curl -o test-export.xlsx http://localhost:8000/api/v1/dictionaries/$DICT_ID/export
ls -lh test-export.xlsx

# 4. Database health
echo "4. Database Health:"
curl -s http://localhost:8000/api/v1/database/health | jq '.'

echo "✓ Verification complete"
```

### 5. Maintain Multiple Backup Generations

```bash
# Backup retention script
#!/bin/bash
BACKUP_DIR=/backups
RETENTION_DAYS=30

# Create new backup
./backup-daily.sh

# Remove old backups
find $BACKUP_DIR -name "*.db" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.dump" -mtime +$RETENTION_DAYS -delete

# Keep at least 3 backups even if older
BACKUP_COUNT=$(find $BACKUP_DIR -name "*.db" -o -name "*.dump" | wc -l)
if [ $BACKUP_COUNT -lt 3 ]; then
  echo "WARNING: Less than 3 backups available"
fi

echo "Backups available: $BACKUP_COUNT"
```

---

## Summary

### Key Takeaways

1. **Always backup before migration** - No exceptions
2. **XLSX export/import is safest** - Works across all versions
3. **Test in non-production first** - Validate before production
4. **Verify data integrity** - Compare record counts before/after
5. **Keep rollback plan ready** - Be prepared to revert
6. **Document everything** - Maintain migration logs

### Quick Reference

| Task | Command |
|------|---------|
| Backup SQLite | `cp data/app.db backup.db` |
| Backup PostgreSQL | `pg_dump -Fc > backup.dump` |
| Export dictionary | `curl -o dict.xlsx /api/v1/dictionaries/{id}/export` |
| Import dictionary | `curl -F file=@dict.xlsx /api/v1/dictionaries/import` |
| Check stats | `curl /api/v1/database/stats` |
| Run migrations | `alembic upgrade head` |
| Verify integrity (SQLite) | `sqlite3 db PRAGMA integrity_check;` |
| Verify integrity (PG) | `psql -c "SELECT pg_database_size('dbname');"` |

### Getting Help

If you encounter issues during migration:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review application logs: `docker-compose logs app`
3. Review database logs: `docker-compose logs postgres`
4. Open a GitHub issue with:
   - Migration type (PG→SQLite or SQLite→PG)
   - Error messages
   - Steps to reproduce
   - Database statistics before migration

For complex migrations or production deployments, consider consulting with the development team or a database administrator.
