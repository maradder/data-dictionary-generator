#!/bin/bash
# Setup script for Data Dictionary Generator backend

set -e

echo "=== Data Dictionary Generator - Backend Setup ==="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-dev.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
else
    echo ".env file already exists"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start database: docker-compose up -d postgres redis"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start server: uvicorn src.main:app --reload"
echo ""
echo "Access the API at: http://localhost:8000/api/docs"
