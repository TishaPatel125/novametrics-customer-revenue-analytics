def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "NovaMetrics" in data["service"]


def test_get_kpis_summary(client):
    response = client.get("/api/v1/kpis/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_mrr" in data
    assert "total_customers" in data
    assert data["total_customers"] == 2
    assert data["total_mrr"] == 49.0


def test_get_revenue_trends(client):
    response = client.get("/api/v1/revenue/trends?months=6")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 6


def test_get_segments(client):
    response = client.get("/api/v1/revenue/segments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s["segment"] == "SMB" for s in data)


def test_get_cohorts(client):
    response = client.get("/api/v1/cohorts/retention")
    assert response.status_code == 200
    data = response.json()
    assert "cohorts" in data
    assert "max_periods" in data


def test_get_churn_overview(client):
    response = client.get("/api/v1/churn/overview")
    assert response.status_code == 200
    data = response.json()
    assert "high_risk_customers" in data
    assert "mrr_at_risk" in data
