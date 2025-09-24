from datetime import date

from pydantic import BaseModel, ConfigDict


class BaseDbSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DecisionDbSchema(BaseDbSchema):
    id: int | None

    child_full_name: str
    child_full_name_gen: str
    child_address: str
    child_town: str
    child_postal_code: str | None = None
    child_post: str | None = None
    child_pesel: str
    child_birth_date: date
    child_birth_place: str
    child_student: bool = True
    klass: str | None = None
    profession: str | None = None

    school_parent_organisation: str | None = None
    school_type: str
    school_name: str
    school_address: str
    school_town: str
    school_postal_code: str
    school_post: str | None = None

    address_child_checkbox: bool = False
    address_first_parent_checkbox: bool = False
    first_parent_full_name: str
    first_parent_full_name_gen: str
    first_parent_address: str
    first_parent_town: str
    first_parent_postal_code: str | None = None
    first_parent_post: str | None = None
    second_parent_full_name: str | None = None
    second_parent_full_name_gen: str | None = None
    second_parent_address: str | None = None
    second_parent_town: str | None = None
    second_parent_postal_code: str | None = None
    second_parent_post: str | None = None

    support_center_name_nominative: str | None = None
    support_center_name_genitive: str | None = None
    support_center_institute_name: str | None = None
    support_center_kurator: str | None = None
    support_center_address: str | None = None
    support_center_town: str | None = None
    support_center_postal_code: str | None = None
    support_center_post: str | None = None

    issue: str
    period: str
    reasons: list[str]
    activity_form: str | None = None
    decision_no: str
    application_date: date
    meeting_date: date
    meeting_time: str
    meeting_members: list[dict[str, int | str]]

    file_no: str | None = None


class SchoolDbSchema(BaseDbSchema):
    id: int
    rspo_id: int | None = None
    rspo_type: int | None = None
    parent_organisation_name: str | None = None
    type: str
    name: str
    address: str
    town: str
    postal_code: str
    post: str


class SupportCenterDbSchema(BaseDbSchema):
    province_id: int | None
    district_id: int | None
    rspo: int | None
    name_nominative: str
    name_genitive: str
    institute_name: str
    kurator: str
    address: str
    town: str
    postal_code: str
    post: str


class TeamMemberDbCreateSchema(BaseDbSchema):
    name: str
    function: str


class TeamMemberDbSchema(TeamMemberDbCreateSchema):
    id: int


class StudentData(BaseModel):
    id: int
    full_name: str
    address: str
    town: str
    postal_code: str
    post: str
    pesel: str
