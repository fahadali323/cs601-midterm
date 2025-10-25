import pytest
from app.input_validators import validate_numeric_pair
from app.exceptions import ValidationError


def test_validate_numeric_pair_non_numeric():
    with pytest.raises(ValidationError):
        validate_numeric_pair("a", "b")


def test_validate_numeric_pair_too_large():
    # use a value larger than config.max_input_value
    # The default max_input_value is extremely large, so use scientific
    large = 1e309
    with pytest.raises(ValidationError):
        validate_numeric_pair(large, 1)
