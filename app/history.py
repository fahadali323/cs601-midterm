# app/history.py
from typing import List
from .calculation import Calculation
from .calculator_config import CalculatorConfig

cfg = CalculatorConfig()


class HistoryManager:
    def __init__(self, max_size: int | None = None):
        self._history: List[Calculation] = []
        self._max_size = max_size or cfg.max_history_size

    def append(self, calc: Calculation):
        self._history.append(calc)
        # enforce max size: drop oldest
        if len(self._history) > self._max_size:
            self._history = self._history[-self._max_size :]

    def clear(self):
        self._history.clear()

    def list(self):
        return list(self._history)  # return shallow copy

    def to_dataframe(self):
        # Deferred import so module doesn't require pandas unless saving happens
        import pandas as pd
        rows = [c.to_dict() for c in self._history]
        return pd.DataFrame(rows)

    def load_from_dataframe(self, df):
        # Expect df to have operation, operand_1, operand_2, result, timestamp
        from datetime import datetime
        self._history = []
        for _, row in df.iterrows():
            op = row.get("operation")
            a = float(row.get("operand_1"))
            b = float(row.get("operand_2"))
            result = row.get("result")
            ts_raw = row.get("timestamp")
            ts = datetime.fromisoformat(ts_raw) if isinstance(ts_raw, str) else ts_raw
            self._history.append(Calculation(operation=op, operands=(a, b), result=result, timestamp=ts))

    def size(self):
        return len(self._history)
