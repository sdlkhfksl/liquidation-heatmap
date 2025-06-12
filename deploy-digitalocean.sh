#!/bin/bash

# Digital Ocean Deployment Script for Liquidation Heatmap
# Run this on your Digital Ocean droplet

echo "🚀 Digital Ocean Deployment - Liquidation Heatmap"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt update
    sudo apt install -y docker-ce
    sudo usermod -aG docker $USER
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🔧 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Clone or update repository
if [ -d "liquidation-heatmap" ]; then
    echo "🔄 Updating existing repository..."
    cd liquidation-heatmap
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/vsching/liquidation-heatmap.git
    cd liquidation-heatmap
fi

# Create data directory
mkdir -p data

# Build and run with Docker Compose
echo "🏗️ Building and starting application..."
sudo docker-compose down 2>/dev/null || true
sudo docker-compose up -d --build

# Setup firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22    # SSH
sudo ufw allow 8501  # Streamlit
sudo ufw --force enable

# Setup nginx reverse proxy (optional)
read -p "🌐 Setup Nginx reverse proxy for custom domain? (y/n): " setup_nginx
if [[ $setup_nginx == "y" ]]; then
    sudo apt install -y nginx
    
    # Get domain name
    read -p "Enter your domain name (e.g., heatmap.yourdomain.com): " domain_name
    
    # Create nginx config
    sudo tee /etc/nginx/sites-available/liquidation-heatmap << EOF
server {
    listen 80;
    server_name $domain_name;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/liquidation-heatmap /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    
    echo "✅ Nginx configured for $domain_name"
    echo "🔒 To enable HTTPS, run: sudo certbot --nginx -d $domain_name"
fi

# Get server IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com)

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "🌐 Access your app at:"
if [[ $setup_nginx == "y" ]]; then
    echo "   Domain: http://$domain_name"
fi
echo "   IP: http://$SERVER_IP:8501"
echo ""
echo "📊 Your liquidation heatmap is now running with:"
echo "   ✅ Real-time crypto prices"
echo "   ✅ Interactive visualizations"
echo "   ✅ Auto-refresh capabilities"
echo "   ✅ Docker containerization"
echo ""
echo "🔧 Management commands:"
echo "   View logs: sudo docker-compose logs -f"
echo "   Restart: sudo docker-compose restart"
echo "   Stop: sudo docker-compose down"
echo "   Update: git pull && sudo docker-compose up -d --build"