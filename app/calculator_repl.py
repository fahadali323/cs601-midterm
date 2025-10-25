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
from colorama import Fore, Style, init

# Initialize colorama for color support (works on Windows and UNIX)
init(autoreset=True)


def calculator_repl():
    """Main interactive REPL loop for the Calculator."""
    calc = Calculator()

    # Load existing history at startup
    try:
        calc.load_history()
    except Exception as e:
        print(f"{Fore.YELLOW}Note: Could not load previous history: {e}")

    print(f"{Fore.CYAN}🧮 Welcome to the Advanced Calculator!")
    print(f"{Fore.CYAN}Type 'help' for a list of commands, or 'exit' to quit.\n")

    while True:
        try:
            command_line = input(f"{Fore.GREEN}calc> {Style.RESET_ALL}").strip()
            if not command_line:
                continue

            parts = command_line.split()
            command = parts[0].lower()

            # Exit condition
            if command in ("exit", "quit"):
                try:
                    calc.save_history()
                    print(f"{Fore.GREEN}History saved successfully before exit.")
                except Exception as e:
                    print(f"{Fore.YELLOW}Warning: Could not save history: {e}")
                print(f"{Fore.CYAN}Goodbye!")
                break

            # Help menu
            elif command == "help":
                print(f"""
{Fore.CYAN}Available Commands:
-------------------
{Fore.YELLOW}add a b{Fore.WHITE}           → Add two numbers
{Fore.YELLOW}subtract a b{Fore.WHITE}      → Subtract two numbers
{Fore.YELLOW}multiply a b{Fore.WHITE}      → Multiply two numbers
{Fore.YELLOW}divide a b{Fore.WHITE}        → Divide two numbers
{Fore.YELLOW}power a b{Fore.WHITE}         → Raise a to the power of b
{Fore.YELLOW}root a b{Fore.WHITE}          → Compute the b-th root of a
{Fore.YELLOW}modulus a b{Fore.WHITE}       → Compute a % b
{Fore.YELLOW}int_divide a b{Fore.WHITE}    → Integer division
{Fore.YELLOW}percent a b{Fore.WHITE}       → (a / b) * 100
{Fore.YELLOW}abs_diff a b{Fore.WHITE}      → |a - b|
-------------------
{Fore.MAGENTA}history{Fore.WHITE}           → Show calculation history
{Fore.MAGENTA}clear{Fore.WHITE}             → Clear calculation history
{Fore.MAGENTA}undo{Fore.WHITE}              → Undo last calculation
{Fore.MAGENTA}redo{Fore.WHITE}              → Redo last undone calculation
{Fore.MAGENTA}save [path]{Fore.WHITE}       → Save history to CSV file
{Fore.MAGENTA}load [path]{Fore.WHITE}       → Load history from CSV file
{Fore.MAGENTA}help{Fore.WHITE}              → Show this help message
{Fore.MAGENTA}exit{Fore.WHITE}              → Exit the program
""")

            # History commands
            elif command == "history":
                history = calc.history()
                if not history:
                    print(f"{Fore.YELLOW}No calculations yet.")
                else:
                    print(f"{Fore.CYAN}\nCalculation History:")
                    for i, c in enumerate(history, start=1):
                        print(f"{Fore.WHITE}{i}. {Fore.GREEN}{c}")

            elif command == "clear":
                calc.clear_history()
                print(f"{Fore.GREEN}History cleared successfully.")

            elif command == "undo":
                if calc.can_undo():
                    calc.undo()
                    print(f"{Fore.GREEN}Undo successful.")
                else:
                    print(f"{Fore.YELLOW}Nothing to undo.")

            elif command == "redo":
                if calc.can_redo():
                    calc.redo()
                    print(f"{Fore.GREEN}Redo successful.")
                else:
                    print(f"{Fore.YELLOW}Nothing to redo.")

            elif command == "save":
                path = parts[1] if len(parts) > 1 else None
                calc.save_history(path)
                print(f"{Fore.GREEN}History saved successfully.")

            elif command == "load":
                path = parts[1] if len(parts) > 1 else None
                calc.load_history(path)
                print(f"{Fore.GREEN}History loaded successfully.")

            # Arithmetic commands
            elif command in (
                "add", "subtract", "multiply", "divide",
                "power", "root", "modulus", "int_divide",
                "percent", "abs_diff",
            ):
                if len(parts) != 3:
                    print(f"{Fore.RED}Error: Operation requires two operands (e.g., add 2 3)")
                    continue

                a, b = validate_numeric_pair(parts[1], parts[2])
                result_calc = calc.perform(command, a, b)
                print(f"{Fore.GREEN}Result: {Fore.WHITE}{result_calc.result}")

            else:
                print(f"{Fore.RED}Unknown command: '{command}'. Type 'help' for available commands.")

        except (OperationError, ValidationError) as e:
            print(f"{Fore.RED}Error: {e}")
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}Exiting. Goodbye!")
            break
        except Exception as e:
            print(f"{Fore.RED}Unexpected error: {e}")
