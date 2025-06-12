#!/bin/bash

# Nginx Domain Setup Script for liquidation.tradertoolspro.com
# This script configures nginx to serve your liquidation heatmap on a custom domain

echo "🌐 Setting up liquidation.tradertoolspro.com"
echo "==========================================="

DOMAIN="liquidation.tradertoolspro.com"
APP_PORT="8501"

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing nginx..."
    sudo apt update
    sudo apt install -y nginx
fi

# Check if certbot is installed for SSL
if ! command -v certbot &> /dev/null; then
    echo "🔒 Installing certbot for SSL..."
    sudo apt install -y certbot python3-certbot-nginx
fi

# Create nginx configuration
echo "⚙️ Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Redirect HTTP to HTTPS (will be enabled after SSL setup)
    # return 301 https://\$server_name\$request_uri;

    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Streamlit specific headers
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Server \$host;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Handle Streamlit WebSocket connections
    location /_stcore/stream {
        proxy_pass http://localhost:$APP_PORT/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
EOF

# Enable the site
echo "🔗 Enabling nginx site..."
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if sudo nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration error!"
    exit 1
fi

# Reload nginx
echo "🔄 Reloading nginx..."
sudo systemctl reload nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

echo ""
echo "📋 NEXT STEPS:"
echo "=============="
echo ""
echo "1. 🌐 Point your domain DNS to this server:"
echo "   Domain: $DOMAIN"
echo "   Type: A Record"
echo "   Value: $(curl -s http://checkip.amazonaws.com 2>/dev/null || echo 'YOUR_SERVER_IP')"
echo ""
echo "2. ⏳ Wait for DNS propagation (5-30 minutes)"
echo ""
echo "3. 🔒 Setup SSL certificate (run after DNS is ready):"
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
echo "4. 🚀 Your app will be available at:"
echo "   http://$DOMAIN (before SSL)"
echo "   https://$DOMAIN (after SSL)"
echo ""
echo "🔧 Useful commands:"
echo "   Check nginx status: sudo systemctl status nginx"
echo "   Reload nginx: sudo systemctl reload nginx"
echo "   Check nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "   Test config: sudo nginx -t"
echo ""
echo "🆘 Troubleshooting:"
echo "   If domain doesn't work, check:"
echo "   - DNS propagation: dig $DOMAIN"
echo "   - Firewall: sudo ufw status"
echo "   - App running: sudo docker-compose ps"
echo "   - Nginx logs: sudo tail -f /var/log/nginx/access.log"