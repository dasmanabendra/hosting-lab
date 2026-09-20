# Chapter 0: How the web actually works

*Read this before stage 0 if terms like "server," "DNS," or "port" are new.
Everything in the rest of the manual assumes this chapter.*

Nothing here is difficult. It's just rarely explained end to end, so most
people assemble a vague mental picture and never get to correct it.

---

## The one idea underneath everything

**Two computers passing messages.** One asks for something; the other sends
it back. The asking computer is the **client** (your browser). The
answering one is the **server**.

That's it. Every website, app, and API is an elaboration on that exchange.

A "server" isn't special hardware. It's any computer running a program that
waits for requests and answers them. In stage 0 of this manual, *your
laptop* is the server. The only thing separating your laptop from a real
web server is whether the rest of the internet can reach it — which is the
entire subject of this project.

---

## What happens when you type a URL

Take `https://dasmanabendra.github.io/hosting-lab/`. Between pressing Enter
and seeing the page, roughly six things happen.

### 1. The URL gets taken apart

```
https://dasmanabendra.github.io/hosting-lab/
└─┬─┘   └────────────┬────────────┘└────┬────┘
scheme            hostname            path
```

- **Scheme** (`https`) — which language to speak, and whether it's encrypted.
- **Hostname** (`dasmanabendra.github.io`) — *which computer* to talk to.
- **Path** (`/hosting-lab/`) — *what to ask it for* once connected.

### 2. The hostname is turned into an address (DNS)

Computers don't know names, only numeric addresses like `140.82.113.4`.
So the browser asks the **DNS** system — the internet's phone book — "what
is the address for `dasmanabendra.github.io`?"

DNS is a real, global network of servers whose only job is answering that
question. Your machine caches the answers for a while, which is why a site
you just visited loads faster, and why DNS changes can take time to "spread"
(the old answer is still cached in places).

**Why this matters later:** in stage 4 you get a server with an address like
`140.238.1.2` and nothing else. Turning that into a human name means adding
an entry to DNS yourself.

### 3. A connection is opened to that address, on a port

A single computer runs many network programs at once — a website, email, a
database. So an address isn't enough; you also need a **port number**, which
is like an apartment number at a street address.

Ports are just numbers, but conventions are strict:

| Port | Used for |
|---|---|
| **80** | HTTP (unencrypted web traffic) |
| **443** | HTTPS (encrypted web traffic) |
| 22 | SSH (getting a remote terminal) |
| 8000, 8080, 8501 | Common choices for apps under development |

When you type a URL with no port, the browser silently adds the usual one:
443 for `https`, 80 for `http`. This is why nobody types
`https://example.com:443`.

**Why this matters later:** in stage 4 your app listens on port 8000, but
visitors arrive on 443. Something has to bridge that gap — that's nginx.

### 4. If it's HTTPS, encryption gets set up

Before any real data moves, the two computers agree on encryption. The
server presents a **certificate** — a file, issued by a trusted authority,
vouching that this really is `dasmanabendra.github.io` and not an impostor.

Your browser checks it against a list of authorities it trusts, built into
your operating system. If the certificate is missing, expired, or for the
wrong name, you get the full-page security warning.

Certificates are issued for *names*, never for bare IP addresses. This is
precisely why stage 4 needs a domain before it can have HTTPS.

**Why this matters later:** stages 1, 2, and 3 hand you HTTPS already
working, and it feels like it's simply part of the internet. It isn't.
Stage 4 makes you obtain, install, and renew that certificate yourself, and
that's when you find out it was a real thing all along.

### 5. The request is sent

The browser sends a small block of text. Simplified:

```
GET /hosting-lab/ HTTP/1.1
Host: dasmanabendra.github.io
User-Agent: Mozilla/5.0 ...
Accept: text/html
```

The first word is the **method**, which says what kind of ask this is:

| Method | Meaning |
|---|---|
| **GET** | "Give me this." Should change nothing. |
| **POST** | "Here's some data, do something with it." Used by forms. |
| PUT / PATCH | "Update this existing thing." |
| DELETE | "Remove this." |

This manual's app uses only GET and POST, because plain HTML forms can only
send those two.

### 6. The server answers

The response is also just text — a status code, some headers, then the
content:

```
HTTP/1.1 200 OK
Content-Type: text/html

<!doctype html><html>...
```

Status codes are grouped by their first digit, which is most of what you
need to know:

