from decimal import Decimal


class DomainError(Exception):
    def __repr__(self):
        return str(self)


class EntityNotFoundError(DomainError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InactiveJobError(DomainError):
    def __str__(self):
        return "Вакансия не активна"


class DuplicateResponseError(DomainError):
    def __str__(self):
        return "Дубликат отклика на вакансию"


class InvalidSalaryRangeError(DomainError):
    def __init__(self, salary_from: Decimal, salary_to: Decimal):
        self.salary_from = salary_from
        self.salary_to = salary_to
        super().__init__()

    def __str__(self):
        return f"Минимальная зарплата {self.salary_from} не может быть больше максимальной {self.salary_to}"


class PermissionDeniedError(DomainError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
