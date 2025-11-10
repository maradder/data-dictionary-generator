#!/bin/bash
# Verification script to check backend setup

echo "=== Data Dictionary Generator - Setup Verification ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check function
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        return 1
    fi
}

echo "Checking directory structure..."
check_dir "src"
check_dir "src/api"
check_dir "src/api/v1"
check_dir "src/core"
check_dir "src/models"
check_dir "src/schemas"
check_dir "src/services"
check_dir "src/processors"
check_dir "src/repositories"
check_dir "src/exporters"
check_dir "tests"
check_dir "alembic"
echo ""

echo "Checking configuration files..."
check_file "pyproject.toml"
check_file "requirements.txt"
check_file "requirements-dev.txt"
check_file ".env.example"
check_file ".gitignore"
check_file "pytest.ini"
check_file "alembic.ini"
check_file "README.md"
echo ""

echo "Checking core modules..."
check_file "src/main.py"
check_file "src/core/config.py"
check_file "src/core/database.py"
check_file "src/core/logging.py"
check_file "src/core/exceptions.py"
check_file "src/core/security.py"
echo ""

echo "Checking models..."
check_file "src/models/base.py"
check_file "src/models/dictionary.py"
check_file "src/models/version.py"
check_file "src/models/field.py"
check_file "src/models/annotation.py"
echo ""

echo "Checking API routes..."
check_file "src/api/middlewares.py"
check_file "src/api/dependencies.py"
check_file "src/api/v1/dictionaries.py"
check_file "src/api/v1/versions.py"
check_file "src/api/v1/exports.py"
check_file "src/api/v1/search.py"
echo ""

echo "Checking tests..."
check_file "tests/conftest.py"
check_file "tests/test_health.py"
echo ""

echo "Checking Python syntax..."
if command -v python3 &> /dev/null; then
    python_files=$(find src -name "*.py" 2>/dev/null)
    syntax_errors=0
    for file in $python_files; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "${RED}✗${NC} Syntax error in $file"
            syntax_errors=$((syntax_errors + 1))
        fi
    done
    if [ $syntax_errors -eq 0 ]; then
        echo -e "${GREEN}✓${NC} All Python files have valid syntax"
    else
        echo -e "${RED}✗${NC} Found $syntax_errors files with syntax errors"
    fi
else
    echo -e "${YELLOW}⚠${NC} Python3 not found, skipping syntax check"
fi
echo ""

echo "=== Verification Complete ==="
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements-dev.txt"
echo "2. Configure .env file"
echo "3. Start infrastructure: docker-compose up -d postgres redis"
echo "4. Run migrations: alembic upgrade head"
echo "5. Start server: uvicorn src.main:app --reload"
