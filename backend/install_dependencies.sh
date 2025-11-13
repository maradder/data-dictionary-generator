#!/bin/bash
# Install/Update Dependencies for Data Dictionary Generator Backend

set -e  # Exit on error

echo "================================================"
echo "Installing Backend Dependencies"
echo "================================================"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "📦 Installing Python packages from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "Installed packages:"
pip list | grep -E "lxml|fastapi|sqlalchemy|pydantic|pandas|ijson|openpyxl|openai"

echo ""
echo "================================================"
echo "Ready to run the server!"
echo "================================================"
echo ""
echo "Start the server with:"
echo "  python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
