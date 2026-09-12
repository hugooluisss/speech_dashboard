from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Plan, UsagePeriod
from app.repositories.usage import UsageRepository
from app.services.usage import UsageService


def make_session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine


def test_usage_repository_creates_and_increments_period():
    engine = make_session()
    with Session(engine) as session:
        repository = UsageRepository(session)
        assert repository.increment("user-1", "2026-09", 10).words_used == 10
        assert repository.increment("user-1", "2026-09", 5).words_used == 15


def test_usage_service_computes_remaining_and_quota():
    engine = make_session()
    plan = Plan(tier_id="plan-pro", display_name="Pro", keycloak_role="plan-pro", word_limit=100, period_unit="month")
    with Session(engine) as session:
        service = UsageService(UsageRepository(session))
        assert service.get_usage("user-1", plan)["used"] == 0
        service.record_usage("user-1", 30)
        assert service.get_usage("user-1", plan)["remaining"] == 70
        service.record_usage("user-1", 70)
        assert not service.has_remaining_quota("user-1", plan)
        service.record_usage("user-1", 20)
        assert service.get_usage("user-1", plan)["remaining"] == 0


def test_usage_repository_parallel_increments_sum_on_postgres():
    engine = create_engine("postgresql+psycopg://speech:speech@localhost:5433/speech", pool_size=2)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.query(UsagePeriod).filter_by(subject_id="concurrent", period_key="2026-09").delete()
        session.commit()

    def increment():
        with Session(engine) as session:
            UsageRepository(session).increment("concurrent", "2026-09", 1)

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda _: increment(), range(2)))
    with Session(engine) as session:
        assert UsageRepository(session).get("concurrent", "2026-09").words_used == 2
