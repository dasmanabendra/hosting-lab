#!/usr/bin/env bash
# Get a free Let's Encrypt certificate and switch nginx over to HTTPS.
# Run ON the VM, after a domain's DNS A record points at this server's IP.
#
# Usage: ./enable-https.sh todo.example.com
set -euo pipefail

DOMAIN="${1:?Usage: ./enable-https.sh <your-domain>}"

echo "==> Installing certbot"
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

echo "==> Pointing nginx at $DOMAIN"
sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/todo-app
sudo nginx -t
sudo systemctl reload nginx

echo "==> Requesting a certificate"
# certbot proves you control the domain by answering a challenge over
# port 80, then rewrites the nginx config to serve HTTPS on 443.
sudo certbot --nginx -d "$DOMAIN" --agree-tos --redirect

echo "==> Checking automatic renewal"
# Certificates expire every 90 days; certbot installs a timer to renew them.
sudo certbot renew --dry-run

echo
echo "Done. https://$DOMAIN should now be live."
