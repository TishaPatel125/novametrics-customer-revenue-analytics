from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Dict
from collections import defaultdict
from app.models.customer import Customer
from app.schemas.analytics import CohortRetentionResponse, CohortRetentionRow


class CohortAnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_retention_matrix(self, max_cohorts: int = 12, max_periods: int = 6) -> CohortRetentionResponse:
        # Fetch all customers with signup_date and churn_date
        customers = (
            self.db.query(Customer.id, Customer.signup_date, Customer.churn_date)
            .order_by(Customer.signup_date.asc())
            .all()
        )

        if not customers:
            return CohortRetentionResponse(cohorts=[], max_periods=0)

        # Group customers by signup YYYY-MM
        cohort_groups = defaultdict(list)
        for c in customers:
            cohort_key = c.signup_date.strftime("%Y-%m")
            cohort_groups[cohort_key].append(c)

        # Sort cohort keys chronologically, take last `max_cohorts`
        sorted_cohorts = sorted(cohort_groups.keys())[-max_cohorts:]
        cohort_rows: List[CohortRetentionRow] = []

        now = datetime.now(timezone.utc)

        for cohort_key in sorted_cohorts:
            group = cohort_groups[cohort_key]
            cohort_size = len(group)
            if cohort_size == 0:
                continue

            cohort_year, cohort_month = map(int, cohort_key.split("-"))
            retention_map: Dict[str, float] = {"M0": 100.0}

            for period in range(1, max_periods + 1):
                # Calculate period date
                target_month = cohort_month + period
                target_year = cohort_year + (target_month - 1) // 12
                target_month = ((target_month - 1) % 12) + 1
                
                period_dt = datetime(target_year, target_month, 1, tzinfo=timezone.utc)

                # Skip future months that haven't occurred yet
                if period_dt > now:
                    continue

                # A customer is retained at period_dt if churn_date is None or churn_date >= period_dt
                retained_count = sum(
                    1
                    for c in group
                    if c.churn_date is None or (c.churn_date.replace(tzinfo=timezone.utc) if c.churn_date.tzinfo is None else c.churn_date) >= period_dt
                )
                retention_rate = round((retained_count / cohort_size) * 100.0, 1)
                retention_map[f"M{period}"] = retention_rate

            cohort_rows.append(
                CohortRetentionRow(
                    cohort_month=cohort_key,
                    cohort_size=cohort_size,
                    retention_percentages=retention_map,
                )
            )

        return CohortRetentionResponse(cohorts=cohort_rows, max_periods=max_periods)
