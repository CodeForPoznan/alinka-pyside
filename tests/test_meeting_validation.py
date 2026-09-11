import re
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QApplication, QWidget

from alinka.widget.components import LabeledTimeComponent
from alinka.widget.containers.main_body.content.application import ApplicationContainer
from alinka.widget.containers.main_body.content.application.application_tabs.meeting_tab import (
    MeetingMemberGroup,
)


@pytest.fixture(scope="module")
def qt_app():
    app = QApplication.instance() or QApplication(["pytest", "-platform", "offscreen"])
    yield app


def test_required_time_component_accepts_displayed_default(qt_app):
    parent = QWidget()
    component = LabeledTimeComponent("Godzina zespołu", parent, required=True)

    assert component.is_valid
    assert re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", component.text)


def test_time_validation_message_disappears_after_value_changes(qt_app):
    parent = QWidget()
    component = LabeledTimeComponent("Godzina zespołu", parent, required=True)
    component.display_validation_result(False)

    component.time_input.setTime(component.time_input.time().addSecs(60))

    assert component._error_label.isHidden()
    assert component._error_label.text() == ""


def test_time_clear_removes_validation_message(qt_app):
    parent = QWidget()
    component = LabeledTimeComponent("Godzina zespołu", parent, required=True)
    component.display_validation_result(False)

    component.clear()

    assert component.is_valid
    assert component._error_label.isHidden()
    assert component._error_label.text() == ""


def test_member_validation_message_disappears_after_valid_selection(qt_app):
    parent = QWidget()
    component = MeetingMemberGroup("Członkowie zespołu", parent)
    for member_id in (1, 2):
        item = QStandardItem(f"Member {member_id}")
        item.setData(member_id)
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Unchecked)
        component.model.appendRow(item)

    assert not component.validate()
    component.model.item(0).setCheckState(Qt.CheckState.Checked)

    assert not component.is_valid
    assert not component.error_label.isHidden()
    assert component.error_label.text() == "Należy wybrać co najmniej dwóch członków zespołu."

    component.model.item(1).setCheckState(Qt.CheckState.Checked)

    assert component.is_valid
    assert component.error_label.isHidden()
    assert component.error_label.text() == ""


def test_member_clear_validation_state_removes_message(qt_app):
    parent = QWidget()
    component = MeetingMemberGroup("Członkowie zespołu", parent)
    assert not component.validate()

    component.clear_validation_state()

    assert component.error_label.isHidden()
    assert component.error_label.text() == ""


def test_member_clear_removes_validation_message(qt_app):
    parent = QWidget()
    component = MeetingMemberGroup("Członkowie zespołu", parent)
    assert not component.validate()

    with patch.object(component, "populate_meeting_members"):
        component.clear()

    assert component.error_label.isHidden()
    assert component.error_label.text() == ""


def test_member_validation_message_is_deferred_until_validation(qt_app):
    parent = QWidget()
    component = MeetingMemberGroup("Członkowie zespołu", parent)

    assert not component.is_valid
    assert component.error_label.isHidden()
    assert component.error_label.text() == ""

    assert not component.validate()
    assert not component.error_label.isHidden()
    assert component.error_label.text() == "Należy wybrać co najmniej dwóch członków zespołu."


def test_invalid_meeting_tab_marker_disappears_when_tab_becomes_valid(qt_app):
    parent = QWidget()
    header = Mock()
    content = SimpleNamespace(main_body_container=SimpleNamespace(header_container=header))
    application = ApplicationContainer(parent, content)
    meeting_tab = application.meeting_tab_container
    members = meeting_tab.meeting_member_group

    for member_id in (1, 2):
        item = QStandardItem(f"Member {member_id}")
        item.setData(member_id)
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Unchecked)
        members.model.appendRow(item)

    meeting_tab_index = application.indexOf(meeting_tab)
    application.mark_invalid_tabs([meeting_tab_index])
    assert not meeting_tab.validate()

    members.model.item(0).setCheckState(Qt.CheckState.Checked)
    assert meeting_tab_index in application._invalid_tabs

    members.model.item(1).setCheckState(Qt.CheckState.Checked)
    assert not meeting_tab.is_valid
    assert meeting_tab_index in application._invalid_tabs

    meeting_tab.meeting_leader.combobox.setCurrentIndex(0)
    assert meeting_tab.is_valid
    assert meeting_tab_index not in application._invalid_tabs
    assert meeting_tab_index not in application.tabBar()._invalid_tabs
    header.clear_message.assert_called_once_with()


def test_invalid_child_tab_marker_disappears_when_tab_becomes_valid(qt_app):
    parent = QWidget()
    header = Mock()
    content = SimpleNamespace(main_body_container=SimpleNamespace(header_container=header))
    application = ApplicationContainer(parent, content)
    child_tab = application.child_tab_container
    general_data = child_tab.general_data_group
    child_data = child_tab.child_data_group

    child_tab_index = application.indexOf(child_tab)
    application.mark_invalid_tabs([child_tab_index])
    assert not child_tab.validate()

    general_data.decision_no.text = "PPP.2026.1"
    general_data.file_no.text = "1/2026"
    child_data.child_name_nom.text = "Jan Kowalski"
    child_data.child_name_gen.text = "Jana Kowalskiego"
    child_data.birth_place.text = "Poznań"
    child_data.pesel.text = "44051401359"
    child_data.address.text = "ul. Testowa 1"
    child_data.town.text = "Poznań"
    child_data.postal_code.text = "60-001"
    child_data.post.text = "Poznań"

    assert child_tab.is_valid
    assert child_tab_index not in application._invalid_tabs
    assert child_tab_index not in application.tabBar()._invalid_tabs
    header.clear_message.assert_called_once_with()
