import copy
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from alinka.db.models import Base
from tests.fixtures import common_data

engine = create_engine("sqlite:///:memory:")
# We may consider running Alembic migrations for tests
# but it will require major change in how we setup & teardown test cases
Base.metadata.create_all(engine)

db_session = scoped_session(sessionmaker(bind=engine))


@pytest.fixture
def common_data_fixture():
    return copy.deepcopy(common_data)


def pytest_configure(config):
    mock_db_session = patch("alinka.db.queries.db_session", db_session)
    mock_db_session.start()


def pytest_runtest_teardown(item):
    from alinka.db.models import Base

    with db_session() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())

        db.commit()
