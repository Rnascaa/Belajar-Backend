import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

DB_PATH = "todos.db"

app = FastAPI(title="To-Do List API", version="1.0.0")


# ---------- Database ----------
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


init_db()


# ---------- Schema ----------
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    done: Optional[bool] = None


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["done"] = bool(d["done"])
    return d


# ---------- Endpoint ----------
@app.get("/")
def root():
    return {"message": "To-Do API berjalan. Buka /docs untuk dokumentasi."}


@app.post("/todos", status_code=201)
def create_todo(data: TodoCreate):
    with get_db() as db:
        cur = db.execute(
            "INSERT INTO todos (title, description) VALUES (?, ?)",
            (data.title, data.description),
        )
        row = db.execute("SELECT * FROM todos WHERE id = ?", (cur.lastrowid,)).fetchone()
    return row_to_dict(row)


@app.get("/todos")
def list_todos(done: Optional[bool] = Query(None, description="Filter status selesai")):
    query, params = "SELECT * FROM todos", []
    if done is not None:
        query += " WHERE done = ?"
        params.append(int(done))
    query += " ORDER BY id DESC"
    with get_db() as db:
        rows = db.execute(query, params).fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    with get_db() as db:
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Tugas tidak ditemukan")
    return row_to_dict(row)


@app.patch("/todos/{todo_id}")
def update_todo(todo_id: int, data: TodoUpdate):
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(400, "Tidak ada data yang diubah")
    if "done" in fields:
        fields["done"] = int(fields["done"])

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_db() as db:
        cur = db.execute(
            f"UPDATE todos SET {set_clause} WHERE id = ?",
            (*fields.values(), todo_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Tugas tidak ditemukan")
        row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return row_to_dict(row)


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    with get_db() as db:
        cur = db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Tugas tidak ditemukan")
