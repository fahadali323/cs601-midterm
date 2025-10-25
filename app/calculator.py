# app/calculator.py
from datetime import datetime, timezone
from typing import List, Optional
import os
import math
from .calculation import Calculation
from .operations import OperationFactory
from .history import HistoryManager
from .calculator_memento import Caretaker
from .logger import LoggingObserver, AutoSaveObserver, Observer
from .calculator_config import CalculatorConfig
from .exceptions import OperationError, PersistenceError

cfg = CalculatorConfig()


class Calculator:
    def __init__(self, config: CalculatorConfig | None = None):
        self.config = config or cfg
        self.config.ensure_dirs()

        self.history_manager = HistoryManager(max_size=self.config.max_history_size)
        self._observers: List[Observer] = []
        self._caretaker = Caretaker()

        # default observers
        self.register_observer(LoggingObserver())
        if self.config.auto_save:
            self.register_observer(AutoSaveObserver(self.config.history_file))

        # save initial empty state for undo semantics
        self._caretaker.save(self.history_manager.list())

    # ===== Observer management =====
    def register_observer(self, observer: Observer):
        self._observers.append(observer)

    def unregister_observer(self, observer: Observer):
        self._observers.remove(observer)

    def _notify(self, calc: Calculation):
        for obs in list(self._observers):
            try:
                obs.update(calc)
            except Exception:
                # Observers should not crash the calculator; log and continue
                try:
                    import logging
                    logging.getLogger("calculator").exception("Observer failed")
                except Exception:
                    pass

    # ===== Core operation execution =====
    def perform(self, op_name: str, a, b) -> Calculation:
        op_obj = OperationFactory.create(op_name, a, b)
        result = op_obj.compute()

        # apply precision if numeric real
        if isinstance(result, (int, float)) and not (isinstance(result, bool)):
            # avoid absurd floating rounding for very large numbers
            result = round(float(result), self.config.precision)

            # handle -0.0
            if result == 0.0:
                result = 0.0

        calc = Calculation(
            operation=op_name,
            operands=(float(a), float(b)),
            result=result,
            timestamp=datetime.now(timezone.utc),
        )

        # Save prior state for undo (save snapshot before modifying)
        self._caretaker.save(self.history_manager.list())

        # append to history and notify observers
        self.history_manager.append(calc)
        self._notify(calc)

        return calc

    # ===== History / persistence =====
    def history(self) -> List[Calculation]:
        return self.history_manager.list()

    def clear_history(self):
        self.history_manager.clear()
        # save this cleared state to caretaker as an operation
        self._caretaker.save(self.history_manager.list())

    def save_history(self, path: str | None = None):
        try:
            import pandas as pd
            df = self.history_manager.to_dataframe()
            save_path = path or self.config.history_file
            df.to_csv(save_path, index=False, encoding=self.config.default_encoding)
        except Exception as e:
            raise PersistenceError(f"Failed to save history: {e}")

    def load_history(self, path: str | None = None):
        try:
            import pandas as pd
            load_path = path or self.config.history_file
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(load_path), exist_ok=True)
            
            if not os.path.exists(load_path):
                # Create an empty history file
                df = pd.DataFrame(columns=['operation', 'operand_1', 'operand_2', 'result', 'timestamp'])
                df.to_csv(load_path, index=False, encoding=self.config.default_encoding)
                return  # nothing to load yet
                
            df = pd.read_csv(load_path, encoding=self.config.default_encoding)
            if not df.empty:  # Only load if there's actual data
                self.history_manager.load_from_dataframe(df)
                # after loading, we should clear undo/redo history and save a snapshot
                self._caretaker.clear()
                self._caretaker.save(self.history_manager.list())
        except Exception as e:
            raise PersistenceError(f"Failed to load history: {e}")

    # ===== Undo / Redo using caretaker =====
    def can_undo(self) -> bool:
        return self._caretaker.can_undo()

    def can_redo(self) -> bool:
        return self._caretaker.can_redo()

    def undo(self) -> Optional[List[Calculation]]:
        # capture current snapshot to detect no-op undos
        current_snapshot = self.history_manager.list()
        prev_snapshot = self._caretaker.undo(current_snapshot)
        if prev_snapshot is None:
            return None
        # if undo would not change state, treat as no-op
        if prev_snapshot == current_snapshot:
            return None
        # restore
        self.history_manager._history = prev_snapshot
        return self.history_manager.list()

    def redo(self) -> Optional[List[Calculation]]:
        current_snapshot = self.history_manager.list()
        redo_snapshot = self._caretaker.redo(current_snapshot)
        if redo_snapshot is None:
            return None
        if redo_snapshot == current_snapshot:
            return None
        self.history_manager._history = redo_snapshot
        return self.history_manager.list()


# CLI / REPL helper (lightweight)
def repl():
    import sys

    calc = Calculator()
    print("Advanced Calculator REPL. Type 'help' for commands. 'exit' to quit.")

    def show_help():
        print(
            """
Commands:
    add a b           subtract a b       multiply a b
    divide a b        power a b          root a b
    modulus a b       int_divide a b     percent a b
    abs_diff a b
    history           clear              undo
    redo              save [path]        load [path]
    help              exit
"""
        )

    while True:
        try:
            raw = input("calc> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        try:
            if cmd in ("exit", "quit"):
                print("Goodbye.")
                break
            elif cmd == "help":
                show_help()
            elif cmd == "history":
                rows = calc.history()
                if not rows:
                    print("[history empty]")
                else:
                    for i, c in enumerate(rows, start=1):
                        print(f"{i}. {c.timestamp.isoformat()} | {c.operation} {c.operands} = {c.result}")
            elif cmd == "clear":
                calc.clear_history()
                print("History cleared.")
            elif cmd == "undo":
                if not calc.can_undo():
                    print("Nothing to undo.")
                else:
                    calc.undo()
                    print("Undo performed.")
            elif cmd == "redo":
                if not calc.can_redo():
                    print("Nothing to redo.")
                else:
                    calc.redo()
                    print("Redo performed.")
            elif cmd == "save":
                path = parts[1] if len(parts) > 1 else None
                calc.save_history(path)
                print("History saved.")
            elif cmd == "load":
                path = parts[1] if len(parts) > 1 else None
                calc.load_history(path)
                print("History loaded.")
            else:
                # treat as operation: requires two operands
                if len(parts) < 3:
                    print("Operation requires two operands. Type 'help' for usage.")
                    continue
                a, b = parts[1], parts[2]
                calc_obj = calc.perform(cmd, a, b)
                print(f"{calc_obj.operation}({a}, {b}) = {calc_obj.result}")
        except Exception as e:
            print(f"Error: {e}")
