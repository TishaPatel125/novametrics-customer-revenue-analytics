from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.churn_service import ChurnRiskService
from app.schemas.analytics import ChurnOverview

router = APIRouter()


@router.get("/overview", response_model=ChurnOverview)
def get_churn_overview(
    limit: int = Query(50, ge=1, le=200, description="Max high-risk accounts to return"),
    db: Session = Depends(get_db),
):
    """Retrieve predictive churn risk overview, high-risk customer list, and at-risk MRR."""
    service = ChurnRiskService(db)
    return service.get_churn_overview(limit=limit)
