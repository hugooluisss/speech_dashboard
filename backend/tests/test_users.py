from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.repositories.users import UserRepository
from app.services.users import UserService


def test_repository_create_and_idempotent_lookup():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        repository = UserRepository(session)
        created = repository.create("user-1")
        assert repository.get_by_subject_id("user-1").subject_id == created.subject_id


def test_service_reuses_existing_user():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        service = UserService(UserRepository(session))
        first = service.get_or_create("user-1", "plan-free")
        second = service.get_or_create("user-1", "plan-pro")
        assert first.subject_id == second.subject_id == "user-1"
