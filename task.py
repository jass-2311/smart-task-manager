"""Task CRUD queries scoped to authenticated user."""
from database import connect

def validate(title, priority):
    title = title.strip()
    if not title or len(title) > 120:
        raise ValueError("Task title must be 1–120 characters.")
    if priority not in {"low", "medium", "high"}:
        raise ValueError("Priority must be low, medium or high.")
    return title

def add_task(uid, title, priority="medium", due_date=None):
    title = validate(title, priority)
    with connect() as db:
        cursor = db.execute("INSERT INTO tasks(user_id,title,priority,due_date) VALUES(?,?,?,?)", (uid,title,priority,due_date))
        return cursor.lastrowid

def view_tasks(uid):
    with connect() as db:
        rows = db.execute("SELECT id,title,priority,due_date FROM tasks WHERE user_id=? ORDER BY id", (uid,)).fetchall()
    return [dict(row) for row in rows]

def get_task(uid, task_id):
    with connect() as db:
        row = db.execute("SELECT id,title,priority,due_date FROM tasks WHERE user_id=? AND id=?", (uid,task_id)).fetchone()
    return dict(row) if row else None

def update_task(uid, task_id, title, priority, due_date=None):
    title = validate(title, priority)
    with connect() as db:
        cursor = db.execute("UPDATE tasks SET title=?,priority=?,due_date=? WHERE id=? AND user_id=?", (title,priority,due_date,task_id,uid))
        return cursor.rowcount > 0

def delete_task(uid, task_id):
    with connect() as db:
        cursor = db.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id,uid))
        return cursor.rowcount > 0
