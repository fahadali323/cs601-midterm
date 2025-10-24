# app/calculator_repl.py

"""
Calculator REPL (Read-Eval-Print Loop)
--------------------------------------

Provides an interactive command-line interface for performing calculations,
managing history, and demonstrating the calculator’s design patterns.

Supported Commands:
-------------------
add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff – Perform calculations.
history – Display calculation history.
clear – Clear calculation history.
undo – Undo the last calculation.
redo – Redo the last undone calculation.
save – Manually save calculation history to file using pandas.
load – Load calculation history from file using pandas.
help – Display available commands.
exit – Exit the application gracefully.
"""

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.input_validators import validate_numeric_pair


def calculator_repl():
    """Main interactive REPL loop for the Calculator."""
    calc = Calculator()
    # Load existing history at startup
    try:
        calc.load_history()  # Will use default path from config
    except Exception as e:
        print(f"Note: Could not load previous history: {e}")
    print("🧮 Welcome to the Advanced Calculator!")
    print("Type 'help' for a list of commands, or 'exit' to quit.\n")

    while True:
        try:
            command_line = input("calc> ").strip()
            if not command_line:
                continue

            parts = command_line.split()
            command = parts[0].lower()

            # Exit condition
            if command in ("exit", "quit"):
                # Auto-save history before exiting
                try:
                    calc.save_history()  
                except Exception as e:
                    print(f"Warning: Could not save history: {e}")
                print("Goodbye!")
                break

            # Help menu
            elif command == "help":
                print(
                    """
Available Commands:
-------------------
add a b           → Add two numbers
subtract a b      → Subtract two numbers
multiply a b      → Multiply two numbers
divide a b        → Divide two numbers
power a b         → Raise a to the power of b
root a b          → Compute the b-th root of a
modulus a b       → Compute a % b
int_divide a b    → Integer division
percent a b       → (a / b) * 100
abs_diff a b      → |a - b|
-------------------
history           → Show calculation history
clear             → Clear calculation history
undo              → Undo last calculation
redo              → Redo last undone calculation
save [path]       → Save history to CSV file
load [path]       → Load history from CSV file
help              → Show this help message
exit              → Exit the program
"""
                )

            # History and persistence commands
            elif command == "history":
                history = calc.history()
                if not history:
                    print("No calculations yet.")
                else:
                    print("\nCalculation History:")
                    for i, c in enumerate(history, start=1):
                        print(f"{i}. {c}")

            elif command == "clear":
                calc.clear_history()
                print("History cleared.")

            elif command == "undo":
                if calc.can_undo():
                    calc.undo()
                    print("Undo successful.")
                else:
                    print("Nothing to undo.")

            elif command == "redo":
                if calc.can_redo():
                    calc.redo()
                    print("Redo successful.")
                else:
                    print("Nothing to redo.")

            elif command == "save":
                path = parts[1] if len(parts) > 1 else None
                calc.save_history(path)
                print("History saved successfully.")

            elif command == "load":
                path = parts[1] if len(parts) > 1 else None
                calc.load_history(path)
                print("History loaded successfully.")

            # Arithmetic commands
            elif command in (
                "add", "subtract", "multiply", "divide",
                "power", "root", "modulus", "int_divide",
                "percent", "abs_diff",
            ):
                if len(parts) != 3:
                    print("Error: Operation requires two operands (e.g., add 2 3)")
                    continue

                a, b = validate_numeric_pair(parts[1], parts[2])
                result_calc = calc.perform(command, a, b)
                print(f"Result: {result_calc.result}")

            else:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")

        except (OperationError, ValidationError) as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
