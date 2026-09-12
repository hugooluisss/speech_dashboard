from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models import UsagePeriod


class UsageRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, subject_id: str, period_key: str) -> UsagePeriod | None:
        return self.session.scalar(select(UsagePeriod).where(
            UsagePeriod.subject_id == subject_id,
            UsagePeriod.period_key == period_key,
        ))

    def increment(self, subject_id: str, period_key: str, word_count: int) -> UsagePeriod:
        values = {"subject_id": subject_id, "period_key": period_key, "words_used": word_count}
        dialect = self.session.bind.dialect.name
        if dialect == "postgresql":
            statement = postgres_insert(UsagePeriod).values(**values).on_conflict_do_update(
                index_elements=["subject_id", "period_key"],
                set_={"words_used": UsagePeriod.words_used + word_count, "updated_at": func.now()},
            )
        elif dialect == "sqlite":
            statement = sqlite_insert(UsagePeriod).values(**values).on_conflict_do_update(
                index_elements=["subject_id", "period_key"],
                set_={"words_used": UsagePeriod.words_used + word_count, "updated_at": func.now()},
            )
        else:
            raise RuntimeError(f"Unsupported database dialect: {dialect}")
        self.session.execute(statement)
        self.session.commit()
        return self.get(subject_id, period_key)
