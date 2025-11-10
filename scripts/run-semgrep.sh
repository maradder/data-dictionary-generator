#!/bin/bash
# Semgrep Security Scanner
# Run this script to perform security analysis on the codebase

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}  Semgrep Security Scanner${NC}"
echo -e "${BLUE}==================================${NC}"
echo ""

# Check if semgrep is installed
if ! command -v semgrep &> /dev/null; then
    echo -e "${YELLOW}Semgrep is not installed.${NC}"
    echo -e "${YELLOW}Installing semgrep via pip...${NC}"
    pip install semgrep
    echo ""
fi

# Determine scan mode
MODE=${1:-full}

case $MODE in
  quick|q)
    echo -e "${GREEN}Running QUICK scan (security-audit only)...${NC}"
    semgrep \
      --config=p/security-audit \
      --error \
      --skip-unknown-extensions \
      --exclude "node_modules" \
      --exclude "venv" \
      --exclude ".venv" \
      --exclude "dist" \
      --exclude "build"
    ;;

  full|f)
    echo -e "${GREEN}Running FULL scan (all rulesets)...${NC}"
    semgrep \
      --config=p/security-audit \
      --config=p/owasp-top-ten \
      --config=p/python \
      --config=p/react \
      --config=p/typescript \
      --config=p/secrets \
      --config=p/sql-injection \
      --config=p/command-injection \
      --error \
      --skip-unknown-extensions \
      --exclude "node_modules" \
      --exclude "venv" \
      --exclude ".venv" \
      --exclude "dist" \
      --exclude "build"
    ;;

  backend|be)
    echo -e "${GREEN}Running BACKEND scan (Python only)...${NC}"
    semgrep \
      --config=p/security-audit \
      --config=p/owasp-top-ten \
      --config=p/python \
      --config=p/sql-injection \
      --config=p/command-injection \
      --error \
      --include "backend/src/**/*.py" \
      --skip-unknown-extensions
    ;;

  frontend|fe)
    echo -e "${GREEN}Running FRONTEND scan (TypeScript/React only)...${NC}"
    semgrep \
      --config=p/security-audit \
      --config=p/owasp-top-ten \
      --config=p/react \
      --config=p/typescript \
      --error \
      --include "frontend/src/**/*.{ts,tsx,js,jsx}" \
      --skip-unknown-extensions
    ;;

  secrets)
    echo -e "${GREEN}Running SECRETS scan...${NC}"
    semgrep \
      --config=p/secrets \
      --error \
      --skip-unknown-extensions
    ;;

  auto)
    echo -e "${GREEN}Running AUTO scan (Semgrep's recommended rules)...${NC}"
    semgrep \
      --config=auto \
      --error \
      --skip-unknown-extensions
    ;;

  json)
    echo -e "${GREEN}Running full scan with JSON output...${NC}"
    semgrep \
      --config=p/security-audit \
      --config=p/owasp-top-ten \
      --config=p/python \
      --config=p/react \
      --config=p/typescript \
      --json \
      --output=semgrep-report.json \
      --skip-unknown-extensions
    echo -e "${GREEN}Results saved to semgrep-report.json${NC}"
    ;;

  *)
    echo -e "${RED}Unknown mode: $MODE${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./scripts/run-semgrep.sh [mode]"
    echo ""
    echo -e "${YELLOW}Available modes:${NC}"
    echo "  quick, q       - Quick scan (security-audit only)"
    echo "  full, f        - Full scan (all rulesets) [DEFAULT]"
    echo "  backend, be    - Backend only (Python)"
    echo "  frontend, fe   - Frontend only (TypeScript/React)"
    echo "  secrets        - Scan for hardcoded secrets"
    echo "  auto           - Use Semgrep's auto-config"
    echo "  json           - Output results as JSON"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./scripts/run-semgrep.sh              # Full scan"
    echo "  ./scripts/run-semgrep.sh quick        # Quick scan"
    echo "  ./scripts/run-semgrep.sh backend      # Backend only"
    echo "  ./scripts/run-semgrep.sh secrets      # Check for secrets"
    exit 1
    ;;
esac

SEMGREP_EXIT_CODE=$?

echo ""
if [ $SEMGREP_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Semgrep scan completed successfully - no issues found!${NC}"
else
    echo -e "${RED}✗ Semgrep found security issues. Please review above.${NC}"
fi
echo ""

exit $SEMGREP_EXIT_CODE
