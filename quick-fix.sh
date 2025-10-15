#!/bin/bash

# Odoo Quick Fix
# One-command solution for common Odoo issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}⚡ Odoo Quick Fix Menu${NC}"
echo "======================"
echo ""
echo "What would you like to do?"
echo ""
echo -e "${YELLOW}1)${NC} Fix branch switch issues (clean views + upgrade modules)"
echo -e "${YELLOW}2)${NC} Reset a specific module completely"
echo -e "${YELLOW}3)${NC} Just start the server"
echo -e "${YELLOW}4)${NC} Upgrade specific modules"
echo -e "${YELLOW}5)${NC} Kill all Odoo processes"
echo ""

read -p "Choose an option (1-5): " choice

case $choice in
    1)
        echo -e "${BLUE}🔀 Running branch switch fixer...${NC}"
        ./fix-branch-switch.sh
        ;;
    2)
        echo -e "${BLUE}🔧 Running module reset...${NC}"
        ./reset-module.sh
        ;;
    3)
        echo -e "${BLUE}🚀 Starting server...${NC}"
        ./start-server.sh
        ;;
    4)
        echo -e "${YELLOW}📝 Enter module names to upgrade (space-separated):${NC}"
        read -p "Modules: " modules
        if [ ! -z "$modules" ]; then
            echo -e "${BLUE}📦 Upgrading modules: $modules${NC}"
            source venv/bin/activate
            pkill -f "odoo-bin" || true
            sleep 1
            module_list=$(echo $modules | tr ' ' ',')
            python3 odoo-bin -c odoo.conf -d odoo19 -u "$module_list" --stop-after-init
            echo -e "${GREEN}✅ Modules upgraded!${NC}"
        fi
        ;;
    5)
        echo -e "${BLUE}🛑 Killing all Odoo processes...${NC}"
        pkill -f "odoo-bin" || true
        echo -e "${GREEN}✅ All processes stopped${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid option${NC}"
        exit 1
        ;;
esac
