from fastapi import APIRouter
from app.api.v1.endpoints import auth, kpis, revenue, cohorts, churn

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["Executive KPIs"])
api_router.include_router(revenue.router, prefix="/revenue", tags=["Revenue Analytics"])
api_router.include_router(cohorts.router, prefix="/cohorts", tags=["Cohort Retention"])
api_router.include_router(churn.router, prefix="/churn", tags=["Churn Prediction"])
