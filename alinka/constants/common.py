from enum import Enum

RPSO_SUPPORT_CENTER_TYPE_ID = 48


class DocumentsTypes(Enum):
    SPECJALNE = "specjalne"
    INDYWIDUALNE = "indywidualne"
    INDYWIDUALNE_ROCZNE = "indywidualne_roczne"
    OPINIA = "opinia"
    REWALIDACYJNE = "rewalidacyjne"
    PROTOKOL = "protokol"
    ZARZADZANIE = "zarzadzenie"
    ZAWIADOMIENIE = "zawiadomienie"


class Issue(Enum):
    SPECJALNE = "specjalne"
    INDYWIDUALNE = "indywidualne"
    INDYWIDUALNE_ROCZNE = "indywidualne_roczne"
    OPINIA = "opinia"
    REWALIDACYJNE = "rewalidacyjne"

    @property
    def issue_description_nominative(self):
        return ISSUE_DESCRIPTION_NOMINATIVE_MAPPER[self]

    @property
    def issue_description_genitive(self):
        return ISSUE_DESCRIPTION_GENITIVE_MAPPER[self]

    @property
    def issue_type_nominative_short(self):
        return "opinia" if self == self.OPINIA else "orzeczenie"

    @property
    def issue_type_genitive_short(self):
        return "opinii" if self == self.OPINIA else "orzeczenia"

    @property
    def issue_type_nominative_long(self):
        return f"{self.issue_type_nominative_short} o potrzebie {self.issue_description_genitive}"

    @property
    def issue_type_genitive_long(self):
        return f"{self.issue_type_genitive_short} o potrzebie {self.issue_description_genitive}"

    @property
    def recipient_description_genitive(self):
        return RECIPIENT_DESCRIPTION_GENITIVE_MAPPER[self]


ISSUE_DESCRIPTION_NOMINATIVE_MAPPER = {
    Issue.SPECJALNE: "kształcenie specjalne",
    Issue.INDYWIDUALNE: "indywidualne nauczanie",
    Issue.INDYWIDUALNE_ROCZNE: "indywidualne roczne przygotowanie przedszkolne",
    Issue.OPINIA: "wczesnege wspomaganie rozwoju",
    Issue.REWALIDACYJNE: "zajęcia rewalidacyjno - wychowawcze",
}

ISSUE_DESCRIPTION_GENITIVE_MAPPER = {
    Issue.SPECJALNE: "kształcenia specjalnego",
    Issue.INDYWIDUALNE: "indywidualnego nauczania",
    Issue.INDYWIDUALNE_ROCZNE: "indywidualnego rocznego przygotowania przedszkolnego",
    Issue.OPINIA: "wczesnego wspomagania rozwoju",
    Issue.REWALIDACYJNE: "zajęć rewalidacyjno - wychowawczych",
}

RECIPIENT_DESCRIPTION_GENITIVE_MAPPER = {
    Issue.SPECJALNE: "dziecka lub ucznia",
    Issue.INDYWIDUALNE: "ucznia",
    Issue.INDYWIDUALNE_ROCZNE: "dziecka",
    Issue.REWALIDACYJNE: "dziecka",
    Issue.OPINIA: "dziecka",
}


