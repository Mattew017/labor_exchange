from datetime import datetime

import factory

from storage.sqlalchemy.tables import Job


class JobFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Job

    id = factory.Sequence(lambda n: n)
    user_id = factory.Faker("pyint")
    title = factory.Faker("pystr")
    description = factory.Faker("email")
    salary_from = factory.Faker("pyint")
    salary_to = factory.Faker("pyint")
    is_active = factory.Faker("pybool")
    created_at = factory.LazyFunction(datetime.utcnow)
