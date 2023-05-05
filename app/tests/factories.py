from datetime import date, datetime, timedelta

from constants import ActivityForm, Issue, Reason
from db.models import Decision
from db.queries import db_session
from factory import lazy_attribute
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from tests.utils import (
    FuzzyKlass,
    FuzzyMeetingMember,
    FuzzyProfession,
    FuzzySchoolName,
    FuzzySchoolParentOrganisation,
    FuzzySchoolType,
    FuzzySupportCenterKurator,
    FuzzySupportCenterNameGenetive,
    FuzzySupportCenterNameNominative,
)

DATE_FORMAT = "%m/%d/%Y"
faker = Faker(locale="pl_PL")


class DecisionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Decision
        sqlalchemy_session = db_session

    child_first_name = faker.first_name()
    child_last_name = faker.last_name()
    child_city = faker.city()
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
    school_city = faker.city()
    school_postal_code = faker.postcode()

    address_child_checkbox = faker.pybool()
    address_first_parent_checkbox = faker.pybool()
    first_parent_first_name = faker.first_name()
    first_parent_last_name = faker.last_name()
    first_parent_address = faker.street_address()
    first_parent_city = faker.city()
    first_parent_postal_code = faker.postcode()
    second_parent_first_name = faker.first_name()
    second_parent_last_name = faker.last_name()
    second_parent_address = faker.street_address()
    second_parent_city = faker.city()
    second_parent_postal_code = faker.postcode()

    support_center_name_nominative = FuzzySupportCenterNameNominative()
    support_center_name_genetive = FuzzySupportCenterNameGenetive()
    support_center_kurator = FuzzySupportCenterKurator()
    support_center_address = faker.street_address()
    support_center_city = faker.city()
    support_center_postal_code = faker.postcode()

    issue = faker.enum(Issue).value
    activity_form = faker.enum(ActivityForm).value
    no = f"PPP.{datetime.now().strftime('%Y')}.AC.{faker.pyint(1,500)}"
    application_date = faker.past_date(start_date="-15d")
    meeting_date = date.today()
    meeting_time = faker.time_object()
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
        return f"Zespół Orzekający przy {self.support_center_name_genetive}"

    @classmethod
    def _save(cls, model_class, session, args, kwargs):
        obj = model_class(*args, **kwargs)
        with session() as db_session:
            db_session.add(obj)
            db_session.commit()

        return obj
