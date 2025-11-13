#!/bin/bash
# ==============================================================================
# Quick Start Script - PostgreSQL Mode
# ==============================================================================
# This script starts the Data Dictionary Generator in PostgreSQL mode
# For production deployments requiring concurrent access and scaling
# ==============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "Data Dictionary Generator - PostgreSQL Mode"
echo "==========================================${NC}"
echo ""

# Check if image exists
if ! docker images | grep -q "data-dictionary-gen"; then
    echo -e "${YELLOW}Docker image not found. Building image...${NC}"
    ./docker-build.sh
fi

# Start PostgreSQL and the application
echo -e "${BLUE}Starting PostgreSQL database and application...${NC}"
docker-compose --profile postgres up -d

echo ""
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
sleep 5

echo ""
echo -e "${GREEN}✓ Application started successfully!${NC}"
echo ""
echo "Application URL: ${GREEN}http://localhost:8001${NC}"
echo "Database: PostgreSQL (data_dictionary_db)"
echo ""
echo "PostgreSQL connection:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  User: ddgen_user"
echo "  Password: ddgen_password"
echo "  Database: data_dictionary_db"
echo ""
echo "Useful commands:"
echo "  View logs:      ${YELLOW}docker-compose logs -f app-postgres${NC}"
echo "  Stop:           ${YELLOW}docker-compose --profile postgres down${NC}"
echo "  Restart:        ${YELLOW}docker-compose restart app-postgres${NC}"
echo "  psql shell:     ${YELLOW}docker exec -it ddgen_postgres psql -U ddgen_user -d data_dictionary_db${NC}"
echo ""
echo "Optional: Start pgAdmin for database management"
echo "  ${YELLOW}docker-compose --profile tools up -d pgadmin${NC}"
echo "  Access at: ${GREEN}http://localhost:5050${NC}"
echo ""
