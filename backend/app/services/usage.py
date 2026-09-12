from datetime import datetime, timezone

from app.models import Plan
from app.repositories.usage import UsageRepository


class UsageService:
    def __init__(self, repository: UsageRepository):
        self.repository = repository

    @staticmethod
    def current_period() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m")

    def get_usage(self, subject_id: str, plan: Plan) -> dict[str, int | str]:
        period = self.current_period()
        usage = self.repository.get(subject_id, period)
        used = usage.words_used if usage else 0
        return {"used": used, "limit": plan.word_limit, "period": period, "remaining": max(plan.word_limit - used, 0)}

    def has_remaining_quota(self, subject_id: str, plan: Plan) -> bool:
        return self.get_usage(subject_id, plan)["remaining"] > 0

    def record_usage(self, subject_id: str, word_count: int) -> None:
        if word_count < 0:
            raise ValueError("word_count must be non-negative")
        self.repository.increment(subject_id, self.current_period(), word_count)
