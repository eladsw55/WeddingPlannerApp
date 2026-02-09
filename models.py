from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    amount = Column(Float, default=0.0)
    is_paid = Column(Boolean, default=False)
    notes = Column(String, default="")

class Budget(Base):
    __tablename__ = "budget"
    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, default=100000.0)
