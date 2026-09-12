from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Plan


class PlanRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_active(self) -> list[Plan]:
        return list(self.session.scalars(select(Plan).where(Plan.active).order_by(Plan.tier_id)))

    def get(self, tier_id: str) -> Plan | None:
        return self.session.get(Plan, tier_id)
