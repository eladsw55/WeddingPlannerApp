"""
Wedding Elite - Backend API
FastAPI application for wedding planning
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
import sqlite3
from contextlib import contextmanager

app = FastAPI(
    title="Wedding Elite API",
    description="Backend API for wedding planning application",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATABASE ====================
DATABASE = "wedding_elite.db"

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with all required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Weddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                groom_name TEXT NOT NULL,
                bride_name TEXT NOT NULL,
                wedding_date DATE NOT NULL,
                total_budget REAL DEFAULT 165000,
                guest_count INTEGER DEFAULT 400,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Budget categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wedding_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                icon TEXT,
                planned_amount REAL NOT NULL,
                actual_amount REAL DEFAULT 0,
                FOREIGN KEY (wedding_id) REFERENCES weddings (id)
            )
        """)
        
        # Vendors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wedding_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                deposit_paid REAL DEFAULT 0,
                payment_date DATE,
                notes TEXT,
                is_confirmed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wedding_id) REFERENCES weddings (id),
                FOREIGN KEY (category_id) REFERENCES budget_categories (id)
            )
        """)
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wedding_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                timeline_period TEXT NOT NULL,
                due_date DATE,
                is_completed BOOLEAN DEFAULT 0,
                is_urgent BOOLEAN DEFAULT 0,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wedding_id) REFERENCES weddings (id)
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wedding_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (wedding_id) REFERENCES weddings (id)
            )
        """)
        
        conn.commit()

# Initialize database on startup
init_database()

# ==================== PYDANTIC MODELS ====================

class WeddingCreate(BaseModel):
    groom_name: str = Field(..., min_length=1)
    bride_name: str = Field(..., min_length=1)
    wedding_date: date
    total_budget: Optional[float] = 165000
    guest_count: Optional[int] = 400

class WeddingResponse(BaseModel):
    id: int
    groom_name: str
    bride_name: str
    wedding_date: date
    total_budget: float
    guest_count: int
    days_remaining: int

class BudgetCategoryCreate(BaseModel):
    name: str
    icon: str
    planned_amount: float

class BudgetCategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    planned_amount: float
    actual_amount: float
    percentage_spent: float

class VendorCreate(BaseModel):
    category_id: int
    name: str
    amount: float
    deposit_paid: Optional[float] = 0
    payment_date: Optional[date] = None
    notes: Optional[str] = ""

class VendorResponse(BaseModel):
    id: int
    category_id: int
    name: str
    amount: float
    deposit_paid: float
    payment_date: Optional[date]
    notes: str
    is_confirmed: bool

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    timeline_period: str
    due_date: Optional[date] = None
    is_urgent: Optional[bool] = False

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    timeline_period: str
    due_date: Optional[date]
    is_completed: bool
    is_urgent: bool

class DashboardResponse(BaseModel):
    days_remaining: int
    control_percentage: int
    tasks_completed: int
    tasks_urgent: int
    budget_planned: float
    budget_actual: float
    budget_remaining: float
    budget_percentage: float

# ==================== HELPER FUNCTIONS ====================

def calculate_days_remaining(wedding_date: date) -> int:
    """Calculate days remaining until wedding"""
    today = datetime.now().date()
    delta = wedding_date - today
    return max(0, delta.days)

def get_default_budget_categories():
    """Return default budget categories for new weddings"""
    return [
        {"name": "אולם ואירוח", "icon": "🏛️", "planned_amount": 90000},
        {"name": "צילום ווידאו", "icon": "📸", "planned_amount": 15000},
        {"name": "מוזיקה ובידור", "icon": "🎵", "planned_amount": 12000},
        {"name": "פרחים ועיצוב", "icon": "💐", "planned_amount": 10500},
        {"name": "לבוש ויופי", "icon": "🤵", "planned_amount": 9000},
        {"name": "הזמנות ומתנות", "icon": "🎁", "planned_amount": 7500},
        {"name": "אחר", "icon": "✨", "planned_amount": 6000},
    ]

def get_default_tasks():
    """Return default timeline tasks"""
    return [
        # 9-12 months before
        {"title": "בחרו תאריך ואולם", "timeline_period": "9-12", "is_urgent": False},
        {"title": "הזמינו צלם ווידאו", "timeline_period": "9-12", "is_urgent": False},
        {"title": "תפריט ראשוני עם קייטרינג", "timeline_period": "9-12", "is_urgent": False},
        
        # 6-9 months before
        {"title": "בחרו DJ או להקה", "timeline_period": "6-9", "is_urgent": False},
        {"title": "התחילו לחפש שמלת כלה", "timeline_period": "6-9", "is_urgent": False},
        {"title": "עיצוב הזמנות", "timeline_period": "6-9", "is_urgent": False},
        
        # 3-6 months before
        {"title": "הדפיסו הזמנות", "timeline_period": "3-6", "is_urgent": True},
        {"title": "קבעו מאפרת ומעצב שיער", "timeline_period": "3-6", "is_urgent": False},
        {"title": "תכננו עיצוב פרחים", "timeline_period": "3-6", "is_urgent": False},
        
        # 1-3 months before
        {"title": "ספירת אורחים סופית", "timeline_period": "1-3", "is_urgent": False},
        {"title": "פגישה אחרונה עם ספקים", "timeline_period": "1-3", "is_urgent": False},
        {"title": "תכנון מסלול יום החתונה", "timeline_period": "1-3", "is_urgent": False},
    ]

