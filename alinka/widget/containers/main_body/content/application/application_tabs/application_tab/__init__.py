from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from alinka.constants.common import (
    INVALID_FORM_MESSAGE,
    ISSUE_DESCRIPTION_NOMINATIVE_MAPPER,
    REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER,
    ActivityForm,
    Issue,
    Reason,
)
from alinka.widget.components import (
    LabeledComboBoxComponent,
    LabeledDateComponent,
    ValidationMixin,
)


class ApplicationTabContainer(ValidationMixin, QWidget):
    def __init__(self, parent: QWidget):
        self.application_container = parent
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        self.application_date = LabeledDateComponent("Data wniosku", self, required=True)
        self.application_date.date_input.setDate(QDate.currentDate())
        self.application_subject = LabeledComboBoxComponent("Wniosek o", self, required=True)
        self.application_subject.combobox.setPlaceholderText("Wybierz z listy...")
        for issue, description in ISSUE_DESCRIPTION_NOMINATIVE_MAPPER.items():
            self.application_subject.addItem(description, issue)
        self.application_subject.combobox.currentTextChanged.connect(self.change_application_subject)

        self.application_reason = LabeledComboBoxComponent("Z uwagi na", self, required=True)
        self.application_reason.combobox.setPlaceholderText("Wybierz z listy...")
        self.application_reason.combobox.currentTextChanged.connect(self.change_application_reason)
        self.application_reason_2 = LabeledComboBoxComponent("Z uwagi na", self, unselectable=True)
        self.application_reason_2.combobox.setPlaceholderText("Wybierz z listy...")
        self.application_reason_2.setVisible(False)

        self._activity_form = LabeledComboBoxComponent("Forma zajęć", self)
        self._activity_form.setVisible(False)
        self._activity_form.combobox.setEnabled(False)
        self._activity_form.combobox.setPlaceholderText("Wybierz z listy...")

        # TODO: not sure if this should be ComboBox or Input
        self.application_period = LabeledComboBoxComponent("Na okres", self, required=True)
        self.application_period.combobox.setEditable(True)
        self.application_period.combobox.setPlaceholderText("np. 24 miesiące")
        # TODO: probably can be removed after changing type
        line_edit = self.application_period.combobox.lineEdit()
        if line_edit:
            line_edit.setPlaceholderText("np. 24 miesiące")
            line_edit.setStyleSheet("QLineEdit { color: #64748b; }")
        # Hide the dropdown arrow to make it look like a text input
        self.application_period.combobox.setStyleSheet("""
            QComboBox::drop-down { width: 0px; border: none; }
            QComboBox::down-arrow { image: none; border: none; }
        """)
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
        self._activity_form.setVisible(False)
        self._activity_form.combobox.setEnabled(False)

        self.application_reason_2.combobox.clear()
        self.application_reason_2.combobox.setEnabled(False)
        self.application_reason_2.setVisible(False)

        self.application_period.combobox.clear()

        for reason, reason_description in self.get_list_of_primary_reasons(application_subject).items():
            self.application_reason.addItem(reason_description, reason)

    def change_application_reason(self):
        self.application_reason_2.clear()
        self.application_period.clear()
        primary_reason = self.application_reason.combobox.currentData()
        if primary_reason == Reason.GLEBOKIE:
            self._activity_form.setVisible(True)
            self._activity_form.combobox.setEnabled(True)
            self._activity_form.addItem(ActivityForm.INDYWIDUALNE.value, ActivityForm.INDYWIDUALNE)
            self._activity_form.addItem(ActivityForm.ZESPOLOWE.value, ActivityForm.ZESPOLOWE)
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
            self.application_reason_2.addItem(reason_description, reason)
        self.application_reason_2.setVisible(True)
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

    def clear(self):
        self.application_date.date_input.clear()
        self.application_subject.remove_selection()
        self.application_reason.remove_selection()
        self.application_reason_2.remove_selection()
        self.application_reason_2.setVisible(False)
        self._activity_form.remove_selection()
        self._activity_form.setVisible(False)
        self._activity_form.combobox.setEnabled(False)
        self.application_period.clear()

    @property
    def is_valid(self) -> bool:
        return all(
            [
                self.application_date.is_valid,
                self.application_subject.is_valid,
                self.application_reason.is_valid,
                self.is_activity_form_valid,
                self.application_period.is_valid,
            ]
        )

    @property
    def error_message(self) -> str | None:
        if not self.is_valid:
            return INVALID_FORM_MESSAGE

    @property
    def is_activity_form_valid(self) -> bool:
        if (
            self.application_subject.combobox.currentData() == Issue.REWALIDACYJNE
            and self._activity_form.combobox.currentIndex() == -1
        ):
            return False
        return True

    def validate_activity_form(self) -> bool:
        self._activity_form.display_validation_result(self.is_activity_form_valid)
        return self.is_activity_form_valid

    def validate(self) -> bool:
        return all(
            [
                self.application_date.validate(),
                self.application_subject.validate(),
                self.application_reason.validate(),
                self.validate_activity_form(),
                self.application_period.validate(),
            ]
        )

    def clear_validation_state(self):
        self.application_container.clear_validation_state()
