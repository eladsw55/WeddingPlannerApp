from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional, List

app = FastAPI()

# אפשור CORS כדי שה-Frontend יוכל לדבר עם ה-Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# חיבור ל-DB ויצירת טבלאות
def init_db():
    conn = sqlite3.connect("wedding.db")
    cursor = conn.cursor()
    # טבלת תקציב
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE,
            amount REAL,
            notes TEXT
        )
    """)
    # טבלת הגדרות כלליות (תקציב יעד)
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
    
    # --- טבלת אורחים חדשה ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            count INTEGER,
            status TEXT, -- 'confirmed', 'maybe', 'declined'
            side TEXT    -- 'groom', 'bride'
        )
    """)
    conn.commit()
    conn.close()

init_db()

# מודלים של נתונים
class BudgetItem(BaseModel):
    category: str
    amount: float
    notes: Optional[str] = ""

class Guest(BaseModel):
    name: str
    count: int
    status: str
    side: str

# --- Endpoints לתקציב ---
@app.post("/budget/add")
def add_budget(item: BudgetItem):
    conn = sqlite3.connect("wedding.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO budget (category, amount, notes) VALUES (?, ?, ?)",
                   (item.category, item.amount, item.notes))
    conn.commit()
    conn.close()
    return {"message": "Success"}

@app.get("/budget/summary")
def get_summary():
    conn = sqlite3.connect("wedding.db")
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
    conn = sqlite3.connect("wedding.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('total_budget', ?)", (amount,))
    conn.commit()
    conn.close()
    return {"message": "Total updated"}

# --- Endpoints חדשים לאורחים ---
@app.get("/guests")
def get_guests():
    conn = sqlite3.connect("wedding.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, count, status, side FROM guests")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "count": r[2], "status": r[3], "side": r[4]} for r in rows]

@app.post("/guests/add")
def add_guest(guest: Guest):
    conn = sqlite3.connect("wedding.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO guests (name, count, status, side) VALUES (?, ?, ?, ?)",
                   (guest.name, guest.count, guest.status, guest.side))
    conn.commit()
    conn.close()
    return {"message": "Guest added"}

@app.delete("/guests/{guest_id}")
def delete_guest(guest_id: int):
    conn = sqlite3.connect("wedding.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
    conn.commit()
    conn.close()
    return {"message": "Guest deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
