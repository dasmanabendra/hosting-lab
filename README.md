# Hosting: a zero-to-hero manual

Learn web hosting by deploying one small **todo list** four different ways —
each stage removing (or handing back) one layer of "someone else handles
this for you."

Written for someone who is **not** a software developer. No prior knowledge
is assumed: every technical term is explained where it's used, and each
chapter ends with a glossary of its own vocabulary.

Written to be re-readable. Coming back after months away, this manual alone
should reconstruct both the theory and the implementation — no outside
notes required.

---

## Contents

**Foundations**
- [Chapter 0 — How the web actually works](docs/how-the-web-works.md)
  *Start here if "server," "DNS," or "port" are unfamiliar.*
- [Before you start: the mechanics](#before-you-start-the-mechanics) — terminal, Python, git
- [Glossary](#glossary)

**The stages** — each builds on the last

| # | Stage | What hosts it | The idea it teaches |
|---|-------|----------------|------------------|
| 0 | [The local app](00-local-app/) | Your machine | What you're deploying, and why it works here |
| 1 | [GitHub Pages](01-github-pages/) | GitHub (static) | Static hosting's ceiling: no backend, no shared data |
| 2 | [Streamlit Community Cloud](02-streamlit/) | Streamlit | A real backend, zero infrastructure — and data becomes *shared* |
| 3 | [Google Cloud Run](03-google-cloud-run/) | Google | Containers, autoscaling — and why stateless hosting destroys SQLite |
| 4 | [Oracle Cloud VM](04-oracle-vps/) | Oracle | Everything the others automated, done by hand |

**Reference and synthesis**
- [The four hosting models, compared](#the-four-hosting-models-compared)
- [The tech stack, explained](#the-tech-stack-explained)
- [Chapter 5 — Choosing a host for your next project](docs/choosing-a-host.md)
- [Chapter 6 — Not getting hacked](docs/security-basics.md)
- [Chapter 7 — What this manual didn't teach you](docs/where-to-go-next.md)

---

## How to use this manual

**If you're starting from zero:** read
[chapter 0](docs/how-the-web-works.md), then
["Before you start"](#before-you-start-the-mechanics) below, then work the
stages in order. Each has a "Try it yourself" section — do those. Reading
about deployment teaches roughly as much as reading about swimming.

**If you're returning to refresh:** the
[comparison table](#the-four-hosting-models-compared) and
[chapter 5](docs/choosing-a-host.md) are the highest-value pages. Each
stage's appendix works as a standalone glossary.

**If you have a decision to make right now:** go straight to
[chapter 5](docs/choosing-a-host.md).

### What you'll be able to do at the end

- Explain what happens between typing a URL and seeing a page
- Deploy a static site, a Python app, a container, and a hand-built server
- Diagnose the common failures (502s, cold starts, vanishing data)
- Choose a hosting model for a new project and defend the choice
- Recognise which problems are worth paying someone else to solve

---

## The one-sentence version

Hosting is the business of keeping a computer running your code somewhere
the public can reach it — and the only real question is **how much of that
computer's care and feeding you do yourself**.

Every hosting product on earth sits somewhere on that spectrum. This
project walks the whole spectrum with one unchanging app, so the *only*
variable is the hosting model.

---

## Before you start: the mechanics

This project is written for someone who isn't a software developer. If the
commands in these files look like gibberish, this section is the missing
context. Nothing here is conceptually hard — it's just unfamiliar.

**The terminal** is a window where you type commands instead of clicking.
On Windows that's PowerShell; on Mac/Linux it's Terminal. When a README
shows a line in a grey box, it means "type this into that window and press
Enter." Commands run inside a *current folder*, which is why you'll often
`cd` (change directory) somewhere first.

**Python doesn't come with the libraries an app needs.** They're installed
separately, and different projects want different versions of the same
library — which would collide if everything shared one pile. So each
project gets a **virtual environment**: a private folder (here, `.venv`)
holding that project's own copy of Python and its libraries.

```powershell
# Windows (PowerShell)
python -m venv .venv                             # create it (once per project)
.venv\Scripts\pip install -r requirements.txt    # install the libraries into it
```

```bash
# Mac / Linux
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`pip` is Python's installer. `requirements.txt` is just a list of library
names and versions — the "shopping list" pip reads. Running things from
inside `.venv` rather than plain `python` is what makes them use that
private environment instead of your system-wide one.

**Commands in this manual are written for Windows**, since that's where it
was built. The only difference on Mac/Linux is the slashes and folder name:
`.venv\Scripts\` becomes `.venv/bin/`.

**To stop a running app**, press `Ctrl+C` in the terminal where it's
running. Closing the terminal window also stops it — which is the whole
problem stages 1–4 exist to solve.

**Git and GitHub are two different things.** Git records snapshots of your
files over time, on your own machine. GitHub is a website that stores a
copy of that history online so it can be shared — and, for us, so hosting
platforms can fetch the code. You'll see this vocabulary constantly:

- **repository (repo)** — one project's folder plus its whole history
- **commit** — one saved snapshot, with a message describing what changed
- **push** — upload your commits to GitHub
- **pull** — download commits from GitHub
- **clone** — make a local copy of a GitHub repo for the first time
- **branch** — a parallel line of history; ours is called `main`

**Nothing here can break your computer.** The worst case is an app that
won't start, which you fix by reading the error and trying again.

---

## Glossary

Terms used throughout, in plain language. Skim now, refer back later.

### Hosting and web concepts

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
| **CDN** | A network of servers worldwide holding copies of your files, so visitors are served from one near them. GitHub Pages does this automatically. |
| **VM (virtual machine)** | A whole computer that exists as software inside a bigger physical machine. Behaves exactly like a real one; you rent it by the hour (or free, on Oracle's tier). |

### Tools and workflow

| Term | What it actually means |
|---|---|
| **Terminal / command line** | The window where you type commands. PowerShell on Windows. |
| **Virtual environment (`.venv`)** | A per-project private copy of Python and its libraries, so projects don't interfere with each other. |
| **pip** | Python's library installer. Reads `requirements.txt`. |
| **Dependency / library / package** | Code someone else wrote that your app uses rather than reinventing. FastAPI and Streamlit are dependencies. |
| **Repo, commit, push, pull, clone, branch** | Git vocabulary — see "Before you start" above. |
| **SSH** | A way to get a terminal on a *remote* computer over the internet, securely. How you reach the Oracle VM in stage 4. |
| **SSH key** | A pair of files — one secret, one public — that proves who you are when connecting, instead of a password. The secret half must never be committed. |
| **root / sudo** | Administrator rights on a Linux machine. `sudo` means "run this command as the administrator." |
| **Environment variable** | A named value passed to a program from outside it, rather than written into the code. Cloud Run uses one (`PORT`) to tell the container which port to listen on. |
| **Wheel** | A pre-built, ready-to-install package. When one doesn't exist for your Python version, pip tries to build from source instead — which is slower and often fails. |

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

## The tech stack, explained

A **tech stack** is just the list of technologies stacked on top of each
other to make one working app. The word is literal: each layer sits on the
one below and depends on it.

### The layers

Reading downward, from the code you write to the machine it lands on:

| | Layer | Job | Ours |
|---|---|---|---|
| ↑ *the app* | **Language** | What the code is written in | Python |
| | **Web framework** | Turns an incoming request into your code, and your code's output into a web page | FastAPI |
| | **Application server** | The program that actually listens on a network port and stays running | uvicorn |
| | **Database** | Stores data so it survives after a request finishes | SQLite |
| ↓ *the hosting* | **Reverse proxy** *(stage 4 only)* | Faces the public internet, handles HTTPS, forwards inward | nginx |
| | **Process manager** *(stage 4 only)* | Keeps the app running, restarts it on crash or reboot | systemd |
| | **Runtime environment** | Where all of the above physically executes | Your laptop → a container → a VM |

**The split in the middle is the whole point of this project.** The top four
rows are *your application* — they stay essentially identical from stage 0
to stage 4. The bottom three are *hosting*, and they're what each platform
argues about:

- **Stage 1** has none of them, because there's no app to run.
- **Stage 2** supplies all three invisibly; you never learn what they are.
- **Stage 3** lets you define the runtime environment (in a Dockerfile) while
  still handling the proxy and process management for you.
- **Stage 4** hands you all three and walks away.

### The confusing one: FastAPI vs uvicorn

Beginners trip on this constantly, so: **FastAPI is a library, not a
program.** It can't listen on a port or talk to the network. It only
describes *what should happen* when a request for `/todos` arrives.

uvicorn is the actual running program. It opens the port, waits for
requests, and hands each one to FastAPI to decide the answer. That's why
you type `uvicorn app.main:app` and never `python main.py` — uvicorn is
the thing being run, and FastAPI is what it consults.

The technical name for the agreement between them is **ASGI**, a standard
saying "here's how a server hands a web request to Python code." Because
both sides follow it, you could swap uvicorn for a different ASGI server
without touching the app.

### Why these specific choices

**Python** — readable, hugely popular, and the language both FastAPI and
Streamlit use, so the same language covers stages 0–4.

**FastAPI** over Django or Flask — Django is a large framework that brings
an admin panel, its own database layer, and strong opinions; excellent for
big applications, far too much machinery for a todo list where hosting is
the real subject. Flask is closer in size to FastAPI and would have worked
fine. FastAPI wins here for automatic request validation and because it's
what new Python web projects most commonly start with now.

**uvicorn** — the standard ASGI server, and the one FastAPI's own docs
use. `uvicorn[standard]` in `requirements.txt` means "install it with its
recommended optional extras" (faster HTTP parsing, etc.).

**SQLite** over PostgreSQL or MySQL — those run as *separate server
programs* you must install, configure, secure, and keep running. SQLite is
a single file with no server at all, which makes it perfect for learning
and for small apps. It's also the honest choice pedagogically: because
SQLite lives on the filesystem, stage 3 breaks it in a way that makes the
stateless-hosting lesson unmissable. A managed Postgres would have quietly
worked everywhere and taught nothing.

**Plain HTML with no frontend framework** — no React, Vue, or build step.
Server-rendered HTML keeps the app small enough that nothing distracts
from the hosting mechanics. Stage 1 uses plain browser JavaScript for the
same reason.

**nginx** over Caddy (stage 4) — Caddy would actually be easier, since it
obtains HTTPS certificates automatically with near-zero configuration.
nginx is used deliberately because it's the overwhelmingly common choice
in real deployments, and because doing certificates manually with certbot
*shows you the step* Caddy would have hidden — which is the entire point
of stage 4.

### What the stack looks like at each stage

The important column is the last one: notice how much stays identical.

| Layer | 0. Local | 1. Pages | 2. Streamlit | 3. Cloud Run | 4. Oracle VM |
|---|---|---|---|---|---|
| **Language** | Python | JavaScript | Python | Python | Python |
| **Framework** | FastAPI | none | Streamlit | FastAPI | FastAPI |
| **App server** | uvicorn | none | Streamlit's own | uvicorn | uvicorn |
| **Data lives in** | SQLite file | browser `localStorage` | SQLite file | SQLite file *(and vanishes)* | SQLite file |
| **Packaged as** | nothing | static files | a repo | Docker image | nothing — runs directly |
| **Public entry point** | none | GitHub's CDN | Streamlit's servers | Google's front end | nginx you configured |
| **Kept running by** | your terminal | nothing to run | Streamlit | Cloud Run | systemd you configured |
| **HTTPS from** | none | GitHub | Streamlit | Google | certbot you ran |
| **Runs on** | your laptop | no server at all | their container | their container | your VM |

Stages 0, 3, and 4 share the top four rows *exactly*. Everything that
differs between them is in the bottom half — which is the definition of a
hosting concern rather than an application concern.

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

If one ever does leak: **revoke and reissue it immediately.** Deleting the
commit does not help — git keeps history, and public repos are scraped for
exactly this within seconds. Full detail in
[chapter 6](docs/security-basics.md).

---

## Repo layout

```
README.md                  this manual's front page
docs/
  how-the-web-works.md     chapter 0 — foundations
  choosing-a-host.md       chapter 5 — picking a host for a new project
  security-basics.md       chapter 6 — not getting hacked
  where-to-go-next.md      chapter 7 — the map beyond this manual
00-local-app/              the FastAPI + SQLite todo app
01-github-pages/           static HTML/JS variant  → deployed
02-streamlit/              Streamlit variant
03-google-cloud-run/       the stage 0 app + a Dockerfile
04-oracle-vps/             the stage 0 app + systemd, nginx, deploy scripts
.github/workflows/         the Pages deploy automation
```

Each stage folder's README is self-contained: theory, implementation,
exercises, troubleshooting, and a glossary of its own terms.
