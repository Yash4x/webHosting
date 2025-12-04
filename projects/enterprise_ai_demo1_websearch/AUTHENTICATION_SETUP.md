# Authentication System Setup Guide

## Overview
This guide will help you set up the complete authentication system for the AI Image Generator with user registration, login, and dashboard functionality.

## What's Been Implemented

### ✅ Database Models
- **User Model**: Username, email, password (hashed with bcrypt), timestamps
- **GeneratedImage Model**: Links images to users with metadata (prompt, type, file paths)
- **Relationships**: One-to-many (User → GeneratedImages) with cascade delete

### ✅ Authentication Routes
- `/register` - User registration with validation
- `/login` - User authentication with session management
- `/logout` - Secure logout
- `/dashboard` - User dashboard showing generated images and statistics

### ✅ Protected Routes
All generation endpoints now require authentication:
- `/generate` - Single image generation page
- `/story` - Visual story generation page
- `/gallery` - Image gallery
- `/api/generate-image` - API endpoint for image generation
- `/api/generate-story` - API endpoint for story generation

### ✅ UI Templates
- `login.html` - Modern login page with Tailwind CSS
- `register.html` - Registration page with client-side validation
- `dashboard.html` - User dashboard with statistics and recent images
- Updated `base.html` - Navigation with login/register/logout links

### ✅ Docker Configuration
- PostgreSQL 16 service added to both docker-compose files
- Database volume persistence configured
- Health checks for database readiness
- Environment variables for database credentials

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and update it:

```bash
cp .env.example .env
```

Edit `.env` and update these critical values:

```env
# REQUIRED: Your OpenAI API key
OPENAI_API_KEY=sk-your-actual-openai-api-key

# REQUIRED: Generate a secure secret key
SECRET_KEY=fdf6e2e8c9f00a998427f452cd0a9a81c75f01a8a92c1961cdf671b72230f7b4

# REQUIRED: Set a secure database password
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://aiuser:your_secure_password_here@postgres:5432/aiimages
```

**⚠️ Important**: Change the `SECRET_KEY` and `POSTGRES_PASSWORD` to unique values for production!

### 2. Start the Application

```bash
# Build and start all services (app + database)
docker compose up --build

# Or run in background
docker compose up -d --build
```

The entrypoint script will automatically:
- Wait for PostgreSQL to be ready
- Initialize Flask-Migrate (first run only)
- Run database migrations to create tables
- Start the Flask application

### 3. Access the Application

Open your browser and navigate to:
- **Homepage**: http://localhost:5000
- **Register**: http://localhost:5000/register
- **Login**: http://localhost:5000/login

### 4. Create Your First User

1. Click "Sign Up" in the navigation
2. Fill in the registration form:
   - Username (minimum 3 characters)
   - Email (valid email format)
   - Password (minimum 6 characters)
   - Confirm Password
3. Click "Create Account"
4. You'll be redirected to login
5. Log in with your credentials

### 5. Generate Images

Once logged in:
1. Navigate to "Generate Image" or "Create Story"
2. Enter a prompt
3. Your generated images are automatically saved to your account
4. View them in your Dashboard

## Database Migrations

### Initial Migration (Automatic)

The entrypoint script handles this automatically on first run. But if you need to run manually:

```bash
# Enter the container
docker compose exec ai-app bash

# Initialize migrations (first time only)
flask db init

# Create a migration
flask db migrate -m "Initial migration - User and GeneratedImage tables"

# Apply the migration
flask db upgrade
```

### Creating New Migrations

If you modify the database models in `models.py`:

```bash
# Create a new migration
docker compose exec ai-app flask db migrate -m "Description of changes"

# Apply the migration
docker compose exec ai-app flask db upgrade
```

### Viewing Migration History

```bash
docker compose exec ai-app flask db history
```

## Database Management

### Accessing PostgreSQL

```bash
# Connect to PostgreSQL container
docker compose exec postgres psql -U aiuser -d aiimages

# List tables
\dt

# View users
SELECT id, username, email, created_at FROM "user";

# View generated images
SELECT id, user_id, prompt, image_type, created_at FROM generated_image;

# Exit
\q
```

### Database Backup

```bash
# Backup database
docker compose exec postgres pg_dump -U aiuser aiimages > backup_$(date +%Y%m%d).sql

# Restore database
docker compose exec -T postgres psql -U aiuser aiimages < backup_20250101.sql
```

## Testing the Authentication System

### 1. Test Registration
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&email=test@example.com&password=testpass123&confirm_password=testpass123"
```

### 2. Test Login
```bash
curl -c cookies.txt -X POST http://localhost:5000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

