"""
Database models and operations
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd
from config import DATABASE_PATH

Base = declarative_base()

class Expense(Base):
    """Database model for expenses"""
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    payment_method = Column(String(50))
    entry_method = Column(String(20))  # manual, voice, ocr
    timestamp = Column(DateTime, default=datetime.now)
    receipt_image_path = Column(String(200))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'date': self.date,
            'category': self.category,
            'amount': self.amount,
            'description': self.description,
            'payment_method': self.payment_method,
            'entry_method': self.entry_method,
            'timestamp': self.timestamp,
            'receipt_image_path': self.receipt_image_path
        }

class Budget(Base):
    """Database model for budgets"""
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path=DATABASE_PATH):
        """Initialize database connection"""
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_expense(self, date, category, amount, description, payment_method, 
                   entry_method='manual', receipt_path=None):
        """Add expense to database"""
        expense = Expense(
            date=date,
            category=category,
            amount=amount,
            description=description,
            payment_method=payment_method,
            entry_method=entry_method,
            receipt_image_path=receipt_path
        )
        self.session.add(expense)
        self.session.commit()
        return expense.id
    
    def get_all_expenses(self):
        """Get all expenses as DataFrame"""
        expenses = self.session.query(Expense).all()
        if not expenses:
            return pd.DataFrame()
        
        data = [exp.to_dict() for exp in expenses]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def get_expenses_by_date_range(self, start_date, end_date):
        """Get expenses within date range"""
        expenses = self.session.query(Expense).filter(
            Expense.date >= start_date,
            Expense.date <= end_date
        ).all()
        
        if not expenses:
            return pd.DataFrame()
        
        data = [exp.to_dict() for exp in expenses]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def delete_expense(self, expense_id):
        """Delete expense by ID"""
        expense = self.session.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            self.session.delete(expense)
            self.session.commit()
            return True
        return False
    
    def update_expense(self, expense_id, **kwargs):
        """Update expense fields"""
        expense = self.session.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            for key, value in kwargs.items():
                setattr(expense, key, value)
            self.session.commit()
            return True
        return False
    
    def set_budget(self, category, amount):
        """Set or update budget for category"""
        budget = self.session.query(Budget).filter(Budget.category == category).first()
        if budget:
            budget.amount = amount
        else:
            budget = Budget(category=category, amount=amount)
            self.session.add(budget)
        self.session.commit()
    
    def get_budgets(self):
        """Get all budgets as dictionary"""
        budgets = self.session.query(Budget).all()
        return {b.category: b.amount for b in budgets}
    
    def get_stats(self):
        """Get database statistics"""
        total_expenses = self.session.query(Expense).count()
        total_amount = self.session.query(func.sum(Expense.amount)).scalar() or 0
        
        return {
            'total_expenses': total_expenses,
            'total_amount': total_amount
        }
    
    def close(self):
        """Close database session"""
        self.session.close()