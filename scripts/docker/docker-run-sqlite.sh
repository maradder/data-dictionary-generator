#!/bin/bash
# ==============================================================================
# Quick Start Script - SQLite Mode
# ==============================================================================
# This script starts the Data Dictionary Generator in SQLite mode
# Perfect for development, testing, and lightweight production use
# ==============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Data Dictionary Generator - Quick Start"
echo "==========================================${NC}"
echo ""

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo -e "${YELLOW}Creating data directory...${NC}"
    mkdir -p data
fi

# Check if image exists
if ! docker images | grep -q "data-dictionary-gen"; then
    echo -e "${YELLOW}Docker image not found. Building image...${NC}"
    ./docker-build.sh
fi

# Start the container
echo -e "${BLUE}Starting application in SQLite mode...${NC}"
docker-compose up -d app

echo ""
echo -e "${GREEN}✓ Application started successfully!${NC}"
echo ""
echo "Application URL: ${GREEN}http://localhost:8000${NC}"
echo "Database location: ${YELLOW}./data/app.db${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:      ${YELLOW}docker-compose logs -f app${NC}"
echo "  Stop:           ${YELLOW}docker-compose down${NC}"
echo "  Restart:        ${YELLOW}docker-compose restart app${NC}"
echo "  View database:  ${YELLOW}sqlite3 ./data/app.db${NC}"
echo ""
echo "The database is persisted in ./data/ directory"
echo ""
