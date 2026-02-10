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

DATABASE = "wedding_app.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # טבלת תקציב בסיסית
    cursor.execute("CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY, category TEXT UNIQUE, amount REAL, notes TEXT)")
    # טבלת הגדרות (לתקציב היעד הכולל)
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value REAL)")
    conn.commit()
    conn.close()

init_db()

# מודל נתונים לסעיף תקציב
class BudgetItem(BaseModel):
    category: str
    amount: float
    notes: str = ""

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