class Reason(str, Enum):
    NIESLYSZACE = "nieslyszace"
    SLABOSLYSZACE = "slaboslyszace"
    NIEWIDZACE = "niewidzace"
    SLABOWIDZACE = "slabowidzace"
    RUCHOWA = "ruchowa"
    LEKKIE = "lekkie"
    UMIARKOWANE = "umiarkowane"
    ZNACZNE = "znaczne"
    GLEBOKIE = "glebokie"
    AUTYZM = "autyzm"
    SPRZEZONA = "sprzezona"
    NIEDOSTOSOWANIE = "niedostosowanie"
    ZAGROZENIE_NIEDOSTOSOWANIEM = "zagrozenie_niedostosowaniem"
    UNIEMOZLIWIAJACY = "uniemozliwiajacy"
    ZNACZNIE_UTRUDNIAJACY = "znacznie_utrudniajacy"
    STWIERDZONA_NIEPELNOSPRAWNOSC = "stwierdzona_niepełnosprawność"

    @classmethod
    def individual_reasons(cls):
        return [cls.UNIEMOZLIWIAJACY, cls.ZNACZNIE_UTRUDNIAJACY]

    @classmethod
    def intellectual_reasons(cls):
        return [cls.LEKKIE, cls.UMIARKOWANE, cls.ZNACZNE]

    @classmethod
    def perception_deficites_reasons(cls):
        return [cls.NIESLYSZACE, cls.SLABOSLYSZACE, cls.NIEWIDZACE, cls.SLABOWIDZACE]

    @classmethod
    def sight_deficites_reasons(cls):
        return [cls.NIEWIDZACE, cls.SLABOWIDZACE]

    @classmethod
    def hearing_deficites_reasons(cls):
        return [
            cls.NIESLYSZACE,
            cls.SLABOSLYSZACE,
        ]

    @classmethod
    def social_maladjustment_reasons(cls):
        return [cls.NIEDOSTOSOWANIE, cls.ZAGROZENIE_NIEDOSTOSOWANIEM]

    @classmethod
    def special_reasons(cls):
        return [
            *cls.intellectual_reasons(),
            *cls.perception_deficites_reasons(),
            *cls.social_maladjustment_reasons(),
            cls.RUCHOWA,
            cls.AUTYZM,
        ]

    @classmethod
    def profound_disability_reason(cls):
        return [cls.GLEBOKIE]

    @classmethod
    def early_development_support_reason(cls):
        return [cls.STWIERDZONA_NIEPELNOSPRAWNOSC]

    @classmethod
    def multiple_disabilities_reasons(cls):
        return [*cls.intellectual_reasons(), *cls.perception_deficites_reasons(), cls.RUCHOWA, cls.AUTYZM]

    @property
    def reason_description_nominative_short(self):
        mapper = {
            self.LEKKIE: "niepełnosprawność",
            self.UMIARKOWANE: "niepełnosprawność",
            self.ZNACZNE: "niepełnosprawność",
            self.NIESLYSZACE: "niesłyszenie",
            self.SLABOSLYSZACE: "słabosłyszenie",
            self.NIEWIDZACE: "niewidzenie",
            self.SLABOWIDZACE: "słabowidzenie",
            self.RUCHOWA: "niepełnosprawność ruchowa",
            self.GLEBOKIE: "niepełnosprawność",
            self.AUTYZM: "autyzm",
            self.SPRZEZONA: "niepełnosprawność sprzężona",
            self.NIEDOSTOSOWANIE: "niedostosowanie społeczne",
            self.ZAGROZENIE_NIEDOSTOSOWANIEM: "zagrożenie niedostosowaniem społecznym",
            self.UNIEMOZLIWIAJACY: "stan zdrowia",
            self.ZNACZNIE_UTRUDNIAJACY: "stan zdrowia",
            self.STWIERDZONA_NIEPELNOSPRAWNOSC: "stwierdzona niepełnosprawność",
        }
        return mapper[self]

    @property
    def reason_description_genitive_short(self):
        mapper = {
            self.LEKKIE: "niepełnosprawności",
            self.UMIARKOWANE: "niepełnosprawności",
            self.ZNACZNE: "niepełnosprawności",
            self.NIESLYSZACE: "niesłyszenia",
            self.SLABOSLYSZACE: "słabosłyszenia",
            self.NIEWIDZACE: "niewidzenia",
            self.SLABOWIDZACE: "słabowidzenia",
            self.RUCHOWA: "niepełnosprawności ruchowej",
            self.GLEBOKIE: "niepełnosprawności",
            self.AUTYZM: "autyzmu",
            self.SPRZEZONA: "niepełnosprawności sprzężonej",
            self.NIEDOSTOSOWANIE: "niedostosowania społecznego",
            self.ZAGROZENIE_NIEDOSTOSOWANIEM: "zagrożenia niedostosowaniem społecznym",
            self.UNIEMOZLIWIAJACY: "stanu zdrowia",
            self.ZNACZNIE_UTRUDNIAJACY: "stanu zdrowia",
            self.STWIERDZONA_NIEPELNOSPRAWNOSC: "stwierdzonej niepełnosprawności",
        }
        return mapper[self]

    @property
    def reason_description_accusative_short(self):
        mapper = {
            self.LEKKIE: "niepełnosprawność",
            self.UMIARKOWANE: "niepełnosprawność",
            self.ZNACZNE: "niepełnosprawność",
            self.NIESLYSZACE: "niesłyszenie",
            self.SLABOSLYSZACE: "słabosłyszenie",
            self.NIEWIDZACE: "niewidzenie",
            self.SLABOWIDZACE: "słabowidzenie",
            self.RUCHOWA: "niepełnosprawność ruchową",
            self.GLEBOKIE: "niepełnosprawność",
            self.AUTYZM: "autyzm",
            self.SPRZEZONA: "niepełnosprawność sprzężoną",
            self.NIEDOSTOSOWANIE: "niedostosowanie społeczne",
            self.ZAGROZENIE_NIEDOSTOSOWANIEM: "zagrożenie niedostosowaniem społecznym",
            self.UNIEMOZLIWIAJACY: "stan zdrowia",
            self.ZNACZNIE_UTRUDNIAJACY: "stan zdrowia",
            self.STWIERDZONA_NIEPELNOSPRAWNOSC: "niepełnosprawność",
        }
        return mapper[self]

    @property
    def reason_description_nominative_long(self):
        mapper = {
            self.LEKKIE: "niepełnosprawność intelektualna w stopniu lekkim",
            self.UMIARKOWANE: "niepełnosprawność intelektualna w stopniu umiarkowanym",
            self.ZNACZNE: "niepełnosprawnosć intelektualna w stopniu znacznym",
            self.NIESLYSZACE: "niesłyszenie",
            self.SLABOSLYSZACE: "słabosłyszenie",
            self.NIEWIDZACE: "niewidzenie",
            self.SLABOWIDZACE: "słabowidzenie",
            self.RUCHOWA: "niepełnosprawność ruchowa",
            self.GLEBOKIE: "niepełnosprawność intelektualna w stopniu głębokim",
            self.AUTYZM: "autyzm",
            self.SPRZEZONA: "niepełnosprawność sprzężona",
            self.NIEDOSTOSOWANIE: "niedostosowanie społeczne",
            self.ZAGROZENIE_NIEDOSTOSOWANIEM: "zagrożenie niedostosowaniem społecznym",
            self.UNIEMOZLIWIAJACY: "stan zdrowia uniemożliwiający uczęszczanie do szkoły",
            self.ZNACZNIE_UTRUDNIAJACY: "stan zdrowia znacznie utrudniający uczęszczanie do szkoły",
            self.STWIERDZONA_NIEPELNOSPRAWNOSC: "stwierdzona niepełnosprawność",
        }
        return mapper[self]

    @property
    def reason_description_genitive_long(self):
        mapper = {
            self.LEKKIE: "niepełnosprawności intelektualnej w stopniu lekkim",
            self.UMIARKOWANE: "niepełnosprawności intelektualnej w stopniu umiarkowanym",
            self.ZNACZNE: "niepełnosprawności intelektualnej w stopniu znacznym",
            self.NIESLYSZACE: "niesłyszenia",
            self.SLABOSLYSZACE: "słabosłyszenia",
            self.NIEWIDZACE: "niewidzenia",
            self.SLABOWIDZACE: "słabowidzenia",
            self.RUCHOWA: "niepełnosprawności ruchowej",
            self.GLEBOKIE: "niepełnosprawności intelektualnej w stopniu głębokim",
            self.AUTYZM: "autyzmu",
            self.SPRZEZONA: "niepełnosprawności sprzężonej",
            self.NIEDOSTOSOWANIE: "niedostosowania społecznego",
            self.ZAGROZENIE_NIEDOSTOSOWANIEM: "zagrożenia niedostosowaniem społecznym",
            self.UNIEMOZLIWIAJACY: "stanu zdrowia uniemozliwiajacego uczęszczanie do szkoły",
            self.ZNACZNIE_UTRUDNIAJACY: "stanu zdrowia znacznie utrudniajacego uczęszczanie do szkoły",
            self.STWIERDZONA_NIEPELNOSPRAWNOSC: "stwierdzonej niepełnosprawności",
        }
        return mapper[self]

    @property
    def reason_description_accusative_long(self):
        return REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER[self]


