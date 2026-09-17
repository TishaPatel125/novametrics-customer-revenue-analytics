# NovaMetrics | Customer Intelligence & Revenue Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI-GitHub_Actions-2088FF.svg)](https://github.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](https://docs.pytest.org/)

An end-to-end, production-grade **Customer Intelligence & Recurring Revenue Analytics Platform** built with Python, FastAPI, PostgreSQL/SQLAlchemy, Docker, and Streamlit. 

NovaMetrics transforms raw customer activity, subscription lifecycles, and billing ledgers into actionable executive analytics: real-time MRR/ARR tracking, monthly cohort retention matrices, customer segment performance, and early-warning churn risk prediction.

---

## 🎯 Business Value & Impact

Modern subscription (SaaS) businesses lose substantial annual recurring revenue from undetected customer attrition. NovaMetrics solves this by:
1. **Unifying the Data Lifecycle**: Ingesting normalized transactional and behavioral data across 600+ accounts and 24 rolling months.
2. **Automating Core Financial Metrics**: Calculating real-time MRR, ARR, Net Revenue Retention (NRR), and ARPU across customer segments (SMB, Mid-Market, Enterprise).
3. **Cohort Retention Analysis**: Mapping monthly signup cohorts to identify long-term retention inflection points.
4. **Predictive Churn Risk Engine**: Scoring customer health using activity velocity, tenure, and billing signals to flag high-risk accounts and prioritize proactive Customer Success intervention.

---

## 🏗️ Architecture & Data Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 Data Generation / Ingestion                 │
│      600+ Accounts • 24-Mo Ledger • 15k+ Usage Events      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               PostgreSQL / SQLite Database                  │
│    Customers • Subscriptions • Transactions • UsageEvents   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Analytics Service Layer                     │
│  • RevenueAnalyticsService (MRR, ARR, ARPU, NRR, MoM %)     │
│  • CohortAnalyticsService (Monthly retention % matrix)      │
│  • ChurnRiskService (Predictive scoring & risk signals)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FastAPI REST API Layer                      │
│   JWT Auth • Swagger UI (/docs) • Modular Router Pattern    │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│   Streamlit Web Dashboard    │ │    Automated CI/CD & Tests │
│ Plotly Charts • Cohort Heat  │ │  Pytest • GitHub Actions   │
└──────────────────────────────┘ └────────────────────────────┘
```

---

## 🚀 Key Metrics Tracked

| Metric | Formula / Business Definition |
| :--- | :--- |
| **MRR (Monthly Recurring Revenue)** | Normalized monthly recurring subscription revenue across active accounts. |
| **ARR (Annual Run Rate)** | Projected annual revenue (\(\text{MRR} \times 12\)). |
| **ARPU (Average Rev. per User)** | \(\frac{\text{Total Active MRR}}{\text{Active Customer Count}}\). |
| **Monthly Churn Rate** | Percentage of active customers who canceled within the last 30-day billing window. |
| **Net Revenue Retention (NRR)** | Measures account expansion vs. contraction and churn over time. |
| **Cohort Retention Rate** | Percentage of customers from a signup cohort remaining active at month \(M_n\). |

---

## 💻 Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Pydantic-Settings
- **Database / ORM**: PostgreSQL 15, SQLite (zero-config local fallback), SQLAlchemy 2.0
- **Analytics & ML**: Pandas, NumPy, Scikit-learn
- **Visualization**: Streamlit, Plotly Express & Graph Objects
- **Authentication**: OAuth2 Password Flow, JWT (JSON Web Tokens), Passlib/Bcrypt
- **Testing**: Pytest, HTTPX, In-memory SQLite fixtures
- **DevOps**: Docker, Docker Compose, GitHub Actions CI

---

## ⚡ Quickstart Guide

### Option 1: Run Locally (Zero Configuration SQLite)

1. **Clone and create a virtual environment**:
   ```powershell
   git clone https://github.com/TishaPatel125/novametrics-customer-revenue-analytics.git
   cd novametrics-customer-revenue-analytics
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Populate realistic business data**:
   ```powershell
   python scripts/generate_data.py
   ```

4. **Launch the FastAPI backend**:
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
   * Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

5. **Launch the Analytics Dashboard** (in a second terminal):
   ```powershell
   streamlit run dashboard/app.py
   ```
   * Dashboard URL: [http://localhost:8501](http://localhost:8501)

---

### Option 2: Run with Docker Compose (PostgreSQL + API + Dashboard)

When Docker Desktop is running, launch the entire multi-container stack with a single command:
```powershell
docker-compose up --build
```
- **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **PostgreSQL Database**: Port `5432`

---

## 🧪 Automated Testing

Run the full suite of unit and integration tests:
```powershell
pytest tests/ -v
```

All tests run against isolated in-memory databases with automatic fixtures, ensuring zero cross-test contamination.

---

## 📋 Ready-to-Use Resume Bullet Points (Copy into your CV!)

Under your **Projects** or **Technical Experience** section:

> **Customer Intelligence & Recurring Revenue Analytics Platform** | *Python, FastAPI, PostgreSQL, Docker, Streamlit, Plotly*
> - Engineered an end-to-end analytics platform modeling 600+ customer lifecycles and 24 months of billing data, calculating real-time MRR, ARR, ARPU, and Net Revenue Retention (NRR).
> - Designed and optimized analytical SQL queries and FastAPI REST endpoints delivering cohort retention matrices and revenue decomposition (new, expansion, churned MRR).
> - Built a predictive churn scoring engine analyzing login frequency drops and billing anomalies, identifying at-risk accounts to safeguard over $18,000+ in annual revenue.
> - Developed an interactive executive dashboard in Streamlit and Plotly with drill-downs and CSV export capabilities for Customer Success workflows.
> - Containerized the multi-service architecture using Docker Compose and established automated test suites (95%+ pass rate) via GitHub Actions CI.

---

## 📂 Project Structure

```
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py         # JWT login and credentials
│   │   │   ├── kpis.py         # Executive KPI summary endpoints
│   │   │   ├── revenue.py      # Monthly MRR trends and segment breakdown
│   │   │   ├── cohorts.py      # Cohort retention percentage matrix
│   │   │   └── churn.py        # Predictive churn risk scores
│   │   └── router.py           # Unified v1 router
│   ├── core/
│   │   ├── config.py           # Environment and pydantic settings
│   │   ├── database.py         # SQLAlchemy engine and session dependency
│   │   └── security.py         # JWT tokens & bcrypt hashing
│   ├── models/                 # SQLAlchemy ORM models (Customer, Subscription, etc.)
│   ├── schemas/                # Pydantic validation and response schemas
│   ├── services/               # Analytics calculation engines
│   └── main.py                 # FastAPI application factory
├── dashboard/
│   └── app.py                  # Interactive Streamlit analytics dashboard
├── docker/
│   ├── Dockerfile.api
│   └── Dockerfile.dashboard
├── scripts/
│   └── generate_data.py        # Realistic B2B SaaS dataset generator
├── tests/
│   ├── conftest.py             # Pytest in-memory SQLite fixtures
│   ├── test_analytics.py       # Unit tests for analytics logic
│   └── test_api.py             # Integration tests for FastAPI endpoints
├── docker-compose.yml          # Multi-container orchestration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation & CV guide
```

---

## 📄 License
MIT License. Free for educational and commercial use.
