import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "guestbook.db"

app = FastAPI(title="Guestbook")


@contextmanager
def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


@app.on_event("startup")
def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def render_page(messages: list[sqlite3.Row]) -> str:
    rows = "\n".join(
        f"<li><strong>{escape(m['name'])}</strong>: {escape(m['message'])} "
        f"<time>{escape(m['created_at'])}</time></li>"
        for m in messages
    )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Guestbook</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }}
    li {{ margin-bottom: 0.5rem; }}
    time {{ color: #777; font-size: 0.85em; display: block; }}
    form {{ display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 2rem; }}
    input, textarea {{ font: inherit; padding: 0.4rem; }}
  </style>
</head>
<body>
  <h1>Guestbook</h1>
  <form method="post" action="/messages">
    <input name="name" placeholder="Your name" required maxlength="80">
    <textarea name="message" placeholder="Say something" required maxlength="500"></textarea>
    <button type="submit">Sign guestbook</button>
  </form>
  <ul>
    {rows or "<li>No messages yet — be the first.</li>"}
  </ul>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        messages = conn.execute(
            "SELECT * FROM messages ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return render_page(messages)


@app.post("/messages")
def add_message(name: str = Form(...), message: str = Form(...)):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO messages (name, message, created_at) VALUES (?, ?, ?)",
            (name.strip()[:80], message.strip()[:500], datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok"}
