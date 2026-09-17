from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import numpy as np
from app.models.customer import Customer
from app.models.subscription import Subscription
from app.models.transaction import Transaction
from app.models.event import UsageEvent
from app.schemas.analytics import ChurnOverview, ChurnRiskCustomer


class ChurnRiskService:
    def __init__(self, db: Session):
        self.db = db

    def get_churn_overview(self, limit: int = 50) -> ChurnOverview:
        now = datetime.now(timezone.utc)
        active_customers = (
            self.db.query(Customer)
            .filter(Customer.churn_date.is_(None))
            .all()
        )

        scored_customers: List[ChurnRiskCustomer] = []
        high_risk = 0
        med_risk = 0
        low_risk = 0
        total_mrr_at_risk = 0.0

        for cust in active_customers:
            # Active subscription MRR
            sub = next((s for s in cust.subscriptions if s.status == "active"), None)
            current_mrr = round(sub.mrr_amount if sub else 0.0, 2)
            plan_tier = sub.plan_tier if sub else "None"

            # Event analysis (last 30 days vs previous 30 days)
            thirty_d_ago = now - timedelta(days=30)
            sixty_d_ago = now - timedelta(days=60)

            events_last_30 = sum(
                1 for e in cust.events
                if (e.event_time.replace(tzinfo=timezone.utc) if e.event_time.tzinfo is None else e.event_time) >= thirty_d_ago
            )
            events_prev_30 = sum(
                1 for e in cust.events
                if sixty_d_ago <= (e.event_time.replace(tzinfo=timezone.utc) if e.event_time.tzinfo is None else e.event_time) < thirty_d_ago
            )

            # Failed transactions
            failed_tx = sum(1 for t in cust.transactions if t.status == "failed")

            # Tenure in days
            signup_dt = cust.signup_date.replace(tzinfo=timezone.utc) if cust.signup_date.tzinfo is None else cust.signup_date
            tenure_days = max(1, (now - signup_dt).days)

            # Heuristic / Predictive feature weights
            risk_score = 0.15  # baseline
            risk_factors: List[str] = []

            # 1. Activity decline signal
            if events_prev_30 > 0 and events_last_30 < (events_prev_30 * 0.4):
                drop_pct = int(round((1 - (events_last_30 / events_prev_30)) * 100))
                risk_score += 0.35
                risk_factors.append(f"Usage dropped by {drop_pct}% in last 30 days")
            elif events_last_30 == 0:
                risk_score += 0.40
                risk_factors.append("Zero user sessions recorded in last 30 days")

            # 2. Payment failures
            if failed_tx > 0:
                risk_score += 0.25
                risk_factors.append(f"{failed_tx} failed billing attempts")

            # 3. Tenure risk (new accounts in first 60 days have highest early-life churn)
            if tenure_days < 60:
                risk_score += 0.10
                risk_factors.append("Early lifecycle account (<60 days tenure)")

            # Normalize score between 0.05 and 0.95
            probability = min(0.95, max(0.05, round(risk_score, 2)))

            # Risk classification
            if probability >= 0.60:
                risk_level = "High"
                high_risk += 1
                total_mrr_at_risk += current_mrr
            elif probability >= 0.35:
                risk_level = "Medium"
                med_risk += 1
            else:
                risk_level = "Low"
                low_risk += 1

            if not risk_factors:
                risk_factors.append("Normal healthy platform utilization")

            scored_customers.append(
                ChurnRiskCustomer(
                    customer_id=cust.id,
                    customer_code=cust.customer_code,
                    name=cust.name,
                    company=cust.company,
                    segment=cust.segment,
                    plan_tier=plan_tier,
                    current_mrr=current_mrr,
                    churn_probability=probability,
                    risk_level=risk_level,
                    key_risk_factors=risk_factors,
                )
            )

        # Sort by churn probability descending
        scored_customers.sort(key=lambda x: (x.churn_probability, x.current_mrr), reverse=True)

        # Historical churn reasons breakdown
        reasons_query = (
            self.db.query(Customer.churn_reason, func.count(Customer.id))
            .filter(Customer.churn_reason.isnot(None))
            .group_by(Customer.churn_reason)
            .all()
        )
        top_reasons = {r[0]: int(r[1]) for r in reasons_query if r[0]}

        return ChurnOverview(
            high_risk_count=high_risk,
            medium_risk_count=med_risk,
            low_risk_count=low_risk,
            mrr_at_risk=round(total_mrr_at_risk, 2),
            top_churn_reasons=top_reasons,
            high_risk_customers=scored_customers[:limit],
        )
