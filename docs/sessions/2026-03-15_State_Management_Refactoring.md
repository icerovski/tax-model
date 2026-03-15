# Session Log: 2026-03-15 - State Management Refactoring & Logic Consolidation

## Objectives
- Eliminate state duplication between `calculator.py` (reactive variables) and `engine.py` (`TaxInputs` dataclass).
- Implement a "Single Source of Truth" architecture for entity parameters.
- Consolidate redundant calculation logic in the tax engine.

## Technical Changes
- **engine.py**:
    - Converted `TaxInputs` from a frozen dataclass to a mutable one to allow direct state updates from the UI.
    - Updated default `md_salary` to €11,000.00 to reflect the user's latest PE shield scenario.
    - Refactored `calculate_taxes` to perform shared source-level withholdings (US Dividends, BG Subsidiary dividends) once at the top of the function, removing duplicate logic blocks between LLC and BVI tracks.
- **calculator.py**:
    - Removed all individual `reactive(...)` variables.
    - Introduced `self.inputs = TaxInputs()` in `__init__` as the central state container.
    - Refactored `on_input_changed` and `on_checkbox_changed` to use dynamic attribute setting (`setattr(self.inputs, id, value)`), significantly reducing boilerplate code.
    - Updated the `compose` and `_update_ui` methods to reference `self.inputs` directly.

## Logic & Decisions
- **Architecture over Boilerplate**: By using Python's `setattr` and `hasattr` introspection, the UI is now automatically compatible with any new fields added to `TaxInputs` without requiring new handler logic.
- **Pre-Entity Taxation**: Moving source withholdings to a "Shared" block in the engine more accurately reflects the financial reality where these taxes are deducted *before* the net cash reaches the Wyoming or BVI accounts.

## Next Steps
- Implement automated unit tests for the consolidated engine logic.
- Explore "Scenario Comparison Saving" to allow users to compare multiple variations of the same strategy.
