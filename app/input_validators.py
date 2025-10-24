# app/input_validators.py
from typing import Tuple
from .exceptions import ValidationError
from .calculator_config import CalculatorConfig


cfg = CalculatorConfig()


def validate_numeric_pair(a, b) -> Tuple[float, float]:
    """
    Validate two numeric inputs and apply max input constraint.
    Return tuple of floats.
    """
    try:
        a_f = float(a)
        b_f = float(b)
    except (TypeError, ValueError):
        raise ValidationError(f"Inputs must be numeric: got {a!r}, {b!r}")

    if abs(a_f) > cfg.max_input_value or abs(b_f) > cfg.max_input_value:
        raise ValidationError(f"Inputs must be <= {cfg.max_input_value} in absolute value")

    return a_f, b_f
