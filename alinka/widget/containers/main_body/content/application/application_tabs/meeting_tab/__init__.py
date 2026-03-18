from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListView,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from alinka.db.queries import (
    delete_team_member,
    get_meeting_member_by_id,
    get_team_members,
)
from alinka.schemas import MeetingData, MeetingMemberData
from alinka.schemas.document_schema import DocumentData
from alinka.widget.components import (
    ConfirmationModal,
    LabeledComboBoxComponent,
    LabeledDateComponent,
    ValidationMixin,
)
from alinka.widget.containers.labeled_time_component import LabeledTimeComponent

from .member_dialog import MemberDialog

MEMBER_LIST_VIEW_STYLESHEET = """
    QListView {
        outline: none;
        background-color: white;
    }
    QListView[validationState="valid"] {
        border: 2px solid #10b981;
    }
    QListView[validationState="invalid"] {
        border: 2px solid #ef4444;
    }
    QListView::item {
        padding: 8px;
        padding-left: 12px;
        border-bottom: 1px solid #e2e8f0;
        min-height: 28px;
    }
    QListView::item {
        background-color: white;
    }
    QListView::item:alternate {
        background-color: #f9fafb;
    }
    QListView::item:hover {
        background-color: #f3f4f6;
    }
    QListView::indicator {
        width: 22px;
        height: 22px;
        border: 2px solid #64748b;
        border-radius: 3px;
        background-color: white;
        margin-right: 8px;
    }
    QListView::indicator:hover {
        border: 2px solid #10b981;
        background-color: white;
    }
    QListView::indicator:checked {
        background-color: white;
        border: 2px solid #10b981;
    }
    QListView::indicator:checked:hover {
        background-color: white;
        border: 2px solid #059669;
    }
"""


class MeetingDatetimeFrame(ValidationMixin, QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.meeting_date = LabeledDateComponent("Data zespołu", self, required=True)
        self.meeting_date.date_input.setDate(QDate.currentDate())

        self.meeting_time = LabeledTimeComponent("Godzina zespołu", self, required=True)

        layout.addWidget(self.meeting_date, 1)
        layout.addWidget(self.meeting_time, 1)

        self.components = [self.meeting_date, self.meeting_time]

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.components)

    @property
    def error_message(self) -> str | None:
        for c in self.components:
            if not c.is_valid:
                return c.error_message
        return None

    def validate(self) -> bool:
        return all([c.validate() for c in self.components])

    def clear_validation_state(self) -> None:
        for c in self.components:
            c.clear_validation_state()


class HandleMemberFrame(ValidationMixin, QFrame):
    team_member_changed = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        self.show_new_member_inputs_btn = QPushButton("Dodaj", self)
        self.show_new_member_inputs_btn.clicked.connect(self.add_new_member)
        self.edit_member_btn = QPushButton("Edytuj", self, enabled=False)
        self.edit_member_btn.clicked.connect(self.edit_member)
        self.remove_member_btn = QPushButton("Usuń", self, enabled=False)
        self.remove_member_btn.clicked.connect(self.remove_member)

        # Apply green styling to match the app theme
        button_style = """
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: 500;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """
        self.show_new_member_inputs_btn.setStyleSheet(button_style)
        self.edit_member_btn.setStyleSheet(button_style)
        self.remove_member_btn.setStyleSheet(button_style)

        layout.addWidget(self.show_new_member_inputs_btn)
        layout.addWidget(self.edit_member_btn)
        layout.addWidget(self.remove_member_btn)

    def add_new_member(self) -> None:
        dialog = MemberDialog(self, title="Dodaj członka zespołu")
        if dialog.exec() == QDialog.Accepted:
            self.team_member_changed.emit()

    def edit_member(self) -> None:
        selected_member = self.get_selected_member()
        if not selected_member:
            return None
        dialog = MemberDialog(
            self,
            title="Edytuj członka zespołu",
            _id=selected_member.id,
            name=selected_member.name,
            function=selected_member.function,
        )
        if dialog.exec() == QDialog.Accepted:
            self.team_member_changed.emit()

    def remove_member(self) -> None:
        selected_member = self.get_selected_member()
        if not selected_member:
            return None
        if not ConfirmationModal(
            self,
            "Potwierdzenie usunięcia członka zespołu",
            "Czy na pewno chcesz usunąć tego członka zespołu?",
        ).confirm():
            return
        delete_team_member(selected_member.id)
        self.team_member_changed.emit()

    def get_selected_member(self) -> MeetingMemberData | None:
        selected_members_id = self.parent().selected_members_id
        if len(selected_members_id) != 1:
            return None
        return get_meeting_member_by_id(selected_members_id[0])


