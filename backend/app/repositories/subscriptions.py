from sqlalchemy.orm import Session

from app.models import UserSubscription


class SubscriptionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_subject(self, subject_id: str) -> UserSubscription | None:
        return self.session.get(UserSubscription, subject_id)

    def get_by_customer(self, customer_id: str) -> UserSubscription | None:
        return self.session.query(UserSubscription).filter_by(stripe_customer_id=customer_id).one_or_none()

    def save(self, subject_id: str, customer_id: str | None, subscription_id: str | None, status: str, plan_tier_id: str):
        row = self.get_by_subject(subject_id) or UserSubscription(subject_id=subject_id, status=status, plan_tier_id=plan_tier_id)
        row.stripe_customer_id, row.stripe_subscription_id = customer_id, subscription_id
        row.status, row.plan_tier_id = status, plan_tier_id
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row
