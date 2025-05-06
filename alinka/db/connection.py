import os
import sys

from alembic import command, config
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

engine = create_engine(f"sqlite:///{settings.DB_PATH}")  # noqa: E231
db_session = scoped_session(sessionmaker(bind=engine))
