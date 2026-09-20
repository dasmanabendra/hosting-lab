# Learning Hosting

Hands-on path through deploying a web app for real — a small **todo list**,
hosted four different ways, each stage removing (or adding back) one layer
of "someone else handles this for you."

This repo is written to be re-readable. If you're coming back to it after
months away, read this file top to bottom, then the stage READMEs in order.
Everything you need to reconstruct both the theory and the implementation
is here — no outside notes required.

---

## The one-sentence version

Hosting is the business of keeping a computer running your code somewhere
the public can reach it — and the only real question is **how much of that
computer's care and feeding you do yourself**.

Every hosting product on earth sits somewhere on that spectrum. This
project walks the whole spectrum with one unchanging app, so the *only*
variable is the hosting model.

---

## Glossary

Terms used throughout, in plain language. Skim now, refer back later.

| Term | What it actually means |
|---|---|
| **Server** | A computer that stays on, waiting for requests from other computers. Not special hardware — your laptop can be one. |
| **Client** | The thing making the request. Usually a web browser. |
| **Request / response** | The whole web in two words: a browser asks for a URL, a server sends something back. |
| **Static hosting** | The server only hands over files as-is (HTML, CSS, images). It never runs your code. Cheap, fast, and unable to remember anything. |
| **Backend** | Code that runs *on the server* when a request comes in. It can read a database, make decisions, and build a different response per visitor. |
| **Frontend** | Code that runs in the visitor's browser. JavaScript, styling, the visible page. |
| **Database** | Where a backend keeps data so it survives after the request ends. Ours is SQLite — a database that's just a single file on disk. |
| **Stateful / stateless** | Stateful means the app remembers things between requests (needs a real disk or database). Stateless means every request starts from a blank slate. This distinction destroys stage 3 and is the single most important idea in this project. |
| **Persistent disk** | Storage that survives restarts. A VM has one; a Cloud Run container does not. |
| **Container** | A frozen, complete snapshot of "my code plus everything it needs to run" (OS libraries, Python, dependencies). Runs identically anywhere. Built from a `Dockerfile`. |
| **Image / registry** | The image is the frozen snapshot itself; a registry is where images are stored so a cloud can download and run them. |
| **Port** | A numbered door on a computer. Web traffic uses 80 (HTTP) and 443 (HTTPS) by convention; our app listens on 8000 internally. |
| **localhost / 127.0.0.1** | "This same computer." A program listening only on 127.0.0.1 cannot be reached from the internet — deliberately. |
| **Reverse proxy** | A program (nginx here) that sits in front of your app, accepts public traffic, and forwards it inward. It handles HTTPS, and lets your app stay safely on localhost. |
| **TLS / HTTPS / certificate** | TLS is the encryption behind HTTPS. A certificate is a file proving you control the domain; browsers refuse to show the padlock without one. Let's Encrypt issues them free. |
| **DNS** | The phone book converting a name (`todo.example.com`) into a server's IP address. You edit it at whoever sells you the domain. |
| **Domain / IP address** | The IP is the numeric address of a machine; the domain is the human-friendly name pointing at it. |
| **systemd** | Linux's process babysitter. It starts your app on boot and restarts it if it crashes. Managed platforms do this invisibly; on a VM, you configure it. |
| **Scale to zero** | The platform shuts your app down entirely when nobody's using it, and starts it again on the next request. Saves money, causes **cold starts**. |
| **Cold start** | The delay while a stopped app boots to serve the first request after idle time. |
| **CI/CD** | Automation that builds/deploys your code when you push it. Ours is the GitHub Actions workflow that publishes stage 1. |
| **PaaS / IaaS** | PaaS (Streamlit, Cloud Run) = you bring code, they run it. IaaS (Oracle VM) = they hand you a bare computer and wish you luck. |

---

## The four hosting models, compared

Same todo list, four hosts. What a *visitor* would actually notice:

| | 1. GitHub Pages | 2. Streamlit Cloud | 3. Cloud Run | 4. Oracle VM |
|---|---|---|---|---|
| **Who sees your todos** | Only you, only in that browser | Everyone who visits — one shared list, no accounts | Everyone who visits — in theory | Everyone who visits — reliably |
| **Survives a reload?** | Yes, unless you clear browser data | Usually, not guaranteed | **Often not** — the lesson | Yes, always |
| **Survives across devices?** | No — your phone sees an empty list | Yes | Yes, in theory | Yes |
| **Speed** | Instant, no network round-trip | Slight lag; 10–30s wake-up if idle | Fast once warm; cold start after idle | Always warm, consistent |
| **When idle a while** | Nothing — there's no "app" | Sleeps, wakes slowly | Scales to zero | Keeps running |
| **URL / HTTPS** | `*.github.io`, automatic | `*.streamlit.app`, automatic | `*.run.app`, automatic | Your own domain; **you** set up HTTPS |
| **If it breaks at 3am** | Can't — static files | Streamlit's problem | Google's problem | **Your problem** |
| **If it goes viral** | Fine | Fine, just slow | Scales up; possible small bill | May fall over — one fixed machine |
| **What you configure** | Nothing | A file path | A Dockerfile | OS, web server, TLS, firewall, DNS, service manager |

### The two moments that teach the most

1. **Stage 1 → 2:** your private todo list becomes a *public shared* one, with
   zero code written to "make it shared." That's just what having a backend
   does. Suddenly the app has users who aren't you.
