import os
import sys

from alembic import command, config
from PySide2.QtSql import QSqlDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from alinka.config import settings

db_dirname = os.path.dirname(settings.DB_PATH)
if not os.path.exists(db_dirname):
    os.makedirs(db_dirname)

if getattr(sys, "frozen", False):
    alembic_dirname = sys._MEIPASS
else:
    alembic_dirname = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

alembic_cfg = config.Config(os.path.join(alembic_dirname, "alembic.ini"))

command.upgrade(alembic_cfg, "head")

engine = create_engine(f"sqlite:///{settings.DB_PATH}")
db_session = scoped_session(sessionmaker(bind=engine))

qt_db = QSqlDatabase.addDatabase("QSQLITE")
qt_db.setDatabaseName(settings.DB_PATH)

# Add handling opening issues https://github.com/CodeForPoznan/alinka-pyside/issues/34
qt_db.open()
