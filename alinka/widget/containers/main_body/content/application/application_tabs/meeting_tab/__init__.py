from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QListView,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from alinka.db.queries import get_team_members
from alinka.schemas import MeetingData, MeetingMemberData
from alinka.schemas.document_schema import DocumentData
from alinka.widget.components import (
    LabeledComboBoxComponent,
    LabeledDateComponent,
    LabeledInputComponent,
    ValidationMixin,
)


class MeetingDatetimeFrame(ValidationMixin, QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)  # Align all widgets to top

        self.meeting_date = LabeledDateComponent("Data zespołu", self)
        self.meeting_date.date_input.setDate(QDate.currentDate())
        self.meeting_time = LabeledInputComponent("Godzina zespołu", self, required=True)
        self.meeting_time.line_edit.setPlaceholderText("np. 10:00")  # Add placeholder text

        # Add with stretch factor to maintain consistent sizing
        layout.addWidget(self.meeting_date, 1)
        layout.addWidget(self.meeting_time, 1)


class MeetingTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)  # Reduced spacing for more compact layout

        self._last_team_members_ids = set()  # Track team member IDs to detect changes

        self.meeting_member_group = QGroupBox("Członkowie zespołu", self)
        meeting_member_group_layout = QVBoxLayout(self.meeting_member_group)
        meeting_member_group_layout.setAlignment(Qt.AlignTop)
        meeting_member_group_layout.setContentsMargins(10, 5, 10, 5)
        meeting_member_group_layout.setSpacing(5)
        self.model = QStandardItemModel()
        self.model.itemChanged.connect(self.item_changed)
        self.listView = QListView(self.meeting_member_group)
        self.listView.setAlternatingRowColors(True)
        
        # Make checkboxes more visible and user-friendly with borders
        self.listView.setSpacing(2)
        self.listView.setWordWrap(False)
        self.listView.setUniformItemSizes(True)
        
        # Add visible borders and styling
        self.listView.setStyleSheet("""
            QListView {
                outline: none;
            }
            QListView::item {
                padding: 6px;
                border-bottom: 1px solid #e2e8f0;
            }
            QListView::item:alternate {
                background-color: #f8fafc;
            }
            QListView::item:hover {
                background-color: #e2e8f0;
            }
            QListView::item:selected {
                color: white;
            }
            QListView::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #94a3b8;
                background-color: white;
            }
            QListView::indicator:checked {
                background-color: white;
                border: 2px solid #94a3b8;
            }
        """)
        
        # Set reasonable height for up to 7 team members
        # Each item is roughly 35px high, so 7 items = ~245px + some padding
        self.listView.setMinimumHeight(80)  # At least 2 items visible
        self.listView.setMaximumHeight(280)  # Max for about 7-8 items
        # Don't expand vertically - use preferred size
        self.listView.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )

        self.populate_meeting_members()

        self.listView.setModel(self.model)
        meeting_member_group_layout.addWidget(self.listView, 0)

        self.meeting_leader = LabeledComboBoxComponent(
            "Przewodniczący zespołu", self, unselectable=True
        )

        self.meeting_datetime_frame = MeetingDatetimeFrame(self)
        self.meeting_date = self.meeting_datetime_frame.meeting_date
        self.meeting_time = self.meeting_datetime_frame.meeting_time

        layout.addWidget(self.meeting_datetime_frame)
        layout.addWidget(self.meeting_member_group)
        layout.addWidget(self.meeting_leader)
        
        # Add stretch to push all content to the top and prevent empty space
        layout.addStretch()

    def populate_meeting_members(self, meeting_members: list[MeetingMemberData] | None = None) -> None:
        self.model.clear()
        for meeting_member_data in self.get_meeting_members_data():
            item = QStandardItem(meeting_member_data["name"])
            item.setData(meeting_member_data["id"])
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.model.appendRow(item)
        
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
        for row_index in range(0, self.model.rowCount()):
            member = self.model.item(row_index)
            if member.checkState() == Qt.CheckState.Unchecked:
                continue
            meeting_member_data = self.get_meeting_member_by_id(member.data())
            if meeting_member_data.name == self.meeting_leader.combobox.currentText():
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
        self.meeting_leader.combobox.setCurrentText(meeting_data.members[0].name)
