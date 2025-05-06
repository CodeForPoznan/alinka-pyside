from datetime import date

import pytest
from pydantic import ValidationError

from alinka.constants import Reason
from alinka.schemas import AddressData, DocumentData
from tests.fixtures import applicants_data, child_data, school_data, support_center_data


class TestAddressData:
    @pytest.mark.parametrize(
        "entity_with_address", [child_data, support_center_data, applicants_data[0], applicants_data[1], school_data]
    )
    def test_address_data_full_address(self, entity_with_address):
        address_data = entity_with_address.copy()
        expected_address = f"{address_data['address']}, {address_data['postal_code']} {address_data['town']}"

        address = AddressData(**address_data)

        assert address.full_address == expected_address


class TestChildDateOfBirth:
    @pytest.mark.parametrize(
        "pesel, date_of_birth",
        [
            ("12121244441", date(1912, 12, 12)),
            ("12120244441", date(1912, 12, 2)),
            ("12220244441", date(2012, 2, 2)),
            ("12320244441", date(2012, 12, 2)),
        ],
    )
    def test_calculate_date_of_birth_from_pesel(self, pesel, date_of_birth, common_data_fixture):
        common_data_fixture["child"]["pesel"] = pesel
        common_data_fixture["child"]["birth_date"] = None
        document_data = DocumentData(**common_data_fixture)
        assert document_data.child.birth_date == date_of_birth

    def test_child_date_of_birth_dont_calculate_if_exists(self, common_data_fixture):
        expected_birth_date = date(1999, 1, 1)
        common_data_fixture["child"]["pesel"] = "12320244441"
        common_data_fixture["child"]["birth_date"] = expected_birth_date
        document_data = DocumentData(**common_data_fixture)
        assert document_data.child.birth_date == expected_birth_date

    def test_child_date_of_birth_calculate_if_theres_no_birth_of_date(self, common_data_fixture):
        expected_birth_date = date(2012, 12, 2)
        common_data_fixture["child"]["pesel"] = "12320244441"
        del common_data_fixture["child"]["birth_date"]
        document_data = DocumentData(**common_data_fixture)
        assert document_data.child.birth_date == expected_birth_date


class TestParentDescription:
    @pytest.mark.parametrize("address_first_parent_checkbox", [True])
    def test_parent_description_one_parent_different_flats(self, address_first_parent_checkbox, common_data_fixture):
        del common_data_fixture["applicants"][-1]
        applicants = common_data_fixture["applicants"]
        expected_description = (
            f"{applicants[0]['full_name']}, "
            f"{applicants[0]['address']}, {applicants[0]['postal_code']} {applicants[0]['town']}"
        )
        common_data_fixture["address_child_checkbox"] = False
        common_data_fixture["address_first_parent_checkbox"] = address_first_parent_checkbox

        document_data = DocumentData(**common_data_fixture)

        assert document_data.parent_descriptions == expected_description

    @pytest.mark.parametrize("address_first_parent_checkbox", [True, False])
    def test_parent_description_one_parent_same_flat(self, address_first_parent_checkbox, common_data_fixture):
        del common_data_fixture["applicants"][-1]
        applicants = common_data_fixture["applicants"]
        child = common_data_fixture["child"]
        expected_description = (
            f"{applicants[0]['full_name']}, " f"{child['address']}, {child['postal_code']} {child['town']}"
        )
        common_data_fixture["address_child_checkbox"] = True
        common_data_fixture["address_first_parent_checkbox"] = address_first_parent_checkbox

        document_data = DocumentData(**common_data_fixture)

        assert document_data.parent_descriptions == expected_description

    @pytest.mark.parametrize("address_first_parent_checkbox", [True, False])
    def test_parent_description_two_parents_same_flat_as_child(
        self, address_first_parent_checkbox, common_data_fixture
    ):
        applicants = common_data_fixture["applicants"]
        child = common_data_fixture["child"]
        expected_description = (
            f"{applicants[0]['full_name']} i "
            f"{applicants[1]['full_name']}, "
            f"{child['address']}, {child['postal_code']} {child['town']}"
        )
        common_data_fixture["address_child_checkbox"] = True
        common_data_fixture["address_first_parent_checkbox"] = address_first_parent_checkbox

        document_data = DocumentData(**common_data_fixture)

        assert document_data.parent_descriptions == expected_description

    def test_parent_description_two_parents_diffrent_flat_as_child(self, common_data_fixture):
        applicants = common_data_fixture["applicants"]
        expected_description = (
            f"{applicants[0]['full_name']} i "
            f"{applicants[1]['full_name']}, "
            f"{applicants[0]['address']}, {applicants[0]['postal_code']} {applicants[0]['town']}"
        )
        common_data_fixture["address_child_checkbox"] = False
        common_data_fixture["address_first_parent_checkbox"] = True

        document_data = DocumentData(**common_data_fixture)

        assert document_data.parent_descriptions == expected_description

    def test_parent_description_two_parents_each_different_flat(self, common_data_fixture):
        applicants = common_data_fixture["applicants"]
        expected_description = (
            f"{applicants[0]['full_name']}, "
            f"{applicants[0]['address']}, {applicants[0]['postal_code']} {applicants[0]['town']}, "
            f"{applicants[1]['full_name']}, "
            f"{applicants[1]['address']}, {applicants[1]['postal_code']} {applicants[1]['town']}"
        )
        common_data_fixture["address_child_checkbox"] = False
        common_data_fixture["address_first_parent_checkbox"] = False

        document_data = DocumentData(**common_data_fixture)

        assert document_data.parent_descriptions == expected_description


