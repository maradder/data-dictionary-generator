#!/bin/bash
# ==============================================================================
# Docker Build Script for Data Dictionary Generator
# ==============================================================================
# This script builds the Docker image with both frontend and backend
# ==============================================================================

set -e  # Exit on error

echo "=========================================="
echo "Data Dictionary Generator - Docker Build"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Build frontend
echo -e "${BLUE}[1/3] Building frontend...${NC}"
cd frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

echo -e "${YELLOW}Building frontend production bundle...${NC}"
npm run build

cd ..
echo -e "${GREEN}✓ Frontend build complete${NC}"
echo ""

# Build Docker image
echo -e "${BLUE}[2/3] Building Docker image...${NC}"
docker build -f backend/Dockerfile -t data-dictionary-gen:latest .
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

# Display image info
echo -e "${BLUE}[3/3] Image information:${NC}"
docker images | grep data-dictionary-gen
echo ""

# Success message
echo -e "${GREEN}=========================================="
echo "Build complete!"
echo "==========================================${NC}"
echo ""
echo "Quick start options:"
echo ""
echo "  1. SQLite mode (lightweight, recommended):"
echo "     ${YELLOW}docker-compose up app${NC}"
echo "     or use: ${YELLOW}./docker-run-sqlite.sh${NC}"
echo ""
echo "  2. PostgreSQL mode (advanced):"
echo "     ${YELLOW}docker-compose --profile postgres up app-postgres${NC}"
echo ""
echo "  3. Direct run with Docker:"
echo "     ${YELLOW}docker run -p 8000:8000 -v \$(pwd)/data:/app/data data-dictionary-gen:latest${NC}"
echo ""
echo "Application will be available at: ${GREEN}http://localhost:8000${NC}"
echo ""
