# app/calculator_config.py

import os 
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  #Load from .env if present

@dataclass
class CalculatorConfig:
    log_dir: str = os.getenv("CALCULATOR_LOG_DIR", "logs")
    history_dir: str = os.getenv("CALCULATOR_HISTORY_DIR", "data")
    history_file: str = os.getenv("CALCULATOR_HISTORY_FILE", "data/history.csv")
    max_history_size: int = int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"))
    auto_save: bool = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower() in ("1", "true", "yes")
    precision: int = int(os.getenv("CALCULATOR_PRECISION", "6"))
    max_input_value: float = float(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e308"))
    default_encoding: str = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    def ensure_dirs(self):
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)