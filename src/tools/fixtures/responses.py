import factory

from storage.sqlalchemy.tables import Response


class ResponseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Response

    id = factory.Sequence(lambda n: n)
    job_id = 0
    user_id = 0
    message = factory.Faker("pystr")
