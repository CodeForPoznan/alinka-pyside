import random
from datetime import date, datetime, timedelta

from factory import LazyAttribute, lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from alinka import rspo_client
from alinka.constants import ActivityForm, Issue, Reason
from alinka.constants.common import RPSO_SUPPORT_CENTER_TYPE_ID
from alinka.db.models import Decision, SupportCenter
from alinka.db.queries import db_session
from alinka.schemas.rspo_schema import InstitutionRequestBody
from tests.factories.atrributes import (
    FuzzyKlass,
    FuzzyMeetingMember,
    FuzzyProfession,
    FuzzySchoolName,
    FuzzySchoolParentOrganisation,
    FuzzySchoolType,
    FuzzySupportCenterKurator,
    FuzzySupportCenterNameGenitive,
    FuzzySupportCenterNameNominative,
)

DATE_FORMAT = "%m/%d/%Y"
faker = Faker(locale="pl_PL")


class DecisionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Decision
        sqlalchemy_session = db_session

    child_full_name = faker.name()
    child_full_name_gen = faker.name()
    child_town = faker.city()
    child_address = faker.street_address()
    child_postal_code = faker.postcode()
    child_pesel = faker.pesel()
    child_birth_date = faker.date_this_decade()
    child_birth_place = faker.city()
    child_student = faker.pybool()
    klass = FuzzyKlass()
    profession = FuzzyProfession()

    school_parent_organisation = FuzzySchoolParentOrganisation()
    school_type = FuzzySchoolType()
    school_name = FuzzySchoolName()
    school_address = faker.street_address()
    school_town = faker.city()
    school_postal_code = faker.postcode()
    school_post = faker.city()

    address_child_checkbox = faker.pybool()
    address_first_parent_checkbox = faker.pybool()
    first_parent_full_name = faker.name()
    first_parent_full_name_gen = faker.name()
    first_parent_address = faker.street_address()
    first_parent_town = faker.city()
    first_parent_postal_code = faker.postcode()
    second_parent_full_name = faker.name()
    second_parent_full_name_gen = faker.name()
    second_parent_address = faker.street_address()
    second_parent_town = faker.city()
    second_parent_postal_code = faker.postcode()

    support_center_name_nominative = FuzzySupportCenterNameNominative()
    support_center_name_genitive = FuzzySupportCenterNameGenitive()
    support_center_kurator = FuzzySupportCenterKurator()
    support_center_address = faker.street_address()
    support_center_town = faker.city()
    support_center_postal_code = faker.postcode()
    support_center_post = faker.city()

    issue = faker.enum(Issue).value
    activity_form = faker.enum(ActivityForm).value
    decision_no = f"PPP.{datetime.now().strftime('%Y')}.AC.{faker.pyint(1, 500)}"
    application_date = faker.past_date(start_date="-15d")
    meeting_date = date.today()
    meeting_time = faker.time_object().isoformat()
    meeting_members = FuzzyMeetingMember()

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
    def support_center_institute_name(self):
        return f"Zespół Orzekający przy {self.support_center_name_genitive}"

    @classmethod
    def _save(cls, model_class, session, args, kwargs):
        obj = model_class(*args, **kwargs)
        with session() as db_session:
            db_session.add(obj)
            db_session.commit()

        return obj


class SupportCenterFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SupportCenter
        sqlalchemy_session = db_session
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
