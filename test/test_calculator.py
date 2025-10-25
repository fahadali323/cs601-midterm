import pytest
from app.calculator import Calculator
from app.exceptions import OperationError


@pytest.fixture
def calc():
    return Calculator()


def test_perform_basic(calc):
    result = calc.perform("add", 3, 2)
    assert result.result == 5


def test_perform_invalid(calc):
    with pytest.raises(OperationError):
        calc.perform("fake_op", 2, 2)


def test_history_and_clear(calc):
    calc.perform("multiply", 2, 3)
    assert len(calc.history()) >= 1
    calc.clear_history()
    assert len(calc.history()) == 0


def test_undo_redo(calc):
    calc.perform("add", 1, 2)
    calc.perform("multiply", 3, 3)
    assert calc.can_undo()
    calc.undo()
    assert calc.can_redo()
    calc.redo()


def test_save_and_load(tmp_path):
    calc = Calculator()
    calc.perform("add", 1, 1)
    path = tmp_path / "history.csv"
    calc.save_history(str(path))
    assert path.exists()
    calc.clear_history()
    calc.load_history(str(path))
    assert len(calc.history()) > 0
