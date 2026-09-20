# Stage 0: Local app

The app itself, running directly on your machine — no hosting yet. Every
later stage deploys some variant of this.

**What it is**: a guestbook. FastAPI serves an HTML page with a form;
submissions get written to a SQLite file on disk; the page re-renders the
list on every request. Deliberately small — the point of this project is
hosting, not the app.

## Run it

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 — sign the guestbook, refresh, see it persist.

## Why this matters for hosting later

- The SQLite file lives at `data/guestbook.db`, next to the app. That's a
  **stateful** app: it needs a real, persistent filesystem to work. Stage 3
  (Cloud Run) will break this on purpose to show why.
- `/health` returns `{"status": "ok"}` — a convention hosting platforms
  and reverse proxies use to check if your app is alive. Not used yet,
  but it'll matter from stage 3 onward.
