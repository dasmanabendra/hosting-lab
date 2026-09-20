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

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --reload
```

On Mac/Linux, `.venv\Scripts\` is `.venv/bin/` instead.

Open http://127.0.0.1:8000 — add a todo, mark it done, delete it, refresh
to confirm it persists. **Press `Ctrl+C` in the terminal to stop it.**

`app.main:app` means "in the file `app/main.py`, use the variable named
`app`." `--reload` restarts the server when you edit code — a development
convenience you would never use in production.

### What the code does

All of it is in [`app/main.py`](app/main.py) — one file, about 120 lines:

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

## Try it yourself

Do these — they take minutes and each one makes a later stage obvious.

1. **Prove it's a real server.** With the app running, visit
   http://127.0.0.1:8000/health in your browser. You'll see
   `{"status":"ok"}` — no page, just data. That's the same app answering a
   different question.

2. **Prove the data is on disk, not in the program.** Add a few todos. Stop
   the app (`Ctrl+C`). Start it again. The todos are still there — they were
   never in the app's memory, they're in `data/todos.db`.

3. **Now delete that file** (with the app stopped) and start it again.
   Empty list. You just did, by hand, exactly what Cloud Run will do to you
   accidentally in stage 3.

4. **Watch the redirect happen.** Press `F12` in your browser, open the
   Network tab, then add a todo. You'll see two entries: a `POST /todos`
   answered with `303`, then a `GET /` answered with `200`. That's the
   Post/Redirect/Get pattern, visible.

5. **Try to reach it from your phone.** Put your phone on the same wi-fi and
   visit `http://<your-computer's-IP>:8000`. It won't work — the app is
   bound to `127.0.0.1`, which means "this machine only." *That* is the
   thing every remaining stage exists to fix.

---

## Troubleshooting

| Symptom | What's happening | Fix |
|---|---|---|
| `[Errno 10048]` / "address already in use" | Something is already on port 8000 — often a copy of this app you forgot to stop | Stop the old one, or run on another port: `--port 8001` |
| `ModuleNotFoundError: No module named 'fastapi'` | You're running system Python, not the virtual environment's | Use the full path: `.venv\Scripts\uvicorn`, not plain `uvicorn` |
| `RuntimeError: Form data requires "python-multipart"` | That library is missing | `.venv\Scripts\pip install -r requirements.txt` |
| Browser shows "can't connect" | The app isn't running, or you used the wrong port | Check the terminal is still showing `Uvicorn running on...` |
| Changes to the code do nothing | You started it without `--reload` | Restart with `--reload`, or stop and start after each edit |
| `python` is not recognised | Python isn't installed, or isn't on your PATH | Install from python.org, ticking "Add Python to PATH" |

**How to read an error:** the useful line is almost always the *last* one,
not the wall of text above it. That wall is the path the program took to get
there; the final line is what actually went wrong.

---

## What this stage costs you

Nothing runs unless you start it, nobody but you can reach it, and it stops
when you close the terminal. Every stage after this one is about solving
exactly that.

**Next:** [Stage 1 — GitHub Pages](../01-github-pages/)

---

## Appendix: every term used on this page

| Term | Plain explanation |
|---|---|
| **Terminal / command line** | The window where you type commands instead of clicking. PowerShell on Windows. A grey box in this README means "type this there and press Enter." |
| **Server** | A computer (or a program on one) that stays running, waiting for requests and sending back responses. Not special hardware — your laptop is one while this app runs. |
| **Request / response** | The entire web in two words. A browser asks for a URL (request); a server sends something back (response). |
| **Port** | A numbered door on a computer, so one machine can run many programs that all use the network. Ours listens on port 8000. Web traffic normally uses 80 and 443. |
| **`127.0.0.1` / localhost** | "This same computer." A program listening only here cannot be reached from the internet — which is why stage 0 is private by default. |
| **Process** | A running program. The app is a process that must stay alive to answer requests; if it stops, the site is down. |
| **Python** | The programming language this app is written in. |
| **Framework** | A pre-built skeleton that handles the boring, universal parts of a job so you only write the parts unique to your app. |
| **FastAPI** | The web framework here. It turns "a browser asked for `/todos`" into "run this specific Python function." |
| **uvicorn** | The program that actually listens on the port and hands requests to FastAPI. FastAPI defines *what* to do; uvicorn is what's *running*. |
| **Route / endpoint** | One URL the app knows how to answer, paired with the code that answers it — e.g. `GET /` or `POST /todos`. |
| **`GET` / `POST`** | The two request types here. GET means "give me this page." POST means "here's some data, do something with it." Forms use POST. |
| **Redirect (303)** | A response that says "don't render anything, go request this other URL instead." Used after every write so refreshing doesn't resubmit the form. |
| **Post/Redirect/Get** | The name of that pattern: handle the POST, then redirect to a GET, so the browser never sits on a submitted form. |
| **HTML** | The language describing what a web page contains. The app builds HTML as text and sends it to the browser. |
| **Form** | The HTML element that collects input and submits it to the server. Our add/toggle/delete buttons are all tiny forms. |
| **Database** | Where data is kept so it outlives a single request. |
| **SQLite** | A database that is simply one file on disk (`data/todos.db`) — no separate program to install or run. Ideal for small apps, and the source of the trouble in stage 3. |
| **Stateful** | Means the app remembers things between requests, so it needs somewhere permanent to write. The opposite, stateless, forgets everything — which is what breaks this app on Cloud Run. |
| **Health endpoint** | A cheap URL (`/health`) that returns "I'm alive." Hosting platforms ping it to decide whether the app is working. |
| **Virtual environment (`.venv`)** | A private, per-project copy of Python and its libraries, so different projects don't fight over versions. |
| **pip** | Python's library installer. |
| **Dependency / library** | Code written by someone else that your app uses. FastAPI and uvicorn are dependencies. |
| **`requirements.txt`** | The list of dependencies and their versions — the shopping list pip reads. |
| **`--reload`** | A development-only option that restarts the app whenever you edit a file. Never used in production. |
| **`app.main:app`** | Tells uvicorn where to find the app: "in the file `app/main.py`, use the variable named `app`." |
| **`python-multipart`** | A small library FastAPI needs in order to read submitted form data. Not installed automatically, hence the crash described above. |
| **JSON** | A plain-text format for structured data, used when a response is meant for another program rather than a person. `/health` returns JSON; `/` returns HTML. |
| **Row** | One record in a database table — here, one todo. |
| **Production** | The real, live version people actually use, as opposed to the copy on your machine for development. Some conveniences (`--reload`) belong only in the latter. |
| **`__file__`** | A Python value meaning "the location of this code file." Used so the app finds its database relative to itself, not to wherever you happened to run the command from. |
| **`Ctrl+C`** | The keystroke that stops a running program in the terminal. |
