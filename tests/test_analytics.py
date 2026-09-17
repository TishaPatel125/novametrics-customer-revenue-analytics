from app.services.revenue_analytics import RevenueAnalyticsService
from app.services.cohort_analytics import CohortAnalyticsService
from app.services.churn_service import ChurnRiskService


def test_kpi_summary_calculation(db_session):
    service = RevenueAnalyticsService(db_session)
    kpis = service.get_kpi_summary()

    assert kpis.total_customers == 2
    assert kpis.active_customers == 1
    assert kpis.churned_customers == 1
    assert kpis.total_mrr == 49.0
    assert kpis.total_arr == 49.0 * 12.0
    assert kpis.arpu == 49.0
    assert kpis.monthly_churn_rate > 0.0


def test_segment_breakdown(db_session):
    service = RevenueAnalyticsService(db_session)
    segments = service.get_segment_breakdown()

    smb_seg = next((s for s in segments if s.segment == "SMB"), None)
    assert smb_seg is not None
    assert smb_seg.customer_count == 1
    assert smb_seg.total_mrr == 49.0

    mid_seg = next((s for s in segments if s.segment == "Mid-Market"), None)
    assert mid_seg is not None
    assert mid_seg.customer_count == 0  # Churned
    assert mid_seg.churn_rate == 100.0


def test_cohort_retention_matrix(db_session):
    service = CohortAnalyticsService(db_session)
    result = service.get_retention_matrix(max_cohorts=6, max_periods=3)

    assert len(result.cohorts) >= 1
    # Check that M0 is always 100%
    for cohort in result.cohorts:
        assert cohort.retention_percentages["M0"] == 100.0


def test_churn_risk_service(db_session):
    service = ChurnRiskService(db_session)
    overview = service.get_churn_overview(limit=10)

    assert "Budget constraints / downsized" in overview.top_churn_reasons
    assert len(overview.high_risk_customers) == 1  # 1 active customer
    cust = overview.high_risk_customers[0]
    assert cust.customer_code == "CUST-001"
    assert cust.risk_level in ["Low", "Medium", "High"]