class MeetingMemberGroup(ValidationMixin, QFrame):
    # signal emitted when the selection changes
    # it should result in updating the meeting leader combobox
    selection_changed = Signal()

    def __init__(self, title: str, parent: QWidget):
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        title_label = QLabel(text=title, parent=self)
        title_label.setStyleSheet("font-weight: 600; color: #000000; font-size: 13px;")
        layout.addWidget(title_label)

        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.item_changed)
        self.listView = QListView(self)
        self.listView.setModel(self.model)
        self.listView.setAlternatingRowColors(True)

        # Disable row selection - only allow checkbox interaction
        self.listView.setSelectionMode(QListView.NoSelection)
        self.listView.setEditTriggers(QListView.NoEditTriggers)
        self.listView.setFocusPolicy(Qt.NoFocus)

        # Make checkboxes more visible and user-friendly with borders
        self.listView.setSpacing(2)
        self.listView.setWordWrap(False)
        self.listView.setUniformItemSizes(True)

        # Add visible borders and styling
        self.listView.setStyleSheet(MEMBER_LIST_VIEW_STYLESHEET)

        # Set reasonable height for up to 7 team members
        self.listView.setMinimumHeight(80)
        self.listView.setMaximumHeight(280)
        self.listView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.handle_member_frame = HandleMemberFrame(self)
        self.handle_member_frame.team_member_changed.connect(self.populate_meeting_members)

        # Label for error message
        self.error_label = QLabel("", self)
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setVisible(False)

        layout.addWidget(self.listView, 0)
        layout.addWidget(self.error_label)
        layout.addWidget(self.handle_member_frame)

    @property
    def selected_members_id(self) -> list[int]:
        return [
            item.data()
            for item in self.model.findItems("*", Qt.MatchWildcard)
            if item.checkState() == Qt.CheckState.Checked
        ]

    def populate_meeting_members(self, meeting_members: list[MeetingMemberData] | None = None) -> None:
        selected_members_id = self.selected_members_id
        meeting_members = self.get_meeting_members()

        self.model.itemChanged.disconnect(self.item_changed)
        self.model.clear()
        for meeting_member_data in meeting_members:
            item = QStandardItem(f"{meeting_member_data['name']} - {meeting_member_data['function']}")
            item.setData(meeting_member_data["id"])
            item.setCheckable(True)
            item.setEditable(False)
            item.setCheckState(
                Qt.CheckState.Checked if meeting_member_data["id"] in selected_members_id else Qt.CheckState.Unchecked
            )
            self.model.appendRow(item)

        self.model.itemChanged.connect(self.item_changed)
        self.selection_changed.emit()

    def clear_selection(self) -> None:
        for row_index in range(0, self.model.rowCount()):
            member = self.model.item(row_index)
            member.setCheckState(Qt.CheckState.Unchecked)

    def item_changed(self):
        self.handle_member_frame.edit_member_btn.setEnabled(len(self.selected_members_id) == 1)
        self.handle_member_frame.remove_member_btn.setEnabled(len(self.selected_members_id) == 1)
        self.selection_changed.emit()
        self.clear_validation_state()

    def get_meeting_members(self) -> dict:
        return [tm.model_dump() for tm in get_team_members()]

    def clear(self) -> None:
        self.populate_meeting_members()
        self.clear_selection()

    @property
    def is_valid(self) -> bool:
        return len(self.selected_members_id) > 1

    @property
    def error_message(self) -> str | None:
        if len(self.selected_members_id) < 2:
            return "Należy wybrać co najmniej dwóch członków zespołu."
        return None

    def display_validation_result(self, validation_result: bool):
        state = "valid" if validation_result else "invalid"
        self.listView.setProperty("validationState", state)
        self.listView.style().unpolish(self.listView)
        self.listView.style().polish(self.listView)

        if validation_result:
            self.error_label.setVisible(False)
        else:
            self.error_label.setVisible(True)
            self.error_label.setText(self.error_message or "")

    def validate(self) -> bool:
        valid = self.is_valid
        self.display_validation_result(valid)
        return valid

    def clear_validation_state(self):
        self.listView.setProperty("validationState", "")
        self.listView.style().unpolish(self.listView)
        self.listView.style().polish(self.listView)


class MeetingTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.application_container = parent
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(8)

        self.meeting_datetime_frame = MeetingDatetimeFrame(self)
        self.meeting_date = self.meeting_datetime_frame.meeting_date
        self.meeting_time = self.meeting_datetime_frame.meeting_time

        self.meeting_member_group = MeetingMemberGroup("Członkowie zespołu", self)
        self.meeting_member_group.selection_changed.connect(self.meeting_member_selection_changed)

        self.meeting_leader = LabeledComboBoxComponent("Przewodniczący zespołu", self, required=True)
        self.meeting_leader.combobox.setPlaceholderText("Wybierz z listy...")

        layout.addWidget(self.meeting_datetime_frame)
        layout.addWidget(self.meeting_member_group)
        layout.addWidget(self.meeting_leader)

        # Add stretch to push all content to the top and prevent empty space
        layout.addStretch()

        # Populate after all widgets are initialized
        self.meeting_member_group.populate_meeting_members()

        # Collect all components for validation
        self.components = [self.meeting_datetime_frame, self.meeting_member_group, self.meeting_leader]

    def meeting_member_selection_changed(self) -> None:
        self.meeting_leader.combobox.clear()
        for row_index in range(0, self.meeting_member_group.model.rowCount()):
            member = self.meeting_member_group.model.item(row_index)
            if member.checkState() == Qt.CheckState.Unchecked:
                continue
            self.meeting_leader.addItem(member.text(), member.data())

    @property
    def is_valid(self) -> bool:
        return all(c.is_valid for c in self.components)

    @property
    def error_message(self) -> str | None:
        for c in self.components:
            if not c.is_valid:
                return c.error_message
        return None

    def validate(self) -> bool:
        results = [c.validate() for c in self.components]
        return all(results)

    def clear_validation_state(self):
        for c in self.components:
            c.clear_validation_state()

    def get_meeting_members_data(self) -> dict:
        return [tm.model_dump() for tm in get_team_members()]

    @property
    def meeting_data(self) -> MeetingData:
        meeting_members = list()
        for row_index in range(0, self.meeting_member_group.model.rowCount()):
            member = self.meeting_member_group.model.item(row_index)
            if member.checkState() == Qt.CheckState.Unchecked:
                continue
            mm_data = get_meeting_member_by_id(member.data())
            meeting_member_data = MeetingMemberData(**mm_data.model_dump())

            if member.data() == self.meeting_leader.combobox.currentData():
                meeting_members.insert(0, meeting_member_data)
            else:
                meeting_members.append(meeting_member_data)

        return MeetingData(
            members=meeting_members, date=self.meeting_date.date_input.date().toPython(), time=self.meeting_time.text
        )

    def clear(self):
        self.meeting_leader.remove_selection()
        self.meeting_date.date_input.setDate(QDate.currentDate())
        self.meeting_time.clear()
        self.meeting_member_group.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        self.clear()
        meeting_data = document_data.meeting_data
        self.meeting_date.date_input.setDate(meeting_data.date)
        self.meeting_time.text = meeting_data.time
        self.meeting_member_group.populate_meeting_members(meeting_data.members)
        self.meeting_leader.combobox.setCurrentText(meeting_data.members[0].name)
