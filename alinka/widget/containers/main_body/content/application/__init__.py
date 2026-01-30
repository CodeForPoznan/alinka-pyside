from PySide6.QtWidgets import QTabWidget, QWidget
import logging

from alinka.constants.common import INVALID_FORM_MESSAGE, INVALID_TAB_TOOLTIP_MESSAGE
from alinka.db.queries import get_support_center_data
from alinka.schemas import DocumentData, SupportCenterData
from alinka.widget.components import ValidationMixin
from alinka.widget.custom_tabbar import ValidationTabBar
from alinka.widget.toast import show_validation_error

from .application_tabs import (
    ApplicantsTabContainer,
    ApplicationTabContainer,
    ChildDataTabContainer,
    MeetingTabContainer,
    SchoolTabContainer,
)

# Module logger
logger = logging.getLogger(__name__)


class ApplicationContainer(ValidationMixin, QTabWidget):
    def __init__(self, parent: QWidget, content_container, visible: bool = False):
        super().__init__(parent)
        self.content_container = content_container
        self.id = None

        # custom tab bar for validation highlighting
        custom_tab_bar = ValidationTabBar(self)
        self.setTabBar(custom_tab_bar)

        # Track invalid tabs persistently
        self._invalid_tabs = set()

        # Track which tabs have been visited/interacted with
        # Only validate tabs that have been visited to avoid errors on pristine tabs
        self._visited_tabs = set()

        self.child_tab_container = ChildDataTabContainer(self)
        self.school_tab_container = SchoolTabContainer(self)
        self.applicants_tab_container = ApplicantsTabContainer(self)
        self.application_tab_container = ApplicationTabContainer(self)
        self.meeting_tab_container = MeetingTabContainer(self)

        self.addTab(self.child_tab_container, "Uczeń")
        self.addTab(self.school_tab_container, "Szkoła")
        self.addTab(self.applicants_tab_container, "Wnioskodawcy")
        self.addTab(self.application_tab_container, "Wniosek")
        self.addTab(self.meeting_tab_container, "Zespół")
        self.setCurrentIndex(0)

        # Mark the first tab as visited since user starts there
        self._visited_tabs.add(0)

        self.previous_tab_index = self.currentIndex()
        self.currentChanged.connect(self.validate_previous_tab)
        self.currentChanged.connect(self.update_breadcrumb)

        self.setCurrentWidget(self.child_tab_container)
        self.setVisible(visible)

        self.containers = [
            self.child_tab_container,
            self.school_tab_container,
            self.applicants_tab_container,
            self.application_tab_container,
            self.meeting_tab_container,
        ]

    @property
    def is_valid(self) -> bool:
        return all(tab.is_valid for tab in self.containers)

    @property
    def error_message(self) -> str | None:
        if not all(tab.is_valid for tab in self.containers):
            return INVALID_FORM_MESSAGE
        else:
            return None

    def clear_validation_state(self) -> None:
        """Clear validation error messages and field highlighting.

        Note: This does not clear tab-level validation state (red tabs with icon).
        Tab validation state is only cleared when tabs actually become valid
        or when the form is reset.
        """
        header_container = self.content_container.main_body_container.header_container
        header_container.clear_message()
        # Don't clear invalid tab styling here - let validate() handle it

        for c in self.containers:
            c.clear_validation_state()

    def check_validity(self, show_errors: bool = False) -> bool:
        """Public helper to check validity.

        - show_errors=False (default): only reads `is_valid` flags and returns
          the combined result without producing any visual side-effects.
        - show_errors=True: performs full validation and highlights errors
          (same behaviour as :meth:`validate`).

        This keeps a clear contract: `validate` highlights errors, while
        `check_validity(False)` only tests the state.
        """
        if show_errors:
            return self.validate()
        return self.is_valid

    def update_breadcrumb(self, index: int):
        """Update breadcrumb when tab changes"""
        header_container = self.content_container.main_body_container.header_container
        tab_name = self.tabText(index)
        header_container.set_breadcrumb(f"Utwórz dokument > {tab_name}")

    def validate_previous_tab(self, new_index: int) -> None:
        """Validate the previous tab when switching tabs.

        Only validates tabs that have been visited. This prevents showing
        validation errors on tabs the user hasn't interacted with yet.
        """
        # Mark the new tab as visited
        self._visited_tabs.add(new_index)

        # Only validate the previous tab if it has been visited
        if self.previous_tab_index in self._visited_tabs:
            previous_tab = self.widget(self.previous_tab_index)

            # Only call validate if the widget implements it. Some child
            # widgets may be plain QWidgets (type checker warns), so guard
            # the call to avoid unresolved attribute references and runtime
            # AttributeError in unusual cases.
            if hasattr(previous_tab, "validate"):
                is_prev_valid = previous_tab.validate()
            else:
                is_prev_valid = True

            if not is_prev_valid:
                tab_name = self.tabText(self.previous_tab_index)
                self._invalid_tabs.add(self.previous_tab_index)
                self._update_invalid_tabs_display()

                show_validation_error(self, INVALID_FORM_MESSAGE, tab_names=[tab_name])
            else:
                self._invalid_tabs.discard(self.previous_tab_index)
                self._update_invalid_tabs_display()

                if not self._invalid_tabs:
                    header_container = self.content_container.main_body_container.header_container
                    header_container.clear_message()

        # Don't validate the new tab automatically - let the user fill it first
        # Validation will occur when they try to move to another tab or submit

        self.previous_tab_index = new_index

    def _update_invalid_tabs_display(self) -> None:
        """Update the visual display of invalid tabs"""
        invalid_list = sorted(list(self._invalid_tabs))

        custom_tab_bar = self.tabBar()
        if isinstance(custom_tab_bar, ValidationTabBar):
            custom_tab_bar.set_invalid_tabs(invalid_list)

        # Update tooltips
        for index in range(self.count()):
            if index in self._invalid_tabs:
                tooltip = INVALID_TAB_TOOLTIP_MESSAGE
                custom_tab_bar.setTabToolTip(index, tooltip)
            else:
                custom_tab_bar.setTabToolTip(index, "")

    def finish_application_flow(self) -> None:
        """
        When application flow is finished (either by generating documents or cancelling)
        we should prepare the form for a new application.
        """
        # Reset form state and visual markers
        self.clear()
        self.setCurrentWidget(self.child_tab_container)
        self.clear_validation_state()

        # Move focus away from any previously focused sidebar/button widget.
        # This prevents leftover "focused" visuals on the sidebar buttons
        # after cancelling the form. We try to focus the header; if that
        # fails, fall back to clearing focus on the top-level window.
        try:
            header_container = self.content_container.main_body_container.header_container
            header_container.setFocus()
        except (AttributeError, RuntimeError, TypeError) as err:
            # If header container or its attributes are missing, fall back to clearing
            # focus on the top-level window. Log at DEBUG because this is usually
            # a benign UI state during teardown/reset.
            logger.debug("Could not focus header container; falling back to window.clearFocus(): %s", err, exc_info=True)
            try:
                win = self.window()
                if win is not None and hasattr(win, "clearFocus"):
                    win.clearFocus()
                else:
                    logger.debug("Window is None or has no clearFocus method; nothing to clear")
            except (AttributeError, RuntimeError, TypeError) as err2:
                # Unexpected failures while trying to clear focus; record stack trace
                logger.exception("Failed to clear focus on window: %s", err2)

    def mark_invalid_tabs(self, invalid_indices: list[int]) -> None:
        """Mark tabs as invalid using custom tab bar painting"""
        self._invalid_tabs = set(invalid_indices)
        self._update_invalid_tabs_display()

    def clear_invalid_tabs(self) -> None:
        """Clear invalid state from all tabs"""
        self._invalid_tabs.clear()
        self._update_invalid_tabs_display()

    def validate(self) -> bool:
        """Validate the whole application and highlight any errors.

        This method performs full validation (field-level checks and visual
        highlighting) and returns True when the form is valid. If a caller
        needs to check validity without side-effects, use
        :meth:`check_validity(show_errors=False)` or the :attr:`is_valid`
        property instead of this method.
        """
        return self._validate(show_errors=True)

    def _validate(self, show_errors: bool = True) -> bool:
        """Internal validation helper.

        show_errors=True -> call each tab.validate() (updates visual state)
        show_errors=False -> only check tab.is_valid (no visual updates)
        """
        if show_errors:
            # First validate all tabs (this will display field-level results)
            validation_results = [tab.validate() for tab in self.containers]
        else:
            # Only read validity without triggering visual updates
            validation_results = [tab.is_valid for tab in self.containers]

        if not all(validation_results):
            # Collect all invalid tab names and indices
            invalid_tabs = []
            invalid_indices = []
            for index, is_valid in enumerate(validation_results):
                if not is_valid:
                    tab_name = self.tabText(index)
                    invalid_tabs.append(tab_name)
                    invalid_indices.append(index)

            self.mark_invalid_tabs(invalid_indices)

            if show_errors:
                show_validation_error(self, self.error_message, tab_names=invalid_tabs)
            return False
        else:
            self.clear_invalid_tabs()
            return True

    @property
    def document_data(self) -> DocumentData:
        support_center_data = get_support_center_data()
        support_center_data = SupportCenterData(**support_center_data.model_dump())

        return DocumentData(
            id=1,
            file_no=self.child_tab_container.general_data_group.file_no.text,
            decision_no=self.child_tab_container.general_data_group.decision_no.text,
            child=self.child_tab_container.child_data,
            school=self.school_tab_container.school_data,
            applicants=self.applicants_tab_container.applicants,
            is_first_parent_address_different=self.applicants_tab_container.is_first_parent_address_different,
            is_second_parent_address_different=self.applicants_tab_container.is_second_parent_address_different,
            issue=self.application_tab_container.issue,
            period=self.application_tab_container.period,
            reasons=self.application_tab_container.reasons,
            activity_form=self.application_tab_container.activity_form,
            application_date=self.application_tab_container.application_date.date_input.date().toPython(),
            meeting_data=self.meeting_tab_container.meeting_data,
            support_center=support_center_data,
        )

    def populate_application_form(self, document_data: DocumentData) -> None:
        self.child_tab_container.populate_data(document_data)
        self.applicants_tab_container.populate_data(document_data)

    def clear(self):
        self.child_tab_container.clear()
        self.school_tab_container.clear()
        self.applicants_tab_container.clear()
        self.application_tab_container.clear()
        self.meeting_tab_container.clear()
        self.id = None
        self.clear_invalid_tabs()
        # Reset visited tabs - only first tab (index 0) is visited initially
        self._visited_tabs = {0}
