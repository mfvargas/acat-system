# 🚀 ACAT System - Staging Deployment Guide

## 📋 Prerequisites
- 2 Ubuntu servers on DigitalOcean
- Domain: `acatcr.org` 
- SSH access to both servers
- DNS access to configure subdomains

## 🎯 Server Configuration

### Server 1: STAGING
- **Domain**: `staging.acatcr.org`
- **Purpose**: Testing and validation environment
- **Requirements**: 2GB RAM, 1 CPU, 25GB SSD (minimum)

### Server 2: PRODUCTION  
- **Domain**: `acatcr.org` or `www.acatcr.org`
- **Purpose**: Live production environment
- **Requirements**: 4GB RAM, 2 CPU, 50GB SSD (recommended)

## 🔧 Step-by-Step Deployment

### Step 1: Configure DNS Records
In your DigitalOcean DNS or domain registrar:
```
A Record: staging.acatcr.org → STAGING_SERVER_IP
A Record: acatcr.org → PRODUCTION_SERVER_IP
A Record: www.acatcr.org → PRODUCTION_SERVER_IP (optional)
```

### Step 2: Setup SSH Access
Ensure you can SSH to your staging server:
```bash
ssh ubuntu@STAGING_SERVER_IP
```

### Step 3: Deploy to Staging Server
1. **Edit deployment script**:
   ```bash
   nano deploy-to-staging-server.sh
   # Change: STAGING_SERVER="YOUR_STAGING_SERVER_IP"
   # To: STAGING_SERVER="YOUR.ACTUAL.IP"
   ```

2. **Run deployment**:
   ```bash
   ./deploy-to-staging-server.sh
   ```

### Step 4: Setup Staging Server
SSH to your staging server and run setup:
```bash
ssh ubuntu@STAGING_SERVER_IP
cd /opt/acat-system
./setup-staging-server.sh
```

### Step 5: Start Application
```bash
# On staging server
cd /opt/acat-system
docker-compose -f docker-compose.production.yml up -d
```

### Step 6: Setup SSL Certificate
```bash
# On staging server - AFTER DNS is pointing to server
sudo certbot --nginx -d staging.acatcr.org
```

### Step 7: Verify Deployment
```bash
# Check service status
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs -f web

# Test endpoints
curl -I https://staging.acatcr.org
curl -I https://staging.acatcr.org/admin/
```

## 🔍 Verification Checklist

### ✅ DNS Configuration
- [ ] `staging.acatcr.org` resolves to staging server IP
- [ ] `acatcr.org` resolves to production server IP

### ✅ Server Setup
- [ ] SSH access working
- [ ] Docker installed and running
- [ ] Nginx installed and configured
- [ ] Firewall configured (UFW)

### ✅ Application Status
- [ ] PostgreSQL container running
- [ ] Redis container running  
- [ ] Django application container running
- [ ] Nginx container running

### ✅ SSL Certificate
- [ ] SSL certificate installed
- [ ] HTTPS redirect working
- [ ] SSL score A+ (test at ssllabs.com)

### ✅ Functionality Tests
- [ ] Main page loads: `https://staging.acatcr.org`
- [ ] Admin panel accessible: `https://staging.acatcr.org/admin/`
- [ ] API responds: `https://staging.acatcr.org/api/`
- [ ] Static files loading correctly
- [ ] Database migrations completed

## 🛠️ Useful Commands

### Docker Management
```bash
# View all containers
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f [service_name]

# Restart services
docker-compose -f docker-compose.production.yml restart

# Update and redeploy
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

### Database Management
```bash
# Access Django shell
docker-compose -f docker-compose.production.yml exec web python manage.py shell

# Run migrations
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

### Monitoring
```bash
# System resources
htop
df -h
free -h

# Nginx status
sudo systemctl status nginx
sudo nginx -t

# SSL certificate info
sudo certbot certificates
```

## 🔧 Troubleshooting

### Common Issues

#### 1. DNS Not Resolving
```bash
# Check DNS propagation
nslookup staging.acatcr.org
dig staging.acatcr.org
```

#### 2. Docker Permission Issues
```bash
sudo usermod -aG docker $USER
# Logout and login again
```

#### 3. Port Already in Use
```bash
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :443
```

#### 4. SSL Certificate Issues
```bash
sudo certbot --nginx --dry-run -d staging.acatcr.org
sudo certbot renew --dry-run
```

## 📞 Support

### Log Locations
- **Nginx logs**: `/var/log/nginx/`
- **Application logs**: `/opt/acat-system/logs/`
- **Docker logs**: `docker-compose logs`

### Health Checks
```bash
# Application health
curl -I https://staging.acatcr.org
curl -I https://staging.acatcr.org/admin/

# Database connectivity
docker-compose -f docker-compose.production.yml exec web python manage.py dbshell
```

---

## 🎉 Next Steps After Staging

Once staging is working perfectly:

1. **Test thoroughly** on staging environment
2. **Configure production server** using similar process
3. **Setup CI/CD pipeline** for automated deployments
4. **Configure monitoring** and alerts
5. **Setup backup strategy** for production

**Remember**: Always test changes on staging before deploying to production!
