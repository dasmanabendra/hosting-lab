# Stage 0: Local app

The app itself, running directly on your machine — no hosting yet. Stages
3 and 4 deploy this exact code; stages 1 and 2 use simpler variants built
for platforms that can't run a real backend this way.

**What it is**: a todo list. FastAPI serves an HTML page with an add form
and the current list; each todo can be marked done or deleted. Everything
is written to a SQLite file on disk. Deliberately small — the point of
this project is hosting, not the app.

## Run it

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — add a todo, mark it done, refresh, see it persist.

## Why this matters for hosting later

- The SQLite file lives at `data/todos.db`, next to the app. That's a
  **stateful** app: it needs a real, persistent filesystem to work. Stage 3
  (Cloud Run) will break this on purpose to show why.
- `/health` returns `{"status": "ok"}` — a convention hosting platforms
  and reverse proxies use to check if your app is alive. Not used yet,
  but it'll matter from stage 3 onward.
