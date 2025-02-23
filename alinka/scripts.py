# flake8: noqa E402
# We could install alinka and expose that inside [project.scripts]
# but I don't believe that would make sense, as these are basically
# development utilities, so simpler was to modify sys.path
import sys

sys.path.insert(0, "")

from sqlalchemy import insert

from alinka.db.connection import db_session
from alinka.db.models import School
from tests.fixtures import schools

GREEN = "\033[32m"


def populate_schools():
    with db_session() as db:
        print(f"{GREEN}Dodaję szkoły do bazy danych.")
        db.execute(insert(School), schools)
        db.commit()
        print(f"{GREEN}Szkoły zostały dodane.")


populate_schools()
