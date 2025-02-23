import pytest

from alinka.constants import Issue, Reason


class TestReasonEnum:
    def test_reason_individual_reasons(self):
        assert Reason.individual_reasons() == [Reason.UNIEMOZLIWIAJACY, Reason.ZNACZNIE_UTRUDNIAJACY]

    def test_reason_intellectual_reasons(self):
        assert Reason.intellectual_reasons() == [Reason.LEKKIE, Reason.UMIARKOWANE, Reason.ZNACZNE]

    def test_reason_perception_deficites_reasons(self):
        assert Reason.perception_deficites_reasons() == [
            Reason.NIESLYSZACE,
            Reason.SLABOSLYSZACE,
            Reason.NIEWIDZACE,
            Reason.SLABOWIDZACE,
        ]

    def test_reason_social_majadjustment_reasons(self):
        assert Reason.social_maladjustment_reasons() == [Reason.NIEDOSTOSOWANIE, Reason.ZAGROZENIE_NIEDOSTOSOWANIEM]

    def test_reason_special_reasons(self):
        assert Reason.special_reasons() == [
            Reason.LEKKIE,
            Reason.UMIARKOWANE,
            Reason.ZNACZNE,
            Reason.NIESLYSZACE,
            Reason.SLABOSLYSZACE,
            Reason.NIEWIDZACE,
            Reason.SLABOWIDZACE,
            Reason.NIEDOSTOSOWANIE,
            Reason.ZAGROZENIE_NIEDOSTOSOWANIEM,
            Reason.RUCHOWA,
            Reason.AUTYZM,
        ]

    def test_reason_multiple_disabilities_reasons(self):
        assert Reason.multiple_disabilities_reasons() == [
            Reason.LEKKIE,
            Reason.UMIARKOWANE,
            Reason.ZNACZNE,
            Reason.NIESLYSZACE,
            Reason.SLABOSLYSZACE,
            Reason.NIEWIDZACE,
            Reason.SLABOWIDZACE,
            Reason.RUCHOWA,
            Reason.AUTYZM,
        ]

    @pytest.mark.parametrize(
        "reason, description",
        [
            ("lekkie", "niepełnosprawność"),
            ("umiarkowane", "niepełnosprawność"),
            ("znaczne", "niepełnosprawność"),
            ("nieslyszace", "niesłyszenie"),
            ("slaboslyszace", "słabosłyszenie"),
            ("niewidzace", "niewidzenie"),
            ("slabowidzace", "słabowidzenie"),
            ("ruchowa", "niepełnosprawność ruchowa"),
            ("glebokie", "niepełnosprawność"),
            ("autyzm", "autyzm"),
            ("sprzezona", "niepełnosprawność sprzężona"),
            ("niedostosowanie", "niedostosowanie społeczne"),
            ("zagrozenie_niedostosowaniem", "zagrożenie niedostosowaniem społecznym"),
            ("uniemozliwiajacy", "stan zdrowia"),
            ("znacznie_utrudniajacy", "stan zdrowia"),
        ],
    )
    def test_reason_description_nominative_short(self, reason, description):
        assert Reason(reason).reason_description_nominative_short == description

    @pytest.mark.parametrize(
        "reason, description",
        [
            ("lekkie", "niepełnosprawności"),
            ("umiarkowane", "niepełnosprawności"),
            ("znaczne", "niepełnosprawności"),
            ("nieslyszace", "niesłyszenia"),
            ("slaboslyszace", "słabosłyszenia"),
            ("niewidzace", "niewidzenia"),
            ("slabowidzace", "słabowidzenia"),
            ("ruchowa", "niepełnosprawności ruchowej"),
            ("glebokie", "niepełnosprawności"),
            ("autyzm", "autyzmu"),
            ("sprzezona", "niepełnosprawności sprzężonej"),
            ("niedostosowanie", "niedostosowania społecznego"),
            ("zagrozenie_niedostosowaniem", "zagrożenia niedostosowaniem społecznym"),
            ("uniemozliwiajacy", "stanu zdrowia"),
            ("znacznie_utrudniajacy", "stanu zdrowia"),
        ],
    )
    def test_reason_description_genitive_short(self, reason, description):
        assert Reason(reason).reason_description_genitive_short == description

    @pytest.mark.parametrize(
        "reason, description",
        [
            ("lekkie", "niepełnosprawność"),
            ("umiarkowane", "niepełnosprawność"),
            ("znaczne", "niepełnosprawność"),
            ("nieslyszace", "niesłyszenie"),
            ("slaboslyszace", "słabosłyszenie"),
            ("niewidzace", "niewidzenie"),
            ("slabowidzace", "słabowidzenie"),
            ("ruchowa", "niepełnosprawność ruchową"),
            ("glebokie", "niepełnosprawność"),
            ("autyzm", "autyzm"),
            ("sprzezona", "niepełnosprawność sprzężoną"),
            ("niedostosowanie", "niedostosowanie społeczne"),
            ("zagrozenie_niedostosowaniem", "zagrożenie niedostosowaniem społecznym"),
            ("uniemozliwiajacy", "stan zdrowia"),
            ("znacznie_utrudniajacy", "stan zdrowia"),
        ],
    )
    def test_reason_description_accusative_short(self, reason, description):
        assert Reason(reason).reason_description_accusative_short == description

    @pytest.mark.parametrize(
        "reason, description",
        [
            ("lekkie", "niepełnosprawność intelektualna w stopniu lekkim"),
            ("umiarkowane", "niepełnosprawność intelektualna w stopniu umiarkowanym"),
            ("znaczne", "niepełnosprawnosć intelektualna w stopniu znacznym"),
            ("nieslyszace", "niesłyszenie"),
            ("slaboslyszace", "słabosłyszenie"),
            ("niewidzace", "niewidzenie"),
            ("slabowidzace", "słabowidzenie"),
            ("ruchowa", "niepełnosprawność ruchowa"),
            ("glebokie", "niepełnosprawność intelektualna w stopniu głębokim"),
            ("autyzm", "autyzm"),
            ("sprzezona", "niepełnosprawność sprzężona"),
            ("niedostosowanie", "niedostosowanie społeczne"),
            ("zagrozenie_niedostosowaniem", "zagrożenie niedostosowaniem społecznym"),
            ("uniemozliwiajacy", "stan zdrowia uniemożliwiający uczęszczanie do szkoły"),
            ("znacznie_utrudniajacy", "stan zdrowia znacznie utrudniający uczęszczanie do szkoły"),
        ],
    )
    def test_reason_description_nominative_long(self, reason, description):
        assert Reason(reason).reason_description_nominative_long == description

    @pytest.mark.parametrize(
        "reason, description",
        [
            ("lekkie", "niepełnosprawności intelektualnej w stopniu lekkim"),
            ("umiarkowane", "niepełnosprawności intelektualnej w stopniu umiarkowanym"),
            ("znaczne", "niepełnosprawności intelektualnej w stopniu znacznym"),
            ("nieslyszace", "niesłyszenia"),
            ("slaboslyszace", "słabosłyszenia"),
            ("niewidzace", "niewidzenia"),
            ("slabowidzace", "słabowidzenia"),
            ("ruchowa", "niepełnosprawności ruchowej"),
            ("glebokie", "niepełnosprawności intelektualnej w stopniu głębokim"),
            ("autyzm", "autyzmu"),
            ("sprzezona", "niepełnosprawności sprzężonej"),
            ("niedostosowanie", "niedostosowania społecznego"),
            ("zagrozenie_niedostosowaniem", "zagrożenia niedostosowaniem społecznym"),
            ("uniemozliwiajacy", "stanu zdrowia uniemozliwiajacego uczęszczanie do szkoły"),
            ("znacznie_utrudniajacy", "stanu zdrowia znacznie utrudniajacego uczęszczanie do szkoły"),
        ],
    )
    def test_reason_description_genitive_long(self, reason, description):
        assert Reason(reason).reason_description_genitive_long == description

    @pytest.mark.parametrize(
        "reason, description",
        [
            ("lekkie", "niepełnosprawność intelektualną w stopniu lekkim"),
            ("umiarkowane", "niepełnosprawność intelektualną w stopniu umiarkowanym"),
            ("znaczne", "niepełnosprawność intelektualną w stopniu znacznym"),
            ("nieslyszace", "niesłyszenie"),
            ("slaboslyszace", "słabosłyszenie"),
            ("niewidzace", "niewidzenie"),
            ("slabowidzace", "słabowidzenie"),
            ("ruchowa", "niepełnosprawność ruchową"),
            ("glebokie", "niepełnosprawność intelektualną w stopniu głębokim"),
            ("autyzm", "autyzm"),
            ("sprzezona", "niepełnosprawność sprzężoną"),
            ("niedostosowanie", "niedostosowanie społeczne"),
            ("zagrozenie_niedostosowaniem", "zagrożenie niedostosowaniem społecznym"),
            ("uniemozliwiajacy", "stan zdrowia uniemozliwiajacy uczęszczanie do szkoły"),
            ("znacznie_utrudniajacy", "stan zdrowia znacznie utrudniajacy uczęszczanie do szkoły"),
        ],
    )
    def test_reason_description_accusative_long(self, reason, description):
        assert Reason(reason).reason_description_accusative_long == description


