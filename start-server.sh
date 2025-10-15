#!/bin/bash

# Odoo Server Starter
# Simple script to start the Odoo server with common options

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ODOO_BIN="python3 odoo-bin"
CONFIG_FILE="odoo.conf"
DATABASE="odoo19"
VENV_PATH="venv/bin/activate"

echo -e "${BLUE}🚀 Odoo Server Starter${NC}"
echo "======================"

# Check if we're in the right directory
if [ ! -f "odoo-bin" ] || [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Error: Not in Odoo root directory${NC}"
    echo "Please run this script from the Odoo project root"
    exit 1
fi

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📍 Current branch: ${YELLOW}$CURRENT_BRANCH${NC}"

# Kill any existing processes
echo -e "${BLUE}🛑 Stopping any running Odoo processes...${NC}"
pkill -f "odoo-bin" || true
sleep 1

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source "$VENV_PATH"

# Start server
echo -e "${GREEN}🚀 Starting Odoo server...${NC}"
echo -e "${YELLOW}   Database: $DATABASE${NC}"
echo -e "${YELLOW}   Config: $CONFIG_FILE${NC}"
echo -e "${YELLOW}   URL: http://localhost:8076${NC}"
echo ""
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

$ODOO_BIN -c "$CONFIG_FILE" -d "$DATABASE" --dev=reload