2. **Stage 3:** you add a todo, come back later, and it's **gone** — because
   Cloud Run threw away the container holding your database. That's not a
   bug; it's the bargain stateless hosting makes. Experiencing it beats
   reading about it.

---

## Why this order (simple → complex)

Deliberate choice, and the opposite of how sysadmin courses usually teach.

The classic approach is manual-first: build everything by hand so you
appreciate what automation does for you. That works if you already
understand servers and processes. Starting from zero, it front-loads a
wall of unfamiliar friction (SSH, Linux config files, firewall rules)
before you've had a single win.

So this goes the other way: get something live fast on the most managed
platform, build vocabulary and confidence, then peel away one layer of
automation at a time. By stage 4 every manual step has context — you're
not learning what nginx is, you're learning *which thing Cloud Run was
secretly doing for you*.

---

## Why these specific platforms (the free-tier landscape)

Options considered, and why these four won:

| Option | Verdict |
|---|---|
| **GitHub Pages** | **Chosen.** Free forever, effectively unbreakable, HTTPS included. Perfect for demonstrating static hosting's ceiling. |
| **Streamlit Community Cloud** | **Chosen.** The easiest real-backend deploy that exists — connect a repo, click. Free tier requires the repo be **public**. |
| **Google Cloud Run** | **Chosen.** Permanent monthly free quota (~2M requests), container-native, and its statelessness teaches the key lesson. Usage-based, so a huge traffic spike could bill you. |
| **Oracle Cloud Free Tier** | **Chosen.** Genuinely permanent free VMs (ARM Ampere, or AMD micros) — a real machine, full root access, at zero cost. Free ARM capacity is often exhausted in popular regions; AMD micro is the fallback. |
| AWS Free Tier | Rejected — free for only 12 months, then it bills. |
| Render | Rejected — free tier sleeps aggressively and its free Postgres expires after 90 days. |
| Railway | Rejected — trial credit, not a perpetual free tier. |
| Vercel / Netlify / Cloudflare Workers | Rejected *for this app* — excellent and free, but serverless functions have no persistent disk, so our SQLite file can't live there. Great for static sites or apps using a hosted database. |
| Cloudflare Tunnel | Not used, worth knowing: exposes an app running on your own laptop to the public internet, free, no port forwarding. Fastest possible "it's live" demo. |
| PythonAnywhere | Not used — free tier fine for small Python apps, but limited CPU and no custom domain. |

**On domains:** a real domain costs roughly $10–15/year — the one genuinely
unavoidable cost if you want your own name. Every stage here works on the
platform's free subdomain instead; only stage 4's HTTPS setup really wants
a domain of your own.

---

## Why the app has three versions

Stages 0, 3, and 4 run **identical** FastAPI + SQLite code — that's the
point, since it isolates hosting as the only variable. But stages 1 and 2
physically can't run it:

- **GitHub Pages** runs no backend at all, so stage 1 is rewritten as plain
  HTML/JavaScript storing todos in the browser.
- **Streamlit Cloud** only hosts apps written in the Streamlit framework, so
  stage 2 is rewritten using it.

Those rewrites aren't detours — each platform's constraints *are* the lesson.

---

## Stages

| # | Stage | What hosts it | What it teaches |
|---|-------|----------------|------------------|
| 00 | [Local app](00-local-app/) | Your machine | The app itself: FastAPI + SQLite, run with `uvicorn` |
| 01 | [GitHub Pages](01-github-pages/) | GitHub (static) | Static hosting's ceiling: no backend, no shared state |
| 02 | [Streamlit Community Cloud](02-streamlit/) | Streamlit's cloud | A real Python backend, zero infrastructure decisions |
| 03 | [Google Cloud Run](03-google-cloud-run/) | Google Cloud | Containers, autoscaling, and why stateless hosting breaks SQLite |
| 04 | [Oracle Cloud VM](04-oracle-vps/) | Oracle Cloud | Everything Cloud Run automated, done by hand |

---

## Status

| Stage | Built | Tested locally | Deployed |
|---|---|---|---|
| 00 Local app | yes | yes — add/toggle/delete all work | n/a |
| 01 GitHub Pages | yes | yes | **yes — [live](https://dasmanabendra.github.io/hosting-lab/)** |
| 02 Streamlit | yes | yes | no |
| 03 Cloud Run | yes | not yet — Docker engine wouldn't start | no |
| 04 Oracle VM | yes | scripts syntax-checked only | no |

**Repo:** https://github.com/dasmanabendra/hosting-lab (public — required by
Streamlit's free tier).

### Next steps

1. **Deploy stage 2** — sign in to Streamlit Community Cloud with GitHub,
   point it at `02-streamlit/app.py`.
2. **Start Docker Desktop** (installed, but its engine wasn't running —
   likely a first-run dialog), then `docker build` stage 3 locally.
3. **Deploy stage 3** — Google Cloud account, then `gcloud run deploy`.
   Then wait for scale-to-zero and watch the todos vanish.
4. **Deploy stage 4** — Oracle account, provision an Always Free VM, run
   the three scripts in `04-oracle-vps/`.

---

## Ground rule: no secrets in this repo

It's public, so anything committed is permanently exposed. Credentials
(SSH keys, cloud service accounts, API tokens) stay in `.gitignore`'d local
files, GitHub Actions secrets, or the cloud provider's own console — never
in tracked files. The `.gitignore` guards the common filename patterns, but
the real protection is not pasting secrets anywhere near the repo.
