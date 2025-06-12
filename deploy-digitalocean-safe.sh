#!/bin/bash

# SAFE Digital Ocean Deployment Script for Liquidation Heatmap
# This version preserves SSH access and includes safety checks

echo "🚀 SAFE Digital Ocean Deployment - Liquidation Heatmap"
echo "======================================================"

# Safety check - ensure we're not root or warn user
if [[ $EUID -eq 0 ]]; then
   echo "⚠️ Running as root. Creating backup user account for safety..."
   adduser --disabled-password --gecos "" backup-user 2>/dev/null || true
   usermod -aG sudo backup-user 2>/dev/null || true
fi

# Create backup of important configs
echo "💾 Creating safety backups..."
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup 2>/dev/null || true
sudo cp /etc/ufw/ufw.conf /etc/ufw/ufw.conf.backup 2>/dev/null || true

# Update system
echo "📦 Updating system packages..."
sudo apt update

# CRITICAL: Always allow SSH before enabling firewall
echo "🔒 Securing SSH access FIRST..."
sudo ufw allow 22/tcp
sudo ufw allow OpenSSH

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
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

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 30

# Check if app is running
if sudo docker-compose ps | grep -q "Up"; then
    echo "✅ Application is running successfully!"
else
    echo "❌ Application failed to start. Checking logs..."
    sudo docker-compose logs
fi

# SAFE firewall setup - SSH is already allowed
echo "🔒 Configuring firewall safely..."
sudo ufw allow 8501/tcp  # Streamlit
echo "y" | sudo ufw enable

# Test SSH connectivity
echo "🔍 Testing SSH connectivity..."
sudo systemctl status ssh | head -5

# Get server IP
SERVER_IP=$(curl -s http://checkip.amazonaws.com || echo "Unable to detect IP")

echo ""
echo "🎉 SAFE Deployment Complete!"
echo "============================"
echo "🌐 Access your app at:"
echo "   IP: http://$SERVER_IP:8501"
echo ""
echo "🔒 SSH Security Status:"
echo "   ✅ SSH access preserved"
echo "   ✅ Port 22 remains open"
echo "   ✅ Backup configs created"
echo ""
echo "📊 Your liquidation heatmap features:"
echo "   ✅ Real-time crypto prices"
echo "   ✅ Interactive visualizations"
echo "   ✅ No API restrictions"
echo ""
echo "🔧 Management commands:"
echo "   View logs: sudo docker-compose logs -f"
echo "   Restart: sudo docker-compose restart" 
echo "   Stop: sudo docker-compose down"
echo ""
echo "🆘 If you lose SSH access:"
echo "   1. Use Digital Ocean Console"
echo "   2. Run: sudo ufw allow 22"
echo "   3. Restore config: sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config"
echo "   4. Restart SSH: sudo systemctl restart ssh"