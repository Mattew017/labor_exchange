class EntityNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InactiveJobError(Exception):
    def __str__(self):
        return "Вакансия не активна"


class DuplicateResponseError(Exception):
    def __str__(self):
        return "Дубликат отклика на вакансию"
