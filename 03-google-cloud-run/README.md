# Stage 3: Google Cloud Run

The same FastAPI + SQLite app from stage 0 — byte for byte identical code —
but packaged in a **container** and run by Google. This is the stage where
hosting gets genuinely interesting, because it breaks.

## What a container is

Stages 1 and 2 let the platform decide how to run your code. A container
is you deciding instead: the `Dockerfile` here says "start from Python
3.12, install these dependencies, copy in this code, run this command."
That image runs identically on your laptop, on Google's machines, or
anywhere else — which is the whole point.

## Run it locally (needs Docker)

```bash
docker build -t todo-app .
docker run -p 8080:8080 todo-app
```

Open http://localhost:8080. Same app as stage 0, just running inside a
container instead of directly on your machine.

## The lesson: stateless hosting breaks SQLite

Cloud Run doesn't keep a machine running for you. It starts a container
when a request arrives, stops it when traffic dies down (**scale to zero**),
and starts *more* copies when traffic spikes. Each of those containers gets
its own fresh, empty filesystem.

So `data/todos.db` — which worked perfectly in stages 0 and 2 — now means:

- Add a todo, come back an hour later: **gone**. The container that held
  your database was shut down, and the new one started from the image.
- Under real traffic, two visitors might hit two different containers and
  see two different todo lists.

This is not a bug in the app. It's the deal you make with this kind of
hosting: it scales effortlessly and costs nothing when idle, *because* it
refuses to remember anything. Real apps on Cloud Run keep their data in a
separate managed database (Cloud SQL, Firestore) rather than on local disk.

We're deliberately not fixing this — feeling it break is the point. Stage 4
gets the data back by going the other direction: one machine, always on,
with a real disk.

## Deploying (needs your account)

Not done yet — requires a Google Cloud account with billing enabled (free
tier covers this app's usage). The deploy itself is one command from this
folder:

```bash
gcloud run deploy todo-app --source . --region us-central1 --allow-unauthenticated
```

Google builds the image, stores it, runs it, and hands back an HTTPS URL.
No server, no certificate, no reverse proxy configuration on your part —
all of which you'll do by hand in stage 4.
