# Session Log: 2026-03-15 - Strategy-Based Input Restructuring

## Objectives
- Resolve Pylance type errors in `calculator.py`.
- Restructure the input panel to separate the two primary strategic models: Consulting Contracts and Bulgarian Subsidiary ownership.
- Simplify the model by removing redundant income fields (Other BG Monthly Salary).
- Enhance the results table to provide a clear breakdown of Strategy I vs. Strategy II, including specific privacy impacts.
- Add "Net Tax Rate (%)" to the entity summary for quick efficiency comparison.

## Technical Changes
- **calculator.py**:
    - Refactored `on_checkbox_changed` to safely handle `id` strings, resolving a `hasattr` type error.
    - Rearranged the `compose` method into four logical sections: I. Consulting, II. Subsidiary, III. Global Investments, and IV. Overhead.
    - Updated `_update_ui` to group results by strategy layer.
    - Added specific Privacy Impact strings per line item in the DataTable.
    - Added "Net Tax Rate (%)" calculation to the Summary section.
- **engine.py**:
    - Updated `TaxResults` dataclass to include strategy-specific subtotals (`consulting_tax_llc`, `bg_subsidiary_wht_llc`, etc.).
    - Removed `other_bg_income` from inputs and gross calculations.
    - Refined privacy logic to explicitly flag Strategy II (Subsidiary) as a "Privacy Breaker" that triggers UBO disclosure for the entire entity.
    - Fixed floating-point artifact display in the policy info section using string formatting.

## Logic & Decisions
- **Privacy Breaker Rule**: The model now explicitly teaches the user that while consulting contracts (Strategy I) are private, the ownership of a Bulgarian entity (Strategy II) triggers mandatory UBO disclosure in the Commercial Register, effectively neutralizing the anonymity benefits of a Wyoming LLC or BVI structure.
- **Social Security Shield**: Confirmed that the "MD Salary" field is the primary driver for social security gap calculations. Removed the redundant "Other BG Salary" to reduce user cognitive load.

## Next Steps
- Implement a "Visual PDF Export" or "Markdown Report" feature to allow the user to present these findings to a board or family office.
- Add support for "EU Trading Statutory Deductions" verification logic.
