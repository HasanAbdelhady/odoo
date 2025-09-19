# Odoo Tasks App - Docker Deployment

This setup containerizes your Odoo instance with the custom Tasks app and makes it publicly accessible.

## Quick Start (Local Testing)

1. **Build and run locally:**
   ```bash
   docker-compose -f docker-compose-simple.yml up -d
   ```

2. **Access Odoo:**
   - URL: http://localhost:8069
   - Database: postgres
   - Admin email: admin
   - Password: admin

3. **Your Tasks app will be automatically installed and available in the menu!**

## Public Deployment with DuckDNS

### Step 1: Get DuckDNS Domain
1. Go to https://www.duckdns.org/
2. Sign in and create a domain (e.g., `myodoo.duckdns.org`)
3. Note your token from the dashboard

### Step 2: Setup DuckDNS and SSL
```bash
./setup-duckdns.sh myodoo.duckdns.org YOUR_DUCKDNS_TOKEN
```

### Step 3: Configure Router
1. Forward ports 80 and 443 to your Linux machine
2. Find your router's admin panel (usually 192.168.1.1 or 192.168.0.1)
3. Add port forwarding rules:
   - External port 80 → Internal port 80 (your machine IP)
   - External port 443 → Internal port 443 (your machine IP)

### Step 4: Start Full Deployment
```bash
docker-compose up -d
```

### Step 5: Access Publicly
- Your Odoo will be available at: https://myodoo.duckdns.org
- The Tasks app will be in the main menu

## File Structure
```
/home/hasan/odoo/odoo/
├── Dockerfile                 # Odoo container with Tasks app
├── docker-compose.yml         # Full setup with HTTPS
├── docker-compose-simple.yml  # Simple setup for testing
├── nginx.conf                 # Reverse proxy config
├── setup-duckdns.sh          # DuckDNS and SSL setup
└── addons/tasks_app/         # Your custom Tasks module
```

## Useful Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f odoo

# Stop services
docker-compose down

# Rebuild after changes
docker-compose build --no-cache odoo
docker-compose up -d

# Update DuckDNS IP manually
./update-duckdns.sh
```

## Troubleshooting

1. **SSL Certificate Issues:**
   ```bash
   # Renew certificates
   sudo certbot renew
   # Copy new certificates
   sudo cp /etc/letsencrypt/live/YOUR_DOMAIN/fullchain.pem ssl/cert.pem
   sudo cp /etc/letsencrypt/live/YOUR_DOMAIN/privkey.pem ssl/key.pem
   ```

2. **Port Forwarding:**
   - Ensure ports 80 and 443 are forwarded to your machine
   - Check your firewall: `sudo ufw allow 80` and `sudo ufw allow 443`

3. **Database Issues:**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

## Security Notes
- Change default admin password after first login
- The setup uses basic authentication - consider adding additional security measures for production
- SSL certificates auto-renew, but monitor them periodically
