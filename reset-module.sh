#!/bin/bash

# Odoo Module Reset Script
# This script completely uninstalls and reinstalls a module to fix schema/view conflicts

set -e  # Exit on any error

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

echo -e "${BLUE}🔧 Odoo Module Reset Tool${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "odoo-bin" ] || [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Error: Not in Odoo root directory${NC}"
    echo "Please run this script from the Odoo project root"
    exit 1
fi

# Get module name from user
if [ -z "$1" ]; then
    echo -e "${YELLOW}📝 Enter the module name to reset:${NC}"
    read -p "Module name: " MODULE_NAME
else
    MODULE_NAME="$1"
fi

if [ -z "$MODULE_NAME" ]; then
    echo -e "${RED}❌ Error: Module name is required${NC}"
    exit 1
fi

echo -e "${BLUE}🎯 Target module: ${YELLOW}$MODULE_NAME${NC}"
echo ""

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source "$VENV_PATH"

# Step 1: Kill any running Odoo processes
echo -e "${BLUE}🛑 Stopping any running Odoo processes...${NC}"
pkill -f "odoo-bin" || true
sleep 2

# Step 2: Database cleanup
echo -e "${BLUE}🗃️  Cleaning up database for module: $MODULE_NAME${NC}"
python3 -c "
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host='localhost',
        database='$DATABASE',
        user='odoo'
    )
    cur = conn.cursor()
    
    print('🔍 Uninstalling module completely...')
    
    # Set module state to uninstalled
    cur.execute('''
        UPDATE ir_module_module 
        SET state = 'uninstalled' 
        WHERE name = %s
    ''', ('$MODULE_NAME',))
    
    print('✅ Module marked as uninstalled')
    
    # Delete all module-related views
    cur.execute('''
        DELETE FROM ir_ui_view 
        WHERE model LIKE %s
    ''', ('$MODULE_NAME.%',))
    
    deleted_views = cur.rowcount
    print(f'✅ Deleted {deleted_views} views')
    
    # Delete all module-related actions
    cur.execute('''
        DELETE FROM ir_act_window 
        WHERE res_model LIKE %s
    ''', ('$MODULE_NAME.%',))
    
    deleted_actions = cur.rowcount
    print(f'✅ Deleted {deleted_actions} actions')
    
    # Clear view cache
    cur.execute('DELETE FROM ir_ui_view_custom WHERE 1=1')
    deleted_custom = cur.rowcount
    print(f'✅ Cleared {deleted_custom} custom view entries')
    
    conn.commit()
    print('✅ Database cleanup completed!')
    
except Exception as e:
    print(f'❌ Database Error: {e}')
    sys.exit(1)
    
finally:
    if 'cur' in locals():
        cur.close()
    if 'conn' in locals():
        conn.close()
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database cleanup failed${NC}"
    exit 1
fi

# Step 3: Fresh install
echo -e "${BLUE}📦 Fresh installing module: $MODULE_NAME${NC}"
$ODOO_BIN -c "$CONFIG_FILE" -d "$DATABASE" -i "$MODULE_NAME" --stop-after-init

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Module installation failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Module $MODULE_NAME has been successfully reset!${NC}"
echo -e "${BLUE}🚀 You can now start the server with:${NC}"
echo -e "${YELLOW}   source $VENV_PATH && $ODOO_BIN -c $CONFIG_FILE -d $DATABASE --dev=reload${NC}"
echo ""
