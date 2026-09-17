"""Data generation script for NovaMetrics Customer Intelligence Platform.

Generates realistic B2B SaaS customer, subscription, billing transaction,
and product usage data over a 24-month horizon.
"""

import random
import os
import sys
from datetime import datetime, timezone, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal, engine, Base
from app.models.customer import Customer
from app.models.subscription import Subscription
from app.models.transaction import Transaction
from app.models.event import UsageEvent

# Seed for reproducibility
random.seed(42)

INDUSTRIES = ["SaaS", "Fintech", "Healthcare", "E-Commerce", "EdTech", "Logistics"]
COUNTRIES = ["United States", "Canada", "United Kingdom", "Germany", "Australia", "France"]
COMPANIES = [
    "Apex Global", "CloudSync Labs", "DataPulse", "Nexora Health", "BlueHorizon",
    "OmniRetail", "Quantum AI", "Strata Financial", "Vanguard Media", "PeakCommerce",
    "Silverline Logistics", "Elevate HR", "BrightPath Learning", "Zulip Security",
    "AlphaCore Technologies", "Beacon Systems", "Veritas Analytics", "IronClad Supply",
    "Skyward Digital", "Frontier Capital", "Crestview Software", "Prism Cloud",
]
FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Avery", "Jamie", "Dakota", "Reese", "Quinn"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson"]

PLANS = {
    "SMB": {"tier": "Starter", "mrr": 49.0},
    "Mid-Market": {"tier": "Growth", "mrr": 199.0},
    "Enterprise": {"tier": "Enterprise", "mrr": 899.0},
}

CHURN_REASONS = [
    "Switched to competitor",
    "Budget constraints / downsized",
    "Lacked requested analytics feature",
    "Low team adoption / onboarding friction",
    "Business closed or acquired",
]


def seed_database(num_customers: int = 600):
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Customer).count()
        if existing >= 100:
            print(f"Database already populated with {existing} customers. Skipping seed.")
            return

        print(f"Generating realistic dataset for {num_customers} customers over 24 months...")
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=730)  # ~24 months ago

        customers_batch = []
        subscriptions_batch = []
        transactions_batch = []
        events_batch = []

        for i in range(1, num_customers + 1):
            cust_code = f"CUST-{1000 + i}"
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            company = f"{random.choice(COMPANIES)} {random.randint(10, 99)}"
            email = f"{name.lower().replace(' ', '.')}@{company.lower().replace(' ', '')}.com"
            country = random.choice(COUNTRIES)
            industry = random.choice(INDUSTRIES)

            # Segment distribution: 60% SMB, 30% Mid-Market, 10% Enterprise
            seg_roll = random.random()
            if seg_roll < 0.60:
                segment = "SMB"
                churn_prob = 0.22
            elif seg_roll < 0.90:
                segment = "Mid-Market"
                churn_prob = 0.12
            else:
                segment = "Enterprise"
                churn_prob = 0.04

            # Signup date with exponential growth curve towards recent months
            random_days = int(730 * (1.0 - (random.random() ** 1.8)))
            signup_dt = now - timedelta(days=random_days)

            # Churn determination
            is_churned = random.random() < churn_prob and (now - signup_dt).days > 45
            churn_dt = None
            churn_reason = None

            if is_churned:
                # Churned between 30 days after signup and now
                active_days = random.randint(30, max(31, (now - signup_dt).days - 10))
                churn_dt = signup_dt + timedelta(days=active_days)
                churn_reason = random.choice(CHURN_REASONS)

            customer = Customer(
                customer_code=cust_code,
                name=name,
                email=email,
                company=company,
                country=country,
                segment=segment,
                industry=industry,
                signup_date=signup_dt,
                churn_date=churn_dt,
                churn_reason=churn_reason,
            )
            customers_batch.append(customer)

        db.add_all(customers_batch)
        db.flush()

        print("Generating subscriptions and historical transaction ledgers...")
        tx_counter = 1
        for customer in customers_batch:
            plan_info = PLANS[customer.segment]
            mrr = plan_info["mrr"]
            if customer.segment == "Enterprise":
                mrr += random.choice([0, 200, 400])

            sub_status = "canceled" if customer.churn_date else "active"
            sub = Subscription(
                customer_id=customer.id,
                plan_tier=plan_info["tier"],
                billing_cycle="monthly",
                mrr_amount=mrr,
                status=sub_status,
                start_date=customer.signup_date,
                end_date=customer.churn_date,
            )
            subscriptions_batch.append(sub)

            # Generate monthly transactions
            end_billing_dt = customer.churn_date if customer.churn_date else now
            cur_dt = customer.signup_date
            while cur_dt <= end_billing_dt:
                tx_code = f"TX-{10000 + tx_counter}"
                tx_counter += 1

                # 97% success, 3% failure
                tx_status = "succeeded" if random.random() > 0.03 else "failed"

                tx = Transaction(
                    customer_id=customer.id,
                    transaction_code=tx_code,
                    amount=mrr,
                    currency="USD",
                    status=tx_status,
                    payment_method=random.choice(["credit_card", "bank_transfer"]),
                    transaction_date=cur_dt,
                )
                transactions_batch.append(tx)
                cur_dt += timedelta(days=30)

            # Generate Usage Events
            # Active/healthy customers have continuous events up to now
            # Churn-risk or churned customers show declining/stagnant events
            num_events = random.randint(15, 60)
            is_high_risk = (not customer.churn_date) and (random.random() < 0.18)

            for _ in range(num_events):
                if customer.churn_date:
                    event_dt = customer.signup_date + timedelta(days=random.randint(0, max(1, (customer.churn_date - customer.signup_date).days)))
                elif is_high_risk:
                    # High risk: events concentrated 40-90 days ago, quiet recently
                    event_dt = now - timedelta(days=random.randint(35, 120))
                else:
                    # Normal active customer
                    event_dt = customer.signup_date + timedelta(days=random.randint(0, max(1, (now - customer.signup_date).days)))

                ev = UsageEvent(
                    customer_id=customer.id,
                    event_type=random.choice(["login", "report_export", "api_call", "dashboard_view"]),
                    event_time=event_dt,
                    properties={"source": "web_app"},
                )
                events_batch.append(ev)

        db.add_all(subscriptions_batch)
        db.add_all(transactions_batch)
        db.add_all(events_batch)
        db.commit()

        print(f"Successfully loaded:")
        print(f"  - {len(customers_batch)} Customers")
        print(f"  - {len(subscriptions_batch)} Subscriptions")
        print(f"  - {len(transactions_batch)} Billing Transactions")
        print(f"  - {len(events_batch)} Usage Events")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
