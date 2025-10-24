# app/calculator_memento.py
from dataclasses import dataclass
from typing import List
from .calculation import Calculation
import copy


@dataclass
class Memento:
    history_snapshot: List[Calculation]


class Caretaker:
    """
    Manages undo/redo stacks using saved snapshots of history.
    Stores deep copies to preserve immutability of snapshots.
    """
    def __init__(self):
        self._undo_stack: list[Memento] = []
        self._redo_stack: list[Memento] = []

    def save(self, history_snapshot: list[Calculation]):
        """Push a snapshot; clear the redo stack."""
        self._undo_stack.append(Memento(copy.deepcopy(history_snapshot)))
        self._redo_stack.clear()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self, current_snapshot: list[Calculation]):
        """
        Move top of undo stack to redo stack and return previous snapshot.
        The caller should set its history to the returned snapshot.
        """
        if not self.can_undo():
            return None
        top = self._undo_stack.pop()
        # push current to redo (so redo can restore it)
        self._redo_stack.append(Memento(copy.deepcopy(current_snapshot)))
        return top.history_snapshot

    def redo(self, current_snapshot: list[Calculation]):
        if not self.can_redo():
            return None
        top = self._redo_stack.pop()
        # push current to undo so we can undo the redo
        self._undo_stack.append(Memento(copy.deepcopy(current_snapshot)))
        return top.history_snapshot

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
