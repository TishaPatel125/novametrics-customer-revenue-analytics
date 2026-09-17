import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.models.customer import Customer
from app.models.subscription import Subscription
from app.models.transaction import Transaction
from app.models.event import UsageEvent
from app.models.user import User
from app.core.security import get_password_hash

# Shared in-memory SQLite with StaticPool for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed minimal deterministic test records
    now = datetime.now(timezone.utc)

    # Test Admin User
    admin = User(
        email="test_admin@novametrics.io",
        hashed_password=get_password_hash("test_password123"),
        full_name="Test Admin",
        is_superuser=True,
        role="admin",
    )
    db.add(admin)

    # Customer 1: Active SMB
    c1 = Customer(
        customer_code="CUST-001",
        name="Alice Walker",
        email="alice@walker.com",
        company="Walker Tech",
        segment="SMB",
        signup_date=now - timedelta(days=90),
        churn_date=None,
    )
    db.add(c1)
    db.flush()

    s1 = Subscription(
        customer_id=c1.id,
        plan_tier="Starter",
        mrr_amount=49.0,
        status="active",
        start_date=c1.signup_date,
    )
    db.add(s1)

    t1 = Transaction(
        customer_id=c1.id,
        transaction_code="TX-001",
        amount=49.0,
        status="succeeded",
        transaction_date=now - timedelta(days=15),
    )
    db.add(t1)

    e1 = UsageEvent(
        customer_id=c1.id,
        event_type="login",
        event_time=now - timedelta(days=2),
    )
    db.add(e1)

    # Customer 2: Churned Mid-Market
    c2 = Customer(
        customer_code="CUST-002",
        name="Bob Builder",
        email="bob@builder.com",
        company="Builder Corp",
        segment="Mid-Market",
        signup_date=now - timedelta(days=120),
        churn_date=now - timedelta(days=10),
        churn_reason="Budget constraints / downsized",
    )
    db.add(c2)
    db.flush()

    s2 = Subscription(
        customer_id=c2.id,
        plan_tier="Growth",
        mrr_amount=199.0,
        status="canceled",
        start_date=c2.signup_date,
        end_date=c2.churn_date,
    )
    db.add(s2)

    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
