from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
import database
from database import engine, SessionLocal

# יצירת הטבלאות במסד הנתונים בעת הרצת האפליקציה
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# הגדרת CORS כדי שה-HTML המעוצב שלך יוכל לתקשר עם השרת ב-Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# פונקציה לקבלת Session של מסד הנתונים
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# מודל נתונים עבור ה-API
class ExpenseCreate(BaseModel):
    category: str
    amount: float
    notes: str = ""

@app.get("/budget/summary")
def get_summary(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    budget_record = db.query(models.Budget).first()
    
    # אתחול תקציב ברירת מחדל אם המערכת חדשה
    if not budget_record:
        budget_record = models.Budget(total_amount=100000)
        db.add(budget_record)
        db.commit()
        db.refresh(budget_record)
    
    total = budget_record.total_amount
    spent = sum(e.amount for e in expenses)
    
    return {
        "total": total,
        "spent": spent,
        "remaining": total - spent,
        "expenses": [{"category": e.category, "amount": e.amount, "is_paid": e.is_paid, "notes": e.notes} for e in expenses]
    }

@app.post("/budget/update_total")
def update_total(amount: float, db: Session = Depends(get_db)):
    budget_record = db.query(models.Budget).first()
    if budget_record:
        budget_record.total_amount = amount
    else:
        budget_record = models.Budget(total_amount=amount)
        db.add(budget_record)
    db.commit()
    return {"status": "success"}

@app.post("/budget/add")
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Expense).filter(models.Expense.category == expense.category).first()
    if existing:
        existing.amount = expense.amount
        existing.notes = expense.notes
    else:
        db.add(models.Expense(category=expense.category, amount=expense.amount, notes=expense.notes))
    db.commit()
    return {"status": "success"}

@app.post("/budget/toggle_paid")
def toggle_paid(category: str, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.category == category).first()
    if expense:
        expense.is_paid = not expense.is_paid
        db.commit()
    return {"status": "success"}