# Stage 0: The app, running on your own machine

No hosting yet. This is the thing all later stages deploy — and the
baseline for "working correctly," so you can tell when hosting breaks it.

Stages 3 and 4 run this code byte-for-byte. Stages 1 and 2 use rewritten
variants, because their platforms can't run this shape of app at all.

---

## Theory: what's actually happening when you run this

You start a program (`uvicorn`) that stays running and listens on **port
8000**. Your browser sends a request to `http://127.0.0.1:8000`, the
program builds an HTML page, and sends it back. That's the whole web, in
miniature — and it's already a "server." The only reason the public can't
reach it is that nothing outside your machine knows how to route to it.

Three ideas worth naming, because later stages break each one:

**1. The app is a long-running process.** Not a document, not a script that
finishes — a program that must *stay alive* to answer requests. If it
crashes, the site is down until something restarts it. Here, nothing
restarts it; that's what systemd does in stage 4 and what Cloud Run does
invisibly in stage 3.

**2. The app is stateful.** It writes todos to `data/todos.db`, a SQLite
database — which is just a single file sitting next to the code. That
works perfectly when there's one machine with one permanent disk. Stage 3
takes the permanent disk away and the app quietly falls apart.

**3. Server-rendered HTML.** Every click submits a form; the server writes
to the database and sends back a fresh page. No JavaScript at all. Stage 1
inverts this completely — all JavaScript, no server.

---

## Implementation

**Stack:** Python, FastAPI (the web framework), uvicorn (the program that
actually listens on the port), SQLite (the database).

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — add a todo, mark it done, delete it, refresh
to confirm it persists.

`app.main:app` means "in the file `app/main.py`, use the variable named
`app`." `--reload` restarts the server when you edit code — a development
convenience you would never use in production.

### What the code does

[`app/main.py`](app/main.py), roughly 120 lines:

| Route | Purpose |
|---|---|
| `GET /` | Read all todos from SQLite, render the HTML page |
| `POST /todos` | Insert a new todo, then redirect back to `/` |
| `POST /todos/{id}/toggle` | Flip done/not-done, redirect back |
| `POST /todos/{id}/delete` | Delete the row, redirect back |
| `GET /health` | Returns `{"status": "ok"}` |

**Why every write redirects (the 303):** without it, the browser would
still be sitting on the POST, and hitting refresh would re-submit the form
and duplicate the todo. Redirecting after a write means refresh just
re-reads the page. This is a standard pattern (Post/Redirect/Get).

**Why `/health` exists:** it's a conventional endpoint that returns cheaply
and proves the app is alive. Hosting platforms and reverse proxies ping it
to decide whether to send traffic, restart the app, or declare a deploy
successful. Unused in stage 0; it matters from stage 3 on.

**Why the database path is computed from `__file__`:** the app resolves
`data/todos.db` relative to its own location, so it works regardless of
which directory you launch it from.

---

## Gotchas hit

- **`python-multipart` is required but not obvious.** FastAPI raises
  `RuntimeError: Form data requires "python-multipart" to be installed` the
  moment you define a form endpoint. It isn't pulled in by FastAPI itself,
  so it's pinned explicitly in `requirements.txt`.

---

## What this stage costs you

Nothing runs unless you start it, nobody but you can reach it, and it stops
when you close the terminal. Every stage after this one is about solving
exactly that.
