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

- **Checkboxes silently refused to work.** The first version put a checkbox
  next to each todo and compared the checkbox's state to the database to
  decide whether you'd just ticked it. Clicking did nothing at all.

  The reason: Streamlit remembers each checkbox's own state internally,
  separately from the database. So two things both believed they knew
  whether a todo was done, and they disagreed — the code couldn't tell a
  real click from Streamlit's remembered state.

  The fix was to use a plain button instead. A button remembers nothing —
  it simply reports "I was clicked just now," which leaves the database as
  the only thing tracking whether a todo is done. **General lesson:** when
  something has to be stored, exactly one place should be in charge of
  storing it.

- **Streamlit 1.38 wouldn't install on this machine.** That version requires
  an older image-handling library that has no ready-made package for Python
  3.14 (installed here). Without one, the installer tried to build it from
  scratch and failed on a missing system component. Version 1.64.0 has
  ready-made packages and installs cleanly — that's what's pinned in
  `requirements.txt`. **General lesson:** version conflicts between a
  library and your Python version are common, and the usual fix is moving
  to a newer version rather than fighting the build.

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

---

## Appendix: every term used on this page

| Term | Plain explanation |
|---|---|
| **Backend** | Code that runs *on the server* when a request arrives. It can read a database and give different answers to different visitors. Stage 1 had none; this stage does. |
| **Frontend** | Code that runs in the visitor's browser. In Streamlit you don't write it — Streamlit generates it for you. |
| **Streamlit** | A Python framework for building web interfaces without writing HTML or JavaScript. You call functions like `st.button()` and it renders the page. |
| **Framework** | A pre-built skeleton handling the universal parts of a job so you only write what's unique to your app. |
| **Rerun** | Streamlit's core mechanic: on every interaction, the *entire script runs again from the top*, and whatever it produces becomes the new page. `st.rerun()` triggers this manually after a database write. |
| **Widget** | One interactive element — a button, a checkbox, a text box. |
| **Session** | One visitor's ongoing use of the app. Streamlit keeps some state per session, which is what caused the checkbox problem above. |
| **State** | Information that has to be remembered. The central question of this whole project is *where* it's remembered and *who* is in charge of it. |
| **Source of truth** | The single place that authoritatively knows a fact. The checkbox bug happened because two things both thought they were it. |
| **SQLite** | A database that is just one file on disk. No separate program to install. |
| **Database** | Where a backend keeps data so it survives after a request finishes. |
| **User accounts / authentication** | Letting people log in, so the app can tell visitors apart and show each their own data. This app has none, which is why everyone shares one list. |
| **Managed / PaaS** | "Platform as a Service" — you supply code, they supply everything else: machine, operating system, web server, HTTPS, restarts. Streamlit and Cloud Run are both PaaS. |
| **Container** | A frozen snapshot of an app plus everything it needs to run. Streamlit builds one for you behind the scenes; in stage 3 you write the recipe yourself. |
| **Sleep / idle** | Free-tier platforms shut apps down when nobody's using them, to save resources. |
| **Cold start** | The delay while a sleeping app wakes up to answer the first request — 10–30 seconds here. |
| **Redeploy** | Pushing a new version, which replaces the running one. On this platform it can also wipe the database file, since a fresh container starts from scratch. |
| **Persistence** | Whether data actually survives over time. Guaranteed on a VM (stage 4), unreliable here, effectively absent in stage 3. |
| **Free tier** | The portion of a paid service given away at no cost, with limits attached. Streamlit's requires your repo be public. |
| **Public repo** | A GitHub repository anyone can read. Required by Streamlit's free tier — and the reason no credentials may ever be committed here. |
| **`requirements.txt`** | The list of libraries the app needs. Streamlit reads it automatically when deploying. |
| **Pin (a version)** | Specifying an exact version (`streamlit==1.64.0`) rather than "whatever's newest," so the app doesn't break when a library changes. |
