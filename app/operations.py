# app/operations.py
from abc import ABC, abstractmethod
from typing import Tuple
from .exceptions import OperationError
from .input_validators import validate_numeric_pair
import math


class Operation(ABC):
    def __init__(self, a, b):
        self.a, self.b = validate_numeric_pair(a, b)

    @abstractmethod
    def compute(self):
        raise NotImplementedError


class Add(Operation):
    def compute(self):
        return self.a + self.b


class Subtract(Operation):
    def compute(self):
        return self.a - self.b


class Multiply(Operation):
    def compute(self):
        return self.a * self.b


class Divide(Operation):
    def compute(self):
        if self.b == 0:
            raise OperationError("Division by zero")
        return self.a / self.b


class Power(Operation):
    def compute(self):
        # handle negative bases with fractional exponents may produce complex result;
        # raise OperationError for invalid real result
        try:
            result = math.pow(self.a, self.b)
        except ValueError as e:
            raise OperationError(f"Power error: {e}")
        return result


class Root(Operation):
    def compute(self):
        # Compute nth root of a: b-th root of a -> a ** (1 / b)
        if self.b == 0:
            raise OperationError("Root degree cannot be zero")
        # For even root and negative a -> invalid in real numbers
        if self.a < 0 and int(self.b) % 2 == 0:
            raise OperationError("Even root of negative number is not a real number")
        try:
            return self.a ** (1.0 / self.b)
        except Exception as e:
            raise OperationError(f"Root error: {e}")


class Modulus(Operation):
    def compute(self):
        if self.b == 0:
            raise OperationError("Modulus by zero")
        return self.a % self.b


class IntDivide(Operation):
    def compute(self):
        if self.b == 0:
            raise OperationError("Integer division by zero")
        return self.a // self.b


class Percent(Operation):
    def compute(self):
        # percent of a with respect to b: (a / b) * 100
        if self.b == 0:
            raise OperationError("Percent calculation division by zero")
        return (self.a / self.b) * 100.0


class AbsDiff(Operation):
    def compute(self):
        return abs(self.a - self.b)


class OperationFactory:
    _map = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntDivide,
        "percent": Percent,
        "abs_diff": AbsDiff,
    }

    @classmethod
    def create(cls, name: str, a, b) -> Operation:
        key = name.lower()
        if key not in cls._map:
            raise OperationError(f"Unsupported operation: {name}")
        OpClass = cls._map[key]
        return OpClass(a, b)
