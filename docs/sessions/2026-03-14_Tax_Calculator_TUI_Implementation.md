# Session: Tax Calculator TUI Implementation

## Objectives
- Research and document the Wyoming LLC structure for a Bulgarian resident.
- Implement an interactive tax calculator for 2026 Euro-based financial modeling.
- Support variable inputs (Salary, Revenue, Trading Profits) and fixed costs.

## Technical Changes
- Created calculator.py: A 	extual-based TUI with reactive inputs and live calculation results.
- Updated main.py: Set as the entry point for the TUI application.
- Updated pyproject.toml: Added 	extual and pandas dependencies.
- Updated README.md: Added setup and run instructions for the new TUI.
- Updated GEMINI.md: Refined the 2026 tax logic and updated the technical architecture.

## Logic & Decisions
- **MD Shield**: Implemented logic to scale social security based on the gap between the 2026 monthly cap (€2,352) and the user's primary salary.
- **Consulting Base**: Applied the 25% statutory deduction as per Bulgarian NRA rules for freelancers/consultants.
- **Privacy Alerts**: Added dynamic warnings for Bulgarian company dividends, which trigger mandatory UBO disclosure under the Measures Against Money Laundering Act.
- **Scrollable UI**: Used VerticalScroll for inputs to ensure usability on smaller terminal windows.

## Verification
- Verified reactive calculations update correctly on input change.
- Fixed a bug where social security was calculated incorrectly when consulting revenue was zero.
- Fixed a CSS error regarding invalid border types in Textual.

## Next Steps
- Implement data export (CSV/Pandas) for the Bulgarian accountant.
- Add support for crypto-specific tax logic (if applicable).
- Create automated tests for the core tax logic in calculator.py.
