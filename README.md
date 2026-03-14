# Wyoming LLC Tax Model (Bulgarian Resident)

This is a TUI-based tax calculator for a Bulgarian resident operating via a Wyoming LLC. 

## Setup

Ensure you have `uv` installed. Then run:

```bash
uv sync
```

## Running the Calculator

To launch the interactive calculator:

```bash
uv run python main.py
```

## Features

- **Reactive Calculation**: Results update as you type.
- **MD Shield Logic**: Automatically calculates if additional social security is due based on your primary job's salary and the 2026 cap.
- **Tax Treaty Credits**: Handles US 15% withholding vs Bulgarian 5% dividend tax.
- **Consulting Deductions**: Applies the 25% statutory deduction for Bulgarian consultants.
- **Privacy First**: Modeled for the highest public privacy achievable for a Bulgarian resident.
