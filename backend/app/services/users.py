from app.repositories.users import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_or_create(self, subject_id: str, plan: str):
        return self.repository.get_by_subject_id(subject_id) or self.repository.create(subject_id)
