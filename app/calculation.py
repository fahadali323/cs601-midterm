# app/calculation.py

from dataclasses import dataclass, field
import datetime
from decimal import Decimal, InvalidOperation, DivisionByZero
import logging
from typing import Any, Dict

from app.exceptions import OperationError

@dataclass
class Calculation:
    """
    Value Object represents a single calculation.
    """
    #Required fields
    operation: str     #name of the operation
    operand1: Decimal  #first operand in the calculation
    operand2: Decimal  #second operand in the calculation

    #Fields with default values
    result = Decimal = field(init=False)
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __post__init__(self):
        """Calculates the result when the object is created."""
        self.result = self.calculate()

    def calculate(self) -> Decimal:
        """
        Performs calculation based on the operation name.
        Returns: Decimal result.
        Raises: OperationError if operation is invalid or fails.
        """

        ops = {
            "add": lambda x, y: x+y,
            "subtract": lambda x, y: x-y,
            "multiply": lambda x, y: x*y,
            "division": lambda x, y: x/y if y!=0 else self.raise_div_zero(),
            "power": lambda x, y: Decimal(pow(float(x), float(y))),
            "root": lambda x, y: Decimal(pow(float(x), 1/float(y))) if y!=0 else self.raise_invalid_root(x,y),
            "modulus": lambda x, y: x % y if y!=0 else self.raise_div_zero(),
            "int_divide": lambda x, y: (x // y) if y!=0 else self.raise_div_zero(),
            "percent": lambda x, y: (x/y *100) if y !=0  else self.raise_div_zero(),
            "abs_diff": lambda x, y: abs(x-y),
        }

        op_func = ops.get(self.operation.lower())
        if not op_func:
            raise OperationError(f"Unknown operation: {self.operation}")
        try:
            return Decimal(op_func(self.operand1, self.operand2))
        except (InvalidOperation, ValueError, ArithmeticError, DivisionByZero) as e:
            raise OperationError(f"Calculation failed: {e}")

    #Error Helpers
    @staticmethod
    def _raise_div_zero(): 
        raise OperationError("Divsion by zero is not allowed")
    
    @staticmethod
    def _raise_invalid_root(x: Decimal, y:Decimal):
        if y == 0:
            raise OperationError("Root degree cannot be zero")
        raise OperationError(f"Invalid root oepration for values: {x}, {y}")

    #Serialization Helpers 
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "result" : str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Calculation":
        try:
            calc = Calculation(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"]),
            )
            calc.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
            saved_result = Decimal(data["result"])
            if calc.result != saved_result:
                logging.warning(
                    f"Loaded result {saved_result} differs from computed {calc.result}"
                )  # pragma: no cover
            return calc
        except (KeyError, InvalidOperation, ValueError) as e:
            raise OperationError(f"Invalid calculation data: {e}")

    # ===== Representations =====
    def __str__(self) -> str:
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def __repr__(self) -> str:
        return (
            f"Calculation(operation='{self.operation}', "
            f"operand1={self.operand1}, operand2={self.operand2}, "
            f"result={self.result}, timestamp='{self.timestamp.isoformat()}')"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Calculation):
            return NotImplemented
        return (
            self.operation == other.operation
            and self.operand1 == other.operand1
            and self.operand2 == other.operand2
            and self.result == other.result
        )

    # ===== Result formatting =====
    def format_result(self, precision: int = 10) -> str:
        """Return formatted result with given precision."""
        try:
            quant = Decimal("1." + "0" * precision)
            return str(self.result.quantize(quant).normalize())
        except InvalidOperation:  # pragma: no cover
            return str(self.result)