# app/calculation.py
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Tuple


@dataclass
class Calculation:
    operation: str
    operands: Tuple[float, float]
    result: Any
    timestamp: datetime

    def __str__(self) -> str:
        """Format the calculation in a readable way."""
        # Capitalize first letter of operation
        op = self.operation.capitalize()
        a, b = self.operands
        return f"{op}({a},{b}) = {self.result}"

    def to_dict(self):
        d = asdict(self)
        # make timestamp serializable (string)
        d['timestamp'] = self.timestamp.isoformat()
        d['operand_1'] = float(self.operands[0])
        d['operand_2'] = float(self.operands[1])
        # keep a clean CSV-friendly shape
        d['operation'] = self.operation
        d['result'] = self.result
        # remove operands tuple to avoid duplication
        d.pop('operands', None)
        return d
