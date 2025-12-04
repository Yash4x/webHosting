# Quick Start Guide - Authentication System

## 🚀 Get Started in 3 Steps

### Step 1: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required changes in `.env`:**
```env
# 1. Add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# 2. Generate a secure secret key (run this command)
python -c "import secrets; print(secrets.token_hex(32))"
# Then paste the output here:
SECRET_KEY=paste_generated_key_here

# 3. Set a secure database password
POSTGRES_PASSWORD=your_secure_password_123
DATABASE_URL=postgresql://aiuser:your_secure_password_123@postgres:5432/aiimages
```

### Step 2: Start the Application

```bash
# Build and start all services (Flask app + PostgreSQL)
docker compose up --build

# Or run in background
docker compose up -d --build
```

**Wait for these messages:**
```
✓ PostgreSQL is ready!
✓ Running database migrations...
✓ Starting Flask application...
✓ * Running on http://0.0.0.0:5000
```

### Step 3: Create Your First User

1. Open browser: http://localhost:5000
2. Click "Sign Up" button
3. Fill in registration form
4. Click "Create Account"
5. Login with your credentials
6. Start generating images! 🎨

---

## 📋 What You Get

### User Features
- ✅ User registration with validation
- ✅ Secure login (bcrypt password hashing)
- ✅ User dashboard with statistics
- ✅ Personal image gallery
- ✅ Generation history tracking

### Security Features
- ✅ Password hashing with bcrypt
- ✅ Session management (Flask-Login)
- ✅ Protected routes (login required)
- ✅ CSRF protection
- ✅ Secure session cookies

### Database
- ✅ PostgreSQL 16 with persistence
- ✅ Automatic migrations on startup
- ✅ User and GeneratedImage tables
- ✅ Relationship tracking

---

## 🔍 Testing Your Setup

### 1. Check Services Are Running
```bash
docker compose ps
```

**Expected output:**
```
NAME              STATUS    PORTS
ai-postgres       healthy   5432/tcp
ai-image-generator up       0.0.0.0:5000->5000/tcp
```

### 2. Check Application Logs
```bash
docker compose logs -f ai-app
```

**Look for:**
- "PostgreSQL is ready!"
- "Running database migrations..."
- "Running on http://0.0.0.0:5000"

### 3. Test Database Connection
```bash
docker compose exec postgres psql -U aiuser -d aiimages -c "\dt"
```

**Should show tables:**
- `user`
- `generated_image`
- `alembic_version`

### 4. Access Web Interface
Open in browser:
- Homepage: http://localhost:5000
- Register: http://localhost:5000/register
- Login: http://localhost:5000/login

---

## 🆘 Quick Troubleshooting

### Problem: Can't access http://localhost:5000

**Solution 1:** Check if container is running
```bash
docker compose ps
# If not running:
docker compose up
```

**Solution 2:** Check port conflicts
```bash
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Use different port
# Edit docker-compose.yml: "5001:5000"
docker compose up
```

### Problem: Database connection error

**Error:** `FATAL: role "aiuser" does not exist`

**Solution:**
```bash
# Restart all services
docker compose down
docker compose up
```

### Problem: Login not working

**Solution:** Check logs for errors
```bash
docker compose logs ai-app | grep -i error

# Common issue: SECRET_KEY not set
# Make sure .env file exists and has SECRET_KEY
cat .env | grep SECRET_KEY
```

### Problem: Permission denied on generated_images

**Solution:**
```bash
# Fix permissions
chmod -R 777 generated_images logs static/generated

# Or use proper ownership
sudo chown -R 1001:1001 generated_images logs static/generated
```

---

## 📱 Quick Commands Reference

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Restart service
docker compose restart ai-app

# Access database
docker compose exec postgres psql -U aiuser -d aiimages

# Access container shell
docker compose exec ai-app bash

# View all users
docker compose exec postgres psql -U aiuser -d aiimages \
  -c "SELECT id, username, email, created_at FROM \"user\";"

# View generated images
docker compose exec postgres psql -U aiuser -d aiimages \
  -c "SELECT id, user_id, prompt, image_type, created_at FROM generated_image;"

# Rebuild from scratch
docker compose down -v  # WARNING: Deletes all data
docker compose up --build
```

---

## 🎯 First User Flow

1. **Start Application**
   ```bash
   docker compose up -d
   ```

2. **Open Browser** → http://localhost:5000

3. **Click "Sign Up"**

4. **Fill Registration Form:**
   - Username: `demo` (min 3 chars)
   - Email: `demo@example.com` (valid email)
   - Password: `demo123` (min 6 chars)
   - Confirm Password: `demo123` (must match)

5. **Click "Create Account"**

6. **Redirected to Login Page**

7. **Login:**
   - Username: `demo`
   - Password: `demo123`

8. **Redirected to Dashboard** 🎉

9. **Generate First Image:**
   - Click "Generate Image" button
   - Enter prompt: "a beautiful sunset over mountains"
   - Wait for generation (15-30 seconds)
   - Image appears in gallery

10. **View in Dashboard:**
    - Click "Dashboard" in navigation
    - See statistics: 1 Total Images, 1 Single Image, 0 Stories
    - See your image in Recent Generations

---

## 🔐 Security Checklist for Production

Before deploying to production:

- [ ] Generate a NEW SECRET_KEY (not the one from .env.example)
- [ ] Use a STRONG database password (20+ chars, mixed case, numbers, symbols)
- [ ] Enable HTTPS (set `SESSION_COOKIE_SECURE = True` in app.py)
- [ ] Never commit `.env` file to Git (add to .gitignore)
- [ ] Use Docker secrets for sensitive values
- [ ] Configure Caddy reverse proxy with SSL
- [ ] Set up database backups
- [ ] Enable firewall (see course docs)
- [ ] Monitor logs for suspicious activity
- [ ] Update dependencies regularly

---

## 📚 Next Steps

Now that authentication is working:

1. **Read Full Documentation:**
   - `AUTHENTICATION_SETUP.md` - Complete setup guide
   - `IMPLEMENTATION_SUMMARY.md` - Technical details

2. **Generate Some Images:**
   - Try single image generation
   - Create a visual story
   - Check your dashboard

3. **Explore the Code:**
   - `models.py` - Database models
   - `app.py` - Authentication routes (lines 200-400)
   - `templates/dashboard.html` - Dashboard UI

4. **Deploy to Production:**
   - See `DEPLOYMENT.md` for server setup
   - Use `docker-compose.prod.yml` for production
   - Configure domain and SSL

---

## 💡 Tips

- Use strong passwords in production
- Back up your database regularly
- Monitor logs for errors: `docker compose logs -f`
- Test authentication before adding real users
- Keep dependencies updated
- Document any custom changes

---

## 🎉 Success!

If you can:
1. ✅ Register a new user
2. ✅ Login successfully
3. ✅ See your dashboard
4. ✅ Generate an image
5. ✅ View it in your dashboard

**Your authentication system is working perfectly!** 🚀

Ready to deploy? See `AUTHENTICATION_SETUP.md` for production deployment guide.

---

**Need help?** Check:
- `AUTHENTICATION_SETUP.md` - Full setup guide with troubleshooting
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- Application logs: `docker compose logs ai-app`
- Database logs: `docker compose logs postgres`
