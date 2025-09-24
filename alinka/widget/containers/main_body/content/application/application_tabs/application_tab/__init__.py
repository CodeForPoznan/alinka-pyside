from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from alinka.constants.common import (
    ISSUE_DESCRIPTION_NOMINATIVE_MAPPER,
    REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER,
    ActivityForm,
    Issue,
    Reason,
)
from alinka.widget.components import LabeledComboBoxComponent, LabeledDateComponent


class ApplicationTabContainer(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.application_date = LabeledDateComponent("Data wniosku", self)
        self.application_date.date_input.setDate(QDate.currentDate())
        self.application_subject = LabeledComboBoxComponent("Wniosek o", self)
        self.application_subject.combobox.setPlaceholderText("Wybierz z listy...")
        for issue, description in ISSUE_DESCRIPTION_NOMINATIVE_MAPPER.items():
            self.application_subject.combobox.addItem(description, issue)
        self.application_subject.combobox.currentTextChanged.connect(self.change_application_subject)

        self.application_reason = LabeledComboBoxComponent("Z uwagi na", self)
        self.application_reason.combobox.setPlaceholderText("Wybierz z listy...")
        self.application_reason.combobox.currentTextChanged.connect(self.change_application_reason)
        self.application_reason_2 = LabeledComboBoxComponent("Z uwagi na", self)
        self.application_reason_2.combobox.setPlaceholderText("Wybierz z listy...")
        self.application_reason_2.setFixedHeight(0)

        self._activity_form = LabeledComboBoxComponent("Forma zajęć", self)
        self._activity_form.setFixedHeight(0)
        self._activity_form.combobox.setEnabled(False)
        self._activity_form.combobox.setPlaceholderText("Wybierz z listy...")

        self.application_period = LabeledComboBoxComponent("Na okres", self)
        self.application_period.combobox.setEditable(True)
        layout.addWidget(self.application_date)
        layout.addWidget(self.application_subject)
        layout.addWidget(self.application_reason)
        layout.addWidget(self.application_reason_2)
        layout.addWidget(self._activity_form)
        layout.addWidget(self.application_period)

    def change_application_subject(self):
        application_subject = self.application_subject.combobox.currentData()
        self.application_reason.combobox.clear()

        self._activity_form.combobox.clear()
        self._activity_form.setFixedHeight(0)
        self._activity_form.combobox.setEnabled(False)

        self.application_reason_2.combobox.clear()
        self.application_reason_2.combobox.setEnabled(False)
        self.application_reason_2.setFixedHeight(0)

        self.application_period.combobox.clear()

        for reason, reason_description in self.get_list_of_primary_reasons(application_subject).items():
            self.application_reason.combobox.addItem(reason_description, reason)

    def change_application_reason(self):
        self.application_reason_2.combobox.clear()
        self.application_period.combobox.clear()
        primary_reason = self.application_reason.combobox.currentData()
        if primary_reason == Reason.GLEBOKIE:
            self._activity_form.setFixedHeight(45)
            self._activity_form.combobox.setEnabled(True)
            self._activity_form.combobox.addItem(ActivityForm.INDYWIDUALNE.value, ActivityForm.INDYWIDUALNE)
            self._activity_form.combobox.addItem(ActivityForm.ZESPOLOWE.value, ActivityForm.ZESPOLOWE)
            return
        if primary_reason not in Reason.multiple_disabilities_reasons():
            # we want to show another reason select box is first is suitable
            # for multiple disability
            return

        secondary_reasons = {
            reason: reason_description
            for reason, reason_description in REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER.items()
            if reason in Reason.multiple_disabilities_reasons() and reason != primary_reason
        }
        if primary_reason in Reason.intellectual_reasons():
            # we need to exclude other intellectual reason if one was already selected.
            reason_to_exclude = Reason.intellectual_reasons()
        elif primary_reason in Reason.sight_deficites_reasons():
            reason_to_exclude = Reason.sight_deficites_reasons()
        elif primary_reason in Reason.hearing_deficites_reasons():
            reason_to_exclude = Reason.hearing_deficites_reasons()
        else:
            reason_to_exclude = []

        secondary_reasons = {
            reason: reason_description
            for reason, reason_description in secondary_reasons.items()
            if reason not in reason_to_exclude
        }
        for reason, reason_description in secondary_reasons.items():
            self.application_reason_2.combobox.addItem(reason_description, reason)
        self.application_reason_2.setFixedHeight(45)
        self.application_reason_2.combobox.setEnabled(True)

    def get_list_of_primary_reasons(self, issue: Issue) -> dict[Reason, str]:
        if issue == Issue.SPECJALNE:
            type_of_reasons = Reason.special_reasons()
        elif issue in [Issue.INDYWIDUALNE, Issue.INDYWIDUALNE_ROCZNE]:
            type_of_reasons = Reason.individual_reasons()
        elif issue == Issue.REWALIDACYJNE:
            type_of_reasons = Reason.profound_disability_reason()
        elif issue == Issue.OPINIA:
            type_of_reasons = Reason.early_development_support_reason()
        else:
            return {}

        return {
            reason: reason_description
            for reason, reason_description in REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER.items()
            if reason in type_of_reasons
        }

    def get_list_of_secondary_reasons(self, reason: Reason) -> dict[Reason, str]:
        reasons = {
            reason: reason_description
            for reason, reason_description in REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER.items()
            if reason in Reason.multiple_disabilities_reasons()
        }
        reasons.pop(reason)

    @property
    def reasons(self) -> list[Reason]:
        return [
            cb.currentData()
            for cb in [self.application_reason.combobox, self.application_reason_2.combobox]
            if cb.currentData()
        ]

    @property
    def issue(self) -> Issue:
        return self.application_subject.combobox.currentData()

    @property
    def period(self) -> str:
        return self.application_period.combobox.currentText()

    @property
    def activity_form(self) -> ActivityForm | None:
        return self._activity_form.combobox.currentData()

    @property
    def is_valid(self) -> bool:
        # Should be implemented in https://github.com/CodeForPoznan/alinka-pyside/issues/92
        return True

    def error_message(self) -> str | None:
        # Should be implemented in https://github.com/CodeForPoznan/alinka-pyside/issues/92
        return None

    def clear(self):
        self.application_date.date_input.clear()
        self.application_subject.combobox.setCurrentIndex(-1)
        self.application_reason.combobox.setCurrentIndex(-1)
        self.application_reason_2.combobox.setCurrentIndex(-1)
        self.application_reason_2.setFixedHeight(0)
        self._activity_form.combobox.setCurrentIndex(-1)
        self._activity_form.setFixedHeight(0)
        self._activity_form.combobox.setEnabled(False)
        self.application_period.combobox.setCurrentIndex(-1)
