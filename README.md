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
| 01 | GitHub Pages | GitHub (static) | Static hosting's ceiling: no backend, no shared state (localStorage only) |
| 02 | Streamlit Community Cloud | Streamlit's cloud | A real Python backend, zero infra — connect a repo, click deploy |
| 03 | Google Cloud Run | Google Cloud | Containers (Docker), autoscaling, and why stateless storage breaks SQLite |
| 04 | Oracle Cloud VM | Oracle Cloud | Everything Cloud Run did for you, done by hand: SSH, systemd, nginx, TLS, DNS |

Start at [00-local-app](00-local-app/).
