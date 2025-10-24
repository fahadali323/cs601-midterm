import pytest
from app.operations import OperationFactory
from app.exceptions import OperationError

@pytest.mark.parametrize(
    "op,a,b,expected",
    [
        ("add", 2, 3, 5),
        ("subtract", 5, 2, 3),
        ("multiply", 3, 4, 12),
        ("divide", 10, 2, 5),
        ("power", 2, 3, 8),
        ("root", 27, 3, 3),
        ("modulus", 10, 3, 1),
        ("int_divide", 9, 2, 4),
        ("percent", 50, 100, 50),
        ("abs_diff", 10, 4, 6),
    ],
)

def test_operations(op,a,b, expected):
    operation = OperationFactory.create(op, a, b)
    assert round(operation.copute(), 6) == pytest.approx(expected, rel=1e-6)
