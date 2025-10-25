import os
import pandas as pd
from datetime import datetime, timezone
from app.logger import LoggingObserver, AutoSaveObserver
from app.calculation import Calculation


def test_logging_observer_creates_log(tmp_path):
    log_file = tmp_path / "test.log"
    calc = Calculation("add", (2, 3), 5, datetime.now(timezone.utc))
    obs = LoggingObserver()
    obs._logger.handlers[0].baseFilename = str(log_file)
    obs.update(calc)
    assert os.path.exists(log_file)


def test_autosave_observer_writes_csv(tmp_path):
    csv_path = tmp_path / "history.csv"
    calc = Calculation("add", (2, 3), 5, datetime.now(timezone.utc))
    obs = AutoSaveObserver(str(csv_path))
    obs.update(calc)
    df = pd.read_csv(csv_path)
    assert "operation" in df.columns