REASON_DESCRIPTION_ACCUSATIVE_LONG_MAPPER = {
    Reason.LEKKIE: "niepełnosprawność intelektualną w stopniu lekkim",
    Reason.UMIARKOWANE: "niepełnosprawność intelektualną w stopniu umiarkowanym",
    Reason.ZNACZNE: "niepełnosprawność intelektualną w stopniu znacznym",
    Reason.NIESLYSZACE: "niesłyszenie",
    Reason.SLABOSLYSZACE: "słabosłyszenie",
    Reason.NIEWIDZACE: "niewidzenie",
    Reason.SLABOWIDZACE: "słabowidzenie",
    Reason.RUCHOWA: "niepełnosprawność ruchową",
    Reason.GLEBOKIE: "niepełnosprawność intelektualną w stopniu głębokim",
    Reason.AUTYZM: "autyzm",
    Reason.SPRZEZONA: "niepełnosprawność sprzężoną",
    Reason.NIEDOSTOSOWANIE: "niedostosowanie społeczne",
    Reason.ZAGROZENIE_NIEDOSTOSOWANIEM: "zagrożenie niedostosowaniem społecznym",
    Reason.UNIEMOZLIWIAJACY: "stan zdrowia uniemozliwiajacy uczęszczanie do szkoły",
    Reason.ZNACZNIE_UTRUDNIAJACY: "stan zdrowia znacznie utrudniajacy uczęszczanie do szkoły",
    Reason.STWIERDZONA_NIEPELNOSPRAWNOSC: "stwierdzoną niepełnosprawność",
}


class ActivityForm(Enum):
    INDYWIDUALNE = "indywidualne"
    ZESPOLOWE = "zespolowe"


class RSPOSchoolTypes(str, Enum):
    PRZEDSZKOLE = "Przedszkole"


class SchoolTypes(Enum):
    PRZEDSZKOLE = "przedszkole"
    SZKOLA_PODSTAWOWA = "szkoła podstawowa"
    SZKOLA_PONADPODSTAWOWA = "szkoła ponadpodstawowa"

    @classmethod
    def values(cls) -> list:
        return list(cls._value2member_map_.keys())
