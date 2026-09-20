#!/usr/bin/env bash
# One-time setup, run ON the Oracle VM after SSHing in.
# Assumes Ubuntu and that this repo is cloned at ~/hosting.
set -euo pipefail

APP_DIR="$HOME/hosting/04-oracle-vps"

echo "==> Installing system packages"
sudo apt-get update
sudo apt-get install -y python3-venv nginx

echo "==> Creating Python environment"
cd "$APP_DIR"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo "==> Installing the systemd service"
sudo cp todo-app.service /etc/systemd/system/todo-app.service
sudo systemctl daemon-reload
sudo systemctl enable --now todo-app
sudo systemctl status todo-app --no-pager

echo "==> Configuring nginx as a reverse proxy"
sudo cp nginx-todo-app.conf /etc/nginx/sites-available/todo-app
sudo ln -sf /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/todo-app
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

echo "==> Opening the firewall"
# Oracle images ship with restrictive iptables rules in addition to the
# cloud-side security list, which must be opened in the Oracle console too.
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save || sudo apt-get install -y iptables-persistent

echo
echo "Done. The app should be reachable at http://<your-server-ip>/"
echo "Next: point a domain at this IP, then run ./enable-https.sh <your-domain>"
