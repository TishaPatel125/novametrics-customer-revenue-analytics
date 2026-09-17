from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.models.base import TimestampMixin


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    plan_tier = Column(String(50), nullable=False)  # 'Starter', 'Growth', 'Enterprise'
    billing_cycle = Column(String(20), default="monthly")  # 'monthly', 'annual'
    mrr_amount = Column(Float, nullable=False)  # Monthly Recurring Revenue value
    status = Column(String(30), default="active", index=True)  # 'active', 'canceled', 'trialing', 'past_due'
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_date = Column(DateTime, nullable=True)

    customer = relationship("Customer", back_populates="subscriptions")
