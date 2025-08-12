import random
from datetime import date, datetime, time, timedelta, timezone

from factory import Faker as factory_faker
from factory import (
    LazyAttribute,
    Maybe,
    SelfAttribute,
    SubFactory,
    fuzzy,
    lazy_attribute,
)
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from alinka import rspo_client
from alinka.constants import ActivityForm, Issue, Reason
from alinka.constants.common import RPSO_SUPPORT_CENTER_TYPE_ID
from alinka.db.models import Decision, School, SupportCenter, TeamMember
from alinka.schemas.rspo_schema import InstitutionRequestBody
from alinka.widget.containers.main_body.content.settings.settings_tabs.schools_tab.select_school_group import (
    SelectSchoolGroup,
)
from tests.factories.atrributes import (
    FuzzySupportCenterKurator,
    FuzzySupportCenterNameGenitive,
    NoPrefixFullName,
    full_name_genitive,
)

DATE_FORMAT = "%m/%d/%Y"
now = datetime.now(timezone.utc)

faker = Faker(locale="pl_PL")
factory_faker._DEFAULT_LOCALE = "pl_PL"


def decision_factory(session):
    class DecisionFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Decision
            sqlalchemy_session = session
            exclude = (
                "create_new_school",
                "_school",
                "_second_parent_exists",
                "_support_center",
                "create_new_meeting_members",
            )

        created_at = fuzzy.FuzzyDateTime(
            start_dt=now - timedelta(days=365),
            end_dt=now,
        )

        child_full_name = NoPrefixFullName()
        child_full_name_gen = LazyAttribute(lambda obj: full_name_genitive(obj.child_full_name))
        child_town = factory_faker("city")
        child_address = factory_faker("street_address")
        child_postal_code = factory_faker("postcode")
        child_pesel = factory_faker("pesel")
        child_birth_date = fuzzy.FuzzyDate(
            start_date=now.date() - timedelta(days=18 * 350),
            # This ensures that child is older then decision itself
            end_date=now.date() - timedelta(days=350),
        )
        child_birth_place = factory_faker("city")
        child_student = fuzzy.FuzzyChoice(choices=[True, False])
        # this should also support None at some point
        klass = fuzzy.FuzzyInteger(1, 8)
        # tis should also support None at some point
        profession = factory_faker("job")

        create_new_school = False
        school_parent_organisation = SelfAttribute("_school.parent_organisation_name")
        school_type = SelfAttribute("_school.type")
        school_name = SelfAttribute("_school.name")
        school_address = SelfAttribute("_school.address")
        school_town = SelfAttribute("_school.town")
        school_postal_code = SelfAttribute("_school.postal_code")
        school_post = SelfAttribute("_school.post")

        _second_parent_exists = fuzzy.FuzzyChoice(choices=[True, False])
        address_child_checkbox = fuzzy.FuzzyChoice(choices=[True, False])
        address_first_parent_checkbox = Maybe(
            "_second_parent_exists",
            yes_declaration=fuzzy.FuzzyChoice(choices=[True, False]),
            no_declaration=False,
        )

        first_parent_full_name = NoPrefixFullName()
        first_parent_full_name_gen = LazyAttribute(lambda obj: full_name_genitive(obj.first_parent_full_name))
        # for unknown reason these 2 values are nullable=False
        first_parent_address = factory_faker("street_address")
        first_parent_town = factory_faker("city")
        first_parent_postal_code = Maybe(
            "address_child_checkbox",
            yes_declaration=None,
            no_declaration=factory_faker("postcode"),
        )

        second_parent_full_name = Maybe(
            "_second_parent_exists",
            yes_declaration=NoPrefixFullName(),
            no_declaration=None,
        )
        second_parent_full_name_gen = Maybe(
            "_second_parent_exists",
            yes_declaration=LazyAttribute(lambda obj: full_name_genitive(obj.second_parent_full_name)),
            no_declaration=None,
        )
        second_parent_address = Maybe(
            "address_first_parent_checkbox",
            yes_declaration=None,
            no_declaration=factory_faker("street_address"),
        )
        second_parent_town = Maybe(
            "address_first_parent_checkbox",
            yes_declaration=None,
            no_declaration=factory_faker("city"),
        )
        second_parent_postal_code = Maybe(
            "address_first_parent_checkbox",
            yes_declaration=None,
            no_declaration=factory_faker("postcode"),
        )

        _support_center = SubFactory(support_center_factory(session))
        support_center_name_nominative = SelfAttribute("_support_center.name_nominative")
        support_center_name_genitive = SelfAttribute("_support_center.name_genitive")
        support_center_kurator = SelfAttribute("_support_center.kurator")
        support_center_address = SelfAttribute("_support_center.address")
        support_center_town = SelfAttribute("_support_center.town")
        support_center_postal_code = SelfAttribute("_support_center.postal_code")
        support_center_post = SelfAttribute("_support_center.post")
        support_center_institute_name = SelfAttribute("_support_center.institute_name")

        issue = fuzzy.FuzzyChoice(choices=[i.value for i in Issue])
        activity_form = fuzzy.FuzzyChoice(choices=[i.value for i in ActivityForm])

        create_new_meeting_members = False

        @lazy_attribute
        def meeting_members(self):
            db = self._Resolver__step.builder.factory_meta.sqlalchemy_session
            desired_members = random.randint(3, 6)

            if self.create_new_meeting_members:
                members = team_member_factory(db).create_batch(desired_members)
            else:
                desired_members = min(desired_members, db.query(TeamMember).count())
                members = random.sample(
                    db.query(TeamMember).all(),
                    desired_members,
                )

            return [
                {
                    "name": member.name,
                    "function": member.function,
                }
                for member in members
            ]

        @lazy_attribute
        def modified_at(self):
            return fuzzy.FuzzyDateTime(
                start_dt=self.created_at,
                end_dt=now,
            ).fuzz()

        @lazy_attribute
        def meeting_date(self):
            return fuzzy.FuzzyDate(
                start_date=self.modified_at - timedelta(weeks=2),
                end_date=self.modified_at + timedelta(weeks=2),
            ).fuzz()

        @lazy_attribute
        def meeting_time(self):
            """
            Lets limit ourselelves to working hours and 5-minute increment.
            """
            return time(
                hour=random.randint(7, 20),
                minute=random.randint(0, 59 // 5) * 5,
            ).isoformat()

        @lazy_attribute
        def application_date(self):
            return fuzzy.FuzzyDate(
                start_date=self.meeting_date - timedelta(days=90),
                end_date=self.meeting_date,
            ).fuzz()

        @lazy_attribute
        def decision_no(self):
            return f"PPP.{self.meeting_date.strftime('%Y')}.AC.{random.randint(1, 500)}"

        @lazy_attribute
        def reasons(self):
            if self.issue in [Issue.INDYWIDUALNE.value, Issue.INDYWIDUALNE_ROCZNE]:
                return faker.random_choices([Reason.UNIEMOZLIWIAJACY, Reason.ZNACZNIE_UTRUDNIAJACY])
            elif self.issue == Issue.SPECJALNE:
                number_of_reasons = faker.pyint(1, 2)
                return faker.random_choices(
                    [
                        Reason.AUTYZM,
                        Reason.LEKKIE,
                        Reason.NIESLYSZACE,
                        Reason.NIEWIDZACE,
                        Reason.RUCHOWA,
                        Reason.SLABOSLYSZACE,
                        Reason.SLABOWIDZACE,
                    ],
                    length=number_of_reasons,
                )
            elif self.issue == Issue.REWALIDACYJNE:
                return [Reason.GLEBOKIE]
            else:
                return [Reason.SLABOWIDZACE]

        @lazy_attribute
        def period(self):
            if self.issue in [Issue.INDYWIDUALNE.value, Issue.INDYWIDUALNE_ROCZNE]:
                return (
                    f"{date.today().strftime(DATE_FORMAT)} -"
                    f" {faker.future_date(end_date=timedelta(weeks=50)).strftime(DATE_FORMAT)}"
                )
            elif self.issue == Issue.SPECJALNE:
                return faker.random_choice(
                    ["pierwszego etapu edukacyjnego", "nauki w szkole ponadpodstawowej", "drugiego etapu edukacyjnego"]
                )
            elif self.issue == Issue.REWALIDACYJNE:
                return "pięciu lat"
            elif self.issue == Issue.OPINIA:
                return "do rozpoczęcia spełniania obowiązku szkolnego"
            else:
                return ""

        @lazy_attribute
        def _school(self):
            session = self._Resolver__step.builder.factory_meta.sqlalchemy_session

            if self.create_new_school:
                return school_factory(session)()
            return random.choice(session.query(School).all())

    return DecisionFactory


def support_center_factory(session):
    class SupportCenterFactory(SQLAlchemyModelFactory):
        class Meta:
            model = SupportCenter
            sqlalchemy_session = session
            sqlalchemy_get_or_create = ("id",)
            exclude = ("_rspo",)

        # This is first number used in autoincrement int
        # alongside sqlalchemy_get_or_create it makes
        # SupportCenter basically a singleton
        id = 1

        district_id = LazyAttribute(lambda o: o._rspo["district_id"])
        rspo = LazyAttribute(lambda o: o._rspo["id"])
        name_nominative = LazyAttribute(lambda o: o._rspo["name"])
        name_genitive = FuzzySupportCenterNameGenitive()
        kurator = FuzzySupportCenterKurator()
        address = LazyAttribute(lambda o: o._rspo["address"])
        town = LazyAttribute(lambda o: o._rspo["town"])
        postal_code = LazyAttribute(lambda o: o._rspo["postal_code"])
        post = LazyAttribute(lambda o: o._rspo["post"])

        @lazy_attribute
        def province_id(self):
            return faker.random_element(rspo_client.list_provinces()).id

        @lazy_attribute
        def _rspo(self):
            """
            As we encountered discrticts without any RSPO, instead of choosing random district
            and then choosing random RSPO from that disctrict only, we shuffle district from provnce
            and then we settle with first district, that contains at least one RSOP.
            """
            districts = rspo_client.list_districts(province_id=self.province_id)
            random.shuffle(districts)

            for district in districts:
                rspos = rspo_client.list_institutions(
                    body=InstitutionRequestBody(
                        province_id=self.province_id,
                        district_id=district.id,
                        institution_type_ids=[RPSO_SUPPORT_CENTER_TYPE_ID],
                    )
                ).items
                if len(rspos) > 0:
                    # rspos contains list of Pydantic's Institution type
                    # but we need to provide district for LazyAttribute
                    # so simples we can do is to dump Institution to dict
                    # and expand that dict
                    return {
                        "district_id": district.id,
                        **faker.random_element(rspos).dict(),
                    }

        @lazy_attribute
        def institute_name(self):
            return f"Zespół Orzekający przy {self.name_genitive}"

    return SupportCenterFactory


def team_member_factory(session):
    class TeamMemberFactory(SQLAlchemyModelFactory):
        class Meta:
            model = TeamMember
            sqlalchemy_session = session

        name = NoPrefixFullName()
        function = fuzzy.FuzzyChoice(
            [
                "logopeda",
                "pedagog",
                "psycholog",
                "socjoterapeuta",
                "tyflopedagog",
            ]
        )

    return TeamMemberFactory


def school_factory(session):
    class SchoolFactory(SQLAlchemyModelFactory):
        class Meta:
            model = School
            sqlalchemy_session = session
            exclude = ("_rspo",)

        rspo_id = SelfAttribute("_rspo.id")
        rspo_type_id = SelfAttribute("_rspo.type.id")
        parent_organisation_name = SelfAttribute("_rspo.parent_organisation_name")
        name = SelfAttribute("_rspo.name")
        address = SelfAttribute("_rspo.address")
        town = SelfAttribute("_rspo.town")
        postal_code = SelfAttribute("_rspo.postal_code")
        post = SelfAttribute("_rspo.post")

        @lazy_attribute
        def _rspo(self):
            province = faker.random_element(rspo_client.list_provinces())
            district = faker.random_element(rspo_client.list_districts(province_id=province.id))
            rspo_id = faker.random_element(
                rspo_client.list_institutions(
                    body=InstitutionRequestBody(
                        province_id=province.id,
                        district_id=district.id,
                        # these ids are basically cached ouptut of
                        # get_instytution_type_ids for all SchoolTypes
                        institution_type_ids=[1, 21, 82, 3, 90, 93, 94, 14, 17, 15, 19, 20, 16, 18],
                    )
                ).items
            ).id

            return rspo_client.get_institution(rspo_id=rspo_id)

        @lazy_attribute
        def type(self):
            # this is really terrible, to use QT widget code in factory, but AFAIK
            # this is only place we have that logic - in future we should move that
            # to model or schema layer
            return SelectSchoolGroup.get_school_type_from_school_data(self._rspo.type)

    return SchoolFactory
