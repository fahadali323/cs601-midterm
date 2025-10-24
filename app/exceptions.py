# app/exceptions.py
class CalculatorError(Exception):
    """Base calculator exception."""


class OperationError(CalculatorError):
    """Raised when an operation fails (e.g. unsupported, invalid inputs)."""


class ValidationError(CalculatorError):
    """Raised when user input fails validation (non-numeric, out-of-range, ...)."""


class PersistenceError(CalculatorError):
    """Raised when saving/loading history fails (I/O or pandas errors)."""
