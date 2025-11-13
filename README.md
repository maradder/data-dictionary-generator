# Data Dictionary Generator

**An intelligent, automated tool that generates comprehensive data dictionaries from JSON, XML, SQLite, GeoPackage, and Protocol Buffer files with AI-powered insights.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178c6.svg)](https://www.typescriptlang.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://www.postgresql.org/)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
  - [Option 1: SQLite Single-Container (Recommended)](#option-1-sqlite-single-container-recommended)
  - [Option 2: Local Development](#option-2-local-development)
  - [Option 3: PostgreSQL Advanced Setup](#option-3-postgresql-advanced-setup)
- [Database Management Guide](#database-management-guide)
- [Import/Export Workflows](#importexport-workflows)
- [Environment Variables Reference](#environment-variables-reference)
- [Migration from PostgreSQL to SQLite](#migration-from-postgresql-to-sqlite)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Architecture Highlights](#architecture-highlights)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Data Dictionary Generator is a powerful tool designed to help data engineers, analysts, and scientists understand their data structures quickly and comprehensively. Simply upload a JSON, XML, SQLite, GeoPackage, or Protocol Buffer file, and the system will:

- **Parse** complex nested structures (up to 500MB files)
- **Analyze** data types, statistics, and quality metrics
- **Detect** personally identifiable information (PII)
- **Generate** intelligent field descriptions using GPT-4
- **Track** schema versions over time
- **Export** professional Excel reports

This tool bridges the gap between raw data and documentation, making it easier for teams to maintain data catalogs, onboard new members, and ensure data quality.

---

## Key Features

### Data Processing
- **Multi-Format Support**: Handles JSON, XML, SQLite, GeoPackage, and Protocol Buffer files with format auto-detection
- **Streaming Parsers**: Memory-efficient streaming for large files (up to 500MB)
  - JSON with MongoDB Extended JSON support
  - **XML with DTD/XSD schema support** (element constraints, attribute types, validation)
  - XML with attributes, namespaces, and repeating elements
  - SQLite with schema extraction, constraints, and relationships
  - **GeoPackage with geospatial awareness** (geometry types, CRS, bounding boxes, spatial metadata)
  - **Protocol Buffers (.proto and .desc)** - Pure Python protoc support (no binary dependency required)
- **Nested Structure Support**: Automatically flattens and documents nested objects and arrays
- **Geospatial Intelligence**: Detects geometry columns, coordinate systems (EPSG codes), and spatial extents
- **Schema Validation**: DTD and XSD validation for XML files with constraint extraction
- **Automatic Type Inference**: Intelligently detects data types from sample values
- **Semantic Type Detection**: Recognizes emails, URLs, phone numbers, dates, currencies, and more

### Analytics & Quality
- **Comprehensive Statistics**: Min, max, mean, median, percentiles, standard deviation
- **Quality Metrics**: Null percentage, cardinality ratio, distinct counts
- **PII Detection**: Identifies emails, phone numbers, SSNs, credit cards
- **Sample Values**: Stores representative examples for each field

### AI-Powered Insights
- **GPT-4 Integration**: Generates contextual field descriptions automatically
- **Batch Processing**: Efficiently processes multiple fields in a single API call
- **Configurable**: Toggle AI generation on/off per dictionary

### Version Management
- **Schema Tracking**: Monitors field additions, removals, and type changes
- **Version Comparison**: Visualize differences between schema versions
- **Change History**: Complete audit trail of all schema modifications

### Export & Integration
- **Excel Export**: Professional, formatted spreadsheets with color-coded metrics
- **REST API**: Comprehensive API for programmatic access
- **Interactive UI**: Modern React interface with search, filters, and visualizations

---

## Technology Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** (0.104+) - Modern, high-performance Python web framework
- **[PostgreSQL](https://www.postgresql.org/)** (15+) - Robust relational database with JSONB support
- **[SQLAlchemy](https://www.sqlalchemy.org/)** (2.0) - Python SQL toolkit and ORM
- **[Pydantic](https://docs.pydantic.dev/)** (2.5+) - Data validation using Python type hints
- **[OpenAI API](https://platform.openai.com/)** - GPT-4 for field description generation
- **[pandas](https://pandas.pydata.org/)** - Statistical analysis and data processing
- **[ijson](https://pypi.org/project/ijson/)** - Streaming JSON parser for large files
- **[lxml](https://lxml.de/)** (5.0+) - High-performance XML parser with streaming support
- **[protobuf](https://protobuf.dev/)** (4.25+) - Protocol Buffer schema parsing
- **[grpcio-tools](https://grpc.io/docs/languages/python/quickstart/)** (1.60+) - Pure Python protoc compiler
- **[openpyxl](https://openpyxl.readthedocs.io/)** - Excel file generation
- **[Redis](https://redis.io/)** (7+) - Caching layer (planned for Phase 2)

### Frontend
- **[React](https://react.dev/)** (19) - Component-based UI library
- **[TypeScript](https://www.typescriptlang.org/)** (5.2+) - Type-safe JavaScript
- **[TanStack Query](https://tanstack.com/query)** - Server state management
- **[shadcn/ui](https://ui.shadcn.com/)** - Accessible component library
- **[TailwindCSS](https://tailwindcss.com/)** (3) - Utility-first CSS framework
- **[Vite](https://vitejs.dev/)** - Fast build tool and dev server
- **[React Router](https://reactrouter.com/)** (v6) - Client-side routing
- **[Recharts](https://recharts.org/)** - Data visualization library

**Note**: The built frontend is served statically by FastAPI, providing a single-port deployment at http://localhost:8000

### Infrastructure
- **[Docker](https://www.docker.com/)** - Containerization
- **[Docker Compose](https://docs.docker.com/compose/)** - Multi-container orchestration
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration tool

---

## Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended for quickest setup)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)
- **OpenAI API Key** (optional, for AI descriptions)

### Option 1: SQLite Single-Container (Recommended)

The fastest way to get started with zero configuration. Uses SQLite for data persistence.

```bash
# 1. Clone the repository
git clone <repository-url>
cd data-dictionary-gen

# 2. Create environment file
cat > .env <<EOF
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=$(openssl rand -hex 32)
OPENAI_API_KEY=your-key-here
OPENAI_ENABLED=true
EOF

# 3. Build and start the container
docker-compose up -d app

# 4. Access the application
# Application: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

**Architecture Note**: FastAPI serves both the API (at `/api/*`) and the built React frontend (at `/`). This single-port deployment simplifies hosting and eliminates CORS concerns.

Your SQLite database will be persisted in `./data/app.db`.

**Backup your data:**
```bash
# Create backup
cp data/app.db data/app-backup-$(date +%Y%m%d).db

# Or use the API
curl -o backup.db http://localhost:8000/api/v1/database/backup/download
```

### Option 2: Local Development

For active development with hot-reload and debugging.

#### 1. Start SQLite Backend (No Docker Required)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cat > .env <<EOF
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
EOF

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

#### 2. Setup Frontend (Choose One)

**Option A: Use Built Frontend (Single Port)**

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

The backend will automatically serve the built frontend at **http://localhost:8000**. This is the recommended approach for most development and all production deployments.

**Option B: Run Frontend Dev Server (Hot Reload)**

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cat > .env.development <<EOF
VITE_API_BASE_URL=http://localhost:8000
EOF

# Start frontend dev server
npm run dev
```

Frontend dev server will be available at **http://localhost:5173** with hot-reload capabilities. Use this for active frontend development only.

#### 3. Test with Sample Data

1. Open the application in your browser:
   - **Built frontend**: http://localhost:8000
   - **Dev server** (if running Option B): http://localhost:5173
2. Click "Upload New" button
3. Upload any supported file from `data/samples/`
4. Fill in the form:
   - Name: "User Analytics Data"
   - Description: "Sample customer data with PII and nested structures"
   - Enable AI descriptions (if you have an API key)
5. Click "Create Dictionary"
6. Explore the generated data dictionary!

**Supported file formats**: `.json`, `.jsonl`, `.ndjson`, `.xml`, `.db`, `.sqlite`, `.sqlite3`, `.gpkg`, `.proto`, `.desc`

### Option 3: PostgreSQL Advanced Setup

For production deployments requiring advanced database features, high concurrency, or multi-user access.

#### 1. Start PostgreSQL Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis
```

#### 2. Configure Backend for PostgreSQL

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
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

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

#### 3. Build and Deploy Frontend

```bash
cd frontend
npm install

# Build for production
npm run build
```

**Important**: Once built, FastAPI automatically serves the frontend from the `frontend/dist` directory at http://localhost:8000. There's no need to run a separate frontend server in production.

**How it works**:
- API routes are available at `/api/*`
- Static assets (JS, CSS, images) are served from `/assets/*`
- All other routes serve `index.html` for React Router to handle client-side routing

#### When to Use PostgreSQL vs SQLite

**Use SQLite if:**
- Single-user or small team (< 5 concurrent users)
- File size < 100GB
- Simple deployment requirements
- Embedded/portable application
- Development or testing

**Use PostgreSQL if:**
- Multiple concurrent users (> 5)
- Large datasets (> 100GB)
- Need advanced features (full-text search, JSON queries, replication)
- High availability requirements
- Compliance requirements (backup, auditing)

---

## Database Management Guide

The application provides comprehensive database management capabilities through both the API and frontend interface.

### Database Statistics

View real-time database metrics:

```bash
# Get database statistics
curl http://localhost:8000/api/v1/database/stats

# Response:
{
  "database_type": "sqlite",
  "database_size": 2048576,
  "database_size_mb": 2.0,
  "database_path": "/app/data/app.db",
  "table_counts": {
    "dictionaries": 15,
    "versions": 42,
    "fields": 1250,
    "annotations": 876
  },
  "total_records": 2183,
  "last_updated": "2025-11-12T14:30:00Z"
}
```

### Database Health Check

Monitor database connectivity and integrity:

```bash
# Check database health
curl http://localhost:8000/api/v1/database/health

# Response:
{
  "status": "healthy",
  "connection": true,
  "integrity": true,
  "checked_at": "2025-11-12T14:30:00Z"
}
```

### Database Backup

#### Manual Backup (SQLite)

```bash
# Copy the database file
cp data/app.db backups/app-$(date +%Y%m%d-%H%M%S).db

# Or use SQLite's backup command
sqlite3 data/app.db ".backup backups/app-backup.db"
```

#### API-Based Backup

```bash
# Download database backup via API
curl -o backup.db http://localhost:8000/api/v1/database/backup/download

# Response: Binary SQLite database file
```

#### Automated Backup Strategy

For production deployments, consider:

**Daily Backups:**
```bash
#!/bin/bash
# backup-daily.sh
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d-%H%M%S)

# SQLite
cp /app/data/app.db $BACKUP_DIR/app-$DATE.db

# PostgreSQL
pg_dump -U ddgen_user data_dictionary_db > $BACKUP_DIR/backup-$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-daily.sh
```

### Clear Database

WARNING: This operation is destructive and cannot be undone.

```bash
# Clear all data (requires confirmation)
curl -X POST "http://localhost:8000/api/v1/database/clear?confirm=DELETE_ALL_DATA"

# Response:
{
  "message": "Database cleared successfully",
  "tables_cleared": ["dictionaries", "versions", "fields", "annotations"],
  "records_deleted": 2183
}
```

### Database Maintenance

#### SQLite Maintenance

```bash
# Optimize database (reclaim space, rebuild indexes)
sqlite3 data/app.db "VACUUM;"
sqlite3 data/app.db "ANALYZE;"

# Check integrity
sqlite3 data/app.db "PRAGMA integrity_check;"
```

#### PostgreSQL Maintenance

```bash
# Inside PostgreSQL container
docker exec -it postgres psql -U ddgen_user -d data_dictionary_db

-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex all tables
REINDEX DATABASE data_dictionary_db;

-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Import/Export Workflows

### Exporting Data

#### Export Single Dictionary

```bash
# Via API
curl -o dictionary.xlsx \
  http://localhost:8000/api/v1/dictionaries/{dictionary_id}/export

# Via Frontend
# 1. Navigate to dictionary detail page
# 2. Click "Export" button
# 3. Choose format (Excel/CSV)
# 4. File downloads automatically
```

#### Batch Export All Dictionaries

```bash
# Create batch export script
cat > export_all.sh <<'EOF'
#!/bin/bash
API_BASE="http://localhost:8000/api/v1"
OUTPUT_DIR="exports/$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"

# Get all dictionary IDs
DICT_IDS=$(curl -s "$API_BASE/dictionaries" | jq -r '.items[].id')

# Export each dictionary
for ID in $DICT_IDS; do
  NAME=$(curl -s "$API_BASE/dictionaries/$ID" | jq -r '.name' | tr ' ' '_')
  echo "Exporting $NAME..."
  curl -o "$OUTPUT_DIR/${NAME}_${ID}.xlsx" \
    "$API_BASE/dictionaries/$ID/export"
done

echo "Exported $(ls -1 $OUTPUT_DIR | wc -l) dictionaries to $OUTPUT_DIR"
EOF

chmod +x export_all.sh
./export_all.sh
```

### Importing Data

#### Import from Excel/XLSX

The import feature allows you to restore exported dictionaries or migrate from other systems.

**XLSX File Format Requirements:**
- Must have been exported from this application
- Contains metadata sheet with dictionary information
- Contains fields sheet with full field definitions

```bash
# Import via API
curl -X POST \
  -F "file=@dictionary_export.xlsx" \
  -F "conflict_mode=skip" \
  http://localhost:8000/api/v1/dictionaries/import

# Conflict modes:
# - skip: Skip existing dictionaries (default)
# - overwrite: Replace existing dictionaries
# - fail: Fail if dictionary already exists

# Response:
{
  "success": true,
  "imported": 5,
  "skipped": 2,
  "failed": 0,
  "errors": []
}
```

#### Import via Frontend

1. Navigate to Database Management page
2. Click "Import Backup" button
3. Select XLSX file
4. Choose conflict resolution mode
5. Review preview
6. Confirm import

#### Batch Import Multiple Files

```bash
#!/bin/bash
# import_batch.sh
IMPORT_DIR="./exports"
API_BASE="http://localhost:8000/api/v1"

for FILE in "$IMPORT_DIR"/*.xlsx; do
  echo "Importing $(basename $FILE)..."
  curl -X POST \
    -F "file=@$FILE" \
    -F "conflict_mode=skip" \
    "$API_BASE/dictionaries/import"
done
```

### Full Database Export/Import

For complete database migration or backup restoration:

#### Export Full Database

```bash
# SQLite - Direct file copy
cp data/app.db full-backup-$(date +%Y%m%d).db

# PostgreSQL - Full dump
docker exec postgres pg_dump \
  -U ddgen_user \
  -Fc \
  data_dictionary_db > full-backup-$(date +%Y%m%d).dump
```

#### Import Full Database

```bash
# SQLite - Replace database file
cp full-backup-20251112.db data/app.db

# PostgreSQL - Restore from dump
docker exec -i postgres pg_restore \
  -U ddgen_user \
  -d data_dictionary_db \
  --clean \
  < full-backup-20251112.dump
```

---

## Environment Variables Reference

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | "Data Dictionary Generator" | Application name |
| `APP_VERSION` | "1.0.0" | Application version |
| `ENVIRONMENT` | "development" | Environment: development, staging, production |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | "INFO" | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | "0.0.0.0" | Server bind address |
| `PORT` | `8000` | Server port |
| `RELOAD` | `false` | Enable hot reload (development only) |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | "sqlite:///./data/app.db" | Database connection string |
| `DATABASE_TYPE` | "sqlite" | Database type: sqlite or postgresql |

#### SQLite-Specific Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SQLITE_TIMEOUT` | `30` | Lock timeout in seconds |
| `SQLITE_CHECK_SAME_THREAD` | `false` | Thread safety check |

#### PostgreSQL-Specific Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_POOL_SIZE` | `10` | Connection pool size |
| `DB_MAX_OVERFLOW` | `20` | Max overflow connections |
| `DB_ECHO` | `false` | Echo SQL queries (debug) |

### Redis Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | "redis://localhost:6380/0" | Redis connection URL |
| `REDIS_CACHE_TTL` | `3600` | Cache TTL in seconds |

### Security Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | (generated) | Secret key for signing (CHANGE IN PRODUCTION) |
| `API_KEY_ENABLED` | `false` | Enable API key authentication |
| `ALLOWED_ORIGINS` | "*" | CORS allowed origins (comma-separated) |

### OpenAI Integration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | "" | OpenAI API key for GPT-4 |
| `OPENAI_ENABLED` | `true` | Enable AI-powered descriptions |
| `OPENAI_MODEL` | "gpt-4" | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | `500` | Max tokens per description |
| `OPENAI_TEMPERATURE` | `0.7` | Model temperature (creativity) |

### File Processing

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_UPLOAD_SIZE` | `524288000` | Max file size in bytes (500MB) |
| `SAMPLE_SIZE` | `1000` | Number of records to sample |
| `NESTED_DEPTH_LIMIT` | `10` | Max nesting depth to process |

### Example Configuration Files

#### `.env.sqlite.example` (Default)

```bash
# Database Configuration
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=change-this-to-a-random-secret-in-production

# OpenAI (optional)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_ENABLED=true

# File Processing
MAX_UPLOAD_SIZE=524288000
SAMPLE_SIZE=1000
```

#### `.env.postgresql.example` (Advanced)

```bash
# Database Configuration
DATABASE_URL=postgresql://ddgen_user:ddgen_password@localhost:5432/data_dictionary_db
DATABASE_TYPE=postgresql
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Redis (optional)
REDIS_URL=redis://localhost:6380/0
REDIS_CACHE_TTL=3600

# Security
SECRET_KEY=change-this-to-a-random-secret-in-production
ALLOWED_ORIGINS=https://yourdomain.com

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_ENABLED=true

# File Processing
MAX_UPLOAD_SIZE=524288000
SAMPLE_SIZE=1000
```

---

## Migration from PostgreSQL to SQLite

If you have an existing PostgreSQL deployment and want to migrate to SQLite for simpler deployment:

### Option 1: Export/Import Method (Recommended)

This is the safest method that works across different schema versions.

#### Step 1: Export All Data

```bash
# While still running PostgreSQL
# Export all dictionaries to XLSX
cd backend
python -m scripts.export_all_dictionaries

# This creates: exports/migration-YYYYMMDD/
# - dictionary1.xlsx
# - dictionary2.xlsx
# - ...
```

#### Step 2: Switch to SQLite

```bash
# Update .env file
cat > .env <<EOF
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite
ENVIRONMENT=production
EOF

# Run migrations for SQLite
alembic upgrade head

# Restart application
# Docker: docker-compose restart app
# Local: restart uvicorn
```

#### Step 3: Import Data

```bash
# Import all XLSX files
for file in exports/migration-*/*.xlsx; do
  curl -X POST \
    -F "file=@$file" \
    -F "conflict_mode=overwrite" \
    http://localhost:8000/api/v1/dictionaries/import
done
```

#### Step 4: Verify Migration

```bash
# Check statistics
curl http://localhost:8000/api/v1/database/stats

# Verify record counts match your PostgreSQL database
```

### Option 2: Direct Database Migration (Advanced)

Use this method if you need to preserve exact timestamps and metadata.

#### Prerequisites

```bash
pip install pgcopy sqlite-utils
```

#### Step 1: Export PostgreSQL to CSV

```bash
# Export from PostgreSQL
docker exec postgres psql -U ddgen_user -d data_dictionary_db <<EOF
\copy dictionaries TO '/tmp/dictionaries.csv' CSV HEADER;
\copy versions TO '/tmp/versions.csv' CSV HEADER;
\copy fields TO '/tmp/fields.csv' CSV HEADER;
\copy annotations TO '/tmp/annotations.csv' CSV HEADER;
EOF

# Copy CSV files out of container
docker cp postgres:/tmp/dictionaries.csv ./
docker cp postgres:/tmp/versions.csv ./
docker cp postgres:/tmp/fields.csv ./
docker cp postgres:/tmp/annotations.csv ./
```

#### Step 2: Create SQLite Database

```bash
# Initialize new SQLite database
cd backend
export DATABASE_URL=sqlite:///./data/app.db
export DATABASE_TYPE=sqlite
alembic upgrade head
```

#### Step 3: Import CSV to SQLite

```bash
# Use sqlite3 import
sqlite3 data/app.db <<EOF
.mode csv
.import dictionaries.csv dictionaries
.import versions.csv versions
.import fields.csv fields
.import annotations.csv annotations
EOF
```

#### Step 4: Verify and Fix Data Types

```bash
# Run data type conversion script
python -m scripts.migrate_postgres_to_sqlite \
  --input-csvs . \
  --output data/app.db

# This script handles:
# - UUID to String conversion
# - Timestamp format conversion
# - JSONB to TEXT conversion
# - Array to JSON conversion
```

### Rollback Procedure

If migration fails or you need to revert:

```bash
# Step 1: Stop application
docker-compose down app

# Step 2: Restore PostgreSQL config
cat > .env <<EOF
DATABASE_URL=postgresql://ddgen_user:ddgen_password@localhost:5432/data_dictionary_db
DATABASE_TYPE=postgresql
EOF

# Step 3: Restart with PostgreSQL
docker-compose up -d postgres app

# Your original PostgreSQL data is unchanged
```

### Migration Checklist

- [ ] Backup PostgreSQL database before starting
- [ ] Export all dictionaries to XLSX format
- [ ] Verify all XLSX files open correctly
- [ ] Update `.env` to use SQLite
- [ ] Run `alembic upgrade head` for SQLite
- [ ] Import all XLSX files
- [ ] Verify record counts match
- [ ] Test critical workflows (upload, export, search)
- [ ] Update deployment scripts/docs
- [ ] Backup new SQLite database
- [ ] Decommission PostgreSQL (after validation period)

For detailed migration procedures and troubleshooting, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

---

## Project Structure

```
data-dictionary-gen/
├── backend/                    # FastAPI backend application
│   ├── src/
│   │   ├── api/               # API routes and endpoints
│   │   │   └── v1/            # API version 1
│   │   ├── core/              # Core configuration (config, logging, security)
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic schemas (DTOs)
│   │   ├── services/          # Business logic layer
│   │   ├── processors/        # Data processing (parsing, type detection, PII)
│   │   ├── repositories/      # Data access layer
│   │   ├── exporters/         # Export handlers (Excel, CSV)
│   │   └── main.py           # Application entry point
│   ├── tests/                 # Test suite (unit & integration)
│   ├── alembic/              # Database migrations
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── api/              # API client and service functions
│   │   ├── components/       # React components
│   │   │   ├── ui/           # shadcn/ui base components
│   │   │   └── layout/       # Layout components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Route pages
│   │   ├── types/            # TypeScript type definitions
│   │   └── lib/              # Utility functions
│   └── package.json          # Node.js dependencies
│
├── docs/                      # Design documentation
│   ├── CONOPS.md             # Concept of Operations
│   ├── REQUIREMENTS.md       # System Requirements
│   └── SOFTWARE_DESIGN.md    # Technical Architecture
│
├── docker-compose.yml         # Docker services configuration
├── sample-data.json          # Sample dataset for testing
├── QUICK_START.md            # 3-minute getting started guide
└── IMPLEMENTATION_STATUS.md  # Current implementation status (~70%)
```

---

## Documentation

### Quick Links
- **[Documentation Index](docs/README.md)** - Complete documentation navigation and overview
- **[Quick Start Guide](docs/guides/QUICK_START.md)** - Get running in 2 minutes

### Deployment
- **[Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md)** - Complete Docker guide (SQLite & PostgreSQL)
- **[Production Deployment](docs/deployment/PRODUCTION_DEPLOYMENT.md)** - Enterprise deployment guide

### Guides
- **[Quick Start](docs/guides/QUICK_START.md)** - Fastest way to get started
- **[Migration Guide](docs/guides/MIGRATION_GUIDE.md)** - Database migration procedures

### Technical Reference
- **[XML DTD/XSD Support](docs/reference/XML_DTD_XSD_SUPPORT.md)** - XML schema documentation
- **[Software Design](docs/reference/SOFTWARE_DESIGN.md)** - Detailed technical architecture
- **[Requirements](docs/reference/REQUIREMENTS.md)** - System requirements specification
- **[Concept of Operations](docs/reference/CONOPS.md)** - Operational overview

### Sample Data
- **[Sample XML Files](docs/samples/SAMPLE_XML_README.md)** - Test files and usage guide

### Component Documentation
- **[Backend README](backend/README.md)** - Backend setup and API documentation
- **[Frontend README](frontend/README.md)** - Frontend setup and development guide

---

## Architecture Highlights

### Clean Architecture Pattern

The backend follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│        API Layer (FastAPI)          │  ← HTTP endpoints, validation
├─────────────────────────────────────┤
│       Service Layer (Business)      │  ← Orchestration, workflows
├─────────────────────────────────────┤
│    Repository Layer (Data Access)   │  ← Database operations, ORM
├─────────────────────────────────────┤
│      Processor Layer (Analysis)     │  ← Parsing, type detection, PII
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│    Database Layer (PostgreSQL)      │  ← Persistence, JSONB storage
└─────────────────────────────────────┘
```

### Key Design Patterns

- **Repository Pattern**: Abstracts data access with generic CRUD operations
- **Dependency Injection**: Services and repositories injected via FastAPI dependencies
- **Service Orchestration**: Complex workflows coordinated in service layer
- **Streaming Processing**: Memory-efficient handling of large JSON files
- **Type-Safe Schemas**: Pydantic models ensure data validation throughout the stack

### Database Schema

Four core entities with relationships:

- **Dictionary**: Top-level container for a dataset
- **Version**: Snapshot of schema at a point in time
- **Field**: Individual data field with comprehensive metadata
- **Annotation**: User-provided or AI-generated field documentation

All entities support JSONB columns for flexible metadata storage.

---

## Current Limitations

### Features Intentionally Not Implemented (Phase 1 MVP)

The following features were mentioned in requirements but are **not yet implemented**:

#### Authentication & Authorization
- No user authentication system (placeholder only)
- No multi-user management
- No role-based access control (RBAC)
- `API_KEY_ENABLED=false` by default

#### Performance & Scalability
- No rate limiting (configured but disabled)
- No request throttling
- No distributed caching (Redis configured but not used)

#### Monitoring & Operations
- No production metrics/monitoring
- No alerting system
- No health dashboards
- Basic health check endpoint only

#### Notifications
- No email notifications
- No webhook integrations
- No real-time updates (WebSocket)

#### Background Processing
- Celery configured but not actively used
- All processing happens synchronously
- No job queues or task scheduling

### Known Technical Gaps

According to [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md), the project is approximately **70% complete** with the following gaps:

- Some API endpoints may be stubs
- Limited test coverage (target: 80%)
- No database migrations created yet (Alembic configured)
- No Dockerfile for backend (docker-compose has commented backend service)
- Security implementation is basic (suitable for development only)

**Recommendation**: This project is suitable for development, testing, and internal tools but requires additional hardening for production use.

---

## Roadmap

### Phase 1: MVP Foundation (Current - ~70% Complete)
- [x] Core data processing pipeline
- [x] Database models and relationships
- [x] Service layer orchestration
- [x] React UI with basic features
- [ ] Complete API endpoint implementation
- [ ] Comprehensive test suite (80% coverage)
- [ ] Database migrations
- [ ] Docker containerization

### Phase 2: Enhanced Features (Planned)
- [ ] Full authentication/authorization system
- [ ] Advanced search with full-text indexing
- [ ] Redis caching layer
- [ ] Rate limiting and quota management
- [ ] Background job processing with Celery
- [ ] Webhook integrations

### Phase 3: Production Readiness (Future)
- [ ] Monitoring and metrics (Prometheus/Grafana)
- [ ] Distributed tracing
- [ ] Email notifications
- [ ] Real-time updates (WebSocket)
- [ ] Multi-tenancy support
- [ ] Advanced data visualizations
- [ ] API versioning strategy

### Phase 4: Advanced Analytics (Future)
- [ ] Data profiling and anomaly detection
- [ ] Schema drift alerts
- [ ] Data lineage tracking
- [ ] Integration with data catalogs (e.g., DataHub, Amundsen)
- [ ] ML-based type inference improvements
- [ ] Custom semantic type definitions

---

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the setup instructions in [Quick Start](#quick-start)
4. Make your changes
5. Run tests and linting
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Coding Standards

**Backend (Python)**
- Follow PEP 8 style guide
- Use type hints throughout
- Write docstrings for all public functions/classes
- Run `ruff check --fix` and `ruff format` before committing
- Maintain test coverage above 80%

**Frontend (TypeScript)**
- Follow TypeScript strict mode
- Use functional components with hooks
- Follow shadcn/ui component patterns
- Use Tailwind utility classes (avoid custom CSS)
- Ensure `npm run build` succeeds

### Testing

```bash
# Backend tests
cd backend
pytest --cov=src --cov-report=html

# Frontend tests (when implemented)
cd frontend
npm test
```

### Areas Needing Help

- Complete API endpoint implementations
- Expand test coverage (currently minimal)
- Add database migrations
- Create Dockerfile for backend
- Implement authentication system
- Add search functionality
- Performance optimization
- Documentation improvements

---

## License

This project does not currently have a license specified. Please contact the repository owner for usage rights and licensing information.

---

## Acknowledgments

- **FastAPI** - For the excellent modern Python web framework
- **shadcn/ui** - For the beautiful, accessible component library
- **OpenAI** - For GPT-4 API enabling intelligent descriptions
- **SQLAlchemy** - For the robust ORM and database toolkit
- **TanStack Query** - For elegant server state management

---

## Support & Contact

- **Issues**: Please report bugs and feature requests via GitHub Issues
- **Documentation**: See the [docs/](docs/) directory for detailed specifications
- **API Docs**: Access interactive API documentation at http://localhost:8000/api/docs when running

---

**Built with care for data professionals who value comprehensive documentation**
