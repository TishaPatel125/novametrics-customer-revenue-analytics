from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.models.base import TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    transaction_code = Column(String(50), unique=True, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    status = Column(String(30), default="succeeded", index=True)  # 'succeeded', 'failed', 'refunded'
    payment_method = Column(String(50), default="credit_card")  # 'credit_card', 'bank_transfer', 'paypal'
    transaction_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    customer = relationship("Customer", back_populates="transactions")
