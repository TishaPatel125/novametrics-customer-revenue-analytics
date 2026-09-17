from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.models.base import TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    company = Column(String(255), nullable=True)
    country = Column(String(100), default="United States")
    segment = Column(String(50), default="SMB")  # 'SMB', 'Mid-Market', 'Enterprise'
    industry = Column(String(100), default="Technology")
    signup_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    churn_date = Column(DateTime, nullable=True, index=True)
    churn_reason = Column(String(255), nullable=True)
    predicted_churn_score = Column(Float, default=0.0)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    events = relationship("UsageEvent", back_populates="customer", cascade="all, delete-orphan")
