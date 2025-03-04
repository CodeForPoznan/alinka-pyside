import os

from PySide2.QtSql import QSqlDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from alinka.config import settings
from alinka.db.models import Base

db_dirname = os.path.dirname(settings.DB_PATH)
if not os.path.exists(db_dirname):
    os.makedirs(db_dirname)

engine = create_engine(f"sqlite:///{settings.DB_PATH}")
Base.metadata.create_all(engine)

db_session = scoped_session(sessionmaker(bind=engine))

qt_db = QSqlDatabase.addDatabase("QSQLITE")
qt_db.setDatabaseName(settings.DB_PATH)

# Add handling opening issues https://github.com/CodeForPoznan/alinka-pyside/issues/34
qt_db.open()
