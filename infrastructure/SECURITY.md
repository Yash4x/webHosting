# Infrastructure Security Guide

## Critical Security Settings

### 1. Environment Variables (.env file)

**NEVER commit your .env file to git!**

The `.env` file contains sensitive credentials:
- Database passwords
- pgAdmin login credentials
- API keys (if you add them later)

```bash
# Always use strong passwords
# Minimum 16 characters, mix of uppercase, lowercase, numbers, symbols
POSTGRES_PASSWORD=MyStr0ng!P@ssw0rd#2024$Secure
PGADMIN_PASSWORD=Pgadm1n!SecureP@ss#2024$
```

**Generate strong passwords:**
```bash
# Option 1: OpenSSL
openssl rand -base64 32

# Option 2: /dev/urandom
tr -dc 'A-Za-z0-9!@#$%^&*()_+=' < /dev/urandom | head -c 32

# Option 3: pwgen (install with: sudo apt install pwgen)
pwgen -s 32 1
```

### 2. PostgreSQL Security

**Default Configuration (Secure):**
- ✅ Only accessible on `internal` network
- ✅ No port exposed to host machine
- ✅ No direct internet access
- ✅ Projects connect via Docker network only

**Connection from Projects:**
```yaml
# In your project's docker-compose.yml
services:
  myapp:
    environment:
      DATABASE_URL: postgresql://dbadmin:password@postgres:5432/production
    networks:
      - internal  # Connect to internal network

networks:
  internal:
    external: true  # Use the infrastructure network
```

**NEVER do this in production:**
```yaml
# ❌ DON'T expose PostgreSQL port
postgres:
  ports:
    - "5432:5432"  # This exposes database to the internet!
```

### 3. pgAdmin Security

**Access URL:** `https://db.mywebclass.org`

**Three Security Options:**

#### Option A: Basic Authentication (Recommended)
Add password protection at the reverse proxy level:

```bash
# Generate password hash
docker exec caddy caddy hash-password

# Enter your password when prompted
# Copy the $2a$14$... hash
```

Edit `Caddyfile`:
```caddy
db.mywebclass.org {
    basicauth {
        admin $2a$14$YOUR_HASH_HERE
    }
    reverse_proxy pgadmin:80
}
```

#### Option B: IP Restriction
Only allow access from your IP:

```caddy
db.mywebclass.org {
    @blocked not remote_ip YOUR.HOME.IP.HERE
    respond @blocked "Access Denied" 403
    
    reverse_proxy pgadmin:80
}
```

#### Option C: Remove Public Access (Most Secure)
Comment out the pgAdmin section in Caddyfile entirely. Access via:
```bash
# SSH tunnel to access pgAdmin
ssh -L 8080:localhost:80 user@mywebclass.org

# Then visit: http://localhost:8080
```

### 4. Caddy Security

**Admin API Disabled:**
```caddy
{
    admin off  # Admin API disabled for security
}
```

If you need the admin API, bind to localhost only:
```caddy
{
    admin localhost:2019  # Only accessible from server
}
```

### 5. Watchtower Security

**Current Configuration:**
- Only updates containers with label: `com.centurylinklabs.watchtower.enable=true`
- Runs daily at 4 AM
- Automatically cleans up old images

**To exclude a container from updates:**
```yaml
services:
  myapp:
    labels:
      - "com.centurylinklabs.watchtower.enable=false"
```

### 6. DNS Security

**Required DNS Records:**

```
Type: A
Name: @
Value: 45.55.209.47
TTL: 600

Type: A
Name: www
Value: 45.55.209.47
TTL: 600

Type: A
Name: *
Value: 45.55.209.47
TTL: 600

Type: A
Name: db
Value: 45.55.209.47
TTL: 600
```

**Why wildcard (*):**
- Allows any subdomain: student1.mywebclass.org, api.mywebclass.org, etc.
- Caddy handles routing based on Caddyfile configuration
- SSL certificates issued automatically per subdomain

**Security Note:**
- Anyone can point a subdomain to your server
- Caddy only serves configured domains in Caddyfile
- Unknown subdomains get no response (404)

### 7. Network Isolation

**Two Networks:**

1. **`web` network:** 
   - External connectivity
   - Caddy reverse proxy
   - Public-facing services

2. **`internal` network:**
   - No external connectivity (internal: true)
   - PostgreSQL
   - Backend services
   - Projects needing database access

**Why this matters:**
- Database is never directly accessible from internet
- Even if someone compromises a container, they can't expose the database
- Services explicitly choose which networks to join

### 8. File Permissions

**Docker volumes are created as root:**
```bash
# Check volume permissions
sudo ls -la /var/lib/docker/volumes/

# Caddy data, config, logs owned by root
# This is normal and secure
```

**Don't modify these unless you know what you're doing.**

### 9. Regular Security Maintenance

**Monthly Tasks:**
1. Review pgAdmin access logs
2. Check for failed login attempts
3. Rotate passwords (every 90 days)
4. Update Docker images: `docker compose pull && docker compose up -d`

**Monitor logs:**
```bash
# Check Caddy access logs
docker exec caddy tail -f /var/log/caddy/mywebclass.log

# Check for auth failures
docker compose logs pgadmin | grep -i "failed\|error"

# Check PostgreSQL logs
docker compose logs postgres | grep -i "fatal\|error"
```

### 10. Backup Security

**Critical data to backup:**
- PostgreSQL data: `postgres_data` volume
- Caddy SSL certificates: `caddy_data` volume
- Your `.env` file (store securely, not in git!)

```bash
# Backup PostgreSQL
docker exec postgres pg_dump -U dbadmin production > backup.sql

# Backup volumes
sudo tar -czf backup.tar.gz /var/lib/docker/volumes/postgres_data
```

**Store backups encrypted:**
```bash
# Encrypt with GPG
gpg -c backup.sql

# Or use openssl
openssl enc -aes-256-cbc -salt -in backup.sql -out backup.sql.enc
```

## Security Checklist

Before going to production:

- [ ] Changed all default passwords in `.env`
- [ ] `.env` is NOT committed to git
- [ ] pgAdmin has basic auth or IP restriction enabled
- [ ] PostgreSQL port is NOT exposed to host
- [ ] DNS records properly configured
- [ ] SSL certificates working (check with: `curl -I https://www.mywebclass.org`)
- [ ] Firewall (UFW) enabled with only ports 22, 80, 443 open
- [ ] Fail2Ban installed and monitoring SSH
- [ ] Regular backups configured
- [ ] Monitoring/alerting set up

## Getting Help

If you discover a security issue:
1. Do NOT post it publicly
2. Email: security@mywebclass.org
3. Document what you found
4. Wait for response before disclosing
