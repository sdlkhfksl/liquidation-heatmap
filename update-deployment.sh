#!/bin/bash

# Digital Ocean Update Deployment Script
# Usage: curl -fsSL https://raw.githubusercontent.com/vsching/liquidation-heatmap/main/update-deployment.sh | bash

echo "🚀 Updating Liquidation Heatmap on Digital Ocean"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory or find it
if [ ! -d "liquidation-heatmap" ] && [ ! -f "docker-compose.yml" ]; then
    print_status "Looking for liquidation-heatmap directory..."
    
    if [ -d "$HOME/liquidation-heatmap" ]; then
        cd "$HOME/liquidation-heatmap"
        print_success "Found app in $HOME/liquidation-heatmap"
    elif [ -d "/root/liquidation-heatmap" ]; then
        cd "/root/liquidation-heatmap"
        print_success "Found app in /root/liquidation-heatmap"
    else
        print_error "liquidation-heatmap directory not found!"
        print_status "Searching entire system..."
        APP_DIR=$(find / -name "liquidation-heatmap" -type d 2>/dev/null | head -1)
        if [ -n "$APP_DIR" ]; then
            cd "$APP_DIR"
            print_success "Found app in $APP_DIR"
        else
            print_error "Could not find liquidation-heatmap installation"
            print_status "Please run this script from the app directory or install first"
            exit 1
        fi
    fi
elif [ -d "liquidation-heatmap" ]; then
    cd liquidation-heatmap
    print_success "Found liquidation-heatmap subdirectory"
fi

# Verify we're in the right place
if [ ! -f "docker-compose.yml" ] && [ ! -f "streamlit_app.py" ]; then
    print_error "Not in liquidation-heatmap directory!"
    print_status "Current directory: $(pwd)"
    print_status "Please navigate to your app directory first"
    exit 1
fi

print_success "Found liquidation-heatmap app directory: $(pwd)"

# Show current status
print_status "Checking current deployment status..."
if command -v docker-compose &> /dev/null; then
    RUNNING_CONTAINERS=$(sudo docker-compose ps --services --filter "status=running" 2>/dev/null | wc -l)
    print_status "Running containers: $RUNNING_CONTAINERS"
else
    print_warning "Docker Compose not found, will try to install"
fi

# Backup current version (just in case)
print_status "Creating backup of current version..."
BACKUP_DIR="backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
cp streamlit_app.py "$BACKUP_DIR/" 2>/dev/null || true
print_success "Backup created in $BACKUP_DIR"

# Pull latest updates from GitHub
print_status "Pulling latest updates from GitHub..."
if git pull origin main; then
    print_success "Successfully pulled latest updates"
    
    # Show what changed
    print_status "Recent changes:"
    git log --oneline -3 --color=always
else
    print_error "Failed to pull updates from GitHub"
    print_status "Checking git status..."
    git status
    exit 1
fi

# Stop current containers
print_status "Stopping current containers..."
if sudo docker-compose down; then
    print_success "Containers stopped successfully"
else
    print_warning "No containers were running or docker-compose failed"
fi

# Build and start updated containers
print_status "Building and starting updated containers..."
if sudo docker-compose up -d --build; then
    print_success "Containers built and started successfully"
else
    print_error "Failed to build/start containers"
    print_status "Checking Docker logs..."
    sudo docker-compose logs --tail=20
    exit 1
fi

# Wait for containers to be ready
print_status "Waiting for application to start..."
sleep 10

# Check container status
print_status "Checking container status..."
sudo docker-compose ps

# Check if app is responding
print_status "Testing application health..."
HEALTH_CHECK_URL="http://localhost:8501/_stcore/health"
if curl -f -s "$HEALTH_CHECK_URL" > /dev/null; then
    print_success "Application is healthy and responding"
else
    print_warning "Health check failed, but app might still be starting"
fi

# Get server IP for user
SERVER_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || echo "YOUR_SERVER_IP")

# Show deployment summary
echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
print_success "Liquidation heatmap updated successfully"
echo ""
echo "🌐 Access your updated app:"
echo "   📱 Direct IP: http://$SERVER_IP:8501"
if [ "$SERVER_IP" != "YOUR_SERVER_IP" ]; then
    echo "   🔗 Click here: http://$SERVER_IP:8501"
fi
echo ""
echo "✨ Latest updates include:"
echo "   🕒 New duration options (12h, 24h, 2d, 3d)"
echo "   📊 Enhanced historical analysis"
echo "   🎯 Risk level indicators (🟢🟡🔴)"
echo "   📈 Improved liquidation calculations"
echo ""
echo "🔧 Management commands:"
echo "   📊 View logs: sudo docker-compose logs -f"
echo "   🔄 Restart: sudo docker-compose restart"
echo "   ⏹️ Stop: sudo docker-compose down"
echo "   🔍 Status: sudo docker-compose ps"
echo ""
echo "🆘 If something went wrong:"
echo "   📋 Check logs: sudo docker-compose logs"
echo "   🔙 Restore backup: cp $BACKUP_DIR/* ."
echo "   🔄 Rebuild: sudo docker-compose up -d --build"
echo ""
print_success "Update deployment completed at $(date)"