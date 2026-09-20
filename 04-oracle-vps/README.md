# Stage 4: Oracle Cloud VM — you are the hosting platform

The same app again, identical code to stage 3. But now there's no
container, no autoscaler, no managed certificate. There's a computer, and
everything that happens to it is your responsibility.

---

## Theory

### What a VM actually is

Oracle rents you a **virtual machine**: a whole Linux computer, running
continuously in a datacenter, with a public IP address and full root
access. It behaves exactly like a physical machine you own — it just
happens to be a slice of a much bigger one.

Nothing is set up on it. No web server, no Python environment, no
firewall rules, no HTTPS. A fresh VM is an empty room with a network cable.

### The four jobs Cloud Run was doing for you

Each of these was invisible in stage 3 because Google handled it. Here
each one is a thing you install and configure:

| Job | Stage 3 | Stage 4 |
|---|---|---|
| Keep the app alive, restart on crash/reboot | Cloud Run | **systemd** |
| Accept public traffic, terminate HTTPS | Cloud Run | **nginx** |
| Obtain and renew a TLS certificate | Cloud Run | **certbot** / Let's Encrypt |
| Give the app a reachable name | Cloud Run | **DNS** you configure |
| Block unwanted traffic | Cloud Run | Oracle security list + **iptables** |
| Ship a new version | `gcloud run deploy` | `git pull` + restart |

### How the pieces fit together

```
internet → nginx (ports 80/443, TLS ends here)
              ↓ proxy_pass
           uvicorn (127.0.0.1:8000 — not reachable from outside)
              ↓
           data/todos.db (on the VM's real, persistent disk)
```

**Why nginx at all,** when uvicorn could listen on port 443 directly? Three
reasons: nginx handles TLS certificates far better, it can serve many sites
or apps from one machine, and it shields the app from malformed or hostile
requests. This front-door-plus-inner-door arrangement is a **reverse proxy**
and it's near-universal in real deployments.

**Why uvicorn binds to `127.0.0.1`** — the exact opposite of stage 3's
`0.0.0.0`. Here, `127.0.0.1` means the app is reachable *only from the
machine itself*, so the only way in is through nginx. If it bound to
`0.0.0.0`, anyone could hit port 8000 directly and bypass HTTPS entirely.
In stage 3 the container was already isolated, so `0.0.0.0` was safe and
necessary. Same setting, opposite correct answer, because the surrounding
architecture differs.

**What systemd does:** it's Linux's process babysitter. `Restart=always`
means if the app crashes it comes straight back; `WantedBy=multi-user.target`
means it starts automatically when the machine boots. Without this, a crash
or a reboot at 3am leaves the site down until you happen to notice. This
is the single most underappreciated thing managed platforms give you.

**How HTTPS actually works here:** certbot proves to Let's Encrypt that you
control the domain (it answers a challenge over port 80), receives a
certificate, and rewrites the nginx config to serve HTTPS on port 443.
Certificates expire every 90 days, so certbot also installs a timer to
renew automatically — which is why `certbot renew --dry-run` is worth
running once to confirm renewal will work unattended.

**Why DNS matters now:** stages 1–3 handed you a free subdomain. Here you
get an IP address like `140.238.x.x`, and turning that into a name means
creating an **A record** at your domain registrar pointing the domain at
the IP. Certificates are issued for *names*, not IPs, so HTTPS requires a
domain.

### Why persistence works again

The VM has one real disk that stays the same across restarts, so
`data/todos.db` behaves exactly as it did on your laptop in stage 0. That
reliability is precisely what you bought by giving up autoscaling and by
paying for a machine that runs 24/7 whether anyone visits or not.

---

## Implementation

Files here, and what each one is:

| File | Role |
|---|---|
| [`app/main.py`](app/main.py) | The application — identical to stage 0 and stage 3 |
| [`todo-app.service`](todo-app.service) | systemd unit: how to start the app, and to restart it forever |
| [`nginx-todo-app.conf`](nginx-todo-app.conf) | Reverse proxy config: public port 80 → internal port 8000 |
| [`setup-server.sh`](setup-server.sh) | One-time server setup |
| [`enable-https.sh`](enable-https.sh) | Gets the TLS certificate, switches nginx to HTTPS |
| [`deploy.sh`](deploy.sh) | Ship a new version: pull, reinstall, restart |

The `proxy_set_header` lines in the nginx config forward the visitor's real
IP and original protocol inward. Without them, the app would think every
request came from nginx itself over plain HTTP.

### Deploying (not done yet — needs your account)

1. **Create an Oracle Cloud account** and provision an Always Free VM
   (Ubuntu). A credit card is required for identity verification; Always
   Free resources don't charge it.
2. **Open ports 80 and 443** in the VM's security list, in the Oracle
   console. This is separate from the OS firewall — Oracle blocks traffic
   at the network level before it ever reaches the machine, and forgetting
   this step is the classic reason a correctly configured server appears
   dead.
3. **SSH in** and clone this repo to `~/hosting`.
4. **Run the scripts in order:**
   ```bash
   cd ~/hosting/04-oracle-vps
   ./setup-server.sh              # installs everything; site live on http://<ip>/
   ./enable-https.sh your.domain  # after DNS points at the IP
   ```
5. **Afterwards, to ship changes:** push to GitHub, then run `./deploy.sh`
   on the VM.

`deploy.sh` restarts the process, which means a few seconds of downtime on
every deploy. Cloud Run avoided that by starting the new version before
retiring the old one — a "zero-downtime deploy," which you'd have to build
yourself here.

---

## Gotchas expected

These scripts are **syntax-checked only** — they've never run on a real VM.
Watch for:

- **Oracle's free ARM capacity is often exhausted** in popular regions.
  "Out of host capacity" is common; the AMD micro instance is the fallback
  and is plenty for this app.
- **Two firewalls, not one.** Oracle's security list *and* the VM's own
  iptables both have to allow traffic. `setup-server.sh` handles iptables;
  the security list is a console task only you can do.
- **The systemd unit hardcodes the `ubuntu` user and `/home/ubuntu` paths.**
  If the VM image uses a different default user, edit
  `todo-app.service` before running setup.

---

## What this model gives you, and what it costs

**Gives:** total control over every layer; genuinely free forever on
Oracle's tier; no cold starts, ever; real persistent disk, so ordinary
stateful apps just work; no usage-based billing surprises.

**Costs:** you own the security patching, the uptime, the certificate
renewals, the backups, and the 3am outage. One machine means a traffic
spike can simply overwhelm it. And every convenience from stages 1–3 —
automatic HTTPS, automatic restarts, automatic scaling, deploy-on-push —
is now something you built and must maintain yourself.

That's the whole lesson of this project, arrived at the long way: managed
hosting isn't doing anything magic. It's doing *these specific jobs*, and
now you know what each one is.
