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

## What this model gives you, and what it costs

**Gives:** you control the entire runtime via the Dockerfile; automatic
HTTPS, scaling, and restarts; genuinely free at low traffic; one command to
deploy; the same image runs anywhere.

**Costs:** you must learn containers; **no persistent local storage at all**,
so any real app needs a separate managed database; cold starts after idle;
usage-based billing that could charge you under heavy traffic.