### 3. Test Protected Route (Dashboard)
```bash
curl -b cookies.txt http://localhost:5000/dashboard
```

## Troubleshooting

### Database Connection Issues

**Error**: `FATAL: role "aiuser" does not exist`

**Solution**: Database hasn't started properly. Check logs:
```bash
docker compose logs postgres
```

Restart services:
```bash
docker compose down
docker compose up
```

### Migration Errors

**Error**: `Can't locate revision identified by 'xyz'`

**Solution**: Reset migrations:
```bash
# Stop containers
docker compose down -v  # WARNING: This deletes all data

# Remove migrations folder
rm -rf migrations/

# Start fresh
docker compose up --build
```

### Permission Denied Errors

**Error**: `Permission denied: 'generated_images'`

**Solution**: Fix directory permissions:
```bash
chmod -R 777 generated_images logs static/generated
```

Or use proper ownership:
```bash
sudo chown -R 1001:1001 generated_images logs static/generated
```

### Login Not Working

**Symptoms**: Can't login after registration

**Check**:
1. Verify database is running: `docker compose ps`
2. Check app logs: `docker compose logs ai-app`
3. Verify user exists:
   ```bash
   docker compose exec postgres psql -U aiuser -d aiimages -c "SELECT * FROM \"user\";"
   ```

### Dashboard Shows No Images

**Solution**: Generate an image first! The dashboard only shows images you've created.

## Security Best Practices

### Production Deployment

When deploying to production (using `docker-compose.prod.yml`):

1. **Use Strong Secrets**:
   ```bash
   # Generate a new secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Set Environment Variables**: Never commit `.env` file to Git
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

3. **Use Docker Secrets** (recommended for production):
   ```yaml
   secrets:
     db_password:
       external: true
     secret_key:
       external: true
   ```

4. **Enable HTTPS**: Configure Caddy reverse proxy (see infrastructure/)

5. **Limit Database Access**: Use internal Docker networks

### Password Requirements

Current validation:
- Minimum 6 characters
- No maximum length
- No special character requirements

To strengthen, update validation in `app.py` `/register` route.

### Session Security

Configured in `app.py`:
- `SESSION_COOKIE_HTTPONLY = True` (prevents JavaScript access)
- `SESSION_COOKIE_SECURE = False` (set to True in production with HTTPS)
- `SESSION_COOKIE_SAMESITE = 'Lax'` (CSRF protection)

## API Changes

### Image Generation API

The `/api/generate-image` endpoint now:
1. Requires authentication (`@login_required`)
2. Saves generated images to database with `user_id`
3. Returns database record ID along with image URL

### Response Format

```json
{
  "success": true,
  "image_url": "/generated_images/image_123456.png",
  "file_path": "generated_images/image_123456.png",
  "db_id": 42,
  "message": "Image generated successfully"
}
```

## Next Steps

### Recommended Enhancements

1. **Email Verification**: Add email confirmation for new registrations
2. **Password Reset**: Implement forgot password functionality
3. **Profile Management**: Allow users to update email/password
4. **Image Sharing**: Add public/private image visibility
5. **Rate Limiting**: Prevent abuse with generation limits per user
6. **Admin Dashboard**: Monitor users and system usage

### Performance Optimization

1. **Database Indexing**: Already implemented on username and email
2. **Query Optimization**: Use `lazy='dynamic'` for large result sets
3. **Caching**: Add Redis for session storage
4. **CDN**: Serve static images from CDN

## Support

### Common Commands

```bash
# View all containers
docker compose ps

# View logs
docker compose logs -f ai-app
docker compose logs -f postgres

# Restart services
docker compose restart

# Stop and remove everything
docker compose down

# Stop and remove including volumes (WARNING: deletes data)
docker compose down -v

# Access container shell
docker compose exec ai-app bash

# Check disk usage
docker system df
```

### File Locations

- **Templates**: `templates/*.html`
- **Models**: `models.py`
- **Routes**: `app.py` (lines 200-400)
- **Migrations**: `migrations/versions/*.py`
- **Generated Images**: `generated_images/`
- **Database Data**: Docker volume `postgres_data`

## Conclusion

Your AI Image Generator now has a complete authentication system with:
- ✅ User registration and login
- ✅ Secure password hashing (bcrypt)
- ✅ Session management (Flask-Login)
- ✅ PostgreSQL database with migrations
- ✅ User dashboard with statistics
- ✅ Protected image generation routes
- ✅ Modern UI with Tailwind CSS

The system is ready for development and testing. For production deployment, follow the security best practices section above.

**Happy generating! 🎨✨**
