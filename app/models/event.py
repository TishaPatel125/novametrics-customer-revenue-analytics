from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.models.base import TimestampMixin


class UsageEvent(Base, TimestampMixin):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # 'login', 'report_export', 'api_call', 'dashboard_view', 'support_ticket'
    event_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    properties = Column(JSON, nullable=True)

    customer = relationship("Customer", back_populates="events")
