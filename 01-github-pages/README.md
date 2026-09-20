# Stage 1: GitHub Pages

The simplest hosting that exists: a folder of files, served as-is, with no
server running your code at all.

**What changed from stage 0**: there is no backend. The todo list is the
same idea, but rewritten as plain HTML/CSS/JavaScript, storing todos in
the browser's `localStorage` instead of a database.

## Run it locally

No build step, no dependencies — it's one file:

```bash
python -m http.server 8001
```

Open http://127.0.0.1:8001. (Opening `index.html` directly also works.)

## What this teaches

- **Static hosting means no code of yours runs on a server.** GitHub just
  hands your files to whoever asks. Any "logic" happens in the visitor's
  browser.
- **Data has nowhere shared to live.** `localStorage` is per-browser, per-device:
  your phone sees an empty list, and clearing browser data wipes it. Even a
  "personal" app needs a backend to be reliable — that's what stage 2 adds.
- **It's free and effectively unbreakable.** No server to crash, no bill to
  run up, HTTPS included. That's the tradeoff static hosting makes.

## Deploying (needs your GitHub account)

Not done yet — requires pushing this repo to GitHub. Note that the classic
Pages setting can only serve the repo root or a `/docs` folder, so publishing
*this* subfolder needs a small GitHub Actions workflow. That gets set up when
we do the deploy together.
