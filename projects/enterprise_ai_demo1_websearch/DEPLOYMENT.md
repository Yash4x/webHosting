# 🚀 AI Image Generator - Deployment Guide

Complete CI/CD pipeline setup for the Enterprise AI Image Generation application.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Local Testing](#local-testing)
- [Docker Hub Setup](#docker-hub-setup)
- [GitHub Repository Setup](#github-repository-setup)
- [Production Server Deployment](#production-server-deployment)
- [Watchtower Auto-Deployment](#watchtower-auto-deployment)
- [Domain Configuration](#domain-configuration)
- [Testing the Pipeline](#testing-the-pipeline)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ GitHub account
- ✅ Docker Hub account
- ✅ Production server with Docker installed
- ✅ Domain name (optional but recommended)
- ✅ Basic knowledge of Docker and CI/CD

---

## 🧪 Local Testing

### 1. Setup Environment

```bash
cd projects/enterprise_ai_demo1_websearch

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env
```

Update `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

### 2. Test Without Docker (Optional)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run the application
python app.py
```

Visit: http://localhost:5000

### 3. Test With Docker

```bash
# Create Docker network if it doesn't exist
docker network create web 2>/dev/null || true

# Build and run
docker compose up --build

# In another terminal, test the endpoints
curl http://localhost:5000/
curl http://localhost:5000/generate
```

### 4. Stop Local Testing

```bash
docker compose down
```

---

## 🐳 Docker Hub Setup

### 1. Create Docker Hub Account

1. Go to https://hub.docker.com
2. Sign up or log in
3. Verify your email

### 2. Create Repository

1. Click "Create Repository"
2. **Name**: `ai-image-generator`
3. **Visibility**: Public (or Private if you prefer)
4. **Description**: "AI Image Generation with DALL-E - Auto-deployed via CI/CD"
5. Click "Create"

### 3. Generate Access Token

1. Click your profile → **Account Settings**
2. Go to **Security** → **Access Tokens**
3. Click "**New Access Token**"
4. **Description**: "GitHub Actions CI/CD"
5. **Access permissions**: Read, Write, Delete
6. Click "**Generate**"
7. **⚠️ COPY THE TOKEN** - you won't see it again!

---

## 🔧 GitHub Repository Setup

### Option A: Fork Entire Repository (Recommended)

```bash
# 1. On GitHub, go to: https://github.com/kaw393939/mywebclass_hosting
# 2. Click "Fork" button
# 3. Clone your fork
git clone https://github.com/YOUR_USERNAME/mywebclass_hosting.git
cd mywebclass_hosting/projects/enterprise_ai_demo1_websearch
```

### Option B: Create New Repository for Just This Project

```bash
cd projects/enterprise_ai_demo1_websearch

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit: AI Image Generator with CI/CD"

# Create new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-image-generator.git
git branch -M main
git push -u origin main
```

### Configure GitHub Secrets

1. Go to your repository on GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click "**New repository secret**"

Add these **THREE** secrets:

| Secret Name | Value | Where to Get It |
|-------------|-------|-----------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Docker Hub profile |
| `DOCKERHUB_TOKEN` | Access token from step above | Docker Hub → Security → Access Tokens |
| `OPENAI_API_KEY_TEST` | Your OpenAI API key | https://platform.openai.com/api-keys |

⚠️ **Important**: The OpenAI API key secret is used for running tests in CI/CD. You'll also need it in production.

---

## 🖥️ Production Server Deployment

### 1. SSH Into Your Server

```bash
ssh your-username@your-server-ip
```

### 2. Create Project Directory

```bash
mkdir -p ~/projects/ai-image-generator
cd ~/projects/ai-image-generator
```

### 3. Create Environment File

```bash
nano .env
```

Add:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key

# Docker Hub Configuration
DOCKERHUB_USERNAME=your-dockerhub-username

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=production
```

**⚠️ Security Note**: Never commit `.env` to Git! It contains your API keys.

### 4. Create Production docker-compose.yml

```bash
nano docker-compose.yml
```

Paste:
```yaml
version: '3.8'

services:
  ai-app:
    image: ${DOCKERHUB_USERNAME}/ai-image-generator:latest
    container_name: ai-image-generator
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./generated_images:/app/generated_images
      - ./logs:/app/logs
    networks:
      - web
    labels:
      - "com.centurylinklabs.watchtower.enable=true"
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  web:
    external: true
```

### 5. Create Directories

```bash
mkdir -p generated_images logs
chmod 755 generated_images logs
```

### 6. Deploy the Application

```bash
# Load environment variables
source .env

# Pull the latest image
docker compose pull

# Start the application
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f ai-app
```

### 7. Test the Deployment

```bash
# Health check
curl http://localhost:5000/

# Should return HTML page
```

---

## 🔄 Watchtower Auto-Deployment

Watchtower automatically updates your containers when new images are pushed to Docker Hub.

### 1. Add to Infrastructure

Edit your main infrastructure docker-compose.yml:

```bash
cd ~/mywebclass_hosting/infrastructure
nano docker-compose.yml
```

Add Watchtower service:

```yaml
  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=300  # Check every 5 minutes
      - WATCHTOWER_LABEL_ENABLE=true  # Only update labeled containers
      - WATCHTOWER_INCLUDE_RESTARTING=true
      - WATCHTOWER_ROLLING_RESTART=true
      - TZ=America/New_York  # Set your timezone
    networks:
      - web
```

### 2. Restart Infrastructure

```bash
docker compose up -d
```

### 3. Verify Watchtower is Running

```bash
docker logs -f watchtower
```

You should see:
```
INFO: Watchtower is running
INFO: Scheduling first run: 2025-11-22T...
```

---

## 🌐 Domain Configuration (Optional)

### 1. Add to Caddyfile

```bash
cd ~/mywebclass_hosting/infrastructure
nano Caddyfile
```

Add:
```
ai.yourdomain.com {
    reverse_proxy ai-image-generator:5000
}
```

### 2. Reload Caddy

```bash
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### 3. Update DNS

Add an A record:
- **Host**: `ai` (or `ai.yourdomain.com`)
- **Points to**: Your server IP address
- **TTL**: 3600 (or Auto)

Wait 5-30 minutes for DNS propagation.

### 4. Test HTTPS

```bash
curl https://ai.yourdomain.com/
```

---

## 🧪 Testing the CI/CD Pipeline

### 1. Make a Test Change

```bash
cd projects/enterprise_ai_demo1_websearch

# Make a small change
echo "# CI/CD test" >> README.md
```

### 2. Commit and Push

```bash
git add .
git commit -m "Test CI/CD pipeline"
git push origin main
```

### 3. Monitor GitHub Actions

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Watch the workflow run:
   - ✅ Test phase (runs pytest)
   - ✅ Build phase (creates Docker image)
   - ✅ Push phase (uploads to Docker Hub)

Expected time: 3-5 minutes

### 4. Verify on Docker Hub

1. Go to https://hub.docker.com
2. Navigate to your `ai-image-generator` repository
3. Check **Tags** tab
4. Should see:
   - `latest` (updated timestamp)
   - `main-<commit-sha>` (specific version)

### 5. Watch Auto-Deployment

```bash
# On your server, watch Watchtower logs
docker logs -f watchtower
```

Within 5-10 minutes, you should see:
```
INFO: Found new image for ai-image-generator
INFO: Stopping container ai-image-generator
INFO: Starting container ai-image-generator
```

### 6. Verify Update

```bash
# Check running container
docker ps | grep ai-image-generator

# Check logs
docker logs ai-image-generator --tail 50

# Test the application
curl http://localhost:5000/
```

---

## 🎉 Complete CI/CD Flow

```
┌──────────────┐
│  Developer   │
│ Makes Change │
└──────┬───────┘
       │ git push
       ▼
┌──────────────┐
│   GitHub     │
│  Repository  │
└──────┬───────┘
       │ Triggers
       ▼
┌──────────────┐
│   GitHub     │
│   Actions    │
│  ├─ Tests    │ (2-3 min)
│  ├─ Build    │
│  └─ Push     │
└──────┬───────┘
       │ Pushes image
       ▼
┌──────────────┐
│  Docker Hub  │
│ (Image Repo) │
└──────┬───────┘
       │ Watches (every 5 min)
       ▼
┌──────────────┐
│  Watchtower  │
│ (On Server)  │
│  Detects new │
│     image    │
└──────┬───────┘
       │ Updates
       ▼
┌──────────────┐
│ Application  │
│   Running    │
│  (Updated!)  │
└──────────────┘

Total Time: 5-10 minutes from push to live
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs ai-app

# Common issues:
# - Missing OPENAI_API_KEY in .env
# - Port 5000 already in use
# - Insufficient permissions on mounted volumes
```

**Solutions:**
```bash
# Verify environment variables
docker compose config

# Check if port is in use
sudo lsof -i :5000

# Fix permissions
sudo chown -R $USER:$USER generated_images logs
```

### CI/CD Pipeline Failing

**Tests Failing:**
```bash
# Check GitHub Actions logs
# Common issues:
# - Missing OPENAI_API_KEY_TEST secret
# - Test dependencies not installed
# - Import errors
```

**Build Failing:**
```bash
# Check Dockerfile syntax
# Verify requirements.txt is correct
# Test build locally:
docker build -t test-build .
```

**Push Failing:**
```bash
# Verify Docker Hub credentials
# Check DOCKERHUB_USERNAME and DOCKERHUB_TOKEN secrets
# Ensure repository exists on Docker Hub
```

### Watchtower Not Updating

```bash
# Check Watchtower logs
docker logs watchtower

# Verify container has label
docker inspect ai-image-generator | grep watchtower

# Force update manually
docker compose pull
docker compose up -d
```

### Application Errors

```bash
# Check application logs
docker compose logs -f ai-app

# Common issues:
# - Invalid OpenAI API key
# - Network connectivity issues
# - Missing permissions on directories
```

### OpenAI API Issues

```bash
# Test API key manually
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Should return list of models
```

---

## 📊 Monitoring

### Check Application Status

```bash
# Container status
docker compose ps

# Health check
curl http://localhost:5000/health

# View recent logs
docker compose logs --tail=100 ai-app

# Follow logs in real-time
docker compose logs -f ai-app
```

### Check Resource Usage

```bash
# Container stats
docker stats ai-image-generator

# Disk usage
du -sh generated_images/
du -sh logs/
```

### Check Generated Content

```bash
# List generated images
ls -lh generated_images/

# Count images
find generated_images/ -type f -name "*.png" | wc -l

# View logs
tail -f logs/app.log
```

---

## 🔒 Security Best Practices

### API Key Management

✅ **DO:**
- Store API keys in `.env` files (never in code)
- Use GitHub Secrets for CI/CD
- Rotate keys periodically
- Use different keys for dev/prod

❌ **DON'T:**
- Commit `.env` files to Git
- Share API keys in plain text
- Use production keys in CI/CD tests
- Expose keys in logs

### Container Security

✅ **Implemented:**
- Non-root user in container
- Minimal base image (python:3.11-slim)
- Health checks enabled
- Resource limits ready to configure

### Network Security

✅ **Recommended:**
- Use Caddy for HTTPS (automatic Let's Encrypt)
- Isolate database on internal network (if added)
- Use firewall rules (UFW)
- Regular security updates

---

## 📈 Performance Optimization

### Image Generation

- Average generation time: 10-30 seconds per image
- Story generation (5 scenes): 2-3 minutes
- Consider implementing queue system for high traffic

### Docker Image

Current size: ~500MB (can be optimized)

**Optimization tips:**
```dockerfile
# Use multi-stage builds
# Remove build dependencies after installation
# Use .dockerignore effectively
```

### Volume Management

```bash
# Clean old generated images periodically
find generated_images/ -type f -mtime +30 -delete

# Rotate logs
# (Already configured with logging_config.py)
```

---

## 🎯 Success Checklist

- [ ] Local testing works (`docker compose up`)
- [ ] Tests pass (`pytest`)
- [ ] Code pushed to GitHub
- [ ] GitHub Actions workflow passes
- [ ] Docker image on Docker Hub
- [ ] Application deployed on server
- [ ] Watchtower configured and running
- [ ] Can access via localhost:5000
- [ ] Domain configured (optional)
- [ ] HTTPS working (optional)
- [ ] CI/CD pipeline tested (push triggers update)
- [ ] Monitoring configured

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Watchtower Documentation](https://containrrr.dev/watchtower/)

---

## 🆘 Getting Help

1. **Check application logs**: `docker compose logs ai-app`
2. **Review CI/CD logs**: GitHub Actions tab
3. **Verify configuration**: `docker compose config`
4. **Test manually**: `curl http://localhost:5000/`

---

**🎉 Congratulations!** You now have a fully automated CI/CD pipeline for your AI image generation application!

**Total Setup Time**: ~60 minutes  
**Deployment Time**: 5-10 minutes (automatic)  
**Maintenance**: Minimal (auto-updates via Watchtower)