# ==================== API ENDPOINTS ====================

@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Wedding Elite API",
        "version": "1.0.0",
        "status": "running"
    }

# ==================== WEDDING ENDPOINTS ====================

@app.post("/weddings", response_model=WeddingResponse)
def create_wedding(wedding: WeddingCreate):
    """Create a new wedding"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Insert wedding
        cursor.execute("""
            INSERT INTO weddings (groom_name, bride_name, wedding_date, total_budget, guest_count)
            VALUES (?, ?, ?, ?, ?)
        """, (wedding.groom_name, wedding.bride_name, wedding.wedding_date, 
              wedding.total_budget, wedding.guest_count))
        
        wedding_id = cursor.lastrowid
        
        # Add default budget categories
        for category in get_default_budget_categories():
            cursor.execute("""
                INSERT INTO budget_categories (wedding_id, name, icon, planned_amount)
                VALUES (?, ?, ?, ?)
            """, (wedding_id, category["name"], category["icon"], category["planned_amount"]))
        
        # Add default tasks
        for task in get_default_tasks():
            cursor.execute("""
                INSERT INTO tasks (wedding_id, title, timeline_period, is_urgent)
                VALUES (?, ?, ?, ?)
            """, (wedding_id, task["title"], task["timeline_period"], task["is_urgent"]))
        
        conn.commit()
        
        # Return wedding data
        days_remaining = calculate_days_remaining(wedding.wedding_date)
        
        return WeddingResponse(
            id=wedding_id,
            groom_name=wedding.groom_name,
            bride_name=wedding.bride_name,
            wedding_date=wedding.wedding_date,
            total_budget=wedding.total_budget,
            guest_count=wedding.guest_count,
            days_remaining=days_remaining
        )

@app.get("/weddings/{wedding_id}", response_model=WeddingResponse)
def get_wedding(wedding_id: int):
    """Get wedding details"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM weddings WHERE id = ?", (wedding_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Wedding not found")
        
        wedding_date = datetime.strptime(row["wedding_date"], "%Y-%m-%d").date()
        days_remaining = calculate_days_remaining(wedding_date)
        
        return WeddingResponse(
            id=row["id"],
            groom_name=row["groom_name"],
            bride_name=row["bride_name"],
            wedding_date=wedding_date,
            total_budget=row["total_budget"],
            guest_count=row["guest_count"],
            days_remaining=days_remaining
        )

# ==================== DASHBOARD ENDPOINT ====================

@app.get("/weddings/{wedding_id}/dashboard", response_model=DashboardResponse)
def get_dashboard(wedding_id: int):
    """Get dashboard data for wedding"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get wedding info
        cursor.execute("SELECT * FROM weddings WHERE id = ?", (wedding_id,))
        wedding = cursor.fetchone()
        if not wedding:
            raise HTTPException(status_code=404, detail="Wedding not found")
        
        wedding_date = datetime.strptime(wedding["wedding_date"], "%Y-%m-%d").date()
        days_remaining = calculate_days_remaining(wedding_date)
        
        # Get budget totals
        cursor.execute("""
            SELECT 
                SUM(planned_amount) as total_planned,
                SUM(actual_amount) as total_actual
            FROM budget_categories
            WHERE wedding_id = ?
        """, (wedding_id,))
        budget = cursor.fetchone()
        
        total_planned = budget["total_planned"] or wedding["total_budget"]
        total_actual = budget["total_actual"] or 0
        remaining = total_planned - total_actual
        budget_percentage = int((total_actual / total_planned * 100)) if total_planned > 0 else 0
        
        # Get task counts
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN is_urgent = 1 AND is_completed = 0 THEN 1 ELSE 0 END) as urgent_tasks
            FROM tasks
            WHERE wedding_id = ?
        """, (wedding_id,))
        tasks = cursor.fetchone()
        
        total_tasks = tasks["total_tasks"] or 1
        completed_tasks = tasks["completed_tasks"] or 0
        urgent_tasks = tasks["urgent_tasks"] or 0
        control_percentage = int((completed_tasks / total_tasks * 100))
        
        return DashboardResponse(
            days_remaining=days_remaining,
            control_percentage=control_percentage,
            tasks_completed=completed_tasks,
            tasks_urgent=urgent_tasks,
            budget_planned=total_planned,
            budget_actual=total_actual,
            budget_remaining=remaining,
            budget_percentage=budget_percentage
        )

# ==================== BUDGET ENDPOINTS ====================

