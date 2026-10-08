import copy
import os
from unittest.mock import patch

# Ensure headless Qt platform before any PySide6 imports
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

# Provide a QApplication for tests that need real widgets. Using a single
# session-scoped application prevents crashes caused by creating multiple
# QApplications and avoids global sys.modules stubbing.
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    try:
        app.quit()
    except Exception:
        pass


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
