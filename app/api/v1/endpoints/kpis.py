from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.revenue_analytics import RevenueAnalyticsService
from app.schemas.analytics import KPISummary

router = APIRouter()


@router.get("/summary", response_model=KPISummary)
def get_executive_summary(db: Session = Depends(get_db)):
    """Retrieve top-level executive KPIs including MRR, ARR, Churn Rate, and ARPU."""
    service = RevenueAnalyticsService(db)
    return service.get_kpi_summary()
