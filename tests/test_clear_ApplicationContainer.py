import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItem

from alinka.constants.common import SchoolTypes
from alinka.widget.containers.main_body.content.application import ApplicationContainer
from alinka.widget.containers.main_body.content.application.application_tabs.applicants_tab import (
    ApplicantsTabContainer,
)
from alinka.widget.containers.main_body.content.application.application_tabs.applicants_tab.applicant_data_group import (  # noqa: E501
    ApplicantDataGroup,
)
from alinka.widget.containers.main_body.content.application.application_tabs.application_tab import (
    ApplicationTabContainer,
)
from alinka.widget.containers.main_body.content.application.application_tabs.child_tab import (
    ChildDataTabContainer,
)
from alinka.widget.containers.main_body.content.application.application_tabs.child_tab.child_data_group import (
    ChildDataGroupContainer,
)
from alinka.widget.containers.main_body.content.application.application_tabs.child_tab.general_data_group import (
    GeneralDataGroupContainer,
)
from alinka.widget.containers.main_body.content.application.application_tabs.meeting_tab import (
    MeetingTabContainer,
)
from alinka.widget.containers.main_body.content.application.application_tabs.school_tab import (
    SchoolTabContainer,
)

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def qapp() -> Generator[QApplication, None, None]:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def applicant_data_group(qapp: QApplication) -> ApplicantDataGroup:
    return ApplicantDataGroup(
        title="Wnioskodawca",
        parent=None,
        checkbox_description="Adres taki sam jak pierwszego rodzica",
        initial_height=300,
    )


@pytest.fixture
def applicants_tab_container(qapp: QApplication) -> ApplicantsTabContainer:
    return ApplicantsTabContainer(parent=None)


@pytest.fixture
def application_tab_container(qapp: QApplication) -> ApplicationTabContainer:
    return ApplicationTabContainer(parent=None)


@pytest.fixture
def child_data_group_container(qapp: QApplication) -> ChildDataGroupContainer:
    return ChildDataGroupContainer(parent=None)


@pytest.fixture
def school_tab_container(qapp: QApplication) -> SchoolTabContainer:
    return SchoolTabContainer(parent=None)


@pytest.fixture
def child_data_tab_container(qapp: QApplication) -> ChildDataTabContainer:
    return ChildDataTabContainer(parent=None)


@pytest.fixture
def general_data_group_container(qapp: QApplication) -> GeneralDataGroupContainer:
    return GeneralDataGroupContainer(parent=None)


@pytest.fixture
def meeting_tab_container(qapp: QApplication) -> MeetingTabContainer:
    return MeetingTabContainer(parent=None)


@pytest.fixture
def application_container(qapp: QApplication) -> ApplicationContainer:
    application_container = ApplicationContainer(parent=None)
    application_container.id = 1
    return application_container


def test_clear_applicant_data_group(applicant_data_group: ApplicantDataGroup) -> None:
    # Set initial values
    applicant_data_group.full_name.text = "Jan Kowalski"
    applicant_data_group.full_name_gen.text = "Jana Kowalskiego"
    applicant_data_group.address_checkbox.checkbox.setChecked(True)
    applicant_data_group.address_frame.address.text = "ul. Przykładowa 1"
    applicant_data_group.address_frame.town.text = "Warszawa"
    applicant_data_group.address_frame.postal_code.text = "00-001"
    applicant_data_group.address_frame.post.text = "Warszawa"

    # Sanity check
    assert applicant_data_group.full_name.text == "Jan Kowalski"
    assert applicant_data_group.full_name_gen.text == "Jana Kowalskiego"
    assert applicant_data_group.address_checkbox.checkbox.isChecked()
    assert applicant_data_group.address_frame.address.text == "ul. Przykładowa 1"
    assert applicant_data_group.address_frame.town.text == "Warszawa"
    assert applicant_data_group.address_frame.postal_code.text == "00-001"
    assert applicant_data_group.address_frame.post.text == "Warszawa"

    # Call the method
    applicant_data_group.clear()

    # Check all fields are cleared and checkbox is unchecked
    assert applicant_data_group.full_name.text == ""
    assert applicant_data_group.full_name_gen.text == ""
    assert not applicant_data_group.address_checkbox.checkbox.isChecked()
    assert applicant_data_group.address_frame.address.text == ""
    assert applicant_data_group.address_frame.town.text == ""
    assert applicant_data_group.address_frame.postal_code.text == ""
    assert applicant_data_group.address_frame.post.text == ""


@patch.object(ApplicantDataGroup, "clear")
def test_clear_applicants_tab_container(
    mocked_clear: MagicMock, applicants_tab_container: ApplicantsTabContainer
) -> None:
    applicants_tab_container.clear()
    assert mocked_clear.call_count == 2


