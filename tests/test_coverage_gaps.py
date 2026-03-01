"""Tests targeting previously uncovered code paths."""

import pytest

from tracking_numbers.checksum_validator import ChecksumValidator
from tracking_numbers.checksum_validator import Mod_37_36
from tracking_numbers.checksum_validator import S10
from tracking_numbers.definition import TrackingNumberDefinition
from tracking_numbers.serial_number import DefaultSerialNumberParser
from tracking_numbers.types import Courier
from tracking_numbers.types import TrackingNumber
from tracking_numbers.value_matcher import ValueMatcher


class TestChecksumValidatorEdgeCases:
    def test_passes_returns_false_for_non_numeric_check_digit(self):
        """Covers checksum_validator.py lines 37-38: except (ValueError, TypeError)."""
        validator = S10()
        # "XY" can't be converted to int, so passes() should catch and return False
        assert validator.passes(list("12345678"), "XY") is False

    def test_from_spec_raises_for_unknown_strategy(self):
        """Covers checksum_validator.py line 72: raise ValueError."""
        with pytest.raises(ValueError, match="Unknown checksum"):
            ChecksumValidator.from_spec({"checksum": {"name": "nonexistent"}})


class TestS10BranchCoverage:
    def test_remainder_equals_1_returns_0(self):
        """Covers checksum_validator.py line 88: remainder==1 -> return 0."""
        validator = S10()
        # Serial "00000008": total=56, 56%11=1
        assert validator._check_digit(list("00000008")) == 0

    def test_remainder_equals_0_returns_5(self):
        """Covers checksum_validator.py line 91: remainder==0 -> return 5."""
        validator = S10()
        # Serial "00000000": total=0, 0%11=0
        assert validator._check_digit(list("00000000")) == 5


class TestMod3736BranchCoverage:
    def test_check_digit_less_than_10_returns_string(self):
        """Covers checksum_validator.py line 161: cd<10 -> return str(cd)."""
        validator = Mod_37_36()
        result = validator._check_digit(list("0"))
        assert result == "2"
        assert result.isdigit()

    def test_check_digit_equals_mod_returns_zero(self):
        """Covers checksum_validator.py line 153: cd==MOD -> cd=0."""
        validator = Mod_37_36()
        result = validator._check_digit(list("J"))
        assert result == "0"

    def test_invalid_check_digit_raises(self):
        """Covers checksum_validator.py line 156: cd out of range."""
        validator = Mod_37_36()
        # Override MOD to force an invalid state
        original_mod = validator.MOD
        validator.MOD = 0  # Forces cd = 1 - cd which will be out of [0, MOD)
        with pytest.raises(ValueError, match="Invalid calculated check digit"):
            validator._check_digit(list("1"))
        validator.MOD = original_mod


class TestDefinitionEdgeCases:
    def _make_definition(self, **kwargs):
        """Helper to create a minimal TrackingNumberDefinition."""
        defaults = dict(
            courier=Courier(code="test", name="Test"),
            product=kwargs.pop(
                "product",
                __import__("tracking_numbers.types", fromlist=["Product"]).Product(
                    name="Test"
                ),
            ),
            number_regex=kwargs.pop(
                "number_regex", __import__("re").compile(r"(?P<All>\d+)")
            ),
            tracking_url_template=None,
            serial_number_parser=DefaultSerialNumberParser(),
            additional=[],
            additional_validator=None,
            checksum_validator=None,
        )
        defaults.update(kwargs)
        return TrackingNumberDefinition(**defaults)

    def test_no_serial_number_in_match(self):
        """Covers definition.py line 199: _get_serial_number returns None."""
        import re
        from tracking_numbers.types import Product

        defn = self._make_definition(
            product=Product(name="NoSerial"),
            number_regex=re.compile(r"(?P<All>\d+)"),
        )
        result = defn.test("12345")
        assert result is not None
        assert result.serial_number is None

    def test_checksum_error_no_serial_number(self):
        """Covers definition.py line 225: checksum error when no SerialNumber."""
        import re
        from tracking_numbers.types import Product

        defn = self._make_definition(
            product=Product(name="NoSerial"),
            number_regex=re.compile(r"(?P<All>\d+)"),
            checksum_validator=S10(),
        )
        result = defn.test("12345")
        assert result is not None
        assert ("checksum", "SerialNumber not found") in result.validation_errors

    def test_checksum_error_no_check_digit(self):
        """Covers definition.py line 229: checksum error when no CheckDigit."""
        import re
        from tracking_numbers.types import Product

        defn = self._make_definition(
            product=Product(name="NoCheckDigit"),
            number_regex=re.compile(r"(?P<All>(?P<SerialNumber>\d+))"),
            checksum_validator=S10(),
        )
        result = defn.test("12345678")
        assert result is not None
        assert ("checksum", "CheckDigit not found") in result.validation_errors

    def test_additional_group_key_not_in_match(self):
        """Covers definition.py line 250: _get_additional returns None when group missing."""
        import re
        from tracking_numbers.definition import Additional
        from tracking_numbers.types import Product
        from tracking_numbers.value_matcher import ExactValueMatcher

        defn = self._make_definition(
            product=Product(name="Test"),
            number_regex=re.compile(r"(?P<All>\d+)"),
            additional=[
                Additional(
                    name="MissingGroup",
                    regex_group_name="NonExistentGroup",
                    value_matchers=[(ExactValueMatcher("x"), {"name": "test"})],
                ),
            ],
        )
        result = defn.test("12345")
        assert result is not None
        assert "MissingGroup" not in result.additional


class TestSerialNumberParserEdgeCases:
    def test_from_spec_with_format_but_no_prepend_if(self):
        """Covers serial_number.py line 56: serial_number_format without prepend_if."""
        parser = DefaultSerialNumberParser.from_spec(
            {"serial_number_format": {"some_other_key": "value"}},
        )
        assert isinstance(parser, DefaultSerialNumberParser)
        assert parser.prepend_if is None


class TestCourierInfoWithNoneValues:
    def test_courier_info_skips_none_values(self):
        """Covers types.py line 59: v is None -> continue."""
        tn = TrackingNumber(
            number="TEST123",
            courier=Courier(code="test", name="Test Courier"),
            product=__import__("tracking_numbers.types", fromlist=["Product"]).Product(
                name="Test"
            ),
            serial_number=None,
            tracking_url=None,
            match_data={},
            additional={"Courier": {"country": None, "region": "US"}},
            validation_errors=[],
        )
        info = tn.courier_info
        assert "country" not in info
        assert info["region"] == "US"


class TestValueMatcherEdgeCases:
    def test_from_spec_raises_for_invalid_spec(self):
        """Covers value_matcher.py line 26: raise ValueError."""
        with pytest.raises(ValueError, match="Invalid matcher spec"):
            ValueMatcher.from_spec({"invalid_key": "value"})
