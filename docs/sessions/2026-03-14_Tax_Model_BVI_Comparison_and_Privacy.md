# Session: Tax Model BVI Comparison and Privacy Refinement

## Objectives
- Rename the project to `tax-model` to reflect a multi-jurisdictional scope.
- Implement a side-by-side comparison mode in `calculator.py` for Wyoming LLC vs. BVI Company.
- Model the "Place of Effective Management" (POEM) risk and its impact on Bulgarian Corporate Tax (CIT).
- Add a Privacy & Anonymity Scorecard with automated UBO disclosure warnings.
- Refine the TUI layout and semantic labeling for professional PE-grade use.

## Technical Changes
- **Project Scope:** Renamed `llc-tax-model` to `tax-model` in `pyproject.toml` and updated documentation.
- **`calculator.py` Implementation:**
  - Bifurcated logic into `MODEL A: WYOMING LLC` and `MODEL B: BVI COMPANY`.
  - Added reactive inputs for `llc_expenses`, `bvi_expenses`, `bvi_payout_ratio`, and `solve_management_risk`.
  - Implemented 10% BG CIT logic for BVI if the management risk is not solved.
  - Added a 4-column `DataTable` for direct comparison of line items.
  - Refined CSS and layout (30/70 width split) and made the results pane scrollable for visibility.
- **Privacy Engine:**
  - Created a dynamic `Anonymity Level` row in the results table.
  - Implemented a "Critical Breach" warning for Bulgarian subsidiary ownership, which triggers mandatory UBO disclosure in the Sofia Commercial Register.
- **Documentation:** Updated `GEMINI.md` to reflect the multi-entity architecture and the solved/unsolved POEM risk assumptions.

## Logic & Decisions
- **POEM Risk (BVI):** Decided to treat this as a binary toggle. If "Not Solved," profits are hit with 10% Bulgarian CIT before dividend distribution, highlighting the risk of managing an offshore entity from Sofia.
- **The Consulting Penalty:** Modeled how the BVI lacks the 25% statutory deduction enjoyed by the Wyoming LLC (under the flow-through model), creating a clear trade-off between social security savings and income tax deductions.
- **Semantic Labeling:** Updated input categories to `REVENUE & INCOME`, `WYOMING LLC PARAMETERS`, and `BVI COMPANY PARAMETERS` to align with PE modeling standards.

## Verification
- Verified side-by-side math accuracy for both structures.
- Confirmed the 10% CIT calculation for BVI correctly reduces the distribution pool.
- Validated the red privacy warnings trigger correctly on BG dividend inputs.
- Syntax checked `calculator.py` using `py_compile`.

## Next Steps
- Add data export to CSV/Excel for professional reporting.
- Implement automated unit tests for the dual-tax logic.
- Consider adding UAE or Cyprus as a third comparison jurisdiction.
