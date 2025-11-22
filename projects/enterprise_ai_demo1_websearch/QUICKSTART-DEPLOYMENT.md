# 🚀 Quick Start - CI/CD Deployment

Get your AI Image Generator deployed with automated CI/CD in ~60 minutes.

## ✅ What's Already Done

- ✅ Application code (Flask web app with DALL-E integration)
- ✅ Dockerfile created
- ✅ Docker Compose files (local + production)
- ✅ GitHub Actions CI/CD workflow configured
- ✅ Watchtower integration ready
- ✅ Comprehensive documentation

## 📝 What You Need

Before starting, have these ready:

1. **OpenAI API Key** - [Get it here](https://platform.openai.com/api-keys)
2. **Docker Hub Account** - [Sign up](https://hub.docker.com)
3. **GitHub Account** - For repository and CI/CD
4. **Production Server** - With Docker installed
5. **Domain Name** - Optional but recommended

## 🎯 5-Minute Local Test

First, verify the application works:

```bash
cd projects/enterprise_ai_demo1_websearch

# 1. Setup environment
cp .env.example .env
nano .env  # Add your OPENAI_API_KEY

# 2. Create network
docker network create web 2>/dev/null || true

# 3. Run the app
docker compose up --build

# 4. Test in browser
# Open: http://localhost:5000
```

**Expected**: See the AI Image Generator homepage.

```bash
# 5. Stop when done testing
docker compose down
```

## 🚀 60-Minute Full Deployment

### Step 1: Docker Hub (5 min)

1. Go to https://hub.docker.com
2. Create repository: `ai-image-generator`
3. Generate access token:
   - Settings → Security → New Access Token
   - Permissions: Read, Write, Delete
   - **Copy the token!**

### Step 2: Push to GitHub (10 min)

**Option A - Fork entire repo:**
```bash
# On GitHub: Fork kaw393939/mywebclass_hosting
# Then clone your fork
```

**Option B - New repo just for this app:**
```bash
cd projects/enterprise_ai_demo1_websearch
git init
git add .
git commit -m "Initial commit: AI Image Generator"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ai-image-generator.git
git push -u origin main
```

### Step 3: GitHub Secrets (5 min)

In your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Token from Step 1 |
| `OPENAI_API_KEY_TEST` | Your OpenAI API key |

### Step 4: Test CI/CD (10 min)

```bash
# Make a test change
echo "# Test CI/CD" >> README.md

# Commit and push
git add .
git commit -m "Test CI/CD pipeline"
git push origin main
```

**Watch on GitHub:**
- Go to **Actions** tab
- See workflow run (3-5 min)
- Check for ✅ on all steps

**Verify on Docker Hub:**
- Go to your `ai-image-generator` repo
- Should see `latest` tag updated

### Step 5: Server Deployment (20 min)

SSH into your server:

```bash
ssh your-user@your-server-ip

# 1. Create directory
mkdir -p ~/projects/ai-image-generator
cd ~/projects/ai-image-generator

# 2. Create .env file
nano .env
```

Add to `.env`:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
DOCKERHUB_USERNAME=your-dockerhub-username
FLASK_APP=app.py
FLASK_ENV=production
```

```bash
# 3. Create docker-compose.yml
nano docker-compose.yml
```

Paste (from docker-compose.prod.yml):
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

networks:
  web:
    external: true
```

```bash
# 4. Create directories
mkdir -p generated_images logs

# 5. Deploy
docker compose pull
docker compose up -d

# 6. Test
curl http://localhost:5000/
docker compose logs -f
```

### Step 6: Watchtower Setup (10 min)

```bash
cd ~/mywebclass_hosting/infrastructure
nano docker-compose.yml
```

Add watchtower service:
```yaml
  watchtower:
    image: containrrr/watchtower:latest
    container_name: watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=300
      - WATCHTOWER_LABEL_ENABLE=true
    networks:
      - web
```

```bash
# Restart infrastructure
docker compose up -d

# Watch it work
docker logs -f watchtower
```

### Step 7: Domain Setup (10 min - Optional)

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

```bash
# Reload Caddy
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

**Add DNS A record:**
- Host: `ai`
- Points to: Your server IP

Wait 5-30 minutes, then test: `https://ai.yourdomain.com`

## 🧪 Test the Full Pipeline

```bash
# On your local machine
cd projects/enterprise_ai_demo1_websearch

# Make a visible change
echo "<!-- Updated via CI/CD -->" >> templates/index.html

# Push it
git add .
git commit -m "Test auto-deployment"
git push origin main
```

**What happens:**
1. ✅ GitHub Actions runs (3-5 min)
2. ✅ New image pushed to Docker Hub
3. ✅ Watchtower detects update (5 min)
4. ✅ Container auto-restarts with new version
5. ✅ App is live with changes (Total: ~10 min)

## ✅ Success Checklist

After deployment, verify:

```bash
# On server
docker compose ps                    # Should show "Up" and "healthy"
curl http://localhost:5000/          # Should return HTML
docker logs ai-image-generator       # Should show no errors
docker logs watchtower               # Should show monitoring activity

# From browser
http://localhost:5000                # Homepage loads
http://localhost:5000/generate       # Generate page loads
https://ai.yourdomain.com (optional) # HTTPS works
```

## 🎉 You're Done!

**You now have:**
- ✅ AI Image Generator running in production
- ✅ Automated testing on every push
- ✅ Automatic Docker image builds
- ✅ Auto-deployment via Watchtower
- ✅ HTTPS with auto-renewal (if domain configured)

**Deployment workflow:**
```
Code change → git push → 10 minutes → Live in production
```

## 🐛 Quick Troubleshooting

**App won't start?**
```bash
docker compose logs ai-app
# Check for API key errors
```

**CI/CD failing?**
- Verify all 3 GitHub Secrets are set
- Check GitHub Actions logs

**Not auto-updating?**
```bash
docker logs watchtower
# Should see polling activity
```

**Can't access app?**
```bash
# Check if running
docker compose ps

# Check firewall
sudo ufw status

# Test locally first
curl http://localhost:5000/
```

## 📚 Full Documentation

For detailed information, see:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[README.md](README.md)** - Application overview
- **[WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md)** - Using the app

## 💡 Quick Commands

```bash
# View logs
docker compose logs -f ai-app

# Restart application
docker compose restart ai-app

# Update manually
docker compose pull && docker compose up -d

# Check resource usage
docker stats ai-image-generator

# Access container shell
docker exec -it ai-image-generator /bin/bash
```

---

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting and advanced configuration.

**Ready to use the app?** Read [WEB_INTERFACE_GUIDE.md](WEB_INTERFACE_GUIDE.md) to learn about generating images and stories!