@app.get("/weddings/{wedding_id}/budget", response_model=List[BudgetCategoryResponse])
def get_budget_categories(wedding_id: int):
    """Get all budget categories for a wedding"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM budget_categories 
            WHERE wedding_id = ?
            ORDER BY planned_amount DESC
        """, (wedding_id,))
        
        categories = []
        for row in cursor.fetchall():
            percentage = int((row["actual_amount"] / row["planned_amount"] * 100)) if row["planned_amount"] > 0 else 0
            categories.append(BudgetCategoryResponse(
                id=row["id"],
                name=row["name"],
                icon=row["icon"],
                planned_amount=row["planned_amount"],
                actual_amount=row["actual_amount"],
                percentage_spent=percentage
            ))
        
        return categories

@app.post("/weddings/{wedding_id}/budget", response_model=BudgetCategoryResponse)
def create_budget_category(wedding_id: int, category: BudgetCategoryCreate):
    """Add a new budget category"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO budget_categories (wedding_id, name, icon, planned_amount)
            VALUES (?, ?, ?, ?)
        """, (wedding_id, category.name, category.icon, category.planned_amount))
        
        category_id = cursor.lastrowid
        conn.commit()
        
        return BudgetCategoryResponse(
            id=category_id,
            name=category.name,
            icon=category.icon,
            planned_amount=category.planned_amount,
            actual_amount=0,
            percentage_spent=0
        )

# ==================== VENDOR ENDPOINTS ====================

@app.get("/weddings/{wedding_id}/vendors", response_model=List[VendorResponse])
def get_vendors(wedding_id: int):
    """Get all vendors for a wedding"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM vendors 
            WHERE wedding_id = ?
            ORDER BY created_at DESC
        """, (wedding_id,))
        
        vendors = []
        for row in cursor.fetchall():
            vendors.append(VendorResponse(
                id=row["id"],
                category_id=row["category_id"],
                name=row["name"],
                amount=row["amount"],
                deposit_paid=row["deposit_paid"],
                payment_date=row["payment_date"],
                notes=row["notes"] or "",
                is_confirmed=bool(row["is_confirmed"])
            ))
        
        return vendors

@app.post("/weddings/{wedding_id}/vendors", response_model=VendorResponse)
def create_vendor(wedding_id: int, vendor: VendorCreate):
    """Add a new vendor"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Insert vendor
        cursor.execute("""
            INSERT INTO vendors (wedding_id, category_id, name, amount, deposit_paid, payment_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (wedding_id, vendor.category_id, vendor.name, vendor.amount, 
              vendor.deposit_paid, vendor.payment_date, vendor.notes))
        
        vendor_id = cursor.lastrowid
        
        # Update category actual amount
        cursor.execute("""
            UPDATE budget_categories 
            SET actual_amount = actual_amount + ?
            WHERE id = ? AND wedding_id = ?
        """, (vendor.amount, vendor.category_id, wedding_id))
        
        conn.commit()
        
        return VendorResponse(
            id=vendor_id,
            category_id=vendor.category_id,
            name=vendor.name,
            amount=vendor.amount,
            deposit_paid=vendor.deposit_paid or 0,
            payment_date=vendor.payment_date,
            notes=vendor.notes or "",
            is_confirmed=False
        )

# ==================== TASK ENDPOINTS ====================

@app.get("/weddings/{wedding_id}/tasks", response_model=List[TaskResponse])
def get_tasks(wedding_id: int, timeline_period: Optional[str] = None):
    """Get all tasks for a wedding, optionally filtered by timeline period"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        if timeline_period:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE wedding_id = ? AND timeline_period = ?
                ORDER BY is_urgent DESC, due_date ASC
            """, (wedding_id, timeline_period))
        else:
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE wedding_id = ?
                ORDER BY is_urgent DESC, timeline_period, due_date ASC
            """, (wedding_id,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append(TaskResponse(
                id=row["id"],
                title=row["title"],
                description=row["description"] or "",
                timeline_period=row["timeline_period"],
                due_date=row["due_date"],
                is_completed=bool(row["is_completed"]),
                is_urgent=bool(row["is_urgent"])
            ))
        
        return tasks

@app.post("/weddings/{wedding_id}/tasks", response_model=TaskResponse)
def create_task(wedding_id: int, task: TaskCreate):
    """Create a new task"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (wedding_id, title, description, timeline_period, due_date, is_urgent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (wedding_id, task.title, task.description, task.timeline_period, 
              task.due_date, task.is_urgent))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        return TaskResponse(
            id=task_id,
            title=task.title,
            description=task.description or "",
            timeline_period=task.timeline_period,
            due_date=task.due_date,
            is_completed=False,
            is_urgent=task.is_urgent or False
        )

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    """Mark a task as completed"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET is_completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (task_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.commit()
        
        return {"message": "Task completed successfully"}

@app.patch("/tasks/{task_id}/uncomplete")
def uncomplete_task(task_id: int):
    """Mark a task as not completed"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks 
            SET is_completed = 0, completed_at = NULL
            WHERE id = ?
        """, (task_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        conn.commit()
        
        return {"message": "Task marked as incomplete"}

# ==================== HEALTH CHECK ====================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
