from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    amount = Column(Float, default=0.0)
    notes = Column(String, default="") # השדה ששומר את הטקסט שרצית
    is_paid = Column(Boolean, default=False)

class Budget(Base):
    __tablename__ = "budget"
    
    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, default=180000.0)
    guest_count = Column(Integer, default=400) # מאפשר לך לשנות את כמות האורחים
