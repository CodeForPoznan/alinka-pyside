from copy import copy
from datetime import date

from pydantic import BaseModel, Field, computed_field, model_validator

from alinka.constants import ActivityForm, Issue, Reason
from alinka.utils import extract_date_of_birth_from_pesel


class AddressData(BaseModel):
    address: str
    town: str | None
    postal_code: str | None
    post: str | None

    @computed_field
    def full_address(self) -> str:
        post_description = f"{self.postal_code} {self.post}"
        address_parts = [self.address]

        if self.town and self.town != self.post:
            address_parts.append(self.town)

        address_parts.append(post_description)
        return ", ".join(address_parts)


class PersonalData(AddressData):
    full_name: str
    full_name_gen: str


class ChildData(PersonalData):
    pesel: str
    birth_place: str
    klass: str | None = Field(None, examples=["3b", "IVa"])
    student: bool
    birth_date: date | None = None
    profession: str | None = None

    @computed_field
    def student_description_genitive(self) -> str:
        return "ucznia" if self.student else "dziecka"

    @model_validator(mode="after")
    def calculate_date_of_birth(self) -> "ChildData":
        if self.birth_date:
            return self
        pesel = self.pesel
        self.birth_date = extract_date_of_birth_from_pesel(pesel)
        return self


class SchoolData(AddressData):
    rspo_id: int | None = None
    rspo_type_id: int | None = None
    parent_organisation_name: str | None = Field(None, examples=["Zespół Szkół Budowlanych"])
    type: str = Field(..., examples=["przedszkole", "szkoła podstawowa"])
    name: str
    description: str | None = None


class MeetingMemberData(BaseModel):
    id: int
    name: str = Field(..., examples=["Krystyna Czarnecka"])
    function: str = Field(..., examples=["psycholog", "logopeda"])


class MeetingData(BaseModel):
    members: list[MeetingMemberData]
    date: date
    time: str


class SupportCenterData(AddressData):
    district_id: int | None = None
    province_id: int | None = None
    rspo: int | None = None
    name_nominative: str = Field(..., examples=["Poradnia Psychologiczno - Pedagogiczna w Poznaniu"])
    name_genitive: str = Field(..., examples=["Poradni Psychologiczno - Pedagogicznej w Poznaniu"])
    institute_name: str = Field(
        ..., examples=["Zespół Orzekający przy Poradni Psychologiczno-Pedagogicznej w Poznaniu"]
    )
    kurator: str


