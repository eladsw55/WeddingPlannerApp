from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI()

# אפשור תקשורת מול ה-Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = "wedding_v2.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # טבלת תקציב
    cursor.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, category TEXT UNIQUE, amount REAL, notes TEXT)")
    # טבלת הגדרות
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
    # טבלת אורחים
    cursor.execute("CREATE TABLE IF NOT EXISTS guests (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, count INTEGER, status TEXT, side TEXT)")
    # טבלת משימות
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, category TEXT, completed INTEGER DEFAULT 0)")
    
    # הכנסת משימות ראשוניות אם הטבלה ריקה
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        defaults = [
            ("סגירת אולם וקייטרינג", "לוגיסטיקה"),
            ("בחירת צלם", "ספקים"),
            ("סגירת DJ", "ספקים"),
            ("פתיחת תיק ברבנות", "בירוקרטיה"),
            ("בחירת שמלה וחליפה", "אישי")
        ]
        cursor.executemany("INSERT INTO tasks (title, category) VALUES (?, ?)", defaults)
        
    conn.commit()
    conn.close()

init_db()

# Models
class BudgetItem(BaseModel):
    category: str
    amount: float
    notes: str = ""

class GuestItem(BaseModel):
    name: str
    count: int
    status: str
    side: str

# API Endpoints - Budget
@app.get("/budget/summary")
def get_summary():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM budget")
    spent = cursor.fetchone()[0] or 0
    cursor.execute("SELECT value FROM settings WHERE key='total_budget'")
    total = cursor.fetchone()
    total = total[0] if total else 0
    conn.close()
    return {"spent": spent, "total": total}

@app.post("/budget/update_total")
def update_total(amount: float):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('total_budget', ?)", (amount,))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/budget/add")
def add_budget(item: BudgetItem):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO budget (category, amount, notes) VALUES (?, ?, ?)", (item.category, item.amount, item.notes))
    conn.commit()
    conn.close()
    return {"status": "success"}

# API Endpoints - Guests
@app.get("/guests")
def get_guests():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, count, status, side FROM guests")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "count": r[2], "status": r[3], "side": r[4]} for r in rows]

@app.post("/guests/add")
def add_guest(guest: GuestItem):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO guests (name, count, status, side) VALUES (?, ?, ?, ?)", (guest.name, guest.count, guest.status, guest.side))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.delete("/guests/{guest_id}")
def delete_guest(guest_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

# API Endpoints - Tasks
@app.get("/tasks")
def get_tasks():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, category, completed FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "title": r[1], "category": r[2], "completed": bool(r[3])} for r in rows]

@app.post("/tasks/toggle/{task_id}")
def toggle_task(task_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = 1 - completed WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}
