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

---

## Appendix: every term used on this page

| Term | Plain explanation |
|---|---|
| **VM (virtual machine)** | A complete computer that exists as software inside a bigger physical one. It behaves exactly like a real machine — own operating system, own disk, own network address. |
| **IaaS** | "Infrastructure as a Service" — they rent you a bare computer and nothing else. The opposite of the managed platforms in stages 2 and 3. |
| **Instance** | One rented VM. |
| **Ubuntu** | A popular version of Linux, the operating system on the VM. |
| **`apt` / `apt-get`** | Ubuntu's software installer, the system-wide equivalent of `pip`. |
| **SSH** | A secure way to open a terminal on a *remote* computer over the internet. How you get "inside" the VM. |
| **SSH key** | A matched pair of files — one secret, one public — proving who you are when connecting, instead of a password. The secret half must never be committed to a repo. |
| **root / `sudo`** | Administrator rights on Linux. `sudo` means "run this one command as the administrator." Needed to install software or edit system configuration. |
| **IP address** | The numeric address of a machine on the internet, e.g. `140.238.1.2`. Your VM gets one. |
| **Domain** | The human-friendly name (`todo.example.com`) that points at an IP address. Costs roughly $10–15/year. |
| **DNS** | The internet's phone book, translating domain names into IP addresses. You edit it wherever you bought the domain. |
| **A record** | The specific DNS entry mapping a name directly to an IP address. The one you create to point your domain at the VM. |
| **Registrar** | The company you buy a domain from, and where you edit its DNS. |
| **Port 80 / 443** | The standard doors for web traffic: 80 for plain HTTP, 443 for encrypted HTTPS. |
| **nginx** | A web server program that accepts public traffic. Here it acts as a reverse proxy. |
| **Reverse proxy** | A program sitting in front of your app that receives public requests and forwards them inward. It handles HTTPS and lets the app itself stay hidden on localhost. |
| **`proxy_pass`** | The nginx setting naming where to forward requests — here, the app on `127.0.0.1:8000`. |
| **`proxy_set_header`** | Passes along details about the original visitor (their real IP, whether they used HTTPS). Without these, the app would think every request came from nginx itself. |
| **`127.0.0.1` / localhost** | "This machine only." Binding the app here means the internet cannot reach it directly — the only way in is through nginx. Deliberately the opposite of stage 3's `0.0.0.0`. |
| **systemd** | Linux's process manager. It starts programs at boot, keeps them running, and restarts them if they crash. |
| **Unit file / service** | The configuration file telling systemd how to run one program — `todo-app.service` here. |
| **`Restart=always`** | The setting that brings the app straight back if it crashes. |
| **`WantedBy=multi-user.target`** | The setting that starts the app automatically when the machine boots. |
| **TLS** | The encryption behind HTTPS. "TLS terminates here" means nginx is where encrypted traffic is decrypted before being passed inward. |
| **Certificate** | A file proving you control a domain. Browsers refuse to show the padlock without one. Issued for *names*, never for bare IP addresses — which is why HTTPS needs a domain. |
| **Let's Encrypt** | A nonprofit certificate authority issuing certificates free of charge. |
| **certbot** | The tool that requests a Let's Encrypt certificate, installs it into nginx, and sets up automatic renewal. |
| **Challenge** | How certbot proves you control the domain: Let's Encrypt asks for a specific response over port 80, and only the real server can give it. |
| **Renewal** | Certificates expire every 90 days. certbot installs a timer to renew automatically; `--dry-run` tests that it will work before it matters. |
| **Firewall** | Rules deciding which network traffic is allowed in. This VM has **two** — see the next two rows. |
| **iptables** | The firewall running *on* the Linux machine itself. `setup-server.sh` configures it. |
| **Security list** | Oracle's *network-level* firewall, configured in their web console, which blocks traffic before it ever reaches the machine. Forgetting this is the classic reason a correctly configured server appears dead. |
| **Deploy** | Making a new version of your code the live one. Here: `git pull`, reinstall dependencies, restart the service. |
| **Downtime** | Time when the site doesn't respond. Restarting the app causes a few seconds of it. |
| **Zero-downtime deploy** | Starting the new version *before* stopping the old one, so visitors never see an outage. Cloud Run did this automatically; here you'd have to build it. |
| **Patching** | Installing security updates for the operating system. Nobody does this for you on a VM. |
| **Backup** | A copy of your data kept elsewhere, in case the machine or its disk is lost. Also now your job. |
