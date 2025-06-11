from alinka.db.queries import create_decision_in_db, update_decision_in_db
from alinka.docx import generate_documents
from alinka.schemas import DecisionDbSchema, DocumentData


def generate_and_save_decision(form_data: DocumentData, generate: bool = False) -> DecisionDbSchema:
    child = form_data.child
    school = form_data.school
    applicant_1 = form_data.applicants[0]
    applicant_2 = form_data.applicants[1] if len(form_data.applicants) > 1 else None
    support_center = form_data.support_center
    meeting_data = form_data.meeting_data
    decision_data = DecisionDbSchema(
        id=form_data.id,
        child_full_name=child.full_name,
        child_full_name_gen=child.full_name_gen,
        child_address=child.address,
        child_town=child.town,
        child_postal_code=child.postal_code,
        child_post=child.post,
        child_pesel=child.pesel,
        child_birth_date=child.birth_date,
        child_birth_place=child.birth_place,
        child_student=child.student,
        klass=child.klass,
        profession=child.profession,
        school_parent_organisation=school.parent_organisation_name,
        school_type=school.type,
        school_name=school.name,
        school_address=school.address,
        school_town=school.town,
        school_postal_code=school.postal_code,
        school_post=school.post,
        address_child_checkbox=form_data.address_child_checkbox,
        address_first_parent_checkbox=form_data.address_first_parent_checkbox,
        first_parent_full_name=applicant_1.full_name,
        first_parent_full_name_gen=applicant_1.full_name_gen,
        first_parent_address=applicant_1.address,
        first_parent_town=applicant_1.town,
        first_parent_postal_code=applicant_1.postal_code,
        first_parent_post=applicant_1.post,
        second_parent_full_name=applicant_2.full_name if applicant_2 else None,
        second_parent_full_name_gen=applicant_2.full_name_gen if applicant_2 else None,
        second_parent_address=applicant_2.address if applicant_2 else None,
        second_parent_town=applicant_2.town if applicant_2 else None,
        second_parent_postal_code=applicant_2.postal_code if applicant_2 else None,
        second_parent_post=applicant_2.post if applicant_2 else None,
        support_center_name_nominative=support_center.name_nominative,
        support_center_name_genitive=support_center.name_genitive,
        support_center_institute_name=support_center.institute_name,
        support_center_kurator=support_center.kurator,
        support_center_address=support_center.address,
        support_center_town=support_center.town,
        support_center_postal_code=support_center.postal_code,
        support_center_post=support_center.post,
        issue=form_data.issue.value,
        period=form_data.period,
        reasons=[r.value for r in form_data.reasons],
        activity_form=form_data.activity_form,
        decision_no=form_data.decision_no,
        application_date=form_data.application_date,
        meeting_date=meeting_data.date,
        meeting_time=meeting_data.time,
        meeting_members=[m.model_dump() for m in meeting_data.members],
        file_no=form_data.file_no,
    )
    if decision_data.id:
        decision = update_decision_in_db(decision_id=decision_data.id, decision_data=decision_data.model_dump())
    else:
        decision = create_decision_in_db(decision_data.model_dump())

    if generate:
        generate_documents(decision.id)

    return decision
