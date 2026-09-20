import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

DB_PATH = Path(__file__).resolve().parent / "data" / "todos.db"


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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
    return conn


def list_todos(conn):
    return conn.execute("SELECT * FROM todos ORDER BY id ASC").fetchall()


def add_todo(conn, task):
    conn.execute(
        "INSERT INTO todos (task, done, created_at) VALUES (?, 0, ?)",
        (task.strip()[:200], datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()


def toggle_todo(conn, todo_id):
    conn.execute("UPDATE todos SET done = NOT done WHERE id = ?", (todo_id,))
    conn.commit()


def delete_todo(conn, todo_id):
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()


st.set_page_config(page_title="Todo List", page_icon="✅")
st.title("Todo List")

st.info(
    "This list lives on a server, so **everyone visiting this URL sees the "
    "same todos** — there are no user accounts. That's the difference a "
    "backend makes, for better and worse."
)

conn = get_db()

with st.form("add", clear_on_submit=True):
    col_input, col_button = st.columns([4, 1])
    task = col_input.text_input(
        "New task", placeholder="What needs doing?", label_visibility="collapsed"
    )
    if col_button.form_submit_button("Add", use_container_width=True) and task.strip():
        add_todo(conn, task)
        st.rerun()

todos = list_todos(conn)

if not todos:
    st.caption("Nothing to do — add a task above.")

for todo in todos:
    col_check, col_task, col_delete = st.columns([1, 8, 1])

    if col_check.button("✓" if todo["done"] else "○", key=f"toggle-{todo['id']}"):
        toggle_todo(conn, todo["id"])
        st.rerun()

    if todo["done"]:
        col_task.markdown(f"~~{todo['task']}~~")
    else:
        col_task.write(todo["task"])

    if col_delete.button("✕", key=f"delete-{todo['id']}"):
        delete_todo(conn, todo["id"])
        st.rerun()
