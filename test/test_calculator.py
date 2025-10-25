import io
import builtins
import pytest
from app import calculator_repl


@pytest.fixture
def mock_calculator(monkeypatch):
    """Mock Calculator to avoid touching actual filesystem."""
    class MockCalculator:
        def __init__(self):
            self._history = []
            self._undone = []

        def load_history(self, path=None): pass
        def save_history(self, path=None): pass
        def history(self): return self._history
        def clear_history(self): self._history.clear()
        def can_undo(self): return bool(self._history)
        def undo(self): 
            if self._history:
                self._undone.append(self._history.pop())
        def can_redo(self): return bool(self._undone)
        def redo(self): 
            if self._undone:
                self._history.append(self._undone.pop())
        def perform(self, command, a, b):
            result = {"add": a+b, "subtract": a-b, "multiply": a*b}.get(command, 0)
            record = f"{command}({a}, {b}) = {result}"
            self._history.append(record)
            return type("CalcResult", (), {"result": result})()

    monkeypatch.setattr(calculator_repl, "Calculator", MockCalculator)
    return MockCalculator


def run_repl_with_input(monkeypatch, capsys, inputs):
    """Helper to simulate user input to the REPL."""
    inputs_iter = iter(inputs)
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs_iter))
    calculator_repl.calculator_repl()
    captured = capsys.readouterr()
    return captured.out


def test_help_and_exit(monkeypatch, capsys, mock_calculator):
    """Test help command and graceful exit."""
    output = run_repl_with_input(monkeypatch, capsys, ["help", "exit"])
    assert "Available Commands" in output
    assert "Goodbye!" in output


def test_add_command(monkeypatch, capsys, mock_calculator):
    """Test an arithmetic operation with color output."""
    output = run_repl_with_input(monkeypatch, capsys, ["add 2 3", "exit"])
    assert "Result:" in output
    assert "5" in output  # Result should be printed


def test_history_and_clear(monkeypatch, capsys, mock_calculator):
    """Test history and clear operations."""
    output = run_repl_with_input(monkeypatch, capsys, [
        "add 1 2",
        "history",
        "clear",
        "history",
        "exit"
    ])
    assert "Calculation History" in output
    assert "History cleared" in output
    assert "No calculations yet" in output


def test_undo_and_redo(monkeypatch, capsys, mock_calculator):
    """Test undo/redo functionality."""
    output = run_repl_with_input(monkeypatch, capsys, [
        "add 1 1",
        "undo",
        "redo",
        "exit"
    ])
    assert "Undo successful" in output or "Redo successful" in output


def test_invalid_command(monkeypatch, capsys, mock_calculator):
    """Test unknown command handling."""
    output = run_repl_with_input(monkeypatch, capsys, ["foobar", "exit"])
    assert "Unknown command" in output


def test_invalid_operands(monkeypatch, capsys, mock_calculator):
    """Test missing operands error."""
    output = run_repl_with_input(monkeypatch, capsys, ["add 5", "exit"])
    assert "Error" in output
