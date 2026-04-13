#!/usr/bin/env bash
# One-time VPS setup script for the SmartSearch Django backend.
# Run as a non-root user with sudo privileges.
# Usage: bash deploy/setup.sh

set -euo pipefail

REPO_DIR="/var/www/smartsearch"
BACKEND_DIR="$REPO_DIR/backend"
VENV_DIR="$REPO_DIR/venv"
DOMAIN="SmartSearchapi.culturemind.org"

echo "=== Installing system packages ==="
sudo apt-get update -q
sudo apt-get install -y python3 python3-pip python3-venv \
    postgresql postgresql-contrib \
    redis-server nginx certbot python3-certbot-nginx

echo "=== Creating app directory ==="
sudo mkdir -p "$REPO_DIR"
sudo chown "$USER":"$USER" "$REPO_DIR"

echo "=== Cloning / pulling repo ==="
# Replace with your actual git remote:
# git clone https://github.com/your-user/smartsearch.git "$REPO_DIR"
# Or if already cloned:
# git -C "$REPO_DIR" pull

echo "=== Creating Python virtual environment ==="
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "=== Installing Python dependencies ==="
pip install --upgrade pip
pip install -r "$BACKEND_DIR/requirements.txt"

echo "=== Copying production .env ==="
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cp "$BACKEND_DIR/.env.production" "$BACKEND_DIR/.env"
    echo ">>> EDIT $BACKEND_DIR/.env with real values before continuing! <<<"
    read -p "Press Enter after editing .env to continue..."
fi

echo "=== Django: migrate + collectstatic ==="
cd "$BACKEND_DIR"
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "=== Installing systemd service ==="
sudo cp deploy/smartsearch.service /etc/systemd/system/smartsearch.service
sudo systemctl daemon-reload
sudo systemctl enable smartsearch
sudo systemctl start  smartsearch

echo "=== Installing nginx config ==="
sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartsearch-api
sudo ln -sf /etc/nginx/sites-available/smartsearch-api \
            /etc/nginx/sites-enabled/smartsearch-api
sudo nginx -t
sudo systemctl reload nginx

echo "=== Obtaining SSL certificate ==="
sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
    -m "admin@culturemind.org" --redirect

echo "=== Done! API is live at https://$DOMAIN ==="
