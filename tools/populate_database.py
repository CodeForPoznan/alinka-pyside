# flake8: noqa E402
# We could install alinka and expose that inside [project.scripts]
# but I don't believe that would make sense, as these are basically
# development utilities, so simpler was to modify sys.path
import sys

sys.path.insert(0, "")

import random

from tqdm import trange

from alinka.db.connection import db_session
from tests.factories import SchoolFactory, SupportCenterFactory, TeamMemberFactory


def populate_database():
    print("Generate support center")
    SupportCenterFactory()
    print("Generate team memebrs")
    for _ in trange(random.randint(3, 20)):
        TeamMemberFactory()
    print("Generate schools")
    for _ in trange(random.randint(3, 100)):
        SchoolFactory()
    db_session.commit()


if __name__ == "__main__":
    populate_database()
