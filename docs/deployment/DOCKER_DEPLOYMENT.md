# Docker Deployment Guide

Complete guide for deploying the Data Dictionary Generator using Docker, including quick start, production deployment, and troubleshooting.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
  - [SQLite Mode (Recommended)](#sqlite-mode-recommended)
  - [PostgreSQL Mode](#postgresql-mode)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Common Operations](#common-operations)
- [Production Deployment](#production-deployment)
- [Security Hardening](#security-hardening)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Backup and Restore](#backup-and-restore)
- [Troubleshooting](#troubleshooting)
- [Build Process Details](#build-process-details)
- [Deployment Review Notes](#deployment-review-notes)

---

## Overview

The Data Dictionary Generator supports two deployment modes:

1. **SQLite Mode** (Recommended): Lightweight, zero-configuration, perfect for most users
2. **PostgreSQL Mode** (Advanced): Production-grade database for concurrent access and scaling

Both modes use a single Docker container that includes the React frontend and FastAPI backend.

### System Requirements

#### Minimum Requirements (SQLite)
- **CPU**: 2 cores
- **RAM**: 2GB
- **Disk**: 10GB SSD
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

#### Recommended Requirements (PostgreSQL)
- **CPU**: 4+ cores
- **RAM**: 8GB+ (4GB app + 4GB database)
- **Disk**: 50GB+ SSD with IOPS 3000+
- **Docker**: 24.0+
- **Docker Compose**: 2.20+

---

## Quick Start

### SQLite Mode (Recommended)

The fastest way to get started:

```bash
# Build and run in one command
./docker-run-sqlite.sh
```

Or manually:

```bash
# Build the Docker image
./docker-build.sh

# Start the application
docker-compose up -d app

# Access at http://localhost:8000
```

**Access Points:**
- **Frontend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

#### SQLite Mode Features

- **Zero Configuration**: No database setup required
- **Lightweight**: Single container, minimal resources
- **Persistent Storage**: Database stored in `./data/app.db`
- **Perfect For**: Development, testing, small teams, single-user deployments

### PostgreSQL Mode

For production deployments requiring concurrent access:

```bash
# Build and run with PostgreSQL
./docker-run-postgres.sh
```

Or manually:

```bash
# Build the Docker image
./docker-build.sh

# Start with PostgreSQL
docker-compose --profile postgres up -d

# Access at http://localhost:8001
```

**Access Points:**
- **Frontend**: http://localhost:8001
- **API Documentation**: http://localhost:8001/api/docs
- **Health Check**: http://localhost:8001/health
- **pgAdmin** (optional): http://localhost:5050

#### PostgreSQL Mode Features

- **Production Ready**: ACID compliance, concurrent access
- **Scalable**: Connection pooling, optimized for performance
- **Enterprise**: Full PostgreSQL features and tooling
- **Perfect For**: Production deployments, multi-user environments, large datasets

---

## Architecture

### Multi-Stage Docker Build

The Dockerfile uses a multi-stage build for optimal size and security:

**Stage 1: Frontend Builder**
- Base: `node:20-alpine`
- Builds the React frontend with Vite
- Output: Optimized production bundle

**Stage 2: Production Runtime**
- Base: `python:3.11-slim`
- Includes FastAPI backend
- Serves frontend via StaticFiles
- Runs database migrations on startup

```
┌─────────────────────────────────────┐
│  Stage 1: Frontend Builder          │
│  - Base: node:20-alpine             │
│  - npm ci (clean install)           │
│  - npm run build                    │
│  - Output: /app/frontend/dist       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Stage 2: Production Runtime        │
│  - Base: python:3.11-slim           │
│  - Install: gcc, postgresql-client  │
│  - Copy: backend code               │
│  - Copy: frontend/dist from Stage 1 │
│  - Setup: migrations & startup      │
└─────────────────────────────────────┘
              ↓
         [Final Image]
    ~300-400MB (optimized)
```

### Container Startup Flow

```
[Container Start]
      ↓
[docker-entrypoint.sh]
      ↓
[Check Database Type]
      ↓
[Wait for PostgreSQL] (if applicable)
      ↓
[Run Alembic Migrations]
      ↓
[Start Uvicorn Server]
      ↓
[Serve Frontend + API]
      ↓
[Health Check Active]
```

### Directory Structure in Container

```
/app/
├── src/                    # Backend Python code
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── processors/        # File processors
│   └── services/          # Business logic
├── alembic/               # Database migrations
│   ├── versions/          # Migration files
│   └── env.py            # Alembic config
├── frontend/dist/         # Built React app (from Stage 1)
│   ├── index.html
│   └── assets/
├── data/                  # SQLite database (volume)
│   └── app.db
├── docker-entrypoint.sh   # Startup script
└── requirements.txt       # Python dependencies
```

---

## Configuration

### Environment Variables

Copy and customize the appropriate template:

**For SQLite:**
```bash
cp .env.sqlite.example .env
```

**For PostgreSQL:**
```bash
cp .env.postgresql.example .env
```

### Key Configuration Options

#### Required Settings

```bash
# Database
DATABASE_URL=sqlite:///./data/app.db  # or postgresql://...
DATABASE_TYPE=sqlite                   # or postgresql

# OpenAI (for AI-powered descriptions)
OPENAI_API_KEY=your-key-here
OPENAI_ENABLED=true
```

#### Optional Settings

```bash
# Security
SECRET_KEY=change-in-production
API_KEY_ENABLED=false

# File Processing
MAX_FILE_SIZE_MB=500
MAX_RECORDS_TO_ANALYZE=10000

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

See `.env.sqlite.example` or `.env.postgresql.example` for complete configuration options.

---

## Common Operations

### Building

```bash
# Build Docker image
./docker-build.sh

# Or manually
docker build -f backend/Dockerfile -t data-dictionary-gen:latest .
```

### Starting

```bash
# SQLite mode
docker-compose up -d app

# PostgreSQL mode
docker-compose --profile postgres up -d

# All services (including pgAdmin, Redis)
docker-compose --profile postgres --profile tools up -d
```

### Stopping

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific profile
docker-compose --profile postgres down
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f app-postgres
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 app
```

### Database Access

**SQLite:**
```bash
# Direct access to SQLite database
sqlite3 ./data/app.db

# Or via Docker
docker exec -it ddgen_app sqlite3 /app/data/app.db
```

**PostgreSQL:**
```bash
# psql shell
docker exec -it ddgen_postgres psql -U ddgen_user -d data_dictionary_db

# Or use pgAdmin at http://localhost:5050
```

### Migrations

Migrations run automatically on container startup. To run manually:

```bash
# SQLite
docker exec -it ddgen_app alembic upgrade head

# PostgreSQL
docker exec -it ddgen_app_postgres alembic upgrade head
```

### Backup and Restore

**SQLite:**
```bash
# Backup
cp ./data/app.db ./backups/app-$(date +%Y%m%d).db

# Restore
cp ./backups/app-20251112.db ./data/app.db
docker-compose restart app
```

**PostgreSQL:**
```bash
# Backup
docker exec ddgen_postgres pg_dump -U ddgen_user data_dictionary_db > backup.sql

# Restore
docker exec -i ddgen_postgres psql -U ddgen_user data_dictionary_db < backup.sql
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] **Server provisioned** with required specifications
- [ ] **Docker installed** and configured
- [ ] **Docker Compose installed**
- [ ] **Firewall configured** - Only required ports open (80, 443, 22)
- [ ] **SSL/TLS certificates** obtained (Let's Encrypt or commercial CA)
- [ ] **Domain name** configured and DNS propagated
- [ ] **Environment variables** configured in `.env`
- [ ] **Database passwords** randomized and secured
- [ ] **Backup storage** provisioned
- [ ] **Monitoring setup** configured

### Security Checklist

- [ ] Change `SECRET_KEY` to a random value
- [ ] Set `DEBUG=false`
- [ ] Use strong database passwords
- [ ] Enable `API_KEY_ENABLED` if needed
- [ ] Configure `ALLOWED_ORIGINS` for CORS
- [ ] Use HTTPS (reverse proxy like Nginx)
- [ ] Restrict database ports (don't expose publicly)
- [ ] Regular backups configured
- [ ] Set up monitoring and logging

### Performance Tuning

**PostgreSQL Connection Pool:**
```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

**File Processing:**
```bash
MAX_FILE_SIZE_MB=500
MAX_RECORDS_TO_ANALYZE=10000
```

**Caching (with Redis):**
```bash
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600
```

### Resource Limits

Add to docker-compose.yml:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name datadictgen.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name datadictgen.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/datadictgen.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/datadictgen.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for large file uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Increase client body size for file uploads (500MB)
    client_max_body_size 500M;
}
```

---

## Security Hardening

### 1. Environment Variables Protection

```bash
# Secure .env files
chmod 600 .env

# Never commit secrets to git
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.*.example" >> .gitignore
```

### 2. Database Security

```bash
# For PostgreSQL - restrict network access
# Update docker-compose.yml to bind only to localhost:
ports:
  - "127.0.0.1:5432:5432"  # Only accessible from host

# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -hex 32)
```

### 3. Application Security

```bash
# Update .env with security settings:

# Enable API key authentication (if needed)
API_KEY_ENABLED=true

# Restrict CORS origins
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Generate strong secret key
SECRET_KEY=$(openssl rand -hex 32)

# Disable debug mode
DEBUG=false

# Set appropriate log level
LOG_LEVEL=WARNING
```

### 4. Network Security

```bash
# Configure firewall (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Fail2ban for SSH protection
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Monitoring and Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app_name": "Data Dictionary Generator",
  "version": "1.0.0",
  "environment": "production"
}
```

### Docker Health Check

Built-in health check runs every 30 seconds:

```bash
# View health status
docker ps
# Look for (healthy) status

# Inspect health check
docker inspect ddgen_app | grep -A 10 Health
```

### Logs and Metrics

```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres

# Resource usage
docker stats ddgen_app
```

---

## Backup and Restore

### Backup Strategy Matrix

| Type | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| **Full** | Daily | 30 days | Automated script |
| **Incremental** | Hourly | 7 days | WAL archiving (PostgreSQL) |
| **Point-in-time** | On-demand | 90 days | Manual trigger |
| **Disaster Recovery** | Weekly | 1 year | Off-site storage |

### Automated Backup Script (SQLite)

```bash
#!/bin/bash
set -e

# Configuration
BACKUP_DIR=/backups/data-dictionary
APP_DIR=/opt/data-dictionary-gen
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Backup database
echo "Backing up database..."
cp $APP_DIR/data/app.db $BACKUP_DIR/app-$TIMESTAMP.db

# Compress old backups
find $BACKUP_DIR -name "*.db" -mtime +1 ! -name "*$(date +%Y%m%d)*" -exec gzip {} \;

# Remove old backups
find $BACKUP_DIR -name "*.db.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup complete: $BACKUP_DIR/app-$TIMESTAMP.db"
```

### Automated Backup Script (PostgreSQL)

```bash
#!/bin/bash
set -e

# Configuration
BACKUP_DIR=/backups/postgresql
CONTAINER_NAME=ddgen-postgres
POSTGRES_USER=ddgen_user
POSTGRES_DB=data_dictionary_db
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Timestamp
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Backup database
echo "Backing up PostgreSQL database..."
docker exec $CONTAINER_NAME pg_dump \
  -U $POSTGRES_USER \
  -Fc \
  $POSTGRES_DB > $BACKUP_DIR/backup-$TIMESTAMP.dump

# Verify backup
if [ -f $BACKUP_DIR/backup-$TIMESTAMP.dump ]; then
  SIZE=$(stat -c%s $BACKUP_DIR/backup-$TIMESTAMP.dump)
  echo "Backup created: $BACKUP_DIR/backup-$TIMESTAMP.dump (${SIZE} bytes)"
else
  echo "ERROR: Backup failed!"
  exit 1
fi

# Remove old backups
find $BACKUP_DIR -name "*.dump" -mtime +$RETENTION_DAYS -delete

echo "Backup complete!"
```

---

## Troubleshooting

### Common Issues

**1. Container won't start**
```bash
# Check logs
docker-compose logs app

# Verify database connection
docker exec -it ddgen_app env | grep DATABASE_URL
```

**2. Frontend not loading**
```bash
# Verify frontend was built
docker exec -it ddgen_app ls -la /app/frontend/dist

# Rebuild if needed
./docker-build.sh
```

**3. Database migration errors**
```bash
# Run migrations manually
docker exec -it ddgen_app alembic upgrade head

# Check migration status
docker exec -it ddgen_app alembic current
```

**4. Permission issues**
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data
chmod -R 755 ./data
```

**5. Port already in use**
```bash
# Check what's using the port
lsof -i :8000

# Or use different port
docker-compose run -p 8080:8000 app
```

### Debug Mode

Enable debug logging:

```bash
# Temporary debug mode
docker-compose run -e DEBUG=true -e LOG_LEVEL=DEBUG app

# Or update .env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Reset Everything

```bash
# Stop all containers
docker-compose down -v

# Remove database
rm -rf ./data

# Rebuild from scratch
./docker-build.sh
docker-compose up -d app
```

---

## Build Process Details

### Three-Stage Build Process

1. **Frontend Build**
   - Navigate to frontend directory
   - Install dependencies (if needed)
   - Build production bundle with Vite

2. **Docker Image Build**
   - Multi-stage Dockerfile
   - Stage 1: Frontend builder (Node)
   - Stage 2: Backend runtime (Python)
   - Optimized layer caching

3. **Image Verification**
   - Check image was created
   - Display image details
   - Show usage instructions

### Build Optimizations

**Current optimizations:**
- Multi-stage build (reduces size by ~60%)
- Alpine base for frontend (minimal size)
- Slim Python base (smaller than full)
- .dockerignore (excludes unnecessary files)
- No-cache pip install (reduces layers)

**Result**: ~300-400MB final image

---

## Deployment Review Notes

### Critical Issues Identified

1. **Health Check Dependency**: Use `curl` instead of `requests` module
2. **Network Configuration**: Add network to SQLite service for consistency
3. **Credential Management**: Use environment variables instead of hardcoded values
4. **Non-root User**: Run containers as non-root for security
5. **Migration Error Handling**: Improve rollback strategy

### Recommended Improvements

1. **Startup Probes**: Add for Kubernetes compatibility
2. **Resource Limits**: Configure CPU and memory limits
3. **Graceful Shutdown**: Implement signal handling
4. **Log Aggregation**: Set up centralized logging
5. **Monitoring Integration**: Add Prometheus metrics

### Deployment Mode Recommendations

**For Most Users**: SQLite mode (default)
- Zero configuration
- Excellent performance for single instance
- Simple backup (copy file)
- No additional services required

**For Production/Scale**: PostgreSQL mode
- Concurrent access support
- Better for multi-instance deployments
- Advanced features (replication, etc.)
- Industry standard for enterprise

---

## Support and Resources

- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health
- **Frontend**: http://localhost:8000

## Related Documentation

- [Quick Start Guide](../guides/QUICK_START.md) - Get started in 2 minutes
- [Production Deployment](./PRODUCTION_DEPLOYMENT.md) - Enterprise deployment guide
- [Migration Guide](../guides/MIGRATION_GUIDE.md) - Database migration procedures
- [Main README](../../README.md) - Project overview

---

**Last Updated**: 2025-11-12
**Deployment Modes**: SQLite, PostgreSQL
**Docker Version**: 24.0+
**Compose Version**: 2.20+
