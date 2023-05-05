from random import randrange

from factory.fuzzy import BaseFuzzyAttribute
from factory.fuzzy import random as factory_random
from faker import Faker

faker = Faker(locale="pl_PL")


class FuzzyKlass(BaseFuzzyAttribute):
    def fuzz(self):
        return randrange(1, 8)


class FuzzyProfession(BaseFuzzyAttribute):
    def fuzz(self):
        professions = [
            "betonarz-zbrojarz",
            "księgowy",
            "malarz-tapeciarz",
            "cukiernik",
            "piekarz",
            "rzeźnik",
            "elektryk",
            "",
        ]
        return factory_random.randgen.choice(professions)


class FuzzySchoolParentOrganisation(BaseFuzzyAttribute):
    def fuzz(self):
        parent_organisation = [
            "Zespół Szkoł Integracyjnych",
            "Zespół Szkół Budowlanych",
            "Zespół Szkół nr 1.",
            "Zespół Szkoł Technicznych",
            "Zespół Liceów Medycznych",
            None,
        ]
        return factory_random.randgen.choice(parent_organisation)


class FuzzySchoolType(BaseFuzzyAttribute):
    def fuzz(self):
        school_types = ["przedszkole", "szkoła podstawowa", "szkoła ponadpodstawowa"]
        return factory_random.randgen.choice(school_types)


class FuzzySchoolName(BaseFuzzyAttribute):
    def fuzz(self):
        school_name = [
            "Szkoła Podstawowa",
            "Technikum Elektryczne",
            "Przedszkole",
            "Liceum Ogólnokształcące",
            "Szkoła Zawodowa",
            "Technikum Mechaniczne",
        ]
        sufix = ["nr 5", "nr 23", "im. Tadeusza Kościuszki", "im. Boh. Westerplatte", ""]
        return f"{factory_random.randgen.choice(school_name)} {factory_random.randgen.choice(sufix)}"


class FuzzySupportCenterNameNominative(BaseFuzzyAttribute):
    def fuzz(self):
        prefix = ["Powiatowa", "Miejska", "Specjalistyczna"]
        support_center_name = "Poradnia Psychologiczno - Pedagogiczna"
        return f"{factory_random.randgen.choice(prefix)} {support_center_name} w {faker.city()}"


class FuzzySupportCenterNameGenetive(BaseFuzzyAttribute):
    def fuzz(self):
        prefix = ["Powiatowej", "Miejskiej", "Specjalistycznej"]
        support_center_name = "Poradni Psychologiczno - Pedagogicznej"
        return f"{factory_random.randgen.choice(prefix)} {support_center_name} w {faker.city()}"


class FuzzySupportCenterKurator(BaseFuzzyAttribute):
    def fuzz(self):
        city_genetive = [
            "Poznaniu",
            "Warszawie",
            "Szczecinie",
            "Bydgoszczy",
            "Gdańsku",
            "Gorzowie Wlkp.",
            "Białej Podlaskiej",
        ]
        return (
            f"{factory_random.randgen.choice(city_genetive)}, {faker.street_address()},"
            f" {faker.postcode()} {faker.city()}"
        )


class FuzzyMeetingMember(BaseFuzzyAttribute):
    def fuzz(self):
        def get_member():
            functions = ["psycholog", "pedagog", "logopeda", "tyflopedagog"]
            return {
                "name": f"{faker.first_name()} {faker.last_name()}",
                "function": ", ".join(faker.random_elements(functions, 2, unique=True)),
            }

        meeting_members_number = faker.pyint(3, 6)
        return [get_member() for _ in range(meeting_members_number)]
