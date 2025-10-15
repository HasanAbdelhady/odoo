# Odoo Development Scripts

This directory contains helpful shell scripts to manage common Odoo development tasks, especially when switching between git branches with different database schemas.

## 🚀 Quick Start

```bash
# One-command solution for most issues
./quick-fix.sh
```

## 📋 Available Scripts

### 1. `quick-fix.sh` - Interactive Menu
**The main script you'll use most often**

```bash
./quick-fix.sh
```

Provides an interactive menu with options:
- Fix branch switch issues
- Reset a specific module
- Start the server
- Upgrade specific modules
- Kill all Odoo processes

### 2. `fix-branch-switch.sh` - Branch Switch Fixer
**Use when switching between git branches causes view/schema errors**

```bash
# Interactive mode
./fix-branch-switch.sh

# Direct mode with module names
./fix-branch-switch.sh gym om_hospital tasks_app
```

**What it does:**
- Cleans up problematic database views from previous branches
- Removes cached views that reference non-existent fields
- Upgrades specified modules to sync with current branch schema
- Fixes common errors like "field is undefined"

### 3. `reset-module.sh` - Complete Module Reset
**Use when a module is completely broken and needs fresh installation**

```bash
# Interactive mode
./reset-module.sh

# Direct mode
./reset-module.sh gym
```

**What it does:**
- Completely uninstalls the module from database
- Removes all views, actions, and menu items
- Fresh installs the module
- Nuclear option for stubborn module issues

### 4. `start-server.sh` - Server Starter
**Simple server starter with automatic cleanup**

```bash
./start-server.sh
```

**What it does:**
- Shows current git branch
- Kills any existing Odoo processes
- Activates virtual environment
- Starts server with dev mode and reload

## 🔧 Common Use Cases

### Switching Git Branches
```bash
# 1. Switch branch
git checkout feature-branch

# 2. Fix any schema conflicts
./fix-branch-switch.sh gym om_hospital

# 3. Start server
./start-server.sh
```

### Module Development Workflow
```bash
# After making changes to a module
./quick-fix.sh
# Choose option 4 to upgrade specific modules

# If module is completely broken
./reset-module.sh my_module
```

### Daily Development
```bash
# Start your day
./start-server.sh

# When things go wrong
./quick-fix.sh
```

## ⚠️ When to Use Each Script

| Problem | Solution | Script |
|---------|----------|--------|
| "Field X is undefined" after branch switch | Clean views + upgrade | `fix-branch-switch.sh` |
| Module completely broken | Nuclear reset | `reset-module.sh` |
| Just want to start server | Simple start | `start-server.sh` |
| Not sure what's wrong | Interactive menu | `quick-fix.sh` |
| Need to upgrade modules | Quick upgrade | `quick-fix.sh` → option 4 |

## 🛠️ Configuration

The scripts use these default settings (edit the scripts to change):

```bash
ODOO_BIN="python3 odoo-bin"
CONFIG_FILE="odoo.conf"
DATABASE="odoo19"
VENV_PATH="venv/bin/activate"
```

## 🔍 Troubleshooting

### Script won't run
```bash
# Make sure it's executable
chmod +x script-name.sh

# Run from Odoo root directory
cd /path/to/odoo
./script-name.sh
```

### Database connection errors
- Ensure PostgreSQL is running
- Check database name in scripts matches your setup
- Verify user 'odoo' has access to the database

### Module not found
- Ensure module exists in `custom_addons/` or `addons/`
- Check module name spelling
- Verify module has proper `__manifest__.py`

## 📝 Examples

### Fixing Gym Module After Branch Switch
```bash
git checkout dev
./fix-branch-switch.sh gym
# Fixes: "gym.membership.product_id field is undefined"
```

### Complete Reset of Hospital Module
```bash
./reset-module.sh om_hospital
# Completely reinstalls the module
```

### Interactive Problem Solving
```bash
./quick-fix.sh
# Choose option 1 for branch issues
# Choose option 2 for module reset
# Choose option 3 to just start server
```

---

**💡 Tip:** Bookmark `./quick-fix.sh` - it handles 90% of common Odoo development issues!
