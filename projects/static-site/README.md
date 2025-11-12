# Static Site Project

Simple static website served with Nginx.

## Structure

```
static-site/
├── docker-compose.yml
└── html/
    └── index.html
```

## Deployment

1. **Make sure infrastructure is running:**
   ```bash
   cd ~/mywebclass_hosting/infrastructure
   docker compose ps
   ```

2. **Start this project:**
   ```bash
   cd ~/mywebclass_hosting/projects/static-site
   docker compose up -d
   ```

3. **View your site:**
   - Visit https://www.mywebclass.org

## Making Changes

1. Edit files in the `html/` directory
2. Restart the container to see changes:
   ```bash
   docker compose restart
   ```

## Stopping

```bash
docker compose down
```

## Notes

- This container connects to the `web` network created by infrastructure
- Caddy routes traffic based on the Caddyfile configuration
- All HTML, CSS, and JavaScript goes in the `html/` directory
