from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
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
    LabeledComboBoxComponent,
    LabeledDateComponent,
    LabeledInputComponent,
    ValidationMixin,
)

from .member_dialog import MemberDialog


class MeetingDatetimeFrame(ValidationMixin, QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        self.meeting_date = LabeledDateComponent("Data zespołu", self)
        self.meeting_date.date_input.setDate(QDate.currentDate())
        self.meeting_time = LabeledInputComponent("Godzina zespołu", self, required=True)
        self.meeting_time.line_edit.setPlaceholderText("np. 10:00")

        layout.addWidget(self.meeting_date, 1)
        layout.addWidget(self.meeting_time, 1)


class HandleMemberFrame(ValidationMixin, QFrame):
    team_member_changed = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
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
        delete_team_member(selected_member.id)
        self.team_member_changed.emit()

    def get_selected_member(self) -> MeetingMemberData | None:
        # Navigate to MeetingTabContainer (parent of parent)
        parent_widget = self.parent()
        if parent_widget and hasattr(parent_widget, "parent"):
            meeting_tab_container = parent_widget.parent()
            if not hasattr(meeting_tab_container, "selected_members_id"):
                return None
            selected_members_id = meeting_tab_container.selected_members_id
            if len(selected_members_id) != 1:
                return None
            return get_meeting_member_by_id(selected_members_id[0])
        return None


class MeetingTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)

        # Track team member IDs to detect changes
        self._last_team_members_ids = set()

        self.meeting_member_group = QGroupBox("Członkowie zespołu", self)
        meeting_member_group_layout = QVBoxLayout(self.meeting_member_group)
        meeting_member_group_layout.setAlignment(Qt.AlignTop)
        meeting_member_group_layout.setContentsMargins(10, 5, 10, 5)
        meeting_member_group_layout.setSpacing(5)

        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.item_changed)
        self.listView = QListView(self.meeting_member_group)
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
        self.listView.setStyleSheet(
            """
            QListView {
                outline: none;
                background-color: white;
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
        )

        # Set reasonable height for up to 7 team members
        self.listView.setMinimumHeight(80)
        self.listView.setMaximumHeight(280)
        self.listView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Add the handle member frame with buttons
        self.handle_member_frame = HandleMemberFrame(self.meeting_member_group)
        self.handle_member_frame.team_member_changed.connect(self.populate_meeting_members)

        meeting_member_group_layout.addWidget(self.listView, 0)
        meeting_member_group_layout.addWidget(self.handle_member_frame)

        self.meeting_leader = LabeledComboBoxComponent("Przewodniczący zespołu", self, unselectable=True)

        self.meeting_datetime_frame = MeetingDatetimeFrame(self)
        self.meeting_date = self.meeting_datetime_frame.meeting_date
        self.meeting_time = self.meeting_datetime_frame.meeting_time

        layout.addWidget(self.meeting_datetime_frame)
        layout.addWidget(self.meeting_member_group)
        layout.addWidget(self.meeting_leader)

        # Add stretch to push all content to the top and prevent empty space
        layout.addStretch()

        # Populate after all widgets are initialized
        self.populate_meeting_members()

    @property
    def selected_members_id(self) -> list[int]:
        """Get IDs of selected (checked) members"""
        return [
            item.data()
            for item in [self.model.item(i) for i in range(self.model.rowCount())]
            if item.checkState() == Qt.CheckState.Checked
        ]

    def populate_meeting_members(self, meeting_members: list[MeetingMemberData] | None = None) -> None:
        # Store current selection
        selected_ids = self.selected_members_id if hasattr(self, "model") else []

        # Temporarily disconnect to avoid multiple signals during population
        self.model.itemChanged.disconnect(self.item_changed)

        self.model.clear()
        for meeting_member_data in self.get_meeting_members_data():
            # Display format: "Name - Function"
            display_text = f"{meeting_member_data['name']} - " f"{meeting_member_data['function']}"
            item = QStandardItem(display_text)
            item.setData(meeting_member_data["id"])
            item.setCheckable(True)
            item.setEditable(False)
            # Restore selection if this member was previously selected
            if meeting_member_data["id"] in selected_ids:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.model.appendRow(item)

        # Reconnect the signal
        self.model.itemChanged.connect(self.item_changed)

        # Manually trigger item_changed to update button states
        self.item_changed()

        # Update the cached IDs
        current_team_members_data = self.get_meeting_members_data()
        self._last_team_members_ids = {tm["id"] for tm in current_team_members_data}

    def refresh_team_members(self):
        """Force refresh of team members list (called from settings when members change)"""
        self.model.clear()
        self.populate_meeting_members()
        # Clear the przewodniczący dropdown since selections have changed
        self.meeting_leader.clear_options()

    def showEvent(self, event):
        # Only refresh if team members have changed
        current_team_members_data = self.get_meeting_members_data()
        current_ids = {tm["id"] for tm in current_team_members_data}

        if current_ids != self._last_team_members_ids:
            # Team members have changed, need to refresh
            self.model.clear()
            self.populate_meeting_members()
            self._last_team_members_ids = current_ids

        return super().showEvent(event)

    def item_changed(self):
        # Update edit/remove button states
        selected_count = len(self.selected_members_id)
        self.handle_member_frame.edit_member_btn.setEnabled(selected_count == 1)
        self.handle_member_frame.remove_member_btn.setEnabled(selected_count == 1)

        # Update meeting leader dropdown
        self.meeting_leader.clear_options()
        for row_index in range(0, self.model.rowCount()):
            member = self.model.item(row_index)
            if member.checkState() == Qt.CheckState.Unchecked:
                continue
            self.meeting_leader.addItem(member.text(), member.data())

    def get_meeting_members_data(self) -> dict:
        return [tm.model_dump() for tm in get_team_members()]

    def get_meeting_member_by_id(self, meeting_member_id) -> MeetingMemberData:
        # To refactor. Maybe direct call to db?
        meeting_members_data = self.get_meeting_members_data()
        meeting_member = list(
            filter(lambda meeting_member: meeting_member["id"] == meeting_member_id, meeting_members_data)
        )[0]
        return MeetingMemberData(
            id=meeting_member["id"], name=meeting_member["name"], function=meeting_member["function"]
        )

    @property
    def meeting_data(self) -> MeetingData:
        meeting_members = list()
        # Get the selected leader's ID from the combobox
        leader_id = self.meeting_leader.combobox.currentData()

        for row_index in range(0, self.model.rowCount()):
            member = self.model.item(row_index)
            if member.checkState() == Qt.CheckState.Unchecked:
                continue
            meeting_member_data = self.get_meeting_member_by_id(member.data())
            # Compare by ID instead of name
            if meeting_member_data.id == leader_id:
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
        self.model.clear()

    def populate_data(self, document_data: DocumentData) -> None:
        self.clear()
        meeting_data = document_data.meeting_data
        self.meeting_date.date_input.setDate(meeting_data.date)
        self.meeting_time.text = meeting_data.time
        self.populate_meeting_members(meeting_data.members)
        # Set leader by ID instead of name
        if meeting_data.members:
            leader_id = meeting_data.members[0].id
            index = self.meeting_leader.combobox.findData(leader_id)
            if index >= 0:
                self.meeting_leader.combobox.setCurrentIndex(index)
