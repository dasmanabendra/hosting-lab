# Stage 2: Streamlit Community Cloud — a backend, zero infrastructure

A real server running real Python again — but you never see a machine, a
container, or a config file. You hand Streamlit a GitHub repo and it runs.

---

## Theory: what changes the moment there's a backend

Stage 1's todos lived in each visitor's browser. Here they live in a SQLite
database **on Streamlit's server**. One database, one copy, shared by
everyone who opens the URL.

Nobody wrote code to "make it shared." Sharing is simply what happens when
data moves from the browser to a server. This is worth sitting with,
because the instinct is backwards: making data *private* is the thing that
takes work. Privacy requires user accounts — logins, sessions, a per-user
key on every row — which is a genuine feature, not a setting.

So this app is now a single global todo list that any visitor can edit or
delete. That's a deliberate teaching artifact, not an oversight.

### What "managed" means here

Streamlit decides essentially everything: the operating system, the Python
version, the web server, the HTTPS certificate, the domain, how the process
gets restarted. You choose a file path. That's the deal — enormous
convenience in exchange for zero control. It's wonderful until you need
something the platform doesn't offer, at which point there's no lever to
pull.

### Free tiers sleep

Community Cloud apps go idle after a period without visitors and take
roughly 10–30 seconds to wake on the next request. Compare stage 4, where
the app runs continuously because you're paying for a machine whether
anyone visits or not. Neither is better — they're different bargains.

### Persistence here is real but not promised

The SQLite file lives on the container Streamlit runs for you. It survives
normal use and ordinary restarts, but a redeploy or a container recycle can
wipe it. This is a mild preview of the problem stage 3 hits head-on: when
you don't control the machine, you don't control whether your files
survive.

### Why the code had to be rewritten again

Streamlit only hosts apps written in Streamlit, which is a fundamentally
different way to build a UI. There's no HTML, no routes, no forms in the
stage 0 sense. Instead the **entire script re-runs from the top on every
interaction**, and the UI is whatever that run produces.

| Stage 0 (FastAPI) | Stage 2 (Streamlit) |
|---|---|
| You write HTML | You call `st.button()`, `st.write()` |
| Routes handle specific URLs | No routes — one script, re-run each time |
| Browser reloads the page | Streamlit re-runs the script and re-renders |
| You control the markup exactly | Streamlit controls the look |

Same SQLite logic underneath — the database functions are nearly identical
to stage 0's. Only the UI layer changed.

---

## Implementation

[`app.py`](app.py) — one file. Database helpers (`get_db`, `list_todos`,
`add_todo`, `toggle_todo`, `delete_todo`) are the stage 0 logic; the rest
is Streamlit UI.

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

Opens at http://localhost:8501.

**The `st.rerun()` calls matter.** After any database write, the script is
told to re-run so the list reflects the change immediately. Without it, the
UI would show stale data until the next interaction.

### Deploying (not done yet — needs your account)

1. Sign in at https://share.streamlit.io with GitHub.
2. Create an app from the `dasmanabendra/hosting-lab` repo.
3. Set the main file path to **`02-streamlit/app.py`** — subfolders are
   supported natively, unlike GitHub Pages.
4. Streamlit reads `02-streamlit/requirements.txt`, installs, and deploys.

**The free tier requires the repo to be public.** That constraint is why
this whole repo is public, and why no credentials can ever be committed.

---

## Gotchas hit

- **A stateful `st.checkbox` fights the database.** The first version used a
  checkbox per row, comparing its return value against the stored `done`
  flag to detect a toggle. It silently never toggled: Streamlit keeps
  widget state in its own session store keyed by the widget's `key`, so the
  widget and the database disagreed about who was the source of truth. A
  plain `st.button` is stateless — it returns `True` once, on the click —
  which makes the database unambiguously authoritative. Same fix pattern
  applies to any Streamlit widget driving external state.
- **Streamlit 1.38 won't install on Python 3.14.** It pins a Pillow version
  with no 3.14 wheel, so pip tries to compile it from source and fails on a
  missing zlib. Version 1.64.0 installs cleanly — that's what's pinned.

---

## What this model gives you, and what it costs

**Gives:** a real backend and database with essentially zero infrastructure
work; free; HTTPS and a URL handled for you; deploys straight from GitHub.

**Costs:** no control over the runtime, no custom domain on the free tier,
cold starts after idling, persistence that isn't guaranteed, and you're
locked into Streamlit's UI conventions. Also: your repo must be public.

Stage 3 keeps the "someone else runs it" convenience but hands back control
of the environment — via containers — and in doing so breaks persistence
completely.
