import copy
import os
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from alinka.db.models import Base
from tests.fixtures import common_data


@pytest.fixture(scope="session", autouse=True)
def qapp():
    # Ensure headless Qt platform before importing PySide6
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    # Import QApplication lazily so PySide6 is imported after the environment is set
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
    try:
        app.quit()
    except Exception:
        pass


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
        session.remove()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def mocked_db_session(db_session):
    with (
        patch("alinka.db.queries.db_session", db_session),
        patch("tests.factories.db_session", db_session),
    ):
        yield db_session
