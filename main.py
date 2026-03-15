"""
main.py: Application Entry Point
-------------------------------
This file serves as the main execution script for the Global Entity Tax Model. 
It initializes and runs the TaxCalculator TUI (Terminal User Interface).
"""

from calculator import TaxCalculator

if __name__ == "__main__":
    app = TaxCalculator()
    app.run()
