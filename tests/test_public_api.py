"""Integration tests for the public API functions."""

from tracking_numbers import get_definition
from tracking_numbers import get_tracking_number
from tracking_numbers import possible_tracking_number

# Known valid tracking numbers from courier specs
VALID_USPS = "9405511108078863434863"
VALID_FEDEX = "9611020987654312345672"
VALID_UPS = "1Z8V92A70367203024"


class TestGetTrackingNumber:
    def test_returns_match_for_valid_number(self):
        result = get_tracking_number(VALID_USPS)
        assert result is not None
        assert result.number == VALID_USPS
        assert result.valid

    def test_returns_none_for_invalid_number(self):
        result = get_tracking_number("NOTAVALIDNUMBER123")
        assert result is None

    def test_returns_none_for_empty_string(self):
        result = get_tracking_number("")
        assert result is None

    def test_returns_correct_courier(self):
        result = get_tracking_number(VALID_UPS)
        assert result is not None
        assert result.courier.code == "ups"

    def test_validate_false_returns_invalid_matches(self):
        # Use a number that matches the format but fails checksum
        result = get_tracking_number("1Z1111111111111111", validate=False)
        assert result is not None
        assert not result.valid

    def test_validate_true_rejects_invalid_checksum(self):
        result = get_tracking_number("1Z1111111111111111", validate=True)
        assert result is None

    def test_tracking_url_populated(self):
        result = get_tracking_number(VALID_UPS)
        assert result is not None
        assert result.tracking_url is not None
        assert VALID_UPS in result.tracking_url

    def test_serial_number_populated(self):
        result = get_tracking_number(VALID_USPS)
        assert result is not None
        assert result.serial_number is not None
        assert len(result.serial_number) > 0


class TestPossibleTrackingNumber:
    def test_returns_list(self):
        result = possible_tracking_number(VALID_USPS)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_returns_empty_for_invalid(self):
        result = possible_tracking_number("NOTAVALIDNUMBER123")
        assert result == []

    def test_returns_empty_for_empty_string(self):
        result = possible_tracking_number("")
        assert result == []

    def test_includes_both_valid_and_invalid_matches(self):
        result = possible_tracking_number(VALID_USPS)
        # Should include at least the valid match
        valid_matches = [tn for tn in result if tn.valid]
        assert len(valid_matches) >= 1


class TestGetDefinition:
    def test_returns_definition_for_known_product(self):
        result = get_definition("UPS")
        assert result is not None
        assert result.product.name.lower() == "ups"

    def test_returns_none_for_unknown_product(self):
        result = get_definition("NonexistentCourier123")
        assert result is None

    def test_case_insensitive_lookup(self):
        upper = get_definition("UPS")
        lower = get_definition("ups")
        mixed = get_definition("Ups")
        assert upper is not None
        assert upper is lower
        assert upper is mixed

    def test_returned_definition_can_parse(self):
        definition = get_definition("UPS")
        assert definition is not None
        result = definition.test(VALID_UPS)
        assert result is not None
        assert result.valid
