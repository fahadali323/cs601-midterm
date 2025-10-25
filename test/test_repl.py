import importlib
import os
from datetime import datetime, timezone


def test_repl_quick_flow(monkeypatch, tmp_path, capsys):
    # Redirect default history file to tmp_path to avoid filesystem pollution
    hist_file = tmp_path / "history.csv"
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(hist_file))

    # Now import (or reload) the repl module so config picks up env var
    import app.calculator_repl as repl_mod
    importlib.reload(repl_mod)

    inputs = iter([
        "add 2 3",
        "history",
        "exit",
    ])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)

    # Run the REPL; it should exit after our inputs
    repl_mod.calculator_repl()

    captured = capsys.readouterr()
    assert "Welcome to the Advanced Calculator" in captured.out
    assert "Result" in captured.out or "Calculation History" in captured.out