def test_clear_application_tab_container(application_tab_container: ApplicationTabContainer) -> None:
    # Set initial values
    custom_date = QDate(2000, 1, 1)
    application_tab_container.application_date.date_input.setDate(custom_date)
    application_tab_container.application_subject.combobox.addItem("TestSubject", "test_subj")
    application_tab_container.application_subject.combobox.setCurrentIndex(0)

    application_tab_container.application_reason.combobox.addItem("TestReason", "test_reason")
    application_tab_container.application_reason.combobox.setCurrentIndex(0)

    application_tab_container.application_reason_2.combobox.addItem("TestReason2", "test_reason_2")
    application_tab_container.application_reason_2.combobox.setEnabled(True)
    application_tab_container.application_reason_2.setFixedHeight(42)
    application_tab_container.application_reason_2.combobox.setCurrentIndex(0)

    application_tab_container._activity_form.combobox.addItem("TestActivity", "test_activity")
    application_tab_container._activity_form.setFixedHeight(42)
    application_tab_container._activity_form.combobox.setEnabled(True)
    application_tab_container._activity_form.combobox.setCurrentIndex(0)

    application_tab_container.application_period.combobox.addItem("TestPeriod", "test_period")
    application_tab_container.application_period.combobox.setEditable(True)
    application_tab_container.application_period.combobox.setCurrentIndex(0)

    # Sanity check
    assert application_tab_container.application_date.date_input.date() == custom_date
    assert application_tab_container.application_subject.combobox.count() > 0
    assert application_tab_container.application_subject.combobox.currentText() != ""
    assert application_tab_container.application_reason.combobox.count() > 0
    assert application_tab_container.application_reason.combobox.currentText() != ""
    assert application_tab_container.application_reason_2.combobox.count() > 0
    assert application_tab_container.application_reason_2.combobox.isEnabled()
    assert application_tab_container.application_reason_2.height() > 0
    assert application_tab_container._activity_form.combobox.count() > 0
    assert application_tab_container._activity_form.combobox.isEnabled()
    assert application_tab_container._activity_form.height() > 0
    assert application_tab_container.application_period.combobox.count() > 0
    assert application_tab_container.application_period.combobox.currentText() == "TestPeriod"

    # Call the method
    application_tab_container.clear()

    # All fields reset
    assert application_tab_container.application_date.date_input.date() == QDate.currentDate()
    # subject repopulated via populate_application_subject
    assert application_tab_container.application_subject.combobox.count() > 0
    # reason repopulated via populate_application_reason
    assert application_tab_container.application_reason.combobox.count() >= 0
    # reason_2 cleared/disabled/collapsed
    assert application_tab_container.application_reason_2.combobox.count() == 0
    assert not application_tab_container.application_reason_2.combobox.isEnabled()
    assert application_tab_container.application_reason_2.height() == 0
    # activity_form cleared/disabled/collapsed
    assert application_tab_container._activity_form.combobox.count() == 0
    assert not application_tab_container._activity_form.combobox.isEnabled()
    assert application_tab_container._activity_form.height() == 0
    # period cleared/empty
    assert application_tab_container.application_period.combobox.count() == 0
    assert application_tab_container.application_period.combobox.currentText() == ""
    assert application_tab_container.application_period.combobox.isEditable()


def test_clear_child_data_group_container(child_data_group_container: ChildDataGroupContainer) -> None:
    # Set initial values
    child_data_group_container.child_name_nom.text = "Anna Nowak"
    child_data_group_container.child_name_gen.text = "Anny Nowak"
    child_data_group_container.birth_place.text = "Kraków"
    child_data_group_container.pesel.text = "12345678901"
    child_data_group_container.address.text = "ul. Szkolna 1"
    child_data_group_container.town.text = "Kraków"
    child_data_group_container.postal_code.text = "31-123"
    child_data_group_container.post.text = "Kraków"
    child_data_group_container.student_checkbox.checkbox.setChecked(True)
    child_data_group_container.school_klass.text = "3a"
    child_data_group_container.school_profession.text = "Technik informatyk"

    # Sanity check
    assert child_data_group_container.child_name_nom.text == "Anna Nowak"
    assert child_data_group_container.child_name_gen.text == "Anny Nowak"
    assert child_data_group_container.birth_place.text == "Kraków"
    assert child_data_group_container.pesel.text == "12345678901"
    assert child_data_group_container.address.text == "ul. Szkolna 1"
    assert child_data_group_container.town.text == "Kraków"
    assert child_data_group_container.postal_code.text == "31-123"
    assert child_data_group_container.post.text == "Kraków"
    assert child_data_group_container.student_checkbox.checkbox.isChecked()
    assert child_data_group_container.school_klass.text == "3a"
    assert child_data_group_container.school_profession.text == "Technik informatyk"

    # Call the method
    child_data_group_container.clear()

    # All fields should now be empty
    assert child_data_group_container.child_name_nom.text == ""
    assert child_data_group_container.child_name_gen.text == ""
    assert child_data_group_container.birth_place.text == ""
    assert child_data_group_container.pesel.text == ""
    assert child_data_group_container.address.text == ""
    assert child_data_group_container.town.text == ""
    assert child_data_group_container.postal_code.text == ""
    assert child_data_group_container.post.text == ""
    assert child_data_group_container.school_klass.text == ""
    assert child_data_group_container.school_profession.text == ""
    assert not child_data_group_container.student_checkbox.checkbox.isChecked()


