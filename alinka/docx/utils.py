from alinka.schemas import (
    ChildData,
    DecisionDbSchema,
    DocumentData,
    MeetingData,
    MeetingMemberData,
    PersonalData,
    SchoolData,
    SupportCenterData,
)


def get_applicants_data(raw_documents_data: DecisionDbSchema) -> list[PersonalData]:
    applicants = [
        PersonalData(
            full_name=raw_documents_data.first_parent_full_name,
            full_name_gen=raw_documents_data.first_parent_full_name_gen,
            address=raw_documents_data.first_parent_address,
            town=raw_documents_data.first_parent_town,
            postal_code=raw_documents_data.first_parent_postal_code,
            post=raw_documents_data.first_parent_post,
        )
    ]
    full_name, full_name_gen = (
        raw_documents_data.second_parent_full_name,
        raw_documents_data.second_parent_full_name_gen,
    )
    if full_name and full_name_gen:
        applicants.append(
            PersonalData(
                full_name=full_name,
                full_name_gen=full_name_gen,
                address=raw_documents_data.second_parent_address,
                town=raw_documents_data.second_parent_town,
                postal_code=raw_documents_data.second_parent_postal_code,
                post=raw_documents_data.second_parent_post,
            )
        )
    return applicants


def get_meeting_data(raw_documents_data: DecisionDbSchema) -> MeetingData:
    return MeetingData(
        members=[MeetingMemberData(**member_data) for member_data in raw_documents_data.meeting_members],
        date=raw_documents_data.meeting_date,
        time=raw_documents_data.meeting_time,
    )


def convert_raw_documents_data(raw_documents_data: DecisionDbSchema) -> DocumentData:
    child_data = ChildData(
        address=raw_documents_data.child_address,
        town=raw_documents_data.child_town,
        post=raw_documents_data.child_post,
        postal_code=raw_documents_data.child_postal_code,
        student=raw_documents_data.child_student,
        full_name=raw_documents_data.child_full_name,
        full_name_gen=raw_documents_data.child_full_name_gen,
        pesel=raw_documents_data.child_pesel,
        profession=raw_documents_data.profession,
        klass=raw_documents_data.klass,
        birth_date=raw_documents_data.child_birth_date,
        birth_place=raw_documents_data.child_birth_place,
    )
    school_data = SchoolData(
        address=raw_documents_data.school_address,
        town=raw_documents_data.school_town,
        postal_code=raw_documents_data.school_postal_code,
        post=raw_documents_data.school_post,
        name=raw_documents_data.school_name,
        parent_organisation=raw_documents_data.school_parent_organisation,
        type=raw_documents_data.school_type,
    )
    meeting_data = MeetingData(
        members=[MeetingMemberData(**member_data) for member_data in raw_documents_data.meeting_members],
        date=raw_documents_data.meeting_date,
        time=raw_documents_data.meeting_time,
    )
    support_center_data = SupportCenterData(
        name_nominative=raw_documents_data.support_center_name_nominative,
        name_genitive=raw_documents_data.support_center_name_genitive,
        kurator=raw_documents_data.support_center_kurator,
        address=raw_documents_data.support_center_address,
        town=raw_documents_data.support_center_town,
        postal_code=raw_documents_data.support_center_postal_code,
        post=raw_documents_data.support_center_post,
        institute_name=raw_documents_data.support_center_institute_name,
    )
    return DocumentData(
        child=child_data,
        is_first_parent_address_different=raw_documents_data.is_first_parent_address_different,
        is_second_parent_address_different=raw_documents_data.is_second_parent_address_different,
        issue=raw_documents_data.issue,
        reasons=raw_documents_data.reasons,
        activity_form=raw_documents_data.activity_form,
        decision_no=raw_documents_data.decision_no,
        file_no=raw_documents_data.file_no,
        school=school_data,
        applicants=get_applicants_data(raw_documents_data),
        application_date=raw_documents_data.application_date,
        meeting_data=meeting_data,
        support_center=support_center_data,
        period=raw_documents_data.period,
    )
