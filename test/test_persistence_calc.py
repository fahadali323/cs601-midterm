import pandas as pd
from datetime import datetime, timezone
from app.calculator import Calculator


def test_save_and_load_history(tmp_path):
    f = tmp_path / "history.csv"

    calc = Calculator()
    calc.clear_history()
    calc.perform("add", 10, 20)
    calc.perform("subtract", 5, 2)

    # Save to explicit path
    calc.save_history(str(f))
    assert f.exists()

    # Create a fresh calculator and load from file
    new_calc = Calculator()
    # ensure loading from provided path works
    new_calc.load_history(str(f))
    hist = new_calc.history()
    assert len(hist) == 2
    # verify file has expected columns
    df = pd.read_csv(f)
    assert {"operation", "operand_1", "operand_2", "result", "timestamp"}.issubset(df.columns)
