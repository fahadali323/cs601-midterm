from datetime import datetime
from app.calculation import Calculation


def test_calculation_to_dict_structure():
    c = Calculation("add", (2, 3), 5, datetime(2024, 1, 1))
    d = c.to_dict()
    assert d["operation"] == "add"
    assert d["operand_1"] == 2
    assert d["operand_2"] == 3
    assert d["result"] == 5
    assert "timestamp" in d
