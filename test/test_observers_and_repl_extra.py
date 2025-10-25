import builtins
import importlib
import sys
from datetime import datetime, timezone

import pytest

from app.calculator import Calculator
from app.logger import AutoSaveObserver
from app.calculation import Calculation
from app.exceptions import PersistenceError


def test_register_unregister_and_notify_exception():
    calc = Calculator()
    # create a bad observer that raises
    class BadObserver:
        def update(self, calc_obj):
            raise RuntimeError("observer fail")

    bad = BadObserver()
    calc.register_observer(bad)
    # performing should not raise despite observer failure
    calc.clear_history()
    calc.perform("add", 1, 2)
    # cleanup
    calc.unregister_observer(bad)


def test_autosave_observer_raises_when_pandas_missing(monkeypatch):
    # Force import of pandas inside AutoSaveObserver.update to fail
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pandas":
            raise ImportError("no pandas")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    obs = AutoSaveObserver("./does_not_matter.csv")
    with pytest.raises(PersistenceError):
        obs.update(Calculation("add", (1, 2), 3, datetime.now(timezone.utc)))


def test_repl_many_commands(monkeypatch, tmp_path, capsys):
    # redirect history file to temp
    hist_file = tmp_path / "history.csv"
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(hist_file))

    import app.calculator_repl as repl_mod
    importlib.reload(repl_mod)

    inputs = iter([
        "help",
        "unknowncmd",
        "add 1",            # wrong args
        "divide 1 0",      # operation error
        "undo",            # nothing to undo
        "redo",            # nothing to redo
        "clear",
        "save",
        "load",
        "exit",
    ])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)

    # run repl
    repl_mod.calculator_repl()
    out = capsys.readouterr().out
    assert "Available Commands" in out or "help" in out
    assert "Unknown command" in out
    assert "Operation requires two operands" in out
    assert "Error:" in out or "Nothing to undo" in out