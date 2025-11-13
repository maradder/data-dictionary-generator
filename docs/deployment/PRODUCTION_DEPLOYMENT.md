# Production Deployment Guide

This guide provides comprehensive instructions for deploying the Data Dictionary Generator in production environments, including security hardening, performance optimization, monitoring setup, and operational best practices.

## Table of Contents

- [Overview](#overview)
- [Deployment Architectures](#deployment-architectures)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [SQLite Deployment](#sqlite-deployment)
- [PostgreSQL Deployment](#postgresql-deployment)
- [Security Hardening](#security-hardening)
- [Performance Optimization](#performance-optimization)
- [Backup Strategies](#backup-strategies)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling Considerations](#scaling-considerations)
- [Maintenance Procedures](#maintenance-procedures)
- [Disaster Recovery](#disaster-recovery)
- [Troubleshooting](#troubleshooting)

---

## Overview

### Deployment Options

The Data Dictionary Generator supports multiple deployment configurations:

1. **Single-Container SQLite** - Simplest deployment for small teams (< 5 users)
2. **Multi-Container PostgreSQL** - Production deployment for larger teams
3. **Kubernetes** - Highly available, scalable deployment
4. **Serverless** - Cost-effective for sporadic usage

### System Requirements

#### Minimum Requirements (SQLite)

- **CPU**: 2 cores
- **RAM**: 2GB
- **Disk**: 10GB SSD
- **OS**: Linux (Ubuntu 20.04+), macOS, Windows Server
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

#### Recommended Requirements (PostgreSQL)

- **CPU**: 4+ cores
- **RAM**: 8GB+ (4GB app + 4GB database)
- **Disk**: 50GB+ SSD with IOPS 3000+
- **OS**: Linux (Ubuntu 22.04 LTS recommended)
- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **Network**: 100Mbps+ bandwidth

#### High-Availability Requirements

- **CPU**: 8+ cores per node
- **RAM**: 16GB+ per node
- **Disk**: 100GB+ SSD with IOPS 10000+
- **Network**: 1Gbps+ with low latency
- **Load Balancer**: nginx, HAProxy, or cloud LB
- **Container Orchestration**: Kubernetes 1.28+

---

## Deployment Architectures

### Architecture 1: Single-Container SQLite

**Use Case**: Small teams, development, testing, embedded deployments

```
┌─────────────────────────────────────┐
│         Docker Host                 │
│                                     │
│  ┌───────────────────────────────┐ │
│  │   Application Container       │ │
│  │                               │ │
│  │  ┌──────────┐  ┌───────────┐ │ │
│  │  │  FastAPI │  │   React   │ │ │
│  │  │  Backend │  │  Frontend │ │ │
│  │  └────┬─────┘  └───────────┘ │ │
│  │       │                       │ │
│  │       ▼                       │ │
│  │  ┌──────────┐                │ │
│  │  │  SQLite  │                │ │
│  │  │   DB     │◄────Volume     │ │
│  │  └──────────┘                │ │
│  └───────────────────────────────┘ │
│                                     │
│  Port 8000                          │
└─────────────────────────────────────┘
```

**Pros**: Simple, portable, low resource usage, easy backup
**Cons**: Limited concurrency, single point of failure

### Architecture 2: Multi-Container PostgreSQL

**Use Case**: Production deployments, multiple concurrent users

```
┌────────────────────────────────────────────────┐
│              Docker Host                       │
│                                                │
│  ┌──────────────────┐    ┌─────────────────┐ │
│  │   App Container  │    │  PostgreSQL     │ │
│  │                  │    │   Container     │ │
│  │  ┌────────────┐  │    │                 │ │
│  │  │  FastAPI   │  │    │  ┌───────────┐ │ │
│  │  │  + React   │──┼────┼─►│ PostgreSQL│ │ │
│  │  └────────────┘  │    │  └─────┬─────┘ │ │
│  │                  │    │        │       │ │
│  └──────────────────┘    │        ▼       │ │
│                          │   ┌─────────┐  │ │
│  ┌──────────────────┐    │   │  Volume │  │ │
│  │  Redis Container │    │   └─────────┘  │ │
│  │   (Optional)     │    │                 │ │
│  └──────────────────┘    └─────────────────┘ │
│                                                │
│  Port 8000                                     │
└────────────────────────────────────────────────┘
```

**Pros**: Better concurrency, reliable, supports replication
**Cons**: More complex, higher resource usage

### Architecture 3: Kubernetes High-Availability

**Use Case**: Enterprise deployments, high availability requirements

```
┌──────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                       │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Ingress Controller                     │  │
│  │                 (nginx/traefik)                     │  │
│  └────────────┬───────────────────────────────────────┘  │
│               │                                           │
│               ▼                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Application Service (LoadBalancer)         │  │
│  └────────────┬───────────────────────────────────────┘  │
│               │                                           │
│         ┌─────┴─────┬──────────┬───────────┐            │
│         ▼           ▼          ▼           ▼            │
│    ┌──────┐    ┌──────┐   ┌──────┐    ┌──────┐        │
│    │ Pod 1│    │ Pod 2│   │ Pod 3│    │ Pod N│        │
│    │      │    │      │   │      │    │      │        │
│    └───┬──┘    └───┬──┘   └───┬──┘    └───┬──┘        │
│        │           │          │            │            │
│        └───────────┴──────────┴────────────┘            │
│                     │                                    │
│                     ▼                                    │
│        ┌────────────────────────────┐                   │
│        │   PostgreSQL StatefulSet   │                   │
│        │                            │                   │
│        │  ┌──────┐  ┌──────┐       │                   │
│        │  │Master│  │Replica│       │                   │
│        │  └───┬──┘  └──────┘       │                   │
│        │      │                     │                   │
│        │      ▼                     │                   │
│        │  ┌──────────┐              │                   │
│        │  │Persistent│              │                   │
│        │  │  Volume  │              │                   │
│        │  └──────────┘              │                   │
│        └────────────────────────────┘                   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Pros**: High availability, auto-scaling, rolling updates
**Cons**: Complex setup, higher cost, requires K8s expertise

---

## Pre-Deployment Checklist

### Infrastructure Preparation

- [ ] **Server provisioned** with required specifications
- [ ] **Docker installed** and configured
- [ ] **Docker Compose installed** (if using)
- [ ] **Firewall configured** - Only required ports open
- [ ] **SSL/TLS certificates** obtained (Let's Encrypt, commercial CA)
- [ ] **Domain name** configured and DNS propagated
- [ ] **Monitoring setup** (Prometheus, Grafana, CloudWatch, etc.)
- [ ] **Backup storage** provisioned (S3, NFS, local disk)
- [ ] **Log aggregation** configured (ELK, Loki, CloudWatch Logs)

### Security Preparation

- [ ] **Security audit** completed
- [ ] **Vulnerability scanning** performed
- [ ] **Secret management** configured (Vault, AWS Secrets Manager)
- [ ] **API keys generated** and secured
- [ ] **Database passwords** randomized and secured
- [ ] **Network policies** defined
- [ ] **Access controls** configured (IAM, RBAC)
- [ ] **Compliance requirements** verified (GDPR, HIPAA, SOC2)

### Application Configuration

- [ ] **Environment variables** configured
- [ ] **Database type** selected (SQLite or PostgreSQL)
- [ ] **OpenAI API key** configured (if using AI features)
- [ ] **CORS origins** configured
- [ ] **Upload limits** configured
- [ ] **Rate limiting** configured
- [ ] **Logging level** set appropriately
- [ ] **Debug mode** disabled

### Testing Preparation

- [ ] **Staging environment** deployed
- [ ] **Smoke tests** passed
- [ ] **Load testing** completed
- [ ] **Security testing** completed
- [ ] **Backup/restore** tested
- [ ] **Failover** tested (if HA)
- [ ] **Rollback procedure** tested

---

## SQLite Deployment

### Quick Start (Single Container)

Perfect for small teams, development, or testing environments.

#### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### Step 2: Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd data-dictionary-gen

# Create directories
mkdir -p data backups logs

# Create production .env file
cat > .env <<EOF
# Database Configuration
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite
SQLITE_TIMEOUT=30
SQLITE_CHECK_SAME_THREAD=false

# Application Settings
APP_NAME=Data Dictionary Generator
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security Settings
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=https://yourdomain.com
API_KEY_ENABLED=false

# OpenAI Integration (optional)
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_ENABLED=true
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.7

# File Processing
MAX_UPLOAD_SIZE=524288000
SAMPLE_SIZE=1000
NESTED_DEPTH_LIMIT=10
EOF

# Secure .env file
chmod 600 .env
```

#### Step 3: Build and Deploy

```bash
# Build the container
docker-compose build app

# Start the application
docker-compose up -d app

# Verify deployment
docker-compose ps
docker-compose logs app

# Check health
curl http://localhost:8000/health
```

#### Step 4: Configure Reverse Proxy (nginx)

```bash
# Install nginx
sudo apt install nginx -y

# Create nginx configuration
sudo tee /etc/nginx/sites-available/data-dictionary <<EOF
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy Configuration
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for large file uploads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Increase client body size for file uploads (500MB)
    client_max_body_size 500M;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/data-dictionary /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 5: Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

#### Step 6: Configure Automated Backups

```bash
# Create backup script
sudo tee /usr/local/bin/backup-data-dictionary.sh <<'EOF'
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

# Backup configuration
echo "Backing up configuration..."
cp $APP_DIR/.env $BACKUP_DIR/.env-$TIMESTAMP

# Compress old backups
echo "Compressing old backups..."
find $BACKUP_DIR -name "*.db" -mtime +1 ! -name "*$(date +%Y%m%d)*" -exec gzip {} \;

# Remove old backups
echo "Removing old backups..."
find $BACKUP_DIR -name "*.db.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name ".env-*" -mtime +$RETENTION_DAYS -delete

# Upload to S3 (optional)
if command -v aws &> /dev/null; then
  echo "Uploading to S3..."
  aws s3 cp $BACKUP_DIR/app-$TIMESTAMP.db s3://your-backup-bucket/data-dictionary/
fi

echo "Backup complete: $BACKUP_DIR/app-$TIMESTAMP.db"
EOF

# Make executable
sudo chmod +x /usr/local/bin/backup-data-dictionary.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-data-dictionary.sh >> /var/log/backup-data-dictionary.log 2>&1") | crontab -
```

#### Step 7: Configure Log Rotation

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/data-dictionary <<EOF
/opt/data-dictionary-gen/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    copytruncate
    su root root
}
EOF
```

#### Step 8: Setup Monitoring

```bash
# Create health check script
sudo tee /usr/local/bin/check-data-dictionary-health.sh <<'EOF'
#!/bin/bash

HEALTH_URL="http://localhost:8000/health"
ALERT_EMAIL="admin@yourdomain.com"

# Check health endpoint
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ "$RESPONSE" != "200" ]; then
  echo "Data Dictionary health check failed: HTTP $RESPONSE" | mail -s "ALERT: Data Dictionary Down" $ALERT_EMAIL
  exit 1
fi

exit 0
EOF

sudo chmod +x /usr/local/bin/check-data-dictionary-health.sh

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/check-data-dictionary-health.sh") | crontab -
```

---

## PostgreSQL Deployment

### Production Setup (Multi-Container)

For production environments with multiple concurrent users.

#### Step 1: Prepare Infrastructure

```bash
# Same as SQLite Step 1
# Ensure adequate resources (4GB+ RAM)
```

#### Step 2: Configure Environment

```bash
# Create production .env file
cat > .env <<EOF
# Database Configuration
DATABASE_URL=postgresql://ddgen_user:$(openssl rand -hex 16)@postgres:5432/data_dictionary_db
DATABASE_TYPE=postgresql
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_ECHO=false

# Application Settings
APP_NAME=Data Dictionary Generator
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Security Settings
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_ORIGINS=https://yourdomain.com
API_KEY_ENABLED=false

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# OpenAI Integration
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_ENABLED=true

# File Processing
MAX_UPLOAD_SIZE=524288000
SAMPLE_SIZE=1000
EOF

chmod 600 .env
```

#### Step 3: Configure PostgreSQL

```bash
# Create PostgreSQL environment file
cat > .env.postgres <<EOF
POSTGRES_USER=ddgen_user
POSTGRES_PASSWORD=$(grep DATABASE_URL .env | cut -d: -f3 | cut -d@ -f1)
POSTGRES_DB=data_dictionary_db
EOF

chmod 600 .env.postgres
```

#### Step 4: Update docker-compose.yml for Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: ddgen-postgres
    env_file:
      - .env.postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres-backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ddgen_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - ddgen-network

  redis:
    image: redis:7-alpine
    container_name: ddgen-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - ddgen-network

  app:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: ddgen-app
    env_file:
      - .env
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - ddgen-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  ddgen-network:
    driver: bridge
```

#### Step 5: Deploy

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify all services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Verify health
curl http://localhost:8000/health
```

#### Step 6: Configure PostgreSQL Backups

```bash
# Create PostgreSQL backup script
sudo tee /usr/local/bin/backup-postgresql.sh <<'EOF'
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
  SIZE=$(stat -f%z $BACKUP_DIR/backup-$TIMESTAMP.dump 2>/dev/null || stat -c%s $BACKUP_DIR/backup-$TIMESTAMP.dump)
  echo "Backup created: $BACKUP_DIR/backup-$TIMESTAMP.dump (${SIZE} bytes)"
else
  echo "ERROR: Backup failed!"
  exit 1
fi

# Compress old backups
find $BACKUP_DIR -name "*.dump" -mtime +1 ! -name "*$(date +%Y%m%d)*" -exec gzip {} \;

# Remove old backups
find $BACKUP_DIR -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

# Upload to S3 (optional)
if command -v aws &> /dev/null; then
  aws s3 cp $BACKUP_DIR/backup-$TIMESTAMP.dump s3://your-backup-bucket/postgresql/
fi

echo "Backup complete!"
EOF

sudo chmod +x /usr/local/bin/backup-postgresql.sh

# Schedule backups
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-postgresql.sh >> /var/log/backup-postgresql.log 2>&1") | crontab -
```

---

## Security Hardening

### 1. Environment Variables Protection

```bash
# Secure .env files
chmod 600 .env .env.postgres

# Never commit secrets to git
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.*.example" >> .gitignore
```

### 2. Database Security

```bash
# For PostgreSQL - restrict network access
# Update docker-compose.prod.yml to bind only to localhost:
ports:
  - "127.0.0.1:5432:5432"  # Only accessible from host

# Use strong passwords
POSTGRES_PASSWORD=$(openssl rand -hex 32)

# Enable SSL for PostgreSQL connections (production)
# Add to postgresql.conf:
# ssl = on
# ssl_cert_file = '/etc/ssl/certs/server.crt'
# ssl_key_file = '/etc/ssl/private/server.key'
```

### 3. Application Security

```bash
# Update .env with security settings:

# Enable API key authentication
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

### 5. Container Security

```bash
# Run containers as non-root user
# Update Dockerfile:
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Use security scanning
docker scan data-dictionary-gen:latest

# Limit container resources
# Add to docker-compose.prod.yml:
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 6. Secrets Management

For production, use a secrets management service:

```bash
# Example: Using AWS Secrets Manager

# Store secret
aws secretsmanager create-secret \
  --name data-dictionary/production/database-url \
  --secret-string "postgresql://user:pass@host:5432/db"

# Retrieve secret in startup script
export DATABASE_URL=$(aws secretsmanager get-secret-value \
  --secret-id data-dictionary/production/database-url \
  --query SecretString --output text)
```

### 7. Security Headers

Already configured in nginx (see SQLite Step 4), but verify:

```bash
# Test security headers
curl -I https://yourdomain.com | grep -i "strict-transport-security\|x-frame-options\|x-content-type-options\|x-xss-protection"
```

---

## Performance Optimization

### 1. Database Optimization

#### SQLite Optimization

```bash
# Add to .env:
SQLITE_TIMEOUT=60
SQLITE_CHECK_SAME_THREAD=false

# Periodic optimization (add to cron):
sqlite3 /app/data/app.db "VACUUM;"
sqlite3 /app/data/app.db "ANALYZE;"
```

#### PostgreSQL Optimization

```bash
# Update PostgreSQL configuration
# Add to docker-compose.prod.yml postgresql command:
command: >
  postgres
  -c shared_buffers=256MB
  -c effective_cache_size=1GB
  -c maintenance_work_mem=128MB
  -c checkpoint_completion_target=0.9
  -c wal_buffers=16MB
  -c default_statistics_target=100
  -c random_page_cost=1.1
  -c effective_io_concurrency=200
  -c work_mem=8MB
  -c min_wal_size=1GB
  -c max_wal_size=4GB

# Periodic maintenance (add to cron):
docker exec ddgen-postgres psql -U ddgen_user -d data_dictionary_db -c "VACUUM ANALYZE;"
```

### 2. Connection Pooling

Already configured in `.env`:

```bash
# For PostgreSQL
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### 3. Caching with Redis

```bash
# Enable Redis caching in .env:
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# Monitor Redis usage:
docker exec ddgen-redis redis-cli INFO stats
```

### 4. Application Performance

```bash
# Increase worker processes (update docker-compose):
command: gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use uvicorn workers:
command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. File Upload Optimization

```bash
# Update nginx configuration:
client_max_body_size 500M;
client_body_timeout 300;
client_body_buffer_size 128k;

# Enable compression:
gzip on;
gzip_types application/json application/javascript text/css text/plain;
gzip_min_length 1000;
```

---

## Backup Strategies

### Backup Strategy Matrix

| Type | Frequency | Retention | Method |
|------|-----------|-----------|--------|
| **Full** | Daily | 30 days | Automated script |
| **Incremental** | Hourly | 7 days | WAL archiving (PostgreSQL) |
| **Point-in-time** | On-demand | 90 days | Manual trigger |
| **Disaster Recovery** | Weekly | 1 year | Off-site storage |

### 3-2-1 Backup Rule

Implement the 3-2-1 backup strategy:
- **3** copies of data (production + 2 backups)
- **2** different storage media (local disk + cloud)
- **1** off-site backup (S3, different region)

### Implementation

```bash
# Comprehensive backup script
sudo tee /usr/local/bin/backup-comprehensive.sh <<'EOF'
#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOCAL_BACKUP_DIR=/backups/local
S3_BUCKET=s3://your-backup-bucket/data-dictionary

# 1. Database backup
if [ "$DATABASE_TYPE" = "sqlite" ]; then
  cp /app/data/app.db $LOCAL_BACKUP_DIR/db-$TIMESTAMP.db
else
  docker exec ddgen-postgres pg_dump -U ddgen_user -Fc data_dictionary_db > $LOCAL_BACKUP_DIR/db-$TIMESTAMP.dump
fi

# 2. Configuration backup
tar czf $LOCAL_BACKUP_DIR/config-$TIMESTAMP.tar.gz .env docker-compose*.yml

# 3. Upload to S3
aws s3 sync $LOCAL_BACKUP_DIR $S3_BUCKET/backups/ --exclude "*" --include "*$TIMESTAMP*"

# 4. Verify backups
aws s3 ls $S3_BUCKET/backups/ | grep $TIMESTAMP

echo "Backup complete: $TIMESTAMP"
EOF
```

---

## Monitoring and Logging

### 1. Application Logging

```bash
# Configure structured logging
# Update .env:
LOG_LEVEL=INFO
LOG_FORMAT=json

# View logs:
docker-compose logs -f app

# Export logs to file:
docker-compose logs app > /var/log/data-dictionary-app.log
```

### 2. Prometheus Monitoring

```yaml
# Add to docker-compose.prod.yml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "127.0.0.1:9090:9090"
    networks:
      - ddgen-network

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - ddgen-network
```

### 3. Health Monitoring

```bash
# Comprehensive health check script
#!/bin/bash

# Check application health
APP_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

# Check database health
DB_HEALTH=$(curl -s http://localhost:8000/api/v1/database/health | jq -r '.status')

# Check disk space
DISK_USAGE=$(df -h /app/data | awk 'NR==2 {print $5}' | sed 's/%//')

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", $3/$2 * 100}')

# Alert if unhealthy
if [ "$APP_HEALTH" != "200" ] || [ "$DB_HEALTH" != "healthy" ] || [ "$DISK_USAGE" -gt 80 ] || [ "$MEM_USAGE" -gt 90 ]; then
  # Send alert
  echo "ALERT: System unhealthy" | mail -s "Data Dictionary Alert" admin@yourdomain.com
fi
```

---

## Scaling Considerations

### Vertical Scaling (Single Instance)

Increase resources for single server:

```bash
# Increase database resources
# PostgreSQL:
shared_buffers=512MB      # 25% of RAM
effective_cache_size=2GB  # 50% of RAM
work_mem=16MB

# Increase application workers:
uvicorn src.main:app --workers $(nproc)
```

### Horizontal Scaling (Multiple Instances)

Deploy multiple application instances behind load balancer:

```bash
# Load balancer configuration (nginx)
upstream data_dictionary_backend {
  least_conn;
  server app1:8000 max_fails=3 fail_timeout=30s;
  server app2:8000 max_fails=3 fail_timeout=30s;
  server app3:8000 max_fails=3 fail_timeout=30s;
}

server {
  listen 443 ssl http2;
  server_name yourdomain.com;

  location / {
    proxy_pass http://data_dictionary_backend;
    # ... proxy settings ...
  }
}
```

### Database Scaling

#### PostgreSQL Read Replicas

```yaml
# Add read replica to docker-compose
services:
  postgres-replica:
    image: postgres:15-alpine
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_SERVICE_HOST=postgres
      - POSTGRES_MASTER_SERVICE_PORT=5432
```

---

## Maintenance Procedures

### Routine Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Backup verification | Daily | `./verify-backups.sh` |
| Database optimization | Weekly | `VACUUM ANALYZE` |
| Log rotation | Daily | Automatic |
| Security updates | Weekly | `apt update && apt upgrade` |
| Certificate renewal | 90 days | Automatic (certbot) |
| Disk space check | Daily | `df -h` |

### Update Procedure

```bash
# 1. Backup current version
./backup-comprehensive.sh

# 2. Pull latest changes
git pull origin main

# 3. Build new version
docker-compose -f docker-compose.prod.yml build

# 4. Stop old version
docker-compose -f docker-compose.prod.yml down

# 5. Run migrations
docker-compose -f docker-compose.prod.yml run --rm app alembic upgrade head

# 6. Start new version
docker-compose -f docker-compose.prod.yml up -d

# 7. Verify deployment
curl http://localhost:8000/health
```

---

## Disaster Recovery

### Recovery Time Objective (RTO): 1 hour
### Recovery Point Objective (RPO): 24 hours

### Recovery Procedure

```bash
# 1. Provision new server
# 2. Install Docker and dependencies
# 3. Restore from backup

# SQLite:
aws s3 cp s3://your-backup-bucket/latest/db.db /app/data/app.db

# PostgreSQL:
docker exec -i ddgen-postgres pg_restore \
  -U ddgen_user \
  -d data_dictionary_db \
  --clean \
  < backup.dump

# 4. Start application
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify recovery
curl http://localhost:8000/api/v1/database/stats
```

---

## Troubleshooting

### Common Issues

See detailed troubleshooting in [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md#troubleshooting)

---

## Summary

This deployment guide provides comprehensive instructions for production deployment. Key takeaways:

1. **Choose appropriate architecture** based on team size and requirements
2. **Follow security best practices** - Never skip security hardening
3. **Implement robust backup strategy** - Test restore procedures regularly
4. **Monitor continuously** - Setup alerting before issues occur
5. **Plan for disasters** - Have recovery procedures documented and tested

For additional support, consult the [README.md](README.md) and [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).
