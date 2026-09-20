# Chapter 7: What this manual didn't teach you

*The map beyond. Knowing the shape of what you don't know is most of what
separates "I followed a tutorial" from "I can navigate this field."*

This manual covers one narrow slice: getting a small app from your machine
onto the internet, four ways. That slice is genuinely foundational, and it's
also small. Here's the territory around it, roughly in the order it becomes
relevant.

---

## Immediately useful next

### Managed databases

The gap stage 3 deliberately left open. Instead of a file on disk, the app
talks over the network to a database that is somebody else's problem to keep
alive, backed up, and patched.

Learn: **PostgreSQL** (the default serious choice), connection strings, and
why you never hardcode one. Try: Cloud SQL, Supabase, Neon, or Railway's
Postgres. Doing this turns stage 3 from broken into genuinely production-shaped.

### Environment variables and configuration

Real apps change behaviour between your laptop and production — different
database, different keys, debug on or off — without changing the code. The
universal mechanism is environment variables, plus a local `.env` file that
is never committed. Closely tied to the secrets rule in
[chapter 6](security-basics.md).

### Logs and monitoring

Right now you'd discover the site was down because you happened to look.
Real operation means: structured logs you can search, an uptime check that
pings the site and alerts you, and error tracking that tells you a visitor
hit a bug before they email you about it.

Look at: `journalctl` on a VM, Cloud Logging on Google, UptimeRobot for
free checks, Sentry for error tracking.

### Backups you've actually restored

Stage 4's data exists in exactly one place. A scheduled copy off the machine
— and one rehearsed restore — is the difference between an incident and a
catastrophe.

---

## When a project grows

### CI/CD, properly

Stage 1's workflow is a real but tiny example. The full version runs your
tests on every change, refuses to deploy if they fail, deploys automatically
when they pass, and can roll back. Once a second person is involved, this
stops being optional.

### Automated tests

This manual tested by clicking. That doesn't scale and doesn't survive you
forgetting how it works. Learn `pytest` for Python and the distinction
between unit tests (one function) and integration tests (the whole app,
against a real database).

### Zero-downtime deploys

Stage 4's `deploy.sh` restarts the app, which means seconds of downtime.
Real deployments start the new version, confirm it's healthy, shift traffic
over, then retire the old one. Terms to look up: blue-green deployment,
rolling deployment, health checks — which is finally what that `/health`
endpoint is for.

### Infrastructure as code

Stage 4 was configured by running scripts on one machine by hand. If that
machine dies, could you rebuild it exactly? Tools like **Terraform** and
**Ansible** make infrastructure a file in git — reviewable, repeatable,
and rebuildable.

---

## The bigger world

### Containers beyond one container

Stage 3 ran one container. Real systems run several that must start in the
right order and find each other: **Docker Compose** for one machine,
**Kubernetes** for many. Kubernetes is genuinely complex and is the correct
answer far less often than its popularity implies — for most projects,
Cloud Run or similar is both simpler and sufficient.

### CDNs and caching

Stage 1 got a CDN for free and never thought about it. Once your app is
dynamic, deciding what can be cached, for how long, and how to invalidate it
becomes one of the highest-leverage performance tools available.

### Authentication

This app has no accounts, which is why everyone shares one todo list. Adding
real users means sessions, password hashing (never store a raw password),
and probably an identity provider like Auth0, Clerk, or "sign in with
Google." Getting this right yourself is harder than it looks, and is one of
the better things to delegate.

### Scaling for real

Load balancers across many servers, read replicas, background job queues,
caching layers. Worth knowing these exist; almost never worth building
before you have a measured problem. Premature scaling work is one of the
most reliable ways to waste months.

---

## A caution worth internalising

Everything above is interesting, and most of it you will never need. The
common failure mode in this field isn't ignorance — it's adopting heavy
machinery for problems you don't have, because the machinery is what serious
people are seen to use.

The reasonable default for a new project stays what
[chapter 5](choosing-a-host.md) concluded: **static if you can, managed
platform plus managed database if you can't, a VM when you can name the
specific reason.** Add complexity when something actually hurts, and not
before.

---

## If you only do three things next

1. **Redo stage 3 with a managed database**, so the todos survive. It closes
   the one loop this manual deliberately left open, and it's the single most
   transferable thing here.
2. **Put an uptime check on whatever you deploy.** Five minutes; the
   difference between knowing and not knowing.
3. **Build something you actually want**, and host it. Everything above is
   theory until a real project forces the decisions.

---

**Back to:** [the manual's front page](../README.md)
