# Project Context: LLC Tax Model

## The Scenario
- **User Profile:** Managing Director at a Private Equity fund, resident in Sofia, Bulgaria.
- **Entity:** Wyoming LLC (Single-Member, Disregarded Entity for US Tax).
- **Revenue Streams:** €150k Consulting (Bulgarian client), €20k Dividends (US sourced), Proprietary Trading (Interactive Brokers).
- **Tech Stack:** Python, VSCode, Pandas, Textual (TUI).

## The Tax Rules (Bulgaria 2026 - Euro Transition)
- **US Tax:** 0% Federal Tax (No US Nexus/ETBUS). Only Form 5472 is required.
- **Bulgarian Consulting Tax:** 10% Flat Rate. (Calculated on 75% of gross due to 25% statutory deduction). Client withholds 10% at source, which acts as a tax credit.
- **Bulgarian Dividend Tax (US/Intl):** 5%. (Usually offset to €0 by the 15% US Treaty withholding at IBKR).
- **Bulgarian Dividend Tax (Local BG):** 5% (withheld by BG subsidiary). Triggers public UBO disclosure.
- **Social Security:** Scaled based on consulting income and primary salary gap (2026 Monthly Cap: €2,352.00).
- **VAT:** 0% invoiced by the LLC. The Bulgarian client applies the "Reverse Charge" mechanism.

## Technical Architecture
- **`main.py`**: Application entry point.
- **`calculator.py`**: Interactive TUI (Textual) for financial modeling and tax set-aside calculations.
- **`pyproject.toml`**: Dependency management (uv).

## Objective
Maintain and expand an interactive financial model that calculates the true net retained wealth of this structure while ensuring maximum public anonymity via the Wyoming Registered Agent.