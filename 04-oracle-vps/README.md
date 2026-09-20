# Stage 4: Oracle Cloud VM

The same app again — identical code to stage 3 — but now *you* are the
hosting platform. There's no container, no autoscaler, no managed
certificate. There's a computer, and you have to do everything to it.

## What you do by hand here

Each of these was invisible in stage 3 because Google did it:

| Job | Who did it in stage 3 | Who does it here |
|---|---|---|
| Keep the app running / restart on crash | Cloud Run | **systemd** (`todo-app.service`) |
| Accept public traffic on port 443 | Cloud Run | **nginx** (`nginx-todo-app.conf`) |
| Get and renew an HTTPS certificate | Cloud Run | **certbot** (`enable-https.sh`) |
| Give the app a URL | Cloud Run | **DNS** — you point a domain at the server's IP |
| Firewall | Cloud Run | Oracle security list + `iptables` |
| Deploy a new version | `gcloud run deploy` | `deploy.sh` — git pull, restart |

## Why the app works here and broke in stage 3

The VM has a real, persistent disk that stays the same machine across
restarts. `data/todos.db` just works, exactly like it did on your laptop
in stage 0. That reliability is what you bought by giving up autoscaling
and paying for a machine that runs 24/7 whether anyone visits or not.

## The scripts

Run these **on the VM** after SSHing in, with this repo cloned to `~/hosting`:

1. `setup-server.sh` — one-time: installs Python/nginx, creates the venv,
   installs the systemd service, configures the reverse proxy, opens the
   firewall. After this, `http://<server-ip>/` serves the app.
2. `enable-https.sh <your-domain>` — after DNS points at the server:
   gets a Let's Encrypt certificate and switches nginx to HTTPS.
3. `deploy.sh` — every time you want to ship changes: pull, reinstall
   dependencies, restart the service.

## Architecture on the box

```
internet → nginx (:80/:443, TLS terminates here)
              ↓ proxy_pass
           uvicorn (127.0.0.1:8000, not publicly reachable)
              ↓
           data/todos.db (on the VM's real disk)
```

uvicorn deliberately binds to `127.0.0.1` rather than `0.0.0.0` — it should
only ever be reachable *through* nginx, never directly from the internet.

## Deploying (needs your account)

Not done yet — requires an Oracle Cloud account and a provisioned
Always Free VM. Two things worth knowing before we do it:

- Oracle asks for a credit card to verify identity. Always Free resources
  don't charge it, but the card entry is a step only you can do.
- The free ARM instances are often capacity-constrained in popular regions.
  If provisioning fails with "out of host capacity," the fallback is the
  smaller AMD micro instance, which is plenty for this app.