class DocumentData(BaseModel):
    # raw
    id: int | None = None
    child: ChildData
    school: SchoolData
    applicants: list[PersonalData] = Field(..., min_length=1, max_length=2)
    is_first_parent_address_different: bool = False
    is_second_parent_address_different: bool = False
    issue: Issue
    period: str
    reasons: list[Reason] = Field(None, description="Can be one or more reasons")
    activity_form: ActivityForm | None = None
    decision_no: str
    application_date: date
    meeting_data: MeetingData
    support_center: SupportCenterData
    file_no: str | None = None

    @computed_field
    def on_request(self) -> str:
        return " i ".join([applicant.full_name for applicant in self.applicants])

    @computed_field
    def parents_names(self) -> str:
        return ", ".join([parent.full_name for parent in self.applicants])

    @computed_field
    def applicants_data(self) -> list[PersonalData]:
        """
        This fields contains applicants data taking into account
        first parent's address checkbox and second parent's checkbox
        """
        applicant1 = copy(self.applicants[0])
        applicants = [applicant1]

        if not self.is_first_parent_address_different:
            applicant1.address = self.child.address
            applicant1.town = self.child.town
            applicant1.postal_code = self.child.postal_code
            applicant1.post = self.child.post

        if len(self.applicants) > 1:
            applicant2 = copy(self.applicants[1])
            applicants.append(applicant2)
            if not self.is_second_parent_address_different:
                applicant2.address = applicant1.address
                applicant2.town = applicant1.town
                applicant2.postal_code = applicant1.postal_code
                applicant2.post = applicant1.post

        return applicants

    @computed_field
    def reason(self) -> Reason:
        return Reason.SPRZEZONA if len(self.reasons) > 1 else self.reasons[0]

    @computed_field
    def multiple_disabilities_nominative(self) -> str | None:
        """
        Join two disabilities description ie.
        "niepełnosprawność intelektualna w stopniu lekkim, słabosłyszenie"
        """
        if self.reason == Reason.SPRZEZONA:
            return ", ".join([getattr(reason, "reason_description_nominative_long") for reason in self.reasons])

    @computed_field
    def multiple_disabilities_genitive(self) -> str | None:
        """
        Join two disabilities description ie.
        "niepełnosprawności intelektualnej w stopniu lekkim, słabosłyszenia"
        """
        if self.reason == Reason.SPRZEZONA:
            return ", ".join([getattr(reason, "reason_description_genitive_long") for reason in self.reasons])

    @computed_field
    def multiple_disabilities_accusative(self) -> str | None:
        """
        Join two disabilities description ie.
        "niepełnosprawność intelektualną w stopniu lekkim, słabosłyszenie"
        """
        if self.reason == Reason.SPRZEZONA:
            return ", ".join([getattr(reason, "reason_description_accusative_long") for reason in self.reasons])

    @computed_field
    def reason_description_nominative_long(self) -> str:
        """
        ie.: "niepełnosprawność ruchowa"
        or: "niepełnosprawność sprzężona: niepełnosprawność ruchowa i słabosłyszenie
        """
        reason_description_nominative_long = self.reason.reason_description_nominative_long
        if self.reason == Reason.SPRZEZONA:
            reason_description_nominative_long += f": {self.multiple_disabilities_nominative}"
        return reason_description_nominative_long

    @computed_field
    def reason_description_genitive_long(self) -> str:
        """
        ie.: "niepełnosprawność ruchowej"
        or: "niepełnosprawność sprzężonej: niepełnosprawności ruchowej i słabosłyszenia
        """
        reason_description_genitive_long = self.reason.reason_description_genitive_long
        if self.reason == Reason.SPRZEZONA:
            reason_description_genitive_long += f": {self.multiple_disabilities_genitive}"
        return reason_description_genitive_long

    @computed_field
    def reason_description_accusative_long(self) -> str:
        """
        ie.: "niepełnosprawność ruchową"
        or: "niepełnosprawność sprzężoną: niepełnosprawność ruchową i słabosłyszenie
        """
        reason_description_accusative_long = self.reason.reason_description_accusative_long
        if self.reason == Reason.SPRZEZONA:
            reason_description_accusative_long += f": {self.multiple_disabilities_accusative}"
        return reason_description_accusative_long

    @computed_field
    def parent_descriptions(self) -> str:
        if self.is_second_parent_address_different:
            if self.is_first_parent_address_different:
                parents_description = ", ".join(
                    [f"{parent.full_name}, {parent.full_address}" for parent in self.applicants]
                )
            else:
                parents_description = ", ".join(
                    [
                        f"{self.applicants[0].full_name}",
                        f"{self.child.full_address}",
                        f"{self.applicants[1].full_name}, {self.applicants[1].full_address}",
                    ]
                )
        else:
            parents_names = " i ".join([parent.full_name for parent in self.applicants])
            if self.is_first_parent_address_different:
                parents_description = f"{parents_names}, {self.applicants[0].full_address}"

            else:
                parents_description = f"{parents_names}, {self.child.full_address}"

        return parents_description

    @computed_field
    def school_description(self) -> str:
        return ", ".join(
            [
                value
                for value in [
                    self.school.name,
                    self.school.full_address,
                    self.child.klass,
                    self.child.profession,
                ]
                if value
            ]
        )

    @computed_field
    def issue_short(self) -> str:
        return "ind_rocz" if self.issue == Issue.INDYWIDUALNE_ROCZNE else self.issue.value[:4]

    @model_validator(mode="after")
    def check_activity_form_required(self) -> "DocumentData":
        if self.issue == Issue.REWALIDACYJNE and not self.activity_form:
            raise ValueError(
                f"If issue is of type '{self.issue.issue_description_nominative}', "
                "activity form (eg 'grupowe') have to be selected."
            )
        return self

    @model_validator(mode="after")
    def check_multiple_disability(self) -> "DocumentData":
        """Validate if multiple disability reasons are correctly set."""
        if {Reason.UNIEMOZLIWIAJACY, Reason.ZNACZNIE_UTRUDNIAJACY}.issubset(self.reasons):
            raise ValueError(f"Reasons: {', '.join(self.reasons)} can't be issued together.")

        intellectual_reasons = [reason for reason in self.reasons if reason in Reason.intellectual_reasons()]
        if len(intellectual_reasons) > 1:
            raise ValueError(f"Two intellectual reasons: {', '.join(intellectual_reasons)} can't be issued together.")

        if Reason.GLEBOKIE in self.reasons and len(self.reasons) > 1:
            raise ValueError("Profound intellectual disability can't be coupled.")

        if any(reason in Reason.social_maladjustment_reasons() for reason in self.reasons) and len(self.reasons) > 1:
            raise ValueError("Social maladjustment reasons can't be coupled with any other reason.")

        return self
