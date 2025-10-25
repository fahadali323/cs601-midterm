import pandas as pd
from datetime import datetime, timezone
from app.history import HistoryManager
from app.calculation import Calculation


def make_calc():
    return Calculation("add", (1, 2), 3, datetime.now(timezone.utc))


def test_append_and_list():
    hm = HistoryManager(max_size=5)
    c = make_calc()
    hm.append(c)
    assert len(hm.list()) == 1


def test_clear_history():
    hm = HistoryManager()
    hm.append(make_calc())
    hm.clear()
    assert hm.size() == 0


def test_to_dataframe_structure():
    hm = HistoryManager()
    hm.append(make_calc())
    df = hm.to_dataframe()
    assert isinstance(df, pd.DataFrame)
    assert {"operation", "result", "timestamp"}.issubset(df.columns)
