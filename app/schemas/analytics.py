from pydantic import BaseModel
from typing import List, Dict, Optional


class KPISummary(BaseModel):
    total_customers: int
    active_customers: int
    churned_customers: int
    total_mrr: float
    total_arr: float
    arpu: float  # Average Revenue Per User
    monthly_churn_rate: float  # Percentage (e.g. 2.5)
    net_revenue_retention: float  # Percentage (e.g. 108.5)
    mrr_growth_rate: float  # Month-over-month growth %


class RevenueDataPoint(BaseModel):
    month: str  # YYYY-MM
    new_mrr: float
    expansion_mrr: float
    churned_mrr: float
    net_mrr_change: float
    ending_mrr: float
    paid_invoices: int


class RevenueTrendResponse(BaseModel):
    data: List[RevenueDataPoint]


class SegmentBreakdown(BaseModel):
    segment: str
    customer_count: int
    total_mrr: float
    arpu: float
    churn_rate: float


class CohortRetentionRow(BaseModel):
    cohort_month: str  # YYYY-MM
    cohort_size: int
    retention_percentages: Dict[str, float]  # e.g., {"M0": 100.0, "M1": 92.4, ...}


class CohortRetentionResponse(BaseModel):
    cohorts: List[CohortRetentionRow]
    max_periods: int


class ChurnRiskCustomer(BaseModel):
    customer_id: int
    customer_code: str
    name: str
    company: Optional[str] = None
    segment: str
    plan_tier: str
    current_mrr: float
    churn_probability: float  # 0.0 - 1.0
    risk_level: str  # "Low", "Medium", "High"
    key_risk_factors: List[str]


class ChurnOverview(BaseModel):
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    mrr_at_risk: float
    top_churn_reasons: Dict[str, int]
    high_risk_customers: List[ChurnRiskCustomer]
