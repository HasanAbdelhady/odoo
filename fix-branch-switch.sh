#!/bin/bash

# Odoo Branch Switch Fixer
# This script fixes module issues when switching between git branches with different schemas

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

echo -e "${BLUE}🔀 Odoo Branch Switch Fixer${NC}"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "odoo-bin" ] || [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}❌ Error: Not in Odoo root directory${NC}"
    echo "Please run this script from the Odoo project root"
    exit 1
fi

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📍 Current branch: ${YELLOW}$CURRENT_BRANCH${NC}"

# Get modules to fix
if [ -z "$1" ]; then
    echo -e "${YELLOW}📝 Enter module names to fix (space-separated):${NC}"
    echo "Common modules: gym, om_hospital, tasks_app"
    read -p "Modules: " MODULES_INPUT
    MODULES=($MODULES_INPUT)
else
    MODULES=("$@")
fi

if [ ${#MODULES[@]} -eq 0 ]; then
    echo -e "${RED}❌ Error: At least one module name is required${NC}"
    exit 1
fi

echo -e "${BLUE}🎯 Target modules: ${YELLOW}${MODULES[*]}${NC}"
echo ""

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source "$VENV_PATH"

# Step 1: Kill any running Odoo processes
echo -e "${BLUE}🛑 Stopping any running Odoo processes...${NC}"
pkill -f "odoo-bin" || true
sleep 2

# Step 2: Clean up problematic views for all modules
echo -e "${BLUE}🧹 Cleaning up problematic views...${NC}"
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
    
    modules = '${MODULES[*]}'.split()
    
    for module in modules:
        print(f'🔍 Cleaning views for module: {module}')
        
        # Find and remove problematic views
        cur.execute('''
            SELECT id, name, model, arch_db::text 
            FROM ir_ui_view 
            WHERE model LIKE %s
            AND (
                arch_db::text LIKE '%product_id%' OR 
                arch_db::text LIKE '%trainer_amount%' OR 
                arch_db::text LIKE '%is_gym_membership%' OR
                arch_db::text LIKE '%currency_id%' OR
                arch_db::text LIKE '%in_time%' OR
                arch_db::text LIKE '%out_time%' OR
                arch_db::text LIKE '%number_of_sessions%' OR
                arch_db::text LIKE '%session_duration%'
            )
        ''', (f'{module}.%',))
        
        problematic_views = cur.fetchall()
        
        if problematic_views:
            print(f'  Found {len(problematic_views)} problematic views')
            
            for view_id, name, model, arch in problematic_views:
                try:
                    # Remove inheritance relationships first
                    cur.execute('UPDATE ir_ui_view SET inherit_id = NULL WHERE inherit_id = %s', (view_id,))
                    # Delete the view
                    cur.execute('DELETE FROM ir_ui_view WHERE id = %s', (view_id,))
                    print(f'  ✅ Deleted view: {name}')
                except Exception as e:
                    print(f'  ⚠️  Could not delete view {name}: {e}')
        else:
            print(f'  ✅ No problematic views found for {module}')
    
    # Clear all custom views
    cur.execute('DELETE FROM ir_ui_view_custom WHERE 1=1')
    deleted_custom = cur.rowcount
    print(f'✅ Cleared {deleted_custom} custom view entries')
    
    conn.commit()
    print('✅ View cleanup completed!')
    
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
    echo -e "${RED}❌ View cleanup failed${NC}"
    exit 1
fi

# Step 3: Upgrade all modules
echo -e "${BLUE}📦 Upgrading modules...${NC}"
MODULE_LIST=$(IFS=,; echo "${MODULES[*]}")
$ODOO_BIN -c "$CONFIG_FILE" -d "$DATABASE" -u "$MODULE_LIST" --stop-after-init

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Module upgrade failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Branch switch issues fixed for modules: ${MODULES[*]}${NC}"
echo -e "${BLUE}🚀 You can now start the server with:${NC}"
echo -e "${YELLOW}   source $VENV_PATH && $ODOO_BIN -c $CONFIG_FILE -d $DATABASE --dev=reload${NC}"
echo ""
