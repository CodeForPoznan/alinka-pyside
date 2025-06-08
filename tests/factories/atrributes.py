from factory.fuzzy import BaseFuzzyAttribute
from factory.fuzzy import random as factory_random
from faker import Faker

faker = Faker(locale="pl_PL")


def full_name_genitive(nominative):
    """
    We would like to create some simple logic here to swich grammatical case.
    """
    return nominative


class NoPrefixFullName(BaseFuzzyAttribute):
    """
    We want to avoid prefix in default facotry.faker("name")
    so to not get "pan Tomasz M."
    """

    def fuzz(self):
        return f"{faker.first_name()} {faker.last_name()}"


class FuzzySupportCenterNameGenitive(BaseFuzzyAttribute):
    def fuzz(self):
        prefix = ["Powiatowej", "Miejskiej", "Specjalistycznej"]
        support_center_name = "Poradni Psychologiczno - Pedagogicznej"
        return f"{factory_random.randgen.choice(prefix)} {support_center_name} w {faker.city()}"


class FuzzySupportCenterKurator(BaseFuzzyAttribute):
    def fuzz(self):
        city_genitive = [
            "Poznaniu",
            "Warszawie",
            "Szczecinie",
            "Bydgoszczy",
            "Gdańsku",
            "Gorzowie Wlkp.",
            "Białej Podlaskiej",
        ]
        return (
            f"{factory_random.randgen.choice(city_genitive)}, {faker.street_address()},"
            f" {faker.postcode()} {faker.city()}"
        )
