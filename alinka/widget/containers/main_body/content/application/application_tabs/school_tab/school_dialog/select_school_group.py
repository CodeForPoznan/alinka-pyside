from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton

# Zakładamy, że posiadasz zaimplementowany rspo_manager na wzór wcześniejszych wyjaśnień
from alinka.managers.rspo_async_manager import rspo_manager
from alinka.constants.common import RSPOSchoolTypes, SchoolTypes
from alinka.schemas import SchoolDbCreateSchema
from alinka.schemas.rspo_schema import BaseEntity
from alinka.widget.components import (
    LabeledComboBoxComponent,
    SelectProvinceDistrictGroup,
    ValidationMixin, CacheStatusWidget,
)


class SelectSchoolGroup(ValidationMixin, QGroupBox):
    # Emitowany dopiero po udanym załadowaniu szczegółów szkoły z cache/API
    school_selected = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(title="Wybierz szkołę", parent=parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. Dodajemy panel cache'u w prawym górnym rogu
        self.cache_status = CacheStatusWidget(self)
        self.cache_status.refresh_requested.connect(self.force_refresh_current_context)
        layout.addWidget(self.cache_status)

        self.province_district_group = SelectProvinceDistrictGroup(self)
        self.province_district_group.selection_changed.connect(self.province_district_changed)
        layout.addWidget(self.province_district_group)

        self.commune_combobox = LabeledComboBoxComponent("Gmina", self, required=True)
        self.commune_combobox.combobox.setPlaceholderText("Wybierz z listy...")
        self.commune_combobox.combobox.currentTextChanged.connect(self.clear_school_types)
        layout.addWidget(self.commune_combobox)

        self.school_type_combobox = LabeledComboBoxComponent("Rodzaj szkoły", self, required=True, static=True)
        self.school_type_combobox.combobox.setPlaceholderText("Wybierz rodzaj szkoły...")
        self.school_type_combobox.addItems(SchoolTypes.values())
        self.school_type_combobox.combobox.setEnabled(True)
        self.school_type_combobox.combobox.currentTextChanged.connect(self.populate_schools_combobox)
        layout.addWidget(self.school_type_combobox)

        self.schools_combobox = LabeledComboBoxComponent("Szkoła", self, required=True)
        self.schools_combobox.combobox.setPlaceholderText("Wybierz szkołę...")
        self.schools_combobox.combobox.currentTextChanged.connect(self.user_selected_school)
        layout.addWidget(self.schools_combobox)

        self.components = [
            self.province_district_group,
            self.commune_combobox,
            self.school_type_combobox,
            self.schools_combobox,
        ]

        # Stan lokalny chroniący przez spowolnieniem UI
        self._loaded_school_details = None

        # Zmienne tymczasowe podtrzymujące wybór na czas odświeżania w tle
        self._last_commune_id = None
        self._last_school_id = None
        self._selected_school_type_for_fetch = None
        self._fetching_school_rspo_id = None

    def province_district_changed(self):
        self.populate_commune_combobox()
        self.school_type_combobox.clear()
        self.schools_combobox.clear()
        self.clear_school_data()

    def force_refresh_current_context(self):
        """Wymusza odświeżenie danych z najniższego wybranego poziomu"""
        if self.schools_combobox.combobox.currentData():
            self.user_selected_school(force_refresh=True)
        elif self.school_type_combobox.combobox.currentText() and self.commune_combobox.combobox.currentData():
            self.populate_schools_combobox(force_refresh=True)
        elif self.province_district_group.province_id and self.province_district_group.district_id:
            self.populate_commune_combobox(force_refresh=True)

    @staticmethod
    def get_institution_type_ids(school_type: str | None, institution_types: list) -> list[int]:
        """Przerobione z API synchronicznego na operację na dostarczonej liście cache'owanej"""
        match school_type:
            case SchoolTypes.PRZEDSZKOLE.value:
                return [it.id for it in institution_types if it.name == RSPOSchoolTypes.PRZEDSZKOLE.value]
            case SchoolTypes.SZKOLA_PODSTAWOWA.value:
                return [it.id for it in institution_types if getattr(it, 'is_primary_school', False)]
            case SchoolTypes.SZKOLA_PONADPODSTAWOWA.value:
                return [it.id for it in institution_types if getattr(it, 'is_secondary_school', False)]
            case _:
                return [
                    it.id for it in institution_types
                    if it.name == RSPOSchoolTypes.PRZEDSZKOLE.value
                       or getattr(it, 'is_primary_school', False)
                       or getattr(it, 'is_secondary_school', False)
                ]

    @staticmethod
    def get_school_type_from_school_data(school_type: BaseEntity, institution_types: list) -> str | None:
        """Przerobione z API synchronicznego na operację na dostarczonej liście cache'owanej"""
        if school_type.name == RSPOSchoolTypes.PRZEDSZKOLE.value:
            return SchoolTypes.PRZEDSZKOLE.value
        elif school_type.id in [it.id for it in institution_types if getattr(it, 'is_primary_school', False)]:
            return SchoolTypes.SZKOLA_PODSTAWOWA.value
        elif school_type.id in [it.id for it in institution_types if getattr(it, 'is_secondary_school', False)]:
            return SchoolTypes.SZKOLA_PONADPODSTAWOWA.value
        else:
            return None

    # --- ASYNCHRONICZNE POBIERANIE GMIN ---

    def populate_commune_combobox(self, force_refresh=False) -> None:
        selected_province_id = self.province_district_group.province_id
        selected_district_id = self.province_district_group.district_id
        if not (selected_province_id and selected_district_id):
            return

        self._last_commune_id = self.commune_combobox.combobox.currentData()

        self.commune_combobox.combobox.clear()
        self.commune_combobox.combobox.addItem("Ładowanie...")
        self.commune_combobox.combobox.setEnabled(False)
        self.cache_status.set_loading()

        rspo_manager.fetch_communes(
            province_id=selected_province_id,
            district_id=selected_district_id,
            force_refresh=force_refresh,
            callback=self._on_communes_loaded
        )

    def _on_communes_loaded(self, result):
        self.commune_combobox.combobox.clear()
        self.commune_combobox.combobox.setEnabled(True)
        self.cache_status.set_data(result.timestamp_str, result.is_error)

        if result.data:
            for commune in result.data:
                self.commune_combobox.addItem(commune.name, commune.id)

            # Przywrócenie wyboru, jeśli nie zniknął po odświeżeniu
            if self._last_commune_id:
                index = self.commune_combobox.combobox.findData(self._last_commune_id)
                if index >= 0:
                    self.commune_combobox.combobox.setCurrentIndex(index)

    # --- ASYNCHRONICZNE POBIERANIE SZKÓŁ (Wymaga najpierw pobrania typów) ---

    def populate_schools_combobox(self, force_refresh=False):
        self._selected_province_id = self.province_district_group.province_id
        self._selected_district_id = self.province_district_group.district_id
        self._selected_commune_id = self.commune_combobox.combobox.currentData()
        self._selected_school_type_for_fetch = self.school_type_combobox.combobox.currentText()

        if not all([self._selected_province_id, self._selected_district_id, self._selected_commune_id]):
            return

        self._last_school_id = self.schools_combobox.combobox.currentData()
        self._force_refresh_flag = force_refresh

        self.schools_combobox.combobox.clear()
        self.schools_combobox.combobox.addItem("Ładowanie...")
        self.schools_combobox.combobox.setEnabled(False)
        self.cache_status.set_loading()

        # Najpierw pobieramy w tle słownik typów instytucji (wymagane do filtracji po IDs)
        rspo_manager.fetch_institution_types(
            force_refresh=force_refresh,
            callback=self._on_institution_types_for_schools_loaded
        )

    def _on_institution_types_for_schools_loaded(self, result):
        if result.is_error and not result.data:
            self.cache_status.set_data(result.timestamp_str, result.is_error)
            self.schools_combobox.combobox.clear()
            self.schools_combobox.combobox.addItem("Błąd pobierania")
            return

        institution_type_ids = self.get_institution_type_ids(self._selected_school_type_for_fetch, result.data)

        if not institution_type_ids:
            self.schools_combobox.combobox.clear()
            self.schools_combobox.combobox.setEnabled(True)
            self.cache_status.set_data(result.timestamp_str, result.is_error)
            return

        rspo_manager.fetch_institutions(
            province_id=self._selected_province_id,
            district_id=self._selected_district_id,
            commune_id=self._selected_commune_id,
            institution_type_ids=institution_type_ids,
            force_refresh=self._force_refresh_flag,
            callback=self._on_schools_loaded
        )

    def _on_schools_loaded(self, result):
        self.schools_combobox.combobox.clear()
        self.schools_combobox.combobox.setEnabled(True)
        self.cache_status.set_data(result.timestamp_str, result.is_error)

        if result.data:
            # Dopasowanie do ewentualnego paginowanego wrappera zwracanego przez RSPO (np. items)
            items = result.data.items if hasattr(result.data, 'items') else result.data
            for school in items:
                self.schools_combobox.addItem(school.name, school.id)

            if self._last_school_id:
                index = self.schools_combobox.combobox.findData(self._last_school_id)
                if index >= 0:
                    self.schools_combobox.combobox.setCurrentIndex(index)

    # --- ASYNCHRONICZNE POBIERANIE SZCZEGÓŁÓW SZKOŁY ---

    def user_selected_school(self, force_refresh=False):
        rspo_id = self.schools_combobox.combobox.currentData()
        if not rspo_id:
            self._loaded_school_details = None
            return

        self.cache_status.set_loading()
        self._fetching_school_rspo_id = rspo_id
        self._force_refresh_flag = force_refresh

        # Potrzebujemy typów do poprawnego mapowania szczegółów, upewniamy się, że są w cache.
        rspo_manager.fetch_institution_types(
            force_refresh=False,
            callback=self._on_institution_types_for_details_loaded
        )

    def _on_institution_types_for_details_loaded(self, result):
        if result.is_error and not result.data:
            self.cache_status.set_data(result.timestamp_str, result.is_error)
            return

        self._cached_institution_types_for_details = result.data

        rspo_manager.fetch_institution(
            rspo_id=self._fetching_school_rspo_id,
            force_refresh=self._force_refresh_flag,
            callback=self._on_school_details_loaded
        )

    def _on_school_details_loaded(self, result):
        self.cache_status.set_data(result.timestamp_str, result.is_error)

        if result.data:
            school = result.data
            self._loaded_school_details = SchoolDbCreateSchema(
                rspo_id=school.rspo_id,
                rspo_type_id=school.type.id,
                address=school.address,
                town=school.town,
                postal_code=school.postal_code,
                post=school.post,
                type=self.get_school_type_from_school_data(school.type, self._cached_institution_types_for_details),
                name=school.name,
                parent_organisation_name=school.parent_organisation_name,
            )
            # Powiadamiamy interfejs użytkownika PO wgraniu szczegółów do pamięci
            self.school_selected.emit()

    # --- WŁAŚCIWOŚĆ ODCZYTU (Nie blokuje interfejsu!) ---

    @property
    def selected_school(self) -> SchoolDbCreateSchema | None:
        """
        Zwraca natychmiast szczegóły uprzednio asynchronicznie załadowanej szkoły,
        bez zamrażania UI i bez wywoływania zapytań HTTP.
        """
        return self._loaded_school_details

    # --- RESZTA LOGIKI WIDOKU ---

    def clear_school_types(self) -> None:
        self.school_type_combobox.clear()
        self.clear_school_data()

    def clear_school_data(self):
        self.parent().school_data_group.clear()

    @property
    def is_valid(self) -> bool:
        return all(component.is_valid for component in self.components)

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