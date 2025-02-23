from PySide2.QtWidgets import QTabWidget, QWidget

from alinka.db.queries import get_support_center_data
from alinka.schemas import DocumentData, SupportCenterData

from .application_tabs import (
    ApplicantsTabContainer,
    ApplicationTabContainer,
    ChildDataTabContainer,
    MeetingTabContainer,
)


class ApplicationContainer(QTabWidget):
    def __init__(self, parent: QWidget, visible: bool = False):
        super().__init__(parent)
        self.id = None
        self.child_tab_container = ChildDataTabContainer(self)
        self.applicants_tab_container = ApplicantsTabContainer(self)
        self.application_tab_container = ApplicationTabContainer(self)
        self.meeting_tab_container = MeetingTabContainer(self)

        self.addTab(self.child_tab_container, "Uczeń")
        self.addTab(self.applicants_tab_container, "Wnioskodawcy")
        self.addTab(self.application_tab_container, "Wniosek")
        self.addTab(self.meeting_tab_container, "Zespół")

        if not visible:
            self.setVisible(visible)

    @property
    def document_data(self) -> DocumentData:
        support_center_data = get_support_center_data()
        support_center_data = SupportCenterData(**support_center_data.model_dump())

        return DocumentData(
            id=1,
            file_no=self.child_tab_container.general_data_group.file_no.text,
            decision_no=self.child_tab_container.general_data_group.decision_no.text,
            child=self.child_tab_container.child_data,
            school=self.child_tab_container.school_data,
            applicants=self.applicants_tab_container.applicants,
            address_child_checkbox=self.applicants_tab_container.address_child_checkbox,
            address_first_parent_checkbox=self.applicants_tab_container.address_first_parent_checkbox,
            issue=self.application_tab_container.issue,
            period=self.application_tab_container.period,
            reasons=self.application_tab_container.reasons,
            activity_form=self.application_tab_container.activity_form,
            application_no=self.child_tab_container.general_data_group.decision_no.text,
            application_date=self.application_tab_container.application_date.date_input.date().toPython(),
            meeting_data=self.meeting_tab_container.meeting_data,
            support_center=support_center_data,
        )
