# 🧮 Advanced Object-Oriented Calculator

A Python-based command-line calculator demonstrating **object-oriented design**, **design patterns**, and **configuration management**.

## 🚀 Features
- Basic and advanced math operations: add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff  
- History management with save/load (CSV via pandas)  
- Undo/redo support using the Memento pattern  
- Auto-saving and logging via Observer pattern  
- Configurable via `.env` using `python-dotenv`  
- **Color-coded output** using `colorama` for a better CLI experience  

## ⚙️ Setup
```bash
pip install -r requirements.txt
```

## Create a .env file:

CALCULATOR_LOG_DIR=logs
CALCULATOR_HISTORY_DIR=data
CALCULATOR_AUTO_SAVE=true


## ▶️ Run
```
python main.py
```
## 🧪 Test & Coverage
```
pytest --cov=app --cov-report=term-missing
```

## 📂 Structure
```app/
 ├── calculator.py
 ├── calculation.py
 ├── history.py
 ├── operations.py
 └── calculator_config.py
tests/
 └── test_calculator.py
```

Author: Fahad Ali
Version: 1.0
License: MIT
