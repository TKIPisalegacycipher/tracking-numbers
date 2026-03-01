import pytest

from tracking_numbers import get_tracking_number
from tracking_numbers import possible_tracking_number


def test_usps_not_confused_for_dhl():
    """Tests that a USPS number is not mistakenly considered to be DHL. This occurs
    if we don't do a full match on the regex, since DHL numbers are syntactically
    short USPS numbers (for the most part).
    """
    tracking_number = get_tracking_number("9405511108078863434863")

    assert tracking_number is not None
    assert tracking_number.courier.code == "usps"


class TestEmptyAndBoundaryInputs:
    def test_empty_string(self):
        assert get_tracking_number("") is None

    def test_single_character(self):
        assert get_tracking_number("A") is None

    def test_whitespace_only(self):
        assert get_tracking_number("   ") is None

    def test_very_long_string(self):
        assert get_tracking_number("1" * 500) is None

    def test_possible_empty_string(self):
        assert possible_tracking_number("") == []


class TestSpecialCharacterInputs:
    def test_unicode_characters(self):
        assert get_tracking_number("\u00e9\u00e8\u00ea\u00eb") is None

    def test_newlines_and_tabs(self):
        assert get_tracking_number("\n\t\r") is None

    def test_special_regex_characters(self):
        assert get_tracking_number(".*+?[](){}|\\^$") is None

    def test_numeric_only_short(self):
        assert get_tracking_number("12345") is None


class TestWhitespaceHandling:
    def test_internal_spaces_in_ups(self):
        result = get_tracking_number(" 1 Z 8 V 9 2 A 7 0 3 6 7 2 0 3 0 2 4 ")
        assert result is not None
        assert result.courier.code == "ups"


class TestValidateParameter:
    @pytest.mark.parametrize(
        "number",
        [
            "1Z1111111111111111",  # UPS format, bad checksum
            "0307 1790 0005 2348 3742",  # USPS 20, bad checksum
        ],
    )
    def test_validate_false_returns_match(self, number):
        assert get_tracking_number(number, validate=False) is not None

    @pytest.mark.parametrize(
        "number",
        [
            "1Z1111111111111111",
            "0307 1790 0005 2348 3742",
        ],
    )
    def test_validate_true_rejects(self, number):
        assert get_tracking_number(number, validate=True) is None
