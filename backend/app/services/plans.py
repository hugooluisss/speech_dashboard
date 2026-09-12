from app.repositories.plans import PlanRepository


class PlanService:
    def __init__(self, repository: PlanRepository):
        self.repository = repository

    def list_active(self):
        return self.repository.list_active()
