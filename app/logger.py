# app/logger.py
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Protocol
from .calculation import Calculation
from .calculator_config import CalculatorConfig
from .exceptions import PersistenceError
import os

cfg = CalculatorConfig()
cfg.ensure_dirs()

LOG_FILE = os.path.join(cfg.log_dir, "calculator.log")


def _get_logger():
    logger = logging.getLogger("calculator")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding=cfg.default_encoding)
        fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


class Observer(Protocol):
    def update(self, calculation: Calculation) -> None:
        ...


class LoggingObserver:
    def __init__(self):
        self._logger = _get_logger()

    def update(self, calculation: Calculation) -> None:
        msg = f"{calculation.operation} | operands={calculation.operands} | result={calculation.result}"

        # If tests or callers change a handler's baseFilename at runtime (tests do
        # this to redirect logging to a tmp file), the handler's stream will still
        # point to the original file. Detect that case and reopen the handler's
        # stream so logs are written to the new file.
        for handler in list(self._logger.handlers):
            # File-like handlers (FileHandler, RotatingFileHandler) expose
            # `baseFilename` and `stream` attributes.
            if hasattr(handler, "baseFilename"):
                try:
                    desired = getattr(handler, "baseFilename")
                    stream_name = getattr(getattr(handler, "stream", None), "name", None)
                    if desired and stream_name != desired:
                        try:
                            # Close existing stream and reopen using the updated baseFilename
                            handler.acquire()
                            try:
                                handler.close()
                            finally:
                                handler.release()
                            # re-open stream using the handler internals
                            if hasattr(handler, "_open"):
                                handler.stream = handler._open()
                        except Exception:
                            # Don't let logging handler errors break the calculator
                            pass
                except Exception:
                    pass

        self._logger.info(msg)


class AutoSaveObserver:
    """
    Auto-saves history to CSV on update. Expects the subject to have a 'history_manager' attribute.
    """
    def __init__(self, csv_path: str | None = None):
        self.csv_path = csv_path or os.path.join(cfg.history_dir, "history.csv")
        # make sure directory exists
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

    def update(self, calculation: Calculation) -> None:
        # lazy import pandas
        try:
            import pandas as pd  # local import so only required when autosave is used
        except Exception as e:
            raise PersistenceError(f"pandas is required for autosave: {e}")

        # append new row to csv safely
        try:
            # If file exists, append; otherwise create new DataFrame
            if os.path.exists(self.csv_path):
                existing = pd.read_csv(self.csv_path, encoding=cfg.default_encoding)
                # convert calc to dict and append
                new_row = pd.DataFrame([calculation.to_dict()])
                combined = pd.concat([existing, new_row], ignore_index=True)
                combined.to_csv(self.csv_path, index=False, encoding=cfg.default_encoding)
            else:
                df = pd.DataFrame([calculation.to_dict()])
                df.to_csv(self.csv_path, index=False, encoding=cfg.default_encoding)
        except Exception as e:
            raise PersistenceError(f"Failed to autosave history: {e}")
