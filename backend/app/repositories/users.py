from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_subject_id(self, subject_id: str) -> User | None:
        return self.session.scalar(select(User).where(User.subject_id == subject_id))

    def create(self, subject_id: str) -> User:
        user = User(subject_id=subject_id)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_all(self) -> list[User]:
        return list(self.session.scalars(select(User).order_by(User.subject_id)))
