import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "todos.db"

app = FastAPI(title="Todo List")


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
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def render_page(todos: list[sqlite3.Row]) -> str:
    rows = "\n".join(
        f"""<li class="{'done' if t['done'] else ''}">
              <form method="post" action="/todos/{t['id']}/toggle">
                <button type="submit" class="check">{'✓' if t['done'] else '○'}</button>
              </form>
              <span>{escape(t['task'])}</span>
              <form method="post" action="/todos/{t['id']}/delete">
                <button type="submit" class="delete">✕</button>
              </form>
            </li>"""
        for t in todos
    )
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Todo List</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 32rem; margin: 2rem auto; padding: 0 1rem; }}
    form.add {{ display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }}
    form.add input {{ flex: 1; font: inherit; padding: 0.4rem; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ display: flex; align-items: center; gap: 0.6rem; padding: 0.4rem 0; border-bottom: 1px solid #eee; }}
    li.done span {{ text-decoration: line-through; color: #888; }}
    li form {{ margin: 0; }}
    button {{ font: inherit; cursor: pointer; }}
    button.check {{ background: none; border: 1px solid #ccc; border-radius: 50%; width: 1.8rem; height: 1.8rem; }}
    button.delete {{ background: none; border: none; color: #c00; }}
    li span {{ flex: 1; }}
  </style>
</head>
<body>
  <h1>Todo List</h1>
  <form class="add" method="post" action="/todos">
    <input name="task" placeholder="What needs doing?" required maxlength="200">
    <button type="submit">Add</button>
  </form>
  <ul>
    {rows or "<li>Nothing to do — add a task above.</li>"}
  </ul>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        todos = conn.execute("SELECT * FROM todos ORDER BY id ASC").fetchall()
    return render_page(todos)


@app.post("/todos")
def add_todo(task: str = Form(...)):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO todos (task, done, created_at) VALUES (?, 0, ?)",
            (task.strip()[:200], datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: int):
    with get_db() as conn:
        conn.execute("UPDATE todos SET done = NOT done WHERE id = ?", (todo_id,))
        conn.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/todos/{todo_id}/delete")
def delete_todo(todo_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/health")
def health():
    return {"status": "ok"}
