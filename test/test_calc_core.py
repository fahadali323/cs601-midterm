import os
from datetime import datetime, timezone
import pytest

from app.calculator import Calculator
from app.calculation import Calculation
from app.exceptions import OperationError


def test_perform_and_history_and_str():
    calc = Calculator()
    # ensure clean start
    calc.clear_history()
    assert calc.history() == []

    res = calc.perform("add", 2, 3)
    assert isinstance(res, Calculation)
    assert res.result == 5.0

    history = calc.history()
    assert len(history) == 1
    # __str__ formatting
    assert str(history[0]).startswith("Add(")


def test_undo_and_redo():
    calc = Calculator()
    calc.clear_history()
    calc.perform("add", 1, 1)
    calc.perform("multiply", 2, 2)
    assert len(calc.history()) == 2

    # Undo should restore previous state (1 entry)
    calc.undo()
    assert len(calc.history()) == 1

    # Redo should restore to 2 entries
    calc.redo()
    assert len(calc.history()) == 2


def test_operation_errors():
    calc = Calculator()
    with pytest.raises(OperationError):
        calc.perform("divide", 1, 0)
