from datetime import datetime, timezone
from app.calculator_memento import Caretaker
from app.calculation import Calculation


def make_calc_list():
    return [Calculation("add", (1, 2), 3, datetime.now(timezone.utc))]


def test_memento_undo_redo():
    caretaker = Caretaker()
    h1 = make_calc_list()
    caretaker.save(h1)
    assert caretaker.can_undo()
    new_snapshot = [Calculation("subtract", (3, 2), 1, datetime.now(timezone.utc))]
    undo_snapshot = caretaker.undo(new_snapshot)
    assert isinstance(undo_snapshot, list)
    redo_snapshot = caretaker.redo(h1)
    assert isinstance(redo_snapshot, list)