class TestIssue:
    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "kształcenie specjalne"),
            ("indywidualne", "indywidualne nauczanie"),
            ("indywidualne_roczne", "indywidualne roczne przygotowanie przedszkolne"),
            ("opinia", "wczesnege wspomaganie rozwoju"),
            ("rewalidacyjne", "zajęcia rewalidacyjno - wychowawcze"),
        ],
    )
    def test_issue_description_nominative(self, issue, description):
        assert Issue(issue).issue_description_nominative == description

    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "kształcenia specjalnego"),
            ("indywidualne", "indywidualnego nauczania"),
            ("indywidualne_roczne", "indywidualnego rocznego przygotowania przedszkolnego"),
            ("opinia", "wczesnego wspomagania rozwoju"),
            ("rewalidacyjne", "zajęć rewalidacyjno - wychowawczych"),
        ],
    )
    def test_issue_description_genitive(self, issue, description):
        assert Issue(issue).issue_description_genitive == description

    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "orzeczenie"),
            ("indywidualne", "orzeczenie"),
            ("indywidualne_roczne", "orzeczenie"),
            ("opinia", "opinia"),
            ("rewalidacyjne", "orzeczenie"),
        ],
    )
    def test_issue_type_nominative_short(self, issue, description):
        assert Issue(issue).issue_type_nominative_short == description

    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "orzeczenia"),
            ("indywidualne", "orzeczenia"),
            ("indywidualne_roczne", "orzeczenia"),
            ("opinia", "opinii"),
            ("rewalidacyjne", "orzeczenia"),
        ],
    )
    def test_issue_type_genitive_short(self, issue, description):
        assert Issue(issue).issue_type_genitive_short == description

    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "orzeczenie o potrzebie kształcenia specjalnego"),
            ("indywidualne", "orzeczenie o potrzebie indywidualnego nauczania"),
            ("indywidualne_roczne", "orzeczenie o potrzebie indywidualnego rocznego przygotowania przedszkolnego"),
            ("opinia", "opinia o potrzebie wczesnego wspomagania rozwoju"),
            ("rewalidacyjne", "orzeczenie o potrzebie zajęć rewalidacyjno - wychowawczych"),
        ],
    )
    def test_issue_type_nominative_long(self, issue, description):
        assert Issue(issue).issue_type_nominative_long == description

    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "orzeczenia o potrzebie kształcenia specjalnego"),
            ("indywidualne", "orzeczenia o potrzebie indywidualnego nauczania"),
            ("indywidualne_roczne", "orzeczenia o potrzebie indywidualnego rocznego przygotowania przedszkolnego"),
            ("opinia", "opinii o potrzebie wczesnego wspomagania rozwoju"),
            ("rewalidacyjne", "orzeczenia o potrzebie zajęć rewalidacyjno - wychowawczych"),
        ],
    )
    def test_issue_type_genitive_long(self, issue, description):
        assert Issue(issue).issue_type_genitive_long == description

    @pytest.mark.parametrize(
        "issue, description",
        [
            ("specjalne", "dziecka lub ucznia"),
            ("indywidualne", "ucznia"),
            ("indywidualne_roczne", "dziecka"),
            ("opinia", "dziecka"),
            ("rewalidacyjne", "dziecka"),
        ],
    )
    def test_issue_recipient_description_genitive(self, issue, description):
        assert Issue(issue).recipient_description_genitive == description
