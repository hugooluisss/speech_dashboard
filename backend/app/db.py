from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def session_factory():
    return sessionmaker(bind=create_engine(get_settings().database_url), expire_on_commit=False)