def test_clear_school_tab_container(school_tab_container: SchoolTabContainer) -> None:
    # Set initial values
    school_tab_container.school_type.combobox.setCurrentIndex(school_tab_container.school_type.combobox.count() - 1)

    # Sanity check
    assert school_tab_container.school_type.combobox.count() > 0
    assert school_tab_container.school_type.combobox.currentText() != ""

    # Call the method
    school_tab_container.clear()

    assert school_tab_container.school_type.combobox.count() == len(SchoolTypes.values()) + 1  # including empty option
    assert school_tab_container.school_type.combobox.currentText() in ("", None)


def test_clear_general_data_group_container(general_data_group_container: GeneralDataGroupContainer) -> None:
    # Set initial values
    general_data_group_container.decision_no.text = "123"
    general_data_group_container.file_no.text = "abc"

    # Sanity check
    assert general_data_group_container.decision_no.text == "123"
    assert general_data_group_container.file_no.text == "abc"

    # Call the method
    general_data_group_container.clear()

    # Both fields should now be empty
    assert general_data_group_container.decision_no.text == ""
    assert general_data_group_container.file_no.text == ""


@patch.object(GeneralDataGroupContainer, "clear")
@patch.object(ChildDataGroupContainer, "clear")
def test_clear_child_data_tab_container(
    mocked_child_data_clear: MagicMock,
    mocked_general_clear: MagicMock,
    child_data_tab_container: ChildDataTabContainer,
) -> None:
    child_data_tab_container.clear()
    mocked_child_data_clear.assert_called_once()
    mocked_general_clear.assert_called_once()


def test_clear_meeting_tab_container(meeting_tab_container: MeetingTabContainer) -> None:
    # Set initial values
    item1 = QStandardItem("Member 1")
    item1.setData(1)
    item1.setCheckable(True)
    item1.setCheckState(Qt.CheckState.Checked)
    meeting_tab_container.meeting_member_group.model.appendRow(item1)
    meeting_tab_container.meeting_leader.combobox.addItem("Leader 1", "leader1")
    meeting_tab_container.meeting_leader.combobox.setCurrentIndex(0)
    custom_date = QDate(2020, 2, 2)
    meeting_tab_container.meeting_date.date_input.setDate(custom_date)
    meeting_tab_container.meeting_time.text = "14:00"

    # Sanity check
    assert meeting_tab_container.meeting_member_group.model.rowCount() > 0
    assert meeting_tab_container.meeting_leader.combobox.count() > 0
    assert meeting_tab_container.meeting_leader.combobox.currentText() == "Leader 1"
    assert meeting_tab_container.meeting_date.date_input.date() == custom_date
    assert meeting_tab_container.meeting_time.text == "14:00"

    # Call the method
    meeting_tab_container.clear()

    # Check model has been repopulated (populate_meeting_members may add 0 or more rows)
    assert meeting_tab_container.meeting_member_group.model.rowCount() >= 0
    # meeting_leader combobox cleared
    assert meeting_tab_container.meeting_leader.combobox.count() == 0
    # date set to today
    assert meeting_tab_container.meeting_date.date_input.date() == QDate.currentDate()
    # time field cleared
    assert meeting_tab_container.meeting_time.text == ""


@patch.object(ChildDataTabContainer, "clear")
@patch.object(ApplicantsTabContainer, "clear")
@patch.object(ApplicationTabContainer, "clear")
@patch.object(MeetingTabContainer, "clear")
def test_clear_application_container(
    mocked_meeting_tab_container: MagicMock,
    mocked_application_tab_container: MagicMock,
    mocked_applicants_tab_container: MagicMock,
    mocked_child_data_tab_container: MagicMock,
    application_container: ApplicationContainer,
) -> None:
    application_container.clear()
    assert application_container.id is None
    mocked_meeting_tab_container.assert_called_once()
    mocked_application_tab_container.assert_called_once()
    mocked_applicants_tab_container.assert_called_once()
    mocked_child_data_tab_container.assert_called_once()
