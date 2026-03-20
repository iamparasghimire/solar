# DigitalOcean Docker Deployment Guide (Full-Stack)

This guide covers the complete deployment of both the **Django backend** and **Next.js frontend** with **Nginx** as a reverse proxy, all running in Docker containers on a single DigitalOcean Droplet.

## GitHub Repos

| Repo | URL |
|------|-----|
| Backend (Django + docker-compose + nginx) | `https://github.com/iamparasghimire/solar_backend.git` |
| Frontend (Next.js) | `https://github.com/iamparasghimire/solar_frontend.git` |

## What gets deployed

| Container | Role | Internal port |
|-----------|------|---------------|
| `backend` | Django + Gunicorn API | 8000 |
| `frontend` | Next.js standalone server | 3000 |
| `nginx` | Reverse proxy (public port 80) | 80 |

## Server directory layout

```
/opt/solar/                         ← cloned from solar_backend repo
├── Dockerfile                      ← Django Dockerfile
├── docker-compose.yml
├── .env
├── nginx/
├── manage.py, apps/, core/...      ← Django app code
└── solar_ecommerce_frontend/       ← cloned from solar_frontend repo
```

How traffic flows:
- Browser hits `http://YOUR_SERVER_IP/` → Nginx → Next.js frontend
- Browser hits `http://YOUR_SERVER_IP/api/...` → Nginx → Django backend
- Browser hits `http://YOUR_SERVER_IP/admin/` → Nginx → Django backend
- Static/media files are served directly by Nginx

## 1. What You Need Before Starting

You need these things first:
- A DigitalOcean account
- A GitHub account
- Your project already pushed to GitHub
- A DigitalOcean Droplet
- Your Droplet public IP address

If your code is not on GitHub yet, push it first from your local machine.

## 2. Create A DigitalOcean Droplet

1. Log in to DigitalOcean.
2. Click `Create`.
3. Click `Droplets`.
4. Choose these options:
    - Image: `Ubuntu 24.04 LTS`
    - Plan: `Basic`
    - Size: at least `2 GB RAM`
    - Authentication: use `SSH Key` if possible, password if you must
5. Create the Droplet.
6. Copy the public IP address.

Example Droplet IP:

```text
159.89.10.20
```

## 3. Connect To The Server

Open a terminal on your own computer and connect to the server.

If you use root:

```bash
ssh root@YOUR_SERVER_IP
```

Example:

```bash
ssh root@159.89.10.20
```

If this is your first time connecting, type `yes` when asked.

## 4. Update The Server

After logging in to the server, run:

```bash
apt update && apt upgrade -y
```

This updates the system packages.

## 5. Install Docker

Run these commands on the server:

```bash
curl -fsSL https://get.docker.com | sh
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL https://github.com/docker/compose/releases/download/v2.36.0/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker --version
docker compose version
```

If both version commands show output, Docker is installed correctly.

## 6. Install Git

Run:

```bash
apt install -y git
```

## 7. Download Both Repos On The Server

Move to a good server folder:

```bash
cd /opt
```

Clone the **backend repo** (contains docker-compose + nginx + Django app code):

```bash
git clone https://github.com/iamparasghimire/solar_backend.git solar
cd /opt/solar
```

Clone the **frontend repo** inside it (so docker-compose can find it at the expected path):

```bash
git clone https://github.com/iamparasghimire/solar_frontend.git solar_ecommerce_frontend
```

After this, your project layout should be:

```
/opt/solar/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── nginx/
├── manage.py
├── apps/
├── core/
└── solar_ecommerce_frontend/
```

## 8. Check That The Needed Files Exist

Run:

```bash
ls
```

You should see at least these important files and folders:

```text
docker-compose.yml
.env.example
solar_ecommerce/
```

## 9. Create The Real Environment File

Your project uses `.env` for real settings.

Create it from the example:

```bash
cp .env.example .env
```

Now open it:

```bash
nano .env
```

## 10. Edit The .env File Properly

You must change these values.

Example safe production-style file for a server IP only setup:

```env
DJANGO_SECRET_KEY=put-a-long-random-secret-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOUR_SERVER_IP
CSRF_TRUSTED_ORIGINS=
CORS_ALLOWED_ORIGINS=http://YOUR_SERVER_IP

SQLITE_PATH=/app/data/db.sqlite3

GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=120

DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_COOKIES=False
DJANGO_SECURE_HSTS_SECONDS=0

USE_POSTGRES=False
DB_NAME=solar_db
DB_USER=solar_user
DB_PASSWORD=change-me-strong-password
DB_HOST=
DB_PORT=5432

NEXT_PUBLIC_API_BASE_URL=http://YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with your actual server IP.

Example:

```env
DJANGO_ALLOWED_HOSTS=159.89.10.20
```

Generate a proper Django secret key from your own computer or on the server:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copy that output and paste it into `DJANGO_SECRET_KEY`.

Why SSL settings are `False` here:
- Your current setup does not yet include Nginx + HTTPS
- If you set them to `True` now, your app will redirect to HTTPS and appear broken
- Later, when HTTPS is added, these can be changed to secure values

Save and exit nano:
- Press `Ctrl + O`
- Press `Enter`
- Press `Ctrl + X`

## 11. Build And Start The Docker Container

Run this inside `/opt/solar`:

```bash
docker compose up -d --build
```

What this does:
- Builds the Docker image
- Creates the container
- Starts Django
- Runs migrations
- Runs collectstatic
- Starts Gunicorn

## 12. Check If The Container Is Running

Run:

```bash
docker compose ps
```

You want to see something like:

```text
NAME               SERVICE    STATUS
solar-backend-1    backend    Up
solar-frontend-1   frontend   Up
solar-nginx-1      nginx      Up    0.0.0.0:80->80/tcp
```

All three containers should show `Up`.

## 13. Check Logs If Something Looks Wrong

Run:

```bash
docker compose logs -f
```

Good signs in the backend logs:
- `Running migrations`
- `Collecting static files`
- `Starting Gunicorn`
- `Listening at: http://0.0.0.0:8000`

