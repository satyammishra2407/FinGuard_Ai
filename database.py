"""
Database models and connection setup for FinGuard AI
"""
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    declared_income = Column(Float, nullable=False)
    occupation = Column(String(100))
    kyc_status = Column(String(20), default="PENDING", index=True)
    account_opening_date = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, default=0.0, index=True)
    last_risk_assessment = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="customer", lazy='dynamic')
    alerts = relationship("Alert", back_populates="customer", lazy='dynamic')
    
    __table_args__ = (
        Index('idx_customer_risk', 'risk_score', 'is_active'),
    )

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    beneficiary = Column(String(100), index=True)
    beneficiary_type = Column(String(50))
    location = Column(String(100))
    currency = Column(String(10), default="INR")
    status = Column(String(20), default="COMPLETED", index=True)
    device_id = Column(String(100))
    ip_address = Column(String(45))
    is_suspicious = Column(Boolean, default=False, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    
    __table_args__ = (
        Index('idx_transaction_customer_time', 'customer_id', 'timestamp'),
        Index('idx_transaction_beneficiary', 'beneficiary', 'is_suspicious'),
    )

class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(String(50), primary_key=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    risk_score = Column(Float, nullable=False, index=True)
    triggered_rules = Column(Text)  # JSON string of triggered rules
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), default="OPEN", index=True)
    assigned_analyst = Column(String(100))
    investigation_notes = Column(Text)
    resolution_date = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="alerts")
    
    __table_args__ = (
        Index('idx_alert_status_risk', 'status', 'risk_score'),
    )

class RiskFactor(Base):
    __tablename__ = "risk_factors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), ForeignKey("customers.customer_id"), nullable=False)
    factor_name = Column(String(100), nullable=False)
    factor_value = Column(Float, nullable=False)
    factor_weight = Column(Float, default=1.0)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database connection
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Efficient query methods
def get_customer_count(db):
    """Get total customer count"""
    return db.query(Customer).count()

def get_high_risk_customer_count(db, threshold=70):
    """Get count of high risk customers"""
    return db.query(Customer).filter(Customer.risk_score > threshold).count()

def get_customers_paginated(db, limit=100, offset=0):
    """Get customers with pagination"""
    return db.query(Customer).limit(limit).offset(offset).all()

def get_transaction_count(db):
    """Get total transaction count"""
    return db.query(Transaction).count()

def get_alert_count_by_status(db, status="OPEN"):
    """Get alert count by status"""
    return db.query(Alert).filter(Alert.status == status).count()

def get_customer_transactions(db, customer_id, limit=100):
    """Get transactions for a specific customer"""
    return db.query(Transaction).filter(
        Transaction.customer_id == customer_id
    ).order_by(Transaction.timestamp.desc()).limit(limit).all()

def get_recent_alerts(db, limit=10):
    """Get recent alerts"""
    return db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

def get_suspicious_transactions_sample(db, limit=1000):
    """Get sample of suspicious transactions for analysis"""
    return db.query(Transaction).filter(
        Transaction.is_suspicious == True
    ).limit(limit).all()

def get_customers_for_network_analysis(db, limit=200):
    """Get high-risk customers for network analysis"""
    return db.query(Customer).filter(
        Customer.risk_score > 60
    ).order_by(Customer.risk_score.desc()).limit(limit).all()
