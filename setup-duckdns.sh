#!/bin/bash

# DuckDNS Setup Script
# Usage: ./setup-duckdns.sh YOUR_DOMAIN YOUR_TOKEN

DOMAIN=$1
TOKEN=$2

if [ -z "$DOMAIN" ] || [ -z "$TOKEN" ]; then
    echo "Usage: $0 <your-domain> <your-token>"
    echo "Example: $0 myodoo.duckdns.org abc123def456"
    exit 1
fi

# Create SSL directory
mkdir -p ssl

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt update
    sudo apt install -y certbot
fi

# Stop nginx if running
docker-compose stop nginx 2>/dev/null || true

# Get SSL certificate from Let's Encrypt
echo "Getting SSL certificate for $DOMAIN..."
sudo certbot certonly --standalone --preferred-challenges http -d $DOMAIN

# Copy certificates to ssl directory
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*.pem

# Create DuckDNS update script
cat > update-duckdns.sh << EOF
#!/bin/bash
# DuckDNS IP update script
curl "https://www.duckdns.org/update?domains=$DOMAIN&token=$TOKEN&ip="
EOF

chmod +x update-duckdns.sh

# Add to crontab for automatic updates (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/update-duckdns.sh >/dev/null 2>&1") | crontab -

echo "DuckDNS setup complete!"
echo "Domain: $DOMAIN"
echo "SSL certificates installed"
echo "DuckDNS will update every 5 minutes"
echo ""
echo "Now run: docker-compose up -d"
