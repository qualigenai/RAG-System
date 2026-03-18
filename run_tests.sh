#!/bin/bash
# RAG System v1.5 - Quick Start Automation Testing
# Run: bash run_tests.sh

echo "=================================="
echo "RAG System v1.5"
echo "Automated Testing Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_URL="http://localhost:8000"
PYTHON_CMD="python"

echo -e "${BLUE}Checking prerequisites...${NC}"
echo ""

# Check Python
echo -n "Python: "
if command -v python &> /dev/null; then
    echo -e "${GREEN}✓ Found${NC}"
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Found${NC}"
    PYTHON_CMD="python3"
else
    echo -e "${RED}✗ Not found${NC}"
    exit 1
fi

# Check Backend
echo -n "Backend ($BACKEND_URL): "
if curl -s $BACKEND_URL/health > /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo -e "${YELLOW}Start backend: python -m uvicorn src.api.main:app --reload${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Installing test dependencies...${NC}"
pip install pytest requests --quiet
if command -v locust &> /dev/null; then
    echo "Locust already installed"
else
    pip install locust --quiet
fi

echo -e "${GREEN}✓ Dependencies ready${NC}"
echo ""

# Run tests
echo -e "${BLUE}Running automated tests...${NC}"
echo ""

$PYTHON_CMD automated_tests.py

echo ""
echo -e "${BLUE}Test run complete!${NC}"
echo -e "${BLUE}Check test_reports/ for detailed reports${NC}"
