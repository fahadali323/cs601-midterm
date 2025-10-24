# app/exceptions.py

class CalculatorError(Exception):
    """Base calculator exceptions."""

class OperationError(CalculatorError):
    """Raised when an operation fails (unsupported, invalid inputs)"""

class ValidationError(CalculatorError):
    """Raise when user input fails validation (non-numerial value inputs, unsupported commands)"""

class PersistenceError(CalculatorError):
    """Raised when saving/loading history fails (I/O or pandas errors.)"""