Good signs in the frontend logs:
- `Ready in ...`
- `Listening on port 3000`

To stop log streaming, press:

```text
Ctrl + C
```

This does not stop the container.

## 14. Open The App In Your Browser

Use your server IP in the browser.

Examples:

```text
http://YOUR_SERVER_IP/         → Next.js frontend (the store)
http://YOUR_SERVER_IP/admin/   → Django admin panel
http://YOUR_SERVER_IP/api/docs/ → API documentation
```

What you should expect:
- `/` shows the EcoPlanet Solar storefront
- `/admin/` shows the Django admin login page
- `/api/docs/` shows the Swagger API documentation

## 15. Create A Django Admin User

Run:

```bash
docker compose exec backend python manage.py createsuperuser
```

You will be asked for:
- username
- email
- password

After that, open:

```text
http://YOUR_SERVER_IP/admin/
```

And log in with the superuser you created.

## 16. Important Daily Commands

Start container:

```bash
docker compose up -d
```

Stop container:

```bash
docker compose down
```

Restart container:

```bash
docker compose restart
```

See running services:

```bash
docker compose ps
```

Watch logs:

```bash
docker compose logs -f             # all containers
docker compose logs -f backend     # backend only
docker compose logs -f frontend    # frontend only
docker compose logs -f nginx       # nginx only
```

Run Django command inside container:

```bash
docker compose exec backend python manage.py shell
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## 17. How To Update The Project Later

When you push new code to GitHub, update the server like this:

```bash
cd /opt/solar
git pull
docker compose up -d --build
docker compose ps
docker compose logs --tail=50 web
```

## 18. How To Reboot The Server And Start Again

If your server restarts, log in again and run:

```bash
cd /opt/solar
docker compose up -d
```

## 19. Common Problems And What They Mean

### Problem: Browser shows nothing

Check:

```bash
docker compose ps
docker compose logs -f web
```

If container is not `Up`, read the logs.

### Problem: App redirects to HTTPS and does not open

Your `.env` probably has:

```env
DJANGO_SECURE_SSL_REDIRECT=True
```

Change it to:

```env
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_COOKIES=False
DJANGO_SECURE_HSTS_SECONDS=0
```

Then restart:

```bash
docker compose up -d --build
```

### Problem: Port 80 is not opening

Run:

```bash
docker compose ps
```

Also check DigitalOcean firewall settings.

### Problem: Admin page does not open

Make sure you are visiting:

```text
http://YOUR_SERVER_IP/admin/
```

Not just `/admin` without the trailing slash.

### Problem: Git pull fails because of local changes

Ask before forcing anything. Do not use destructive git commands unless you understand them.

## 20. DigitalOcean Firewall

In DigitalOcean, allow at least:
- Port `22` for SSH
- Port `80` for HTTP

If you add HTTPS later, also allow:
- Port `443`

## 21. Your Current Deployment Flow In One Short Version

Run these on your server (first-time setup):

```bash
# 1. System setup
apt update && apt upgrade -y
apt install -y git
curl -fsSL https://get.docker.com | sh
mkdir -p /usr/local/lib/docker/cli-plugins
curl -fsSL https://github.com/docker/compose/releases/download/v2.36.0/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# 2. Clone both repos
cd /opt
git clone https://github.com/iamparasghimire/solar_backend.git solar
cd /opt/solar
git clone https://github.com/iamparasghimire/solar_frontend.git solar_ecommerce_frontend

# 3. Configure environment
cp .env.example .env
nano .env   # set DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, NEXT_PUBLIC_API_BASE_URL

# 4. Start everything
docker compose up -d --build
docker compose ps
docker compose exec backend python manage.py createsuperuser
```

Then open:

```text
http://YOUR_SERVER_IP/         → Store frontend
http://YOUR_SERVER_IP/admin/   → Django admin
http://YOUR_SERVER_IP/api/docs/ → API docs
```

## 22. CI/CD with GitHub Actions

Each repo has its own workflow that only deploys its own container:

| Repo | Workflow | What it rebuilds |
|------|----------|------------------|
| `solar_backend` | `.github/workflows/deploy.yml` | `backend` + `nginx` |
| `solar_frontend` | `.github/workflows/deploy.yml` | `frontend` only |

### Setup GitHub Secrets (do this in BOTH repos)

Go to each GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|---|---|
| `SERVER_IP` | `138.197.11.80` |
| `SSH_PRIVATE_KEY` | Contents of `~/.ssh/id_ed25519` (your private key) |

To copy your private key:

```bash
cat ~/.ssh/id_ed25519
```

Copy the full output (including `-----BEGIN...` and `-----END...` lines) and paste it as the secret value.

After this, every push to `main` in either repo will automatically test and deploy only its own container.

## 23. What To Do Next After This Works

After the full-stack is working, the next improvements should be:
1. Add a real domain name
2. Add HTTPS with Let's Encrypt (use `nginx.ssl.conf`)
3. Move from SQLite to PostgreSQL (use `docker-compose.backend.yml`)
4. Add a domain to `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`
