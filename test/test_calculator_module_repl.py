import importlib
import os
import sys
from datetime import datetime, timezone

import pytest


def test_calc_repl_basic_flow(monkeypatch, tmp_path, capsys):
    # redirect calculator config to temp dirs
    hist_file = tmp_path / "history.csv"
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(hist_file))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))

    # reload module so Calculator picks up env vars
    import app.calculator as calc_mod
    importlib.reload(calc_mod)

    inputs = iter([
        "",                # empty input -> ignored
        "help",
        "history",        # empty history
        "add 1",          # invalid args
        "add 2 3",        # valid op
        "history",        # now has entry
        "undo",           # should undo
        "redo",           # redo
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

    # run repl (will exit normally)
    calc_mod.repl()

    out = capsys.readouterr().out
    assert "Advanced Calculator REPL" in out
    assert "Available Commands" in out or "help" in out
    assert "Operation requires two operands" in out
    assert "History cleared." in out or "History" in out or "Undo performed." in out


def test_calc_repl_keyboard_interrupt(monkeypatch):
    import app.calculator as calc_mod
    importlib.reload(calc_mod)

    def raise_keyboard(prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_keyboard)

    with pytest.raises(SystemExit):
        calc_mod.repl()


def test_init_registers_autosave_and_logging(tmp_path, monkeypatch):
    # ensure auto_save True
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "true")
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(tmp_path / "history.csv"))
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path))

    import importlib
    import app.calculator as calc_mod
    importlib.reload(calc_mod)

    calc = calc_mod.Calculator()
    # should have at least LoggingObserver and AutoSaveObserver registered
    types = [type(obs).__name__ for obs in calc._observers]
    assert "LoggingObserver" in types
    assert "AutoSaveObserver" in types
