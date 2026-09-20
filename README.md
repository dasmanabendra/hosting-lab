# Learning Hosting

Hands-on path through deploying a web app for real — a small **todo list**,
hosted four different ways, each stage removing (or adding back) one layer
of "someone else handles this for you."

Not every stage can run the exact same code: GitHub Pages has no backend,
and Streamlit needs its own framework. So the app has a few variants —
stages 0, 3, and 4 share one real FastAPI+SQLite backend; stages 1 and 2
are deliberately simpler, static/Streamlit-only versions, used to teach
what those platforms can and can't do.

## Stages

| # | Stage | What hosts it | What it teaches |
|---|-------|----------------|------------------|
| 00 | [Local app](00-local-app/) | Your machine | The app itself: FastAPI + SQLite, run with `uvicorn` |
| 01 | [GitHub Pages](01-github-pages/) | GitHub (static) | Static hosting's ceiling: no backend, no shared state (localStorage only) |
| 02 | [Streamlit Community Cloud](02-streamlit/) | Streamlit's cloud | A real Python backend, zero infra — connect a repo, click deploy |
| 03 | [Google Cloud Run](03-google-cloud-run/) | Google Cloud | Containers (Docker), autoscaling, and why stateless storage breaks SQLite |
| 04 | [Oracle Cloud VM](04-oracle-vps/) | Oracle Cloud | Everything Cloud Run did for you, done by hand: SSH, systemd, nginx, TLS, DNS |

Start at [00-local-app](00-local-app/).

## Status

Code for all five stages is written. What's verified and what still needs
doing:

| Stage | Built | Tested locally | Deployed |
|---|---|---|---|
| 00 Local app | yes | yes — add/toggle/delete all work | n/a |
| 01 GitHub Pages | yes | yes — add/toggle/delete all work | no |
| 02 Streamlit | yes | yes — add/toggle/delete all work | no |
| 03 Cloud Run | yes | not yet — Docker daemon wasn't running | no |
| 04 Oracle VM | yes | scripts syntax-checked only; needs a real VM | no |

Every remaining step needs an account: a GitHub repo to push to, a
Streamlit Community Cloud login, a Google Cloud project with billing
enabled, and an Oracle Cloud account with a provisioned VM. Those are
deliberately left for a session together rather than done unattended.

## Next session

In rough order, easiest first:

1. **Start Docker Desktop** (it's installed but its engine wasn't running —
   probably a first-run dialog). Then `docker build` stage 3 locally to
   confirm the container works before involving Google.
2. **Create a GitHub repo and push this code.** Everything downstream needs
   it: Pages serves from it, Streamlit connects to it, the VM pulls from it.
   It needs to be public for Streamlit's free tier.
3. **Turn on GitHub Pages** (Settings → Pages → source: GitHub Actions).
   The workflow is already written; stage 1 goes live on the next push.
4. **Deploy stage 2** — sign in to Streamlit Community Cloud with GitHub,
   point it at `02-streamlit/app.py`.
5. **Deploy stage 3** — Google Cloud account, then `gcloud run deploy`.
   Then wait for it to scale to zero and watch the todos disappear.
6. **Deploy stage 4** — Oracle account, provision an Always Free VM, then
   run the three scripts in `04-oracle-vps/`.

**No secrets belong in this repo.** It needs to be public for Streamlit's
free tier, so credentials stay in `.gitignore`'d local files, GitHub Actions
secrets, or the cloud provider's own console — never in tracked files.
