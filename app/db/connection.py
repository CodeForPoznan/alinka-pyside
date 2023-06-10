import os

from config import settings
from db.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.path.exists(settings.PERSISTENT_DATA_PATH):
    os.mkdir(settings.PERSISTENT_DATA_PATH)


engine = create_engine(f"sqlite:///{settings.DB_PATH}")
Base.metadata.create_all(engine)


db_session = scoped_session(sessionmaker(bind=engine))
