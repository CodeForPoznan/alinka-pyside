# flake8: noqa E402
# We could install alinka and expose that inside [project.scripts]
# but I don't believe that would make sense, as these are basically
# development utilities, so simpler was to modify sys.path
import sys

sys.path.insert(0, "")

import random

from tqdm import trange

from alinka.db.connection import db_session
from tests.factories import (
    decision_factory,
    school_factory,
    support_center_factory,
    team_member_factory,
)


def populate_database():
    with db_session() as db:
        DecisionFactory = decision_factory(db)
        SchoolFactory = school_factory(db)
        SupportCenterFactory = support_center_factory(db)
        TeamMemberFactory = team_member_factory(db)

        print("Generate support center")
        SupportCenterFactory()

        print("Generate team memebrs")
        for _ in trange(random.randint(3, 20)):
            TeamMemberFactory()

        print("Generate schools")
        for _ in trange(random.randint(3, 100)):
            SchoolFactory()

        print("Generate decisions")
        for _ in trange(random.randint(10, 1000)):
            DecisionFactory()

        db.commit()


if __name__ == "__main__":
    populate_database()
