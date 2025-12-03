from datetime import date

import pytest

from alinka.utils import extract_date_of_birth_from_pesel, is_valid_pesel


class TestValidatePesel:
    @pytest.mark.parametrize(
        "pesel",
        [
            "44051401359",
            "07290423766",
            "02070803628",
        ],
    )
    def test_validate_pesel__valid_pesel(self, pesel):
        assert is_valid_pesel(pesel)

    @pytest.mark.parametrize(
        "pesel",
        [
            "44051401358",  # Invalid checksum
            "1234567890",  # Too short
            "83010412345",
            "99022912345",
            "88888888888",  # Invalid date
            "abcdefghijk",  # Non-digit characters
            "123456789012",  # Too long
            "",  # Empty string
        ],
    )
    def test_validate_pesel__invalid_pesel(self, pesel):
        assert not is_valid_pesel(pesel)


class TestPeselToDateOfBirth:
    @pytest.mark.parametrize(
        "pesel, expected_date",
        [
            ("40301362951", date(2040, 10, 13)),
            ("39251058614", date(2039, 5, 10)),
            ("14230216474", date(2014, 3, 2)),
            ("39280845434", date(2039, 8, 8)),
            ("09321992876", date(2009, 12, 19)),
            ("05212294647", date(2005, 1, 22)),
        ],
    )
    def test_extract_date_of_birth_from_pesel__success(self, pesel, expected_date):
        assert is_valid_pesel(pesel)
        assert extract_date_of_birth_from_pesel(pesel) == expected_date
