# Deploy Solar E-Commerce on DigitalOcean Droplet

**Droplet:** Ubuntu 24.04 · 512MB RAM · IP: `138.197.11.80`

---

## Step 1 — SSH into Your Droplet

```bash
ssh root@138.197.11.80
```

---

## Step 2 — Create Swap Space (Required for 512MB RAM)

Building Next.js and Docker images needs more than 512MB. Add 2GB swap:

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

Verify:

```bash
free -h
```

---

## Step 3 — Install Docker & Docker Compose

```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y ca-certificates curl gnupg git

# Add Docker GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add Docker repo
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify
docker --version
docker compose version
```

---

## Step 4 — Configure Firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

---

## Step 5 — Clone Your Repository

```bash
cd /opt
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git solar
cd /opt/solar
```

> Replace with your actual GitHub repo URL.

---

## Step 6 — Create the `.env` File

```bash
cp .env.example .env
nano .env
```

Edit the `.env` file with your production values:

```env
# Generate a real secret key (run this and paste the output):
#   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
DJANGO_SECRET_KEY=paste-your-generated-secret-key-here

DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=138.197.11.80,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://138.197.11.80
CORS_ALLOWED_ORIGINS=http://138.197.11.80

SQLITE_PATH=/app/data/db.sqlite3

GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=120

DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_COOKIES=False
DJANGO_SECURE_HSTS_SECONDS=0

NEXT_PUBLIC_API_BASE_URL=http://138.197.11.80
```

Save: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## Step 7 — Build & Start Containers

```bash
cd /opt/solar
docker compose up -d --build
```

This will:
1. Build the Django backend image (installs Python deps, copies code)
2. Build the Next.js frontend image (npm install, next build with standalone output)
3. Pull and start Nginx as reverse proxy

> **First build takes 5-10 minutes** on a small droplet. Subsequent builds are faster due to Docker layer caching.

Monitor the build progress:

```bash
docker compose logs -f
```

Press `Ctrl+C` to stop following logs.

---

## Step 8 — Verify Everything is Running

```bash
docker compose ps
```

You should see 3 containers running: `backend`, `frontend`, `nginx`.

Test the services:

```bash
# Backend health
curl http://localhost:8000/

# Frontend through Nginx
curl -I http://localhost/

# API through Nginx
curl http://localhost/api/products/
```

---

## Step 9 — Create Django Superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

Enter your admin email, username, and password when prompted.

Access admin at: `http://138.197.11.80/admin/`

---

## Step 10 — Visit Your Live Site

Open in browser:
- **Frontend:** http://138.197.11.80
- **Admin Panel:** http://138.197.11.80/admin/
- **API Root:** http://138.197.11.80/api/products/

---

## Common Operations

### View logs

```bash
# All containers
docker compose logs -f

# Specific container
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
```

### Restart services

```bash
docker compose restart
```

### Pull latest code & redeploy

```bash
cd /opt/solar
git pull origin main
docker compose up -d --build
```

### Stop everything

```bash
docker compose down
```

### Stop and remove all data (database, static files)

```bash
docker compose down -v
```

### Django shell

```bash
docker compose exec backend python manage.py shell
```

### Run migrations manually

```bash
docker compose exec backend python manage.py migrate
```

---

## Troubleshooting

### "Cannot connect to the Docker daemon"
```bash
systemctl start docker
systemctl enable docker
```

### Build fails with out-of-memory
Make sure swap is enabled (Step 2). You can also build one at a time:
```bash
docker compose build backend
docker compose build frontend
docker compose up -d
```

### Frontend shows API errors
- Check `NEXT_PUBLIC_API_BASE_URL` in `.env` — must be `http://138.197.11.80` (no trailing slash, no port)
- This value is baked into the frontend at build time. If you change it, rebuild:
  ```bash
  docker compose up -d --build frontend
  ```

### Backend 400 Bad Request
- Check `DJANGO_ALLOWED_HOSTS` includes `138.197.11.80`
- Check `CSRF_TRUSTED_ORIGINS` includes `http://138.197.11.80`

### Check container resource usage
```bash
docker stats
```

### View disk usage
```bash
df -h
docker system df
```

### Clean up unused Docker images (free disk space)
```bash
docker system prune -f
```

---

## Optional: Add a Domain Name + SSL

Once you have a domain pointing to `138.197.11.80`:

1. Update DNS A record for your domain → `138.197.11.80`
2. Wait for DNS propagation (5-30 minutes)
3. Update `.env`:

```env
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,138.197.11.80
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
NEXT_PUBLIC_API_BASE_URL=https://yourdomain.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_COOKIES=True
DJANGO_SECURE_HSTS_SECONDS=31536000
```

4. Install Certbot and get SSL certificate:

```bash
apt install -y certbot
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
```

5. Switch nginx config to SSL version in `docker-compose.yml` and rebuild.
