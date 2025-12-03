from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Decision(Base):
    __tablename__ = "decision"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    child_full_name = Column(String(100), nullable=False)
    child_full_name_gen = Column(String(100), nullable=False)
    child_address = Column(String(1024), nullable=False)
    child_town = Column(String(128), nullable=False)
    child_postal_code = Column(String(12), nullable=True)
    child_post = Column(String(12), nullable=True)
    child_pesel = Column(String(12), nullable=False)
    child_birth_date = Column(Date, nullable=False)
    child_birth_place = Column(String(100), nullable=False)
    child_student = Column(Boolean(), nullable=False, default=True)
    klass = Column(String(30), nullable=True)
    profession = Column(String(120), nullable=True)

    school_parent_organisation = Column(String(512), nullable=True)
    school_type = Column(String(50), nullable=False)
    school_name = Column(String(1024), nullable=False)
    school_address = Column(String(1024), nullable=False)
    school_town = Column(String(128), nullable=False)
    school_postal_code = Column(String(12), nullable=False)
    school_post = Column(String(128), nullable=False)

    is_first_parent_address_different = Column(Boolean, nullable=False, default=False)
    is_second_parent_address_different = Column(Boolean, nullable=False, default=False)
    first_parent_full_name = Column(String(100), nullable=False)
    first_parent_full_name_gen = Column(String(100), nullable=False)
    first_parent_address = Column(String(1024), nullable=False)
    first_parent_town = Column(String(128), nullable=False)
    first_parent_post = Column(String(128), nullable=True)
    first_parent_postal_code = Column(String(12), nullable=True)
    second_parent_full_name = Column(String(100), nullable=True)
    second_parent_full_name_gen = Column(String(100), nullable=True)
    second_parent_address = Column(String(1024), nullable=True)
    second_parent_town = Column(String(128), nullable=True)
    second_parent_postal_code = Column(String(12), nullable=True)
    second_parent_post = Column(String(128), nullable=True)

    support_center_name_nominative = Column(String(1024), nullable=True)
    support_center_name_genitive = Column(String(1024), nullable=True)
    support_center_institute_name = Column(String(1024), nullable=True)
    support_center_kurator = Column(String(1024), nullable=True)
    support_center_address = Column(String(1024), nullable=True)
    support_center_town = Column(String(128), nullable=True)
    support_center_postal_code = Column(String(12), nullable=True)
    support_center_post = Column(String(128), nullable=True)

    issue = Column(String(256), nullable=False)
    period = Column(String(256), nullable=False)
    reasons = Column(JSON, nullable=False)
    activity_form = Column(String(20), nullable=True)
    decision_no = Column(String(15), nullable=False)
    application_date = Column(Date, nullable=False)
    meeting_date = Column(Date, nullable=False)
    meeting_time = Column(String(50), nullable=False)
    meeting_members = Column(JSON, nullable=False)

    file_no = Column(String(20), nullable=True)


class School(Base):
    __tablename__ = "school"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    rspo_id = Column(Integer(), nullable=True)
    rspo_type_id = Column(Integer(), nullable=True)
    type = Column(String(50), nullable=False)
    parent_organisation_name = Column(String(512), nullable=True)
    name = Column(String(1024), nullable=False)
    address = Column(String(1024), nullable=False)
    town = Column(String(128), nullable=False)
    postal_code = Column(String(12), nullable=False)
    post = Column(String(128), nullable=False)

    __table_args__ = (UniqueConstraint("rspo_id", name="uq_school_rspo_id"),)


class SupportCenter(Base):
    __tablename__ = "support_center"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    district_id = Column(Integer(), nullable=True)
    province_id = Column(Integer(), nullable=True)
    rspo = Column(Integer(), nullable=True)
    name_nominative = Column(String(1024), nullable=False)
    name_genitive = Column(String(1024), nullable=False)
    institute_name = Column(String(1024), nullable=False)
    kurator = Column(String(1024), nullable=False)
    address = Column(String(1024), nullable=False)
    town = Column(String(128), nullable=False)
    postal_code = Column(String(12), nullable=False)
    post = Column(String(128), nullable=False)


class TeamMember(Base):
    __tablename__ = "team_member"

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(512), nullable=False)
    function = Column(String(512), nullable=False)
