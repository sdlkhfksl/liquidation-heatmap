#!/bin/bash

# SSL Setup Script for liquidation.tradertoolspro.com
# Run this AFTER DNS propagation is complete

DOMAIN="liquidation.tradertoolspro.com"

echo "🔒 Setting up SSL for $DOMAIN"
echo "============================="

# Check if domain resolves to this server
SERVER_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || echo "unknown")
DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null || echo "unknown")

echo "🌐 Checking DNS resolution..."
echo "   Server IP: $SERVER_IP"
echo "   Domain IP: $DOMAIN_IP"

if [ "$SERVER_IP" != "$DOMAIN_IP" ] && [ "$DOMAIN_IP" != "unknown" ]; then
    echo "⚠️ WARNING: Domain doesn't point to this server yet!"
    echo "   Please wait for DNS propagation or check your DNS settings"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Aborted. Please fix DNS first."
        exit 1
    fi
fi

# Setup SSL with certbot
echo "🔒 Setting up SSL certificate..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@tradertoolspro.com --redirect

# Check if SSL was successful
if [ $? -eq 0 ]; then
    echo "✅ SSL certificate installed successfully!"
    
    # Test the configuration
    echo "🧪 Testing nginx configuration..."
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        echo "🔄 Reloading nginx..."
        sudo systemctl reload nginx
        
        echo ""
        echo "🎉 SUCCESS! Your liquidation heatmap is now available at:"
        echo "   🔒 https://$DOMAIN"
        echo ""
        echo "🔧 SSL Certificate Info:"
        sudo certbot certificates | grep -A 5 $DOMAIN
        
        echo ""
        echo "📅 SSL Auto-renewal:"
        echo "   Certbot will automatically renew your certificate"
        echo "   Test renewal: sudo certbot renew --dry-run"
        
    else
        echo "❌ Nginx configuration error after SSL setup"
        exit 1
    fi
else
    echo "❌ SSL certificate installation failed!"
    echo "🔍 Check the error above and try again"
    echo ""
    echo "💡 Common issues:"
    echo "   - Domain doesn't point to this server"
    echo "   - Port 80/443 not accessible"
    echo "   - DNS not propagated yet"
    exit 1
fi

echo ""
echo "🔒 HTTPS Setup Complete!"
echo "======================="