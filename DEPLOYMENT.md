# 🚀 Digital Ocean Deployment Guide

Deploy your liquidation heatmap to Digital Ocean in minutes!

## 📋 Prerequisites

- Digital Ocean account
- Basic droplet ($4-6/month is enough)
- Domain name (optional)

## 🔧 Step-by-Step Deployment

### 1. Create Digital Ocean Droplet

```bash
# Recommended specs:
- OS: Ubuntu 22.04 LTS
- Size: Basic ($4/month) or Regular ($6/month)
- Datacenter: Choose closest to your users
- Additional options: Enable monitoring
```

### 2. Connect to Your Droplet

```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP
```

### 3. One-Command Deployment

```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/vsching/liquidation-heatmap/main/deploy-digitalocean.sh | bash
```

### 4. Access Your App

Your liquidation heatmap will be available at:
- **Direct IP**: `http://YOUR_DROPLET_IP:8501`
- **Domain** (if configured): `http://yourdomain.com`

## 🎯 What the Script Does

✅ **System Updates** - Updates Ubuntu packages  
✅ **Docker Installation** - Installs Docker & Docker Compose  
✅ **Repository Clone** - Downloads your app from GitHub  
✅ **Container Build** - Creates optimized Docker container  
✅ **Firewall Setup** - Configures UFW security  
✅ **Nginx Proxy** - Optional reverse proxy setup  
✅ **SSL Ready** - Prepared for HTTPS with Certbot  

## 🌐 Custom Domain Setup (Optional)

If you want a custom domain like `crypto.yourdomain.com`:

1. **Point your domain** to your droplet IP in your DNS settings
2. **Run the script** and choose "y" for Nginx setup
3. **Enable HTTPS** (recommended):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## 🔧 Management Commands

```bash
# View live logs
sudo docker-compose logs -f

# Restart the app
sudo docker-compose restart

# Update to latest version
cd liquidation-heatmap
git pull
sudo docker-compose up -d --build

# Stop the app
sudo docker-compose down

# Check container status
sudo docker-compose ps
```

## 📊 Performance Optimization

### For High Traffic:
```bash
# Upgrade to a larger droplet
# Add more memory/CPU via Digital Ocean panel

# Enable Docker resource limits
# Edit docker-compose.yml:
services:
  liquidation-heatmap:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### For Multiple Apps:
```bash
# Use different ports for multiple instances
# Edit docker-compose.yml ports section:
ports:
  - "8502:8501"  # Different external port
```

## 🔒 Security Best Practices

1. **SSH Key Authentication**
   ```bash
   # Disable password auth, use SSH keys only
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```

2. **Regular Updates**
   ```bash
   # Set up automatic security updates
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure unattended-upgrades
   ```

3. **Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install htop nethogs iotop
   ```

## 💰 Cost Estimate

- **Basic Droplet**: $4-6/month
- **Domain**: $10-15/year  
- **Total**: ~$5-7/month for professional crypto heatmap

## 🆘 Troubleshooting

### App Not Loading?
```bash
# Check if container is running
sudo docker-compose ps

# View error logs
sudo docker-compose logs

# Restart if needed
sudo docker-compose restart
```

### Port Issues?
```bash
# Check if port is open
sudo netstat -tulpn | grep 8501

# Check firewall
sudo ufw status
```

### Memory Issues?
```bash
# Check memory usage
free -h

# Upgrade droplet or add swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 Monitoring & Analytics

Add monitoring to track your app usage:

```bash
# Install monitoring stack (optional)
curl -fsSL https://get.docker.com | sh
docker run -d --name=netdata --restart=unless-stopped \
  -p 19999:19999 \
  -v netdataconfig:/etc/netdata \
  -v netdatalib:/var/lib/netdata \
  -v netdatacache:/var/cache/netdata \
  -v /etc/passwd:/host/etc/passwd:ro \
  -v /etc/group:/host/etc/group:ro \
  -v /proc:/host/proc:ro \
  -v /sys:/host/sys:ro \
  -v /etc/os-release:/host/etc/os-release:ro \
  --cap-add SYS_PTRACE \
  --security-opt apparmor=unconfined \
  netdata/netdata
```

Access monitoring at: `http://YOUR_IP:19999`

---

🎉 **Your professional liquidation heatmap is now live on Digital Ocean!**