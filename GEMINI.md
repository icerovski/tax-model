# Project Context: Global Entity Tax Model

## The Scenario
- **User Profile:** Managing Director at a Private Equity fund, resident in Sofia, Bulgaria.
- **Entity:** Wyoming LLC (Single-Member, Disregarded Entity for US Tax) vs. BVI Company (Corporate Entity, "Effective Management" risk solved).
- **Revenue Streams:** €150k Consulting (Bulgarian client), €20k Dividends (US sourced), Proprietary Trading (Interactive Brokers).
- **Tech Stack:** Python, VSCode, Pandas, Textual (TUI).

## The Tax Rules (Bulgaria 2026 - Euro Transition)
- **US Tax:** 0% Federal Tax (No US Nexus/ETBUS). Only Form 5472 is required for LLC.
- **BVI Tax:** 0% Corporate Tax. Requires Economic Substance filings.
- **Bulgarian Consulting Tax (Wyoming LLC):** 10% Flat Rate. (Calculated on 75% of gross due to 25% statutory deduction). Client withholds 10% at source, which acts as a tax credit.
- **Bulgarian Consulting Tax (BVI Company):** Not directly taxable at the corporate level (assuming management is non-BG). Taxed at 5% dividend rate only upon distribution.
- **Bulgarian Dividend Tax (US/Intl):** 5%. (Usually offset to €0 by the 15% US Treaty withholding at IBKR for LLC; 5% flat on distributions for BVI).
- **Bulgarian Dividend Tax (Local BG):** 5% (withheld by BG subsidiary). Triggers public UBO disclosure.
- **Social Security (Wyoming LLC):** Scaled based on consulting income and primary salary gap (2026 Monthly Cap: €2,352.00).
- **Social Security (BVI Company):** €0 (Corporate dividends do not trigger BG social security).
- **VAT:** 0% invoiced by the entities. The Bulgarian client applies the "Reverse Charge" mechanism.

## Technical Architecture
- **`main.py`**: Application entry point.
- **`engine.py`**: Stateless core logic. Uses a mutable `TaxInputs` dataclass as the single source of truth for entity parameters. Calculates taxes based on two primary tracks:
    - **Strategy I (Consulting)**: Service contract logic with social security shields.
    - **Strategy II (Subsidiary)**: Ownership logic with UBO disclosure triggers.
    - **Consolidated Logic**: Source-level withholdings are calculated once and applied to both models to ensure consistency.
- **`calculator.py`**: Interactive TUI (Textual). Uses dynamic introspection (`setattr`/`hasattr`) to map UI inputs directly to the `TaxInputs` state object, eliminating boilerplate state sync code.
- **`pyproject.toml`**: Dependency management (uv).

## Strategic Logic Protocols
1. **The Privacy Breaker**: Any non-zero input in "Bulgarian Subsidiary" (Strategy II) automatically downgrades the Privacy status of the entire entity from HIGH to LOW, regardless of Registered Agent shields.
2. **The MD Shield**: Social security for LLC consulting is calculated by applying the 27.8% rate only to the "Gap" between the MD Salary and the monthly cap (€2,352).
3. **The POEM Trap**: BVI structures are modeled with a 10% CIT risk if management risk is not explicitly marked as "Solved".

## Objective
Maintain and expand an interactive financial model that compares the true net retained wealth between different international corporate structures (e.g., Wyoming LLC vs. BVI Company) while ensuring maximum public anonymity.