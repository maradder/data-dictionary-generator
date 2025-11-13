#!/bin/bash
# Quick start script for Data Dictionary Generator Backend

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "================================================"
echo "🚀 Starting Data Dictionary Generator Backend"
echo "================================================"
echo ""
echo "Environment: $(which python)"
echo "Python version: $(python --version)"
echo ""
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/api/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop"
echo "================================================"
echo ""

# Start the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
