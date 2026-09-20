# Stage 3: Google Cloud Run — containers, and the day SQLite dies

The same FastAPI + SQLite app from stage 0, byte-for-byte — but packaged in
a **container** and run by Google. This is where hosting gets genuinely
interesting, because this is the stage where the app breaks.

---

## Theory

### What a container is, and why anyone bothered

Stages 1 and 2 let the platform decide how to run your code. That's fine
until the platform's Python version isn't yours, or it lacks a library you
need. A container is you taking that decision back.

A **container image** is a frozen snapshot of an entire miniature operating
system with your app inside it: the OS libraries, the Python interpreter,
your dependencies, your code, and the command to start it. It runs
identically on your laptop, on Google's machines, or on a competitor's,
because it carries its whole world with it. That's the famous promise —
"it works on my machine" stops being a problem, because the machine ships
with the app.

The recipe for building that snapshot is a **Dockerfile**. Ours:

```dockerfile
FROM python:3.12-slim          # start from a minimal Linux with Python 3.12
WORKDIR /app                   # work inside /app
COPY requirements.txt .        # copy the dependency list in
RUN pip install -r ...         # install them (baked into the image)
COPY app/ ./app/               # copy the code in
ENV PORT=8080                  # default port
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Two details in that last line matter:

- **`--host 0.0.0.0`**, not `127.0.0.1`. Inside a container, `127.0.0.1`
  means "this container only," so Cloud Run couldn't reach it. Note this is
  the exact opposite of stage 4, where binding to `127.0.0.1` is the
  correct and safer choice — because there, nginx sits in front.
- **`$PORT`**. Cloud Run picks the port and tells the container via this
  environment variable. Hardcoding 8000 would fail. `exec` makes uvicorn
  replace the shell, so shutdown signals reach it properly.

Dependencies are installed *before* the code is copied because Docker
caches each step: changing your code then doesn't force a reinstall of
every library.

### What Cloud Run actually does

It never keeps a machine running for you. It:

- starts a container when a request arrives,
- stops it when traffic dies down (**scale to zero**),
- starts *more copies* when traffic spikes (**autoscaling**),
- and gives each copy its own fresh, empty filesystem from the image.

You pay only while containers are running, which is why the free tier is
generous. HTTPS, the URL, certificates, load balancing, and restart-on-crash
all come included and invisible.

### The lesson: stateless hosting destroys SQLite

`data/todos.db` worked perfectly in stages 0 and 2. Here it means:

- **Add a todo, come back an hour later: gone.** Traffic stopped, Cloud Run
  shut the container down, and the next request started a brand-new one
  from the original image — which never contained your database.
- **Under real traffic, visitors disagree.** Two containers running at once
  have two separate database files. Two people see two different todo lists,
  and each thinks the other's todos don't exist.

This is not a bug in the app and not a misconfiguration. It's the deal:
Cloud Run scales effortlessly and costs nothing when idle *precisely
because* it refuses to remember anything between requests.

**The real fix** — which we're deliberately not applying — is to stop
storing data on local disk and use a managed database (Cloud SQL,
Firestore) that lives outside the container and survives independently.
Local disk in a container is scratch space, nothing more.

We leave it broken because experiencing the disappearance teaches the idea
permanently in a way reading about it does not. Stage 4 fixes it the other
way: by going back to one machine with one real disk.

---

## Implementation

Run it locally (needs Docker):

```bash
docker build -t todo-app .
docker run -p 8080:8080 todo-app
```

Open http://localhost:8080. `-p 8080:8080` connects port 8080 on your
machine to 8080 inside the container — without it, the container is sealed
off and unreachable.

[`.dockerignore`](.dockerignore) keeps `.venv/`, `data/`, and caches out of
the image — they'd bloat it and, worse, could bake a local database file
into what gets deployed.

### Deploying (not done yet — needs your account)

Requires a Google Cloud account with billing enabled; the free tier covers
this app's usage, but a card must be on file.

```bash
gcloud run deploy todo-app --source . --region us-central1 --allow-unauthenticated
```

Google builds the image from the Dockerfile, stores it in its registry,
runs it, and returns an HTTPS URL. No server, no certificate, no reverse
proxy on your part — all of which stage 4 does by hand.

`--allow-unauthenticated` makes it a public website; without it, callers
would need Google credentials.

**Then run the experiment:** add a todo, wait for traffic to stop and the
container to scale to zero, come back, and watch it be gone.

---

## Gotchas hit

- **Docker Desktop's engine wouldn't start unattended.** The CLI was
  installed and the app process was running, but its WSL backend distro
  (`docker-desktop`) stayed stopped, so every `docker` command hung. Almost
  certainly a first-run dialog waiting for a click. The image has therefore
  **not been built or tested yet** — do that before deploying.

---

## Try it yourself

1. **Look inside a container.** With the image built, run
   `docker run -it todo-app /bin/bash`. You get a shell inside a complete
   miniature Linux. Run `ls`, `python --version`, `cat app/main.py`. Type
   `exit` to leave. That whole world ships with your app.

2. **Prove containers start empty every time.** Run the app, add a todo,
   stop the container (`Ctrl+C`), and start it again with the same command.
   Gone. Not a Cloud Run quirk — that's how containers work, and Cloud Run
   just does it to you automatically.

3. **Prove the image is self-contained.** Delete your `.venv` folder. Run
   the container again. It still works — nothing on your machine is involved
   any more except Docker itself.

4. **Break it on purpose.** Change the Dockerfile's last line to hardcode
   `--port 8000` instead of `$PORT`, rebuild, and deploy. Cloud Run will
   fail to start the container, because it told you which port to use and
   you ignored it. Change it back.

5. **The main event.** Once deployed: add several todos, close the tab, wait
   long enough for the service to scale to zero (15+ minutes with no
   traffic), then reload. Watch them be gone. Sit with that for a moment —
   it's the most important thing in this manual.

6. **See two instances disagree** (optional). Deploy with
   `--min-instances 2`, then reload repeatedly. Different requests hit
   different containers with different database files, so the list flickers
   between two versions of reality.

---

## Troubleshooting

| Symptom | What's happening | Fix |
|---|---|---|
| `docker` commands hang or say "cannot connect to the daemon" | Docker Desktop's engine isn't running | Open Docker Desktop, complete any first-run dialog, wait for "Engine running" |
| Cloud Run deploy fails: "container failed to start and listen" | The app isn't listening on `$PORT`, or bound to `127.0.0.1` | Must be `--host 0.0.0.0 --port $PORT` |
| Deployed URL returns 403 | The service is private | Redeploy with `--allow-unauthenticated` |
| Todos keep disappearing | Working exactly as designed | Not fixable on local disk — needs a managed database |
| Different visitors see different lists | Multiple instances, each with its own file | Same cause, same fix |
| First request after idle takes several seconds | Cold start — a container is booting | Normal; `--min-instances 1` avoids it but costs money |
| Build is very slow every time | Dependencies reinstall on each build | Ensure `COPY requirements.txt` and `RUN pip install` come *before* `COPY app/` |
| `gcloud: command not found` | The CLI isn't installed | Install the Google Cloud SDK, then `gcloud auth login` |

---

## What this model gives you, and what it costs

**Gives:** you control the entire runtime via the Dockerfile; automatic
HTTPS, scaling, and restarts; genuinely free at low traffic; one command to
deploy; the same image runs anywhere.

**Costs:** you must learn containers; **no persistent local storage at all**,
so any real app needs a separate managed database; cold starts after idle;
usage-based billing that could charge you under heavy traffic.

Before deploying, set a **budget alert** on the Google Cloud project. The
free tier is generous, but it's an allowance rather than a hard limit —
exceeding it bills you rather than switching you off.

**Next:** [Stage 4 — the Oracle VM](../04-oracle-vps/) — but read
[chapter 6, Not getting hacked](../docs/security-basics.md) first, since
stage 4 puts a Linux machine on the public internet in your name.

---

## Appendix: every term used on this page

| Term | Plain explanation |
|---|---|
| **Container** | A frozen snapshot of an app *plus everything it needs to run* — a miniature operating system, the Python interpreter, the libraries, the code. It runs identically anywhere, because it carries its whole world with it. |
| **Image** | The snapshot file itself. A container is a running copy of an image. (Image is to container roughly as a recipe is to a meal.) |
| **Docker** | The most common tool for building and running containers. |
| **Docker Desktop** | The Windows/Mac application that runs Docker on your machine. Its background service is the "engine" — the thing that wouldn't start here. |
| **Dockerfile** | The plain-text recipe for building an image: start from this base, install that, copy this in, run this command. |
| **Registry** | Online storage for images, so a cloud service can download and run yours. Google's is called Artifact Registry. |
| **Base image (`FROM`)** | The starting point you build on — here `python:3.12-slim`, a minimal Linux with Python already installed. "slim" means stripped of everything unnecessary, so it's smaller and faster to ship. |
| **`WORKDIR` / `COPY` / `RUN` / `CMD`** | Dockerfile instructions: set the working folder, copy files in, execute a command while building, and define the command to run when the container starts. |
| **Layer / build cache** | Each Dockerfile line produces a cached layer. Unchanged steps are reused on later builds — which is why dependencies are installed *before* code is copied. Otherwise every code edit would reinstall everything. |
| **`0.0.0.0` vs `127.0.0.1`** | `127.0.0.1` means "reachable only from this same machine"; `0.0.0.0` means "reachable from outside too." Inside a container you need `0.0.0.0`, or the platform can't reach the app. In stage 4 the correct answer flips, because nginx sits in front. |
| **Environment variable** | A named value handed to a program from outside, rather than written into its code. Cloud Run sets `PORT` to tell the container which port to use. |
| **`exec`** | Makes the started program replace the shell that launched it, so shutdown signals reach the app directly and it can stop cleanly. |
| **`.dockerignore`** | A list of files to keep *out* of the image — here the virtual environment, caches, and any local database file, which must never be baked in. |
| **Port mapping (`-p 8080:8080`)** | Connects a port on your machine to a port inside the container. Without it the container is sealed off and unreachable. |
| **Stateless** | Every request starts from a blank slate; nothing written to disk is expected to survive. The defining property of Cloud Run, and what breaks SQLite here. |
| **Scale to zero** | The platform shuts the app down completely when no one is using it, and starts it again on the next request. Why it costs nothing while idle. |
| **Autoscaling** | Automatically running more copies when traffic rises, fewer when it falls. |
| **Instance** | One running copy of your container. Several can exist at once — each with its own separate, empty filesystem. |
| **Cold start** | The delay while a stopped container boots to serve the first request after idle time. |
| **Load balancing** | Spreading incoming requests across multiple running copies. Cloud Run does it for you. |
| **Managed database** | A database run as a separate service (Cloud SQL, Firestore) that lives *outside* your containers and therefore survives them. The real fix for the problem on this page. |
| **`gcloud`** | Google Cloud's command-line tool. |
| **`--source .`** | Tells `gcloud` to build the image from the current folder's Dockerfile rather than from a pre-built image. |
| **`--allow-unauthenticated`** | Makes the service a public website. Without it, visitors would need Google credentials to load the page. |
| **Region** | Which datacenter your app runs in (`us-central1` here). Closer regions mean lower latency for nearby visitors. |
| **Billing account** | A payment method on file. Required even to use the free tier, because usage beyond it is charged. |
| **WSL** | "Windows Subsystem for Linux" — the Linux environment Windows uses to run Docker. Docker Desktop's engine runs inside it, which is why its state matters when Docker won't start. |
