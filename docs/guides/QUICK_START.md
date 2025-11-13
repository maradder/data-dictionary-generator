# Quick Start Guide

Get the Data Dictionary Generator running in 2 minutes.

## One-Command Start

### SQLite Mode (Recommended)
```bash
./docker-run-sqlite.sh
```
Access at: **http://localhost:8000**

### PostgreSQL Mode
```bash
./docker-run-postgres.sh
```
Access at: **http://localhost:8001**

## First Time Setup

### 1. Clone and Build
```bash
git clone <repository-url>
cd data-dictionary-gen
./docker-build.sh
```

### 2. Configure (Optional)
```bash
cp .env.sqlite.example .env
# Edit .env to add your OpenAI API key
nano .env
```

### 3. Start
```bash
./docker-run-sqlite.sh
```

### 4. Access
Open browser to: **http://localhost:8000**

## Common Commands

### Start/Stop
```bash
# Start
docker-compose up -d app

# Stop
docker-compose down

# Restart
docker-compose restart app
```

### View Logs
```bash
# Follow logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app
```

### Database
```bash
# SQLite - Access database
sqlite3 ./data/app.db

# PostgreSQL - Access database
docker exec -it ddgen_postgres psql -U ddgen_user -d data_dictionary_db
```

### Backup
```bash
# SQLite - Backup
cp ./data/app.db ./backups/app-$(date +%Y%m%d).db

# PostgreSQL - Backup
docker exec ddgen_postgres pg_dump -U ddgen_user data_dictionary_db > backup.sql
```

## Endpoints

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/health
- **Database Stats**: http://localhost:8000/api/v1/database/stats

## Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Or use a different port
docker run -p 8080:8000 -v $(pwd)/data:/app/data data-dictionary-gen:latest
```

### Container Won't Start
```bash
# Check logs
docker-compose logs app

# Rebuild
./docker-build.sh
docker-compose up -d app
```

### Frontend Not Loading
```bash
# Rebuild frontend
cd frontend && npm run build && cd ..
./docker-build.sh
```

## Need Help?

- **Full Docker Guide**: See [Docker Deployment](../deployment/DOCKER_DEPLOYMENT.md)
- **Production Deployment**: See [Production Deployment](../deployment/PRODUCTION_DEPLOYMENT.md)
- **Migration Guide**: See [Migration Guide](./MIGRATION_GUIDE.md)
- **API Reference**: http://localhost:8000/api/docs
- **Documentation Index**: See [Documentation README](../README.md)