class TestMultipleDisabilityCheck:
    @pytest.mark.parametrize(
        "_, reasons, exception_message",
        [
            (
                "uniemozliwiajacy and utrudniajacy together",
                [Reason.UNIEMOZLIWIAJACY, Reason.ZNACZNIE_UTRUDNIAJACY],
                f"Value error, Reasons: {Reason.UNIEMOZLIWIAJACY.value}, {Reason.ZNACZNIE_UTRUDNIAJACY.value} "
                "can't be issued together.",
            ),
            (
                "two intellectual reasons together",
                [Reason.SLABOSLYSZACE, Reason.UMIARKOWANE, Reason.LEKKIE],
                f"Value error, Two intellectual reasons: {Reason.UMIARKOWANE.value}, {Reason.LEKKIE.value} "
                "can't be issued together.",
            ),
            (
                "profound disability coupled with other reasons",
                [Reason.GLEBOKIE, Reason.RUCHOWA],
                "Value error, Profound intellectual disability can't be coupled.",
            ),
            (
                "social maladjustment coupled with other reasons.",
                [Reason.ZAGROZENIE_NIEDOSTOSOWANIEM, Reason.LEKKIE],
                "Value error, Social maladjustment reasons can't be coupled with any other reason.",
            ),
        ],
    )
    def test_multiple_disabilities_check(self, _, reasons, exception_message, common_data_fixture):
        common_data_fixture["reasons"] = reasons
        with pytest.raises(ValidationError) as exception:
            DocumentData(**common_data_fixture)
        assert exception.value.errors()[0]["msg"] == exception_message


class TestMultipleDisabilityDescription:
    @pytest.mark.parametrize(
        "reasons, expected_description",
        [
            (
                [Reason.LEKKIE, Reason.RUCHOWA],
                "niepełnosprawność intelektualna w stopniu lekkim, niepełnosprawność ruchowa",
            ),
            (
                [Reason.LEKKIE, Reason.AUTYZM, Reason.RUCHOWA],
                "niepełnosprawność intelektualna w stopniu lekkim, autyzm, niepełnosprawność ruchowa",
            ),
        ],
    )
    def test_multiple_disabilities_description(self, reasons, expected_description, common_data_fixture):
        common_data_fixture["reasons"] = reasons
        document_data = DocumentData(**common_data_fixture)
        assert document_data.multiple_disabilities_nominative == expected_description
