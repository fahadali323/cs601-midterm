import os
import tempfile
import pytest
import pandas as pd
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, PersistenceError
from app.calculation import Calculation


@pytest.fixture
def temp_config(tmp_path):
    """Temporary CalculatorConfig for isolated testing."""
    log_dir = tmp_path / "logs"
    history_dir = tmp_path / "history"
    cfg = CalculatorConfig(
        log_dir=str(log_dir),
        history_dir=str(history_dir),
        history_file=str(history_dir / "test_history.csv"),
        auto_save=False,
        max_history_size=50,
        precision=4,
    )
    cfg.ensure_dirs()
    return cfg


@pytest.fixture
def calculator(temp_config):
    """Fixture to create a fresh Calculator instance."""
    return Calculator(config=temp_config)


# ========== BASIC OPERATION TESTS ==========

@pytest.mark.parametrize(
    "operation,a,b,expected",
    [
        ("add", 2, 3, 5),
        ("subtract", 10, 4, 6),
        ("multiply", 2, 5, 10),
        ("divide", 10, 2, 5),
        ("power", 2, 3, 8),
        ("root", 9, 2, 3),
        ("modulus", 10, 3, 1),
        ("int_divide", 9, 2, 4),
        ("percent", 25, 100, 25),  # 25/100 * 100
        ("abs_diff", 10, 3, 7),
    ],
)
def test_perform_basic_operations(calculator, operation, a, b, expected):
    calc = calculator.perform(operation, a, b)
    assert isinstance(calc, Calculation)
    assert round(float(calc.result), 4) == pytest.approx(expected, rel=1e-3)
    assert calc.operation == operation
    assert len(calculator.history()) == 1
    calculator.clear_history()


def test_divide_by_zero(calculator):
    with pytest.raises(OperationError):
        calculator.perform("divide", 10, 0)


def test_invalid_operation(calculator):
    with pytest.raises(OperationError):
        calculator.perform("unknown", 5, 2)


# ========== HISTORY & CLEARING ==========

def test_history_management(calculator):
    calculator.perform("add", 1, 1)
    calculator.perform("multiply", 2, 3)
    hist = calculator.history()
    assert len(hist) == 2

    calculator.clear_history()
    assert len(calculator.history()) == 0


# ========== UNDO / REDO ==========

def test_undo_redo(calculator):
    calculator.perform("add", 1, 1)
    calculator.perform("subtract", 5, 2)
    assert len(calculator.history()) == 2

    calculator.undo()
    assert len(calculator.history()) == 1
    calculator.redo()
    assert len(calculator.history()) == 2


def test_undo_redo_limits(calculator):
    """Undo and redo should gracefully handle empty stacks."""
    assert calculator.undo() is None
    assert calculator.redo() is None


# ========== SAVE / LOAD HISTORY ==========

def test_save_and_load_history(calculator, temp_config):
    calculator.perform("add", 2, 3)
    calculator.save_history(temp_config.history_file)
    assert os.path.exists(temp_config.history_file)

    # new calculator should load that history
    calc2 = Calculator(config=temp_config)
    calc2.load_history(temp_config.history_file)
    assert len(calc2.history()) >= 1


def test_load_creates_empty_file(temp_config):
    """Ensure load_history creates file if it doesn't exist."""
    calc = Calculator(config=temp_config)
    path = temp_config.history_dir + "/nonexistent.csv"
    calc.load_history(path)
    assert os.path.exists(path)


def test_load_malformed_csv(calculator, temp_config):
    """Corrupted CSV should raise PersistenceError."""
    bad_path = temp_config.history_file
    with open(bad_path, "w", encoding="utf-8") as f:
        f.write("bad,data,here\n1,2,3")
    with pytest.raises(PersistenceError):
        calculator.load_history(bad_path)


def test_save_failure(monkeypatch, calculator):
    """Simulate pandas failure during save."""
    def bad_to_csv(*args, **kwargs):
        raise OSError("cannot write file")
    monkeypatch.setattr("pandas.DataFrame.to_csv", bad_to_csv)
    with pytest.raises(PersistenceError):
        calculator.save_history("dummy.csv")


# ========== OBSERVERS ==========

def test_observer_registration(calculator):
    before = len(calculator._observers)
    from app.logger import LoggingObserver
    observer = LoggingObserver()
    calculator.register_observer(observer)
    assert len(calculator._observers) == before + 1
    calculator.unregister_observer(observer)
    assert len(calculator._observers) == before


def test_observer_error_does_not_crash(calculator):
    """Observer that raises should not break notifications."""
    class BadObserver:
        def update(self, calc): raise RuntimeError("fail")
    calculator.register_observer(BadObserver())
    calculator.perform("add", 1, 1)  # should not raise


# ========== EDGE CASES ==========

def test_clear_history_saves_state(calculator):
    calculator.perform("add", 2, 2)
    calculator.clear_history()
    assert calculator.can_undo()


def test_large_numbers(calculator):
    """Ensure large numbers are handled and rounded correctly."""
    c = calculator.perform("multiply", 1e10, 3.33333)
    assert isinstance(c.result, float)
    assert round(c.result, calculator.config.precision) == pytest.approx(c.result)


def test_invalid_persistence_path(calculator):
    """Invalid file path should raise PersistenceError."""
    with pytest.raises(PersistenceError):
        calculator.save_history("/invalid/path/test.csv")
