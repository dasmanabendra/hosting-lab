# Stage 2: Streamlit Community Cloud

A real backend again — but you never touch a server, a container, or a
config file. You point Streamlit at a GitHub repo and it runs your Python.

**What changed from stage 1**: the todos live in a SQLite database on a
server instead of in your browser. The immediate, visible consequence:
everyone who opens the URL sees the *same* list. There are no accounts,
so "your" todos are now everyone's todos.

## Run it locally

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
```

Opens at http://localhost:8501.

## What this teaches

- **A backend changes who data belongs to.** Stage 1's todos were private
  to one browser by accident of the technology. Here they're shared by
  default — making them private again would mean adding user accounts,
  which is real work.
- **"Managed" means someone else picks your infrastructure.** You don't
  choose the OS, the Python version, the web server, or the HTTPS
  certificate. Streamlit decides, and it just works — until you need
  something it doesn't offer.
- **Free tiers sleep.** Community Cloud apps go idle after inactivity and
  take a while to wake up on the next visit. Compare with stage 4, where
  the app just keeps running because you're paying for a VM around the clock.
- **Persistence here is real but not guaranteed.** The SQLite file lives on
  the container Streamlit runs for you — it survives normal use, but a
  redeploy or container recycle can wipe it. That's a milder version of the
  problem stage 3 hits head-on.

## Deploying (needs your accounts)

Not done yet — requires a GitHub repo plus a Streamlit Community Cloud
account. Note the free tier requires the repo to be **public**. When
connecting, point it at `02-streamlit/app.py` as the main file.
