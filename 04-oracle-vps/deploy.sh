#!/usr/bin/env bash
# Deploy the latest code. Run ON the VM after pushing changes to GitHub.
set -euo pipefail

cd "$HOME/hosting"

echo "==> Pulling latest code"
git pull

echo "==> Updating dependencies"
cd 04-oracle-vps
.venv/bin/pip install -r requirements.txt

echo "==> Restarting the app"
sudo systemctl restart todo-app
sleep 2
sudo systemctl status todo-app --no-pager

echo
echo "Deployed. Note what just happened: a few seconds of downtime while"
echo "the process restarted. Cloud Run avoided that by starting the new"
echo "version before retiring the old one."
