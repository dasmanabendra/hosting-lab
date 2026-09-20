# Chapter 5: Choosing a host for your next project

*Read this after working through the stages. It's the payoff — the point
of learning four hosting models is being able to pick one deliberately.*

---

## The only question that matters first

**Does your app need to remember anything that everyone shares?**

Almost every hosting decision follows from this, and people routinely get it
wrong by starting from the technology instead.

- **No** → static hosting. You are done. Use GitHub Pages, Netlify, or
  Cloudflare Pages, pay nothing, and never think about servers again.
- **Yes, a little** → managed platform plus a managed database.
- **Yes, and it's complicated** → you still probably want a managed platform
  plus a managed database. Reach for a VM only for a specific reason you can
  name out loud.

The instinct after finishing stage 4 is to feel that a VM is the "real"
answer and everything else is training wheels. That's backwards. Stage 4
exists so you understand what managed platforms do for you, not so you
reproduce it by hand every time.

---

## The decision, as a flowchart

```
Does the server need to run your code at all?
│
├─ NO ──────────────► STATIC HOSTING
│                     GitHub Pages / Netlify / Cloudflare Pages
│                     Free, fast, unbreakable. Stop here.
│
└─ YES
   │
   Does it need to store data that outlives a single visit?
   │
   ├─ NO ───────────► CONTAINERS / SERVERLESS
   │                  Cloud Run, Fly.io, Vercel functions
   │                  Statelessness costs you nothing here.
   │
   └─ YES
      │
      Can the data live in a managed database (not a local file)?
      │
      ├─ YES ───────► CONTAINERS + MANAGED DATABASE  ← the default
      │               Cloud Run + Cloud SQL, Fly.io + Postgres,
      │               Render + its Postgres
      │               Scales, survives, little to maintain.
      │
      └─ NO ────────► A VM
                      Oracle / Hetzner / DigitalOcean
                      Because you need: a real filesystem, unusual
                      software, GPU access, long-running background
                      work, strict data-location rules, or predictable
                      flat cost at high traffic.
```

---

## Good and bad reasons to choose a VM

**Good reasons**

- You genuinely need a persistent filesystem (the SQLite situation).
- You need software that won't run on a managed platform.
- Long-running background work — managed platforms often kill requests after
  a fixed timeout.
- Cost predictability at sustained high traffic, where usage-based billing
  becomes more expensive than one fixed machine.
- Legal or contractual requirements about *where* data physically lives.
- You want to learn. Completely legitimate — just name it honestly.

**Bad reasons**

- "It's cheaper." At low traffic, managed platforms are usually free and a
  VM isn't. Your time is also a cost.
- "It's more professional." Serious companies run enormous systems on managed
  platforms specifically to avoid this work.
- "I want control." Control is a bill, payable in security patches, certificate
  renewals, backups, and 3am outages that are now yours.
- "Containers seem complicated." They're less complicated than everything
  stage 4 makes you do.

---

## What things actually cost

Rough figures, and they change — always check current pricing. The point is
the *shape* of the costs, not the exact numbers.

### A small personal project (a few hundred visits a month)

| Approach | Monthly cost | What you maintain |
|---|---|---|
| Static hosting | **$0** | Nothing |
| Streamlit Community Cloud | **$0** | Nothing |
| Cloud Run (within free tier) | **$0** | A Dockerfile |
| Cloud Run + managed database | **~$7–25** | A Dockerfile — the database is the cost |
| Oracle Always Free VM | **$0** | The entire machine |
| A VM anywhere else | **~$4–6** | The entire machine |
| A domain name | **~$1/month** ($10–15/year) | One DNS record |

Note the trap: on Cloud Run the *app* is free, but the managed database
usually isn't. A small managed Postgres is often the single biggest line
item in a hobby project's bill — which is exactly why Oracle's free VM plus
SQLite is such a good deal for genuinely small things.

### If it gets popular (say 100k visits a month)

| Approach | Rough monthly cost | What changes |
|---|---|---|
| Static hosting | Still **$0** | Nothing — CDNs eat this easily |
| Cloud Run + database | **~$20–60** | Scales up automatically; you pay per use |
| One VM | **Still ~$5** | Nothing — *until it falls over*, and then it's your evening |

This is the real trade. Managed platforms convert traffic into money
automatically. A VM converts traffic into *your personal problem* at a fixed
price. Which is better depends entirely on whether you'd rather spend money
or attention.

### How to not get a surprise bill

1. **Set a budget alert** on any usage-based platform. Google Cloud, AWS, and
   Azure all support this, and it should be the first thing you configure.
2. **Cap the maximum instances** on autoscaling platforms. Cloud Run's
   `--max-instances` bounds your worst case.
3. Prefer platforms that **stop serving** rather than keep billing when you
   exceed a free tier, if you have that choice.
4. Remember that "free tier" usually means a *monthly allowance*, not a hard
   cap. Exceeding it charges you rather than switching you off.

---

## Matching the stages to real situations

| If you're building... | Use | Because |
|---|---|---|
| Portfolio, blog, docs, landing page | Static (stage 1 model) | No backend needed; free and unbreakable |
| A data dashboard or internal tool for a few people | Streamlit (stage 2 model) | Fastest path from Python script to shared URL |
| A normal web app or API | Containers + managed DB (stage 3 model, done properly) | Scales, survives, minimal maintenance |
| Something needing unusual software or a real filesystem | A VM (stage 4 model) | The only option that gives you the whole machine |
| A side project you want to cost exactly $0 forever | Oracle free VM, or static | Free tiers that don't expire |

---

## The honest summary

After all four stages, the useful conclusion isn't "VMs are real hosting" or
"managed platforms are for beginners." It's:

**Every hosting model is the same six jobs — stay running, be reachable, have
a name, have a certificate, restart on failure, keep the data — allocated
differently between you and a vendor.** Paying someone else to do those jobs
is usually correct. Knowing exactly what you're paying them *for* is what
you just learned, and it's the difference between choosing a platform and
cargo-culting one.

---

**Back to:** [the manual's front page](../README.md)
