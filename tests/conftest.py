import copy
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from alinka.db.models import Base
from tests.fixtures import common_data


@pytest.fixture
def common_data_fixture():
    return copy.deepcopy(common_data)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = scoped_session(sessionmaker(bind=engine))

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def mocked_db_session(db_session):
    with patch("alinka.db.queries.db_session", db_session) as session:
        yield session
