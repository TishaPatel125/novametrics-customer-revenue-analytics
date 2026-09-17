from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.cohort_analytics import CohortAnalyticsService
from app.schemas.analytics import CohortRetentionResponse

router = APIRouter()


@router.get("/retention", response_model=CohortRetentionResponse)
def get_cohort_retention(
    max_cohorts: int = Query(12, ge=1, le=24, description="Number of cohorts to analyze"),
    max_periods: int = Query(6, ge=1, le=12, description="Number of retention months to calculate"),
    db: Session = Depends(get_db),
):
    """Retrieve cohort retention percentage matrix for customer cohorts."""
    service = CohortAnalyticsService(db)
    return service.get_retention_matrix(max_cohorts=max_cohorts, max_periods=max_periods)
