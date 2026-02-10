from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
import database
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    notes: str = ""

# הוספנו מודל לעדכון תקציב ואורחים
class BudgetUpdate(BaseModel):
    total_amount: float = None
    guest_count: int = None

@app.get("/budget/summary")
def get_summary(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()
    budget_record = db.query(models.Budget).first()
    
    if not budget_record:
        budget_record = models.Budget(total_amount=180000, guest_count=400)
        db.add(budget_record)
        db.commit()
        db.refresh(budget_record)
    
    total = budget_record.total_amount
    spent = sum(e.amount for e in expenses)
    
    return {
        "total": total,
        "spent": spent,
        "remaining": total - spent,
        "guest_count": budget_record.guest_count or 400,
        "expenses": [{"category": e.category, "amount": e.amount} for e in expenses]
    }

# שינינו את השם ל /expenses כדי שיתאים ל-JS
@app.post("/expenses")
def add_or_update_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Expense).filter(models.Expense.category == expense.category).first()
    if existing:
        existing.amount = expense.amount
        existing.notes = expense.notes
    else:
        db.add(models.Expense(category=expense.category, amount=expense.amount, notes=expense.notes))
    db.commit()
    return {"status": "success"}

# נתיב מאוחד לעדכון תקציב ואורחים
@app.post("/budget/update")
def update_budget_settings(data: BudgetUpdate, db: Session = Depends(get_db)):
    budget_record = db.query(models.Budget).first()
    if budget_record:
        if data.total_amount is not None:
            budget_record.total_amount = data.total_amount
        if data.guest_count is not None:
            budget_record.guest_count = data.guest_count
        db.commit()
    return {"status": "success"}
