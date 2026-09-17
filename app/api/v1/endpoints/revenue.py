from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.revenue_analytics import RevenueAnalyticsService
from app.schemas.analytics import RevenueTrendResponse, SegmentBreakdown

router = APIRouter()


@router.get("/trends", response_model=RevenueTrendResponse)
def get_revenue_trends(
    months: int = Query(12, ge=1, le=36, description="Number of past months to retrieve"),
    db: Session = Depends(get_db),
):
    """Retrieve monthly time-series revenue breakdown (new, expansion, churned, ending MRR)."""
    service = RevenueAnalyticsService(db)
    trends = service.get_revenue_trends(months=months)
    return RevenueTrendResponse(data=trends)


@router.get("/segments", response_model=List[SegmentBreakdown])
def get_customer_segments(db: Session = Depends(get_db)):
    """Retrieve revenue and customer breakdown by market segment (SMB, Mid-Market, Enterprise)."""
    service = RevenueAnalyticsService(db)
    return service.get_segment_breakdown()
