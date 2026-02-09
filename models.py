import enum
from sqlalchemy import Column, Integer, String, Enum as SAEnum, DateTime, Boolean, Float
from sqlalchemy.sql import func
from .database import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False) # שם הסעיף (DJ, רחפן וכו')
    amount = Column(Float, nullable=False)
    notes = Column(String, nullable=True)     # הערות אישיות בעברית
    is_paid = Column(Boolean, default=False)  # האם שולם
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Budget(Base):
    __tablename__ = "budget"
    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Integer, default=100000)