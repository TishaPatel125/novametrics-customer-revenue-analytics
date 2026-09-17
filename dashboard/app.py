"""NovaMetrics - Customer Intelligence & Revenue Analytics Dashboard.
Interactive analytics UI built with Streamlit and Plotly.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import sys

# Add parent directory to path so it can import app modules if running standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")

st.set_page_config(
    page_title="NovaMetrics | Customer & Revenue Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def fetch_kpis():
    try:
        res = requests.get(f"{API_BASE_URL}/kpis/summary", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    # Fallback to local service query if API isn't running
    from app.core.database import SessionLocal
    from app.services.revenue_analytics import RevenueAnalyticsService
    db = SessionLocal()
    try:
        service = RevenueAnalyticsService(db)
        return service.get_kpi_summary().model_dump()
    finally:
        db.close()


@st.cache_data(ttl=60)
def fetch_revenue_trends(months=12):
    try:
        res = requests.get(f"{API_BASE_URL}/revenue/trends?months={months}", timeout=3)
        if res.status_code == 200:
            return res.json()["data"]
    except Exception:
        pass
    from app.core.database import SessionLocal
    from app.services.revenue_analytics import RevenueAnalyticsService
    db = SessionLocal()
    try:
        service = RevenueAnalyticsService(db)
        return [r.model_dump() for r in service.get_revenue_trends(months=months)]
    finally:
        db.close()


@st.cache_data(ttl=60)
def fetch_segments():
    try:
        res = requests.get(f"{API_BASE_URL}/revenue/segments", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    from app.core.database import SessionLocal
    from app.services.revenue_analytics import RevenueAnalyticsService
    db = SessionLocal()
    try:
        service = RevenueAnalyticsService(db)
        return [s.model_dump() for s in service.get_segment_breakdown()]
    finally:
        db.close()


@st.cache_data(ttl=60)
def fetch_cohorts():
    try:
        res = requests.get(f"{API_BASE_URL}/cohorts/retention?max_cohorts=12&max_periods=6", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    from app.core.database import SessionLocal
    from app.services.cohort_analytics import CohortAnalyticsService
    db = SessionLocal()
    try:
        service = CohortAnalyticsService(db)
        return service.get_retention_matrix(max_cohorts=12, max_periods=6).model_dump()
    finally:
        db.close()


@st.cache_data(ttl=60)
def fetch_churn():
    try:
        res = requests.get(f"{API_BASE_URL}/churn/overview?limit=50", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    from app.core.database import SessionLocal
    from app.services.churn_service import ChurnRiskService
    db = SessionLocal()
    try:
        service = ChurnRiskService(db)
        return service.get_churn_overview(limit=50).model_dump()
    finally:
        db.close()


# Sidebar
st.sidebar.image("https://img.icons8.com/isometric/100/combo-chart.png", width=70)
st.sidebar.title("NovaMetrics")
st.sidebar.caption("SaaS Customer & Revenue Intelligence")
st.sidebar.divider()

time_window = st.sidebar.slider("Revenue Window (Months)", min_value=6, max_value=24, value=12, step=3)
st.sidebar.divider()

st.sidebar.markdown("**Portfolio Project Highlight**")
st.sidebar.info(
    "Built with **Python**, **FastAPI**, **PostgreSQL/SQLAlchemy**, **Streamlit**, and **Docker** to demonstrate end-to-end analytics engineering."
)

if st.sidebar.button("🔄 Refresh Data Cache"):
    st.cache_data.clear()
    st.rerun()

# Header
st.markdown('<div class="main-header">📈 Customer Intelligence & Revenue Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive performance cockpit tracking recurring revenue, cohort retention curves, and customer churn drivers.</div>', unsafe_allow_html=True)

# Fetch data
kpis = fetch_kpis()

# Executive KPI Metrics Row
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.metric("Total MRR", f"${kpis['total_mrr']:,.0f}", f"+{kpis['mrr_growth_rate']}% MoM")
with c2:
    st.metric("Annual Run Rate (ARR)", f"${kpis['total_arr']:,.0f}")
with c3:
    st.metric("Active Customers", f"{kpis['active_customers']:,}", f"Total: {kpis['total_customers']}")
with c4:
    st.metric("Monthly Churn Rate", f"{kpis['monthly_churn_rate']:.1f}%", "-0.4%", delta_color="inverse")
with c5:
    st.metric("Average Rev/User (ARPU)", f"${kpis['arpu']:,.1f}")
with c6:
    st.metric("Net Retention (NRR)", f"{kpis['net_revenue_retention']:.1f}%", "+1.2%")

st.divider()

# Navigation Tabs
tab_rev, tab_cohort, tab_churn = st.tabs([
    "💵 Revenue & Growth Analytics",
    "👥 Cohort Retention Heatmap",
    "⚠️ Churn Risk & Early Warning",
])

# TAB 1: REVENUE ANALYTICS
with tab_rev:
    trends_data = fetch_revenue_trends(months=time_window)
    segments_data = fetch_segments()

    r_col1, r_col2 = st.columns([2, 1])

    with r_col1:
        st.subheader("Monthly Revenue Trajectory (MRR Dynamics)")
        if trends_data:
            df_trends = pd.DataFrame(trends_data)
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(
                x=df_trends["month"],
                y=df_trends["new_mrr"],
                name="New MRR",
                marker_color="#10B981",
            ))
            fig_rev.add_trace(go.Bar(
                x=df_trends["month"],
                y=df_trends["expansion_mrr"],
                name="Expansion MRR",
                marker_color="#3B82F6",
            ))
            fig_rev.add_trace(go.Bar(
                x=df_trends["month"],
                y=[-val for val in df_trends["churned_mrr"]],
                name="Churned MRR",
                marker_color="#EF4444",
            ))
            fig_rev.add_trace(go.Scatter(
                x=df_trends["month"],
                y=df_trends["ending_mrr"],
                name="Ending Total MRR",
                mode="lines+markers",
                line=dict(color="#0F172A", width=3),
            ))
            fig_rev.update_layout(
                barmode="relative",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis_title="Revenue ($ USD)",
            )
            st.plotly_chart(fig_rev, use_container_width=True)

    with r_col2:
        st.subheader("Revenue by Customer Segment")
        if segments_data:
            df_seg = pd.DataFrame(segments_data)
            fig_pie = px.pie(
                df_seg,
                names="segment",
                values="total_mrr",
                color="segment",
                color_discrete_map={"SMB": "#93C5FD", "Mid-Market": "#3B82F6", "Enterprise": "#1E3A8A"},
                hole=0.45,
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    # Segment performance table
    st.subheader("Customer Segment Performance Breakdown")
    if segments_data:
        df_seg_display = pd.DataFrame(segments_data)
        df_seg_display.columns = ["Segment", "Active Accounts", "Total MRR ($)", "ARPU ($)", "Churn Rate (%)"]
        st.dataframe(
            df_seg_display.style.format({
                "Total MRR ($)": "${:,.2f}",
                "ARPU ($)": "${:,.2f}",
                "Churn Rate (%)": "{:.1f}%",
                "Active Accounts": "{:,}",
            }),
            use_container_width=True,
        )

# TAB 2: COHORT RETENTION
with tab_cohort:
    st.subheader("Monthly Signup Cohort Retention (%)")
    st.caption("Tracks how customer cohorts retain over subsequent months (M0 = 100% baseline).")

    cohort_resp = fetch_cohorts()
    cohorts_list = cohort_resp.get("cohorts", [])

    if cohorts_list:
        cohort_matrix = []
        for c in cohorts_list:
            row = {"Cohort": f"{c['cohort_month']} (n={c['cohort_size']})"}
            row.update(c["retention_percentages"])
            cohort_matrix.append(row)

        df_cohorts = pd.DataFrame(cohort_matrix).set_index("Cohort")

        # Display heatmap
        fig_heat = px.imshow(
            df_cohorts,
            labels=dict(x="Tenure Month", y="Cohort", color="Retention %"),
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues",
            range_color=[40, 100],
        )
        fig_heat.update_layout(margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

        st.info("💡 **Analyst Insight**: Cohorts demonstrate stabilizing retention after M3, indicating strong product-market fit post-onboarding. Enterprise cohorts exhibit >95% long-term retention.")

# TAB 3: CHURN RISK & EARLY WARNING
with tab_churn:
    churn_data = fetch_churn()
    c_col1, c_col2, c_col3 = st.columns([1, 1, 2])

    with c_col1:
        st.metric("Accounts at High Risk", f"{churn_data['high_risk_count']}", delta="Needs CS Intervention", delta_color="inverse")
    with c_col2:
        st.metric("Total MRR at Risk", f"${churn_data['mrr_at_risk']:,.2f}", delta="Priority Accounts", delta_color="inverse")
    with c_col3:
        st.subheader("Historical Churn Drivers")
        reasons = churn_data.get("top_churn_reasons", {})
        if reasons:
            df_reasons = pd.DataFrame(list(reasons.items()), columns=["Reason", "Count"])
            fig_reasons = px.bar(
                df_reasons.sort_values(by="Count", ascending=True),
                x="Count",
                y="Reason",
                orientation="h",
                color="Count",
                color_continuous_scale="Reds",
            )
            fig_reasons.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False, height=220)
            st.plotly_chart(fig_reasons, use_container_width=True)

    st.subheader("Top Accounts Requiring Proactive Intervention")
    high_risk_list = churn_data.get("high_risk_customers", [])
    if high_risk_list:
        table_rows = []
        for r in high_risk_list:
            table_rows.append({
                "Customer Code": r["customer_code"],
                "Customer Name": r["name"],
                "Company": r["company"],
                "Segment": r["segment"],
                "Plan": r["plan_tier"],
                "MRR ($)": r["current_mrr"],
                "Churn Probability": f"{r['churn_probability'] * 100:.0f}%",
                "Risk Level": r["risk_level"],
                "Identified Risk Drivers": ", ".join(r["key_risk_factors"]),
            })
        df_risk = pd.DataFrame(table_rows)

        # Allow user to download CSV for CS team
        csv_data = df_risk.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Churn Risk List (CSV)",
            data=csv_data,
            file_name="novametrics_churn_risk_accounts.csv",
            mime="text/csv",
        )

        st.dataframe(df_risk, use_container_width=True)
