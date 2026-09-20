# Chapter 6: Not getting hacked

*Read this before stage 4. Stages 1–3 are largely protected by the platform;
a VM is not, and it is genuinely yours to secure.*

This isn't a security course. It's the short list of things that actually
go wrong for small projects, in rough order of how often.

---

## The honest risk picture

Nobody is targeting your todo list personally. What actually happens is
**automated scanning**: bots continuously sweep the entire internet looking
for known-weak machines. A new VM with a public IP typically starts
receiving login attempts within minutes of existing.

This sounds alarming and mostly isn't, because the defences are simple and
largely one-time. But it does mean "nobody knows my server exists" is not a
defence. They find it immediately, automatically, and without malice.

---

## The rules, in priority order

### 1. Never put secrets in a repository

The single most common serious mistake, and the reason this manual's repo
has a standing rule about it.

A **secret** is anything that grants access: API keys, database passwords,
cloud service-account files, SSH private keys, `.env` files. Once pushed to
a public repo they are compromised — permanently. Bots scan GitHub for
exactly this, sometimes finding keys within *seconds* of a push, and the
usual outcome is someone running up an enormous cloud bill on your account.

Deleting the commit afterwards does **not** fix it. Git keeps history, forks
and caches exist, and it has already been scraped. The only real remedy is
to **revoke and reissue the secret**.

Instead, secrets belong in: environment variables, the cloud provider's own
secret manager, GitHub Actions secrets, or a local file listed in
`.gitignore`.

### 2. Use SSH keys, not passwords

Password logins can be guessed by bots, endlessly, forever. Key-based login
can't be meaningfully brute-forced.

Most cloud providers, Oracle included, default to key-only login — don't
change that. And on the VM:

```bash
sudo nano /etc/ssh/sshd_config
# ensure:  PasswordAuthentication no
sudo systemctl restart ssh
```

Your **private** key (usually `~/.ssh/id_ed25519`, no `.pub`) never leaves
your machine, is never emailed, never pasted into chat, never committed. The
`.pub` half is the one that goes on servers and is safe to share.

### 3. Expose as little as possible

Every open port is a door. The rule: if nothing needs to reach it from the
internet, it shouldn't be reachable from the internet.

This is exactly why stage 4 binds the app to `127.0.0.1:8000` rather than
`0.0.0.0:8000`. Only nginx can reach it; the outside world can't touch the
app directly at all. On a VM, ports 22 (SSH), 80, and 443 are typically all
you should have open.

Databases especially should never be publicly reachable. Historically, tens
of thousands of databases have been found exposed to the open internet with
no password — a mistake that requires no sophistication to exploit.

### 4. Install security updates

Vulnerabilities are found in common software constantly. Patches ship
quickly; the danger window is machines that never apply them. Managed
platforms patch for you invisibly. On a VM:

```bash
sudo apt update && sudo apt upgrade        # occasionally, by hand
sudo apt install unattended-upgrades       # or let security patches auto-apply
```

A server nobody has updated in two years is the classic compromised machine.

### 5. Keep HTTPS working

certbot sets up automatic renewal, but verify it actually functions —
expired certificates are a common, entirely avoidable outage:

```bash
sudo certbot renew --dry-run
```

### 6. Back up anything you'd miss

A VM's disk is durable, not immortal. Stage 4's SQLite file exists in
exactly one place, and "the server died" and "I deleted the wrong thing" are
both ordinary events.

```bash
# copy the database off the server periodically
scp ubuntu@<server-ip>:~/hosting/04-oracle-vps/data/todos.db ./backup/
```

A backup you have never restored from isn't yet known to be a backup. Test
it once.

### 7. Don't trust what visitors send you

Any text a visitor submits may be hostile. Two classic attacks, and how this
app avoids them:

**SQL injection** — crafted input that changes what your database command
*means*, potentially dumping or destroying everything. Avoided by passing
values as parameters rather than gluing them into the command text:

```python
# safe — the value can never be interpreted as a command
conn.execute("INSERT INTO todos (task) VALUES (?)", (task,))

# never do this
conn.execute(f"INSERT INTO todos (task) VALUES ('{task}')")
```

**XSS (cross-site scripting)** — submitted text containing markup that the
browser then executes in other visitors' sessions. Avoided by escaping user
text before putting it in a page. Stage 0 uses Python's `escape()`; stage 1
sets `textContent` rather than `innerHTML`, which escapes automatically.

Both defences are already in this app's code. Both are one careless line
away from being undone, which is why they're worth recognising.

---

## What stage 4 specifically leaves undone

Honesty about this manual's own scope. The stage 4 setup is deliberately
minimal, and a production system would also want:

- **A firewall tool** like `ufw` with a default-deny policy, rather than the
  hand-written `iptables` rules in `setup-server.sh`.
- **`fail2ban`**, which watches logs and temporarily blocks addresses that
  repeatedly fail to log in.
- **Rate limiting** in nginx, so one visitor can't overwhelm the app.
- **No public write access.** This todo list lets any visitor edit or delete
  anything, because it has no accounts. That's fine for a teaching exercise
  and unacceptable for anything real.
- **Monitoring**, so you learn the site is down from an alert rather than
  from a person.

---

## The short version

| Do | Don't |
|---|---|
| Keep secrets out of git | Commit `.env`, keys, or service-account files |
| Use SSH keys | Enable password login |
| Open only 22, 80, 443 | Expose the app or a database directly |
| Apply security updates | Leave a VM untouched for months |
| Back up the data | Assume one disk is forever |
| Escape user input; parameterise SQL | Build SQL or HTML by string-concatenation |

If a secret does leak: **revoke it immediately**, then worry about tidying
history. Rotation is the fix; deletion is not.

---

**Next:** [Stage 4 — the Oracle VM](../04-oracle-vps/)
