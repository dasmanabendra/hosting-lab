# Stage 1: GitHub Pages — static hosting

**Status: deployed and live at https://dasmanabendra.github.io/hosting-lab/**

The simplest hosting that exists: a folder of files handed to whoever asks,
with none of your code running on the server.

---

## Theory: what "static" really means

A static host is a very fast, very reliable photocopier. A browser asks for
`index.html`; GitHub sends that exact file back. It never executes
anything, never opens a database, never knows who's asking.

That constraint has enormous upsides. There's no process to crash, no
server to patch, no bill to run up, and no code that an attacker can make
do something unintended. GitHub serves it from a CDN, so it's fast
worldwide, and HTTPS comes free and pre-configured. It is nearly impossible
to break.

The cost: **the server cannot remember anything.** Any data has to live in
the visitor's own browser.

### Where the data actually lives

`localStorage` is a small storage box the browser gives each website,
keyed to that exact site. It persists across reloads and even restarts —
but it lives on **that one device, in that one browser**. Consequences:

- Open the site on your phone → empty list. Nothing syncs.
- Clear browsing data → todos gone, permanently, with no backup.
- Send the link to a friend → they see *their own* empty list, never yours.

That last point is the interesting one. This app *looks* multi-user but
isn't: every visitor gets a private, isolated copy. Stage 2 shows the
opposite extreme.

### Why the code had to be rewritten

Stage 0's app is Python that runs on a server. There is no server here, so
none of it could survive. The rewrite moves the same logic into JavaScript
running in the visitor's browser:

| Stage 0 (server) | Stage 1 (browser) |
|---|---|
| Python builds the HTML | JavaScript builds the HTML |
| Data in SQLite on disk | Data in `localStorage` |
| Every click = form POST + page reload | Every click handled in-page, no reload |
| Logic hidden on the server | Logic fully visible via "view source" |

The last row matters: on a static site, all your code ships to the visitor.
There is no place to keep a secret — no API keys, no passwords, ever.

---

## Implementation

One file, [`index.html`](index.html) — markup, styling, and logic together.
No framework, no build step, no dependencies.

Run it locally:

```bash
python -m http.server 8001
```

Then http://127.0.0.1:8001. (Opening the file directly also mostly works,
but a local server better matches how it's really served.)

### How it was deployed

GitHub Pages' built-in setting can only publish from the **repo root** or a
**`/docs` folder** — not an arbitrary subfolder like `01-github-pages/`.
Rather than rename the folder and lose the stage numbering, deployment goes
through GitHub Actions, which can publish any path.

[`.github/workflows/deploy-pages.yml`](../.github/workflows/deploy-pages.yml)
runs on every push to `main`: it checks out the repo, packages the
`01-github-pages` folder as a Pages artifact, and deploys it. That's CI/CD
in its smallest useful form — you push, it publishes, nobody clicks
anything.

Steps actually performed:

```bash
gh repo create hosting-lab --public --source=. --remote=origin
git branch -M main
git push -u origin main
gh api --method POST repos/dasmanabendra/hosting-lab/pages -f build_type=workflow
```

The last command is the one that isn't obvious — see below.

---

## Gotchas hit

- **The workflow fails until Pages is enabled.** The first run died with
  `Get Pages site failed... Not Found`. The deploy action cannot create the
  Pages site itself; Pages has to be switched on first, with its source set
  to "GitHub Actions" (Settings → Pages in the UI, or the `gh api` command
  above). After enabling, re-running the same workflow succeeded.
- **`gh api` paths need no leading slash on Git Bash.** Writing
  `/repos/...` makes the shell rewrite it into a Windows filesystem path
  and the call fails with `invalid API endpoint`. Drop the leading slash.

---

## What this model gives you, and what it costs

**Gives:** free forever, extremely fast, HTTPS included, essentially
unbreakable, deploys automatically on push, no maintenance ever.

**Costs:** no shared data, no accounts, no secrets, no server-side logic of
any kind. Perfect for documentation, portfolios, landing pages, or any app
whose data belongs to one browser. Wrong for anything where two people need
to see the same thing.

That limitation is what drives stage 2.

---

## Appendix: every term used on this page

| Term | Plain explanation |
|---|---|
| **Static hosting** | The server only hands over files exactly as they are. It never runs your code, never opens a database. Fast, cheap, and unable to remember anything. |
| **Static site** | A website made only of such files: HTML, CSS, JavaScript, images. |
| **HTML** | The language describing what a page contains — headings, text, buttons. |
| **CSS** | The language describing how it looks — colours, spacing, fonts. In this stage it's inside the same file, in a `<style>` block. |
| **JavaScript** | The only programming language browsers run. On a static site it's the *only* place your logic can live, since there's no server executing anything. |
| **Browser** | The visitor's program — Chrome, Firefox, Edge. On this stage, it does all the work. |
| **`localStorage`** | A small storage box the browser gives each website, saved on that device. Survives reloads and restarts, but never leaves that one browser. |
| **View source** | The browser feature showing a page's underlying code. On a static site this reveals *everything*, which is why secrets can never live here. |
| **API key / secret** | A password-like string that proves an app may use some paid or private service. Must never appear in code that ships to visitors. |
| **CDN** | A worldwide network of servers each holding a copy of your files, so visitors are served from one physically near them. GitHub Pages does this for free. |
| **HTTPS** | The encrypted version of web traffic — the padlock in the address bar. GitHub provides and renews it automatically here; in stage 4 you set it up by hand. |
| **Repository (repo)** | One project's folder plus its complete history, stored by Git. |
| **Branch / `main`** | A line of history within a repo. Ours is called `main`; pushing to it triggers the deploy. |
| **Push** | Uploading your saved snapshots (commits) from your machine to GitHub. |
| **GitHub Actions** | GitHub's automation service. It can run commands for you whenever something happens — here, on every push. |
| **Workflow** | One automation recipe, written as a `.yml` file in `.github/workflows/`. Ours has three steps: check out the code, package a folder, publish it. |
| **YAML (`.yml`)** | A plain-text format for configuration, where indentation indicates structure. |
| **Artifact** | A bundle of files produced by one workflow step and handed to the next. Here it's the contents of `01-github-pages/`. |
| **CI/CD** | "Continuous integration / continuous deployment" — the practice of having automation build and publish your work automatically instead of by hand. This workflow is a small, real example. |
| **`gh`** | GitHub's official command-line tool, used here to create the repo and enable Pages without opening a browser. |
| **API** | A way for programs to talk to a service directly instead of through its website. `gh api` calls GitHub's API to change repo settings. |
| **Deploy** | To make a new version of your code the one that's actually live. |