| Code | Meaning | When you'll see it here |
|---|---|---|
| **200** | OK | Everything worked |
| **204** | OK, nothing to send back | — |
| **301 / 302 / 303** | "Go ask this other URL instead" (redirect) | After every add/toggle/delete in stage 0 |
| **400** | You sent something malformed | Bad form data |
| **401 / 403** | Not authenticated / not allowed | Forgetting `--allow-unauthenticated` in stage 3 |
| **404** | No such thing here | Wrong path; a missing `favicon.ico` |
| **500** | The server's own code crashed | A bug in the app |
| **502 / 504** | A proxy couldn't reach the app behind it | nginx is up but your app isn't — classic stage 4 failure |

That 502/504 row is worth remembering. It is the single most common
confusing failure in stage 4, and it tells you something precise: the front
door is fine, but nobody's home behind it.

---

## Static versus dynamic: the fork in the road

When that request arrives, the server can do one of two fundamentally
different things.

**Static:** find a file on disk and send it back, unchanged. The server
never runs your code, never makes a decision, never consults a database.
Every visitor gets byte-identical content.

**Dynamic:** run your program, which decides what to send. It can read a
database, check who's asking, and build a different answer for each visitor.

| | Static | Dynamic |
|---|---|---|
| Server runs your code | No | Yes |
| Can store data centrally | No | Yes |
| Per-visitor content | No | Yes |
| Cost | Nearly free | You're paying for a running computer |
| Ways it can break | Almost none | Many |
| This manual | Stage 1 | Stages 2, 3, 4 |

Neither is better. A huge share of the web — documentation, blogs,
marketing pages — is static and should be, because static is faster,
cheaper, and vastly harder to break or hack.

---

## Where data can live

This becomes the central drama of the manual, so it's worth laying out
plainly. There are only three places data can go:

1. **In the visitor's browser** (`localStorage`). Survives reloads, but only
   on that one device, in that one browser. Nobody else can see it, and
   clearing browser data destroys it. → Stage 1.
2. **On the server's disk** (a file, like SQLite). Shared by everyone,
   survives restarts — *provided the server keeps its disk*. → Stages 0, 2, 4.
3. **In a separate database service** that the app talks to over the network.
   Survives even if the app's own machine is destroyed, because the data
   was never on it. → What stage 3 would need, and doesn't have.

Stage 3's disaster comes from choosing option 2 on a platform that quietly
takes the disk away.

---

## "Hosting," defined properly

Now the word can be pinned down. Hosting is arranging for:

1. A computer that **stays running**, so the app is there when asked.
2. That computer being **reachable** from the public internet.
3. A **name** pointing at it (DNS).
4. **Encryption** so browsers trust it (a certificate).
5. Something that **restarts the app** when it crashes.
6. Somewhere the **data survives**.

Every hosting product is a different answer to "who does each of those six
things — you, or us?" That's the only question. This manual's four stages
are four different answers, from "all of it, for free, invisibly" to "all of
it is yours now."

---

## Check your understanding

Answers below — try first.

1. Why can't you get an HTTPS certificate for a bare IP address?
2. Your app is running fine on port 8000 on a server, but visitors to
   `https://yoursite.com` see nothing. Name two things that could be wrong.
3. A friend opens your stage 1 todo list. Why don't they see your todos?
4. You get a `502 Bad Gateway`. Is the problem more likely nginx or your app?
5. Why does a form use POST instead of GET?

<details>
<summary>Answers</summary>

1. Certificates vouch that you control a *name*. An IP address isn't a name,
   and nobody can prove ownership of one in the way the system requires.
2. Plenty of options: DNS isn't pointing at the server; nothing is listening
   on port 443; the firewall is blocking it; no reverse proxy is forwarding
   443 → 8000; the certificate is missing. Stage 4 covers all of these.
3. Their todos live in *their* browser's `localStorage`, not on any server.
   There is no shared copy anywhere — nothing was ever sent to GitHub.
4. Your app. 502 means the proxy is running and accepted the request, but
   whatever it tried to forward to didn't answer. nginx is fine; the thing
   behind it is down.
5. GET is defined as "just give me this, change nothing" — browsers
   pre-fetch, cache, and re-request GETs freely. Sending data that changes
   something via GET means a refresh or a cache could silently do it again.

</details>

---

**Next:** [Stage 0 — the app on your own machine](../00-local-app/)
