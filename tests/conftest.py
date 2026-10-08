import os
import copy
from unittest.mock import patch

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from alinka.db.models import Base
from tests.fixtures import common_data

# Create in-memory DB and session for tests
engine = create_engine("sqlite:///:memory:")
# We may consider running Alembic migrations for tests
# but it will require major change in how we setup & teardown test cases
Base.metadata.create_all(engine)

db_session = scoped_session(sessionmaker(bind=engine))


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


def pytest_configure(config):
    mock_db_session = patch("alinka.db.queries.db_session", db_session)
    mock_db_session.start()


def pytest_runtest_teardown(item):
    from alinka.db.models import Base

    with db_session() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())

        db.commit()
