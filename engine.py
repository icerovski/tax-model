"""
engine.py: Mathematical Core & Tax Logic
----------------------------------------
This module contains the stateless logic for the Global Entity Tax Model. 
It defines the data structures for inputs and results, and implements the 
tax calculations for both Wyoming LLC (Pass-Through) and BVI Company 
(Corporate Blocker) structures, including specific protocols for Bulgarian 
social security shields and privacy impacts.
"""

from dataclasses import dataclass, field
from typing import Dict, Any

# Constants (2026 Euro)
BG_INCOME_TAX = 0.10
BG_DIVIDEND_TAX = 0.05
STATUTORY_DEDUCTION_CONSULTING = 0.25
STATUTORY_DEDUCTION_TRADING = 0.10
MAX_SOC_SEC_CAP = 2352.0  # Monthly Cap
SOC_SEC_RATE = 0.278
US_WITHHOLDING_RATE = 0.15

@dataclass
class TaxInputs:
    md_salary: float = 11000.0  # Monthly MD Salary (Tax Shield)
    consulting_rev: float = 150000.0
    dividends: float = 0.0
    bg_company_dividends: float = 0.0
    trading_profits: float = 0.0
    is_us_dividend: bool = True
    is_eu_trading: bool = False
    client_withholds: bool = True
    llc_expenses: float = 1200.0
    bvi_expenses: float = 2500.0
    bvi_payout_ratio: float = 0.0  # Percentage 0-100
    solve_management_risk: bool = True

    # Optional policy parameters
    bg_income_tax: float = BG_INCOME_TAX
    bg_dividend_tax: float = BG_DIVIDEND_TAX
    statutory_deduction_consulting: float = STATUTORY_DEDUCTION_CONSULTING
    statutory_deduction_trading: float = STATUTORY_DEDUCTION_TRADING
    max_soc_sec_cap: float = MAX_SOC_SEC_CAP
    soc_sec_rate: float = SOC_SEC_RATE
    us_withholding_rate: float = US_WITHHOLDING_RATE
    is_bg_tax_resident: bool = True


@dataclass(frozen=True)
class TaxResults:
    total_gross: float
    
    # Strategy I: Consulting
    consulting_tax_llc: float
    soc_sec_due_llc: float
    consulting_cit_bvi: float
    
    # Strategy II: BG Subsidiary
    bg_subsidiary_wht_llc: float
    bg_subsidiary_wht_bvi: float
    
    # Totals LLC
    total_tax_llc: float
    net_wealth_llc: float
    privacy_llc: str
    
    # Totals BVI
    total_tax_bvi: float
    personal_wealth_bvi: float
    trapped_in_bvi: float
    total_net_wealth_bvi: float
    privacy_bvi: str
    
    # Helpers for table
    trading_tax_llc: float
    intl_div_tax_llc: float
    us_withholding_bvi: float
    corporate_tax_bvi: float
    payout_amount_bvi: float
    bg_dividend_tax_bvi: float
    effective_rate_llc: float
    effective_rate_bvi: float
    vat_status_llc: str = "Reverse Charge (0%)"
    vat_status_bvi: str = "Reverse Charge (0%)"

def calculate_taxes(inputs: TaxInputs) -> TaxResults:
    # 1. SHARED SOURCE-LEVEL CALCULATIONS (Happens before money hits the entity)
    total_gross = (inputs.consulting_rev + inputs.dividends + 
                   inputs.bg_company_dividends + inputs.trading_profits)
    
    # Source Withholding on US/Intl Dividends
    src_us_withholding = inputs.dividends * inputs.us_withholding_rate if inputs.is_us_dividend else 0.0
    src_intl_div_tax = 0.0 if inputs.is_us_dividend else inputs.dividends * inputs.bg_dividend_tax
    
    # Source Withholding on Local BG Company Dividends
    src_bg_subsidiary_wht = inputs.bg_company_dividends * inputs.bg_dividend_tax

    # --- MODEL A: WYOMING LLC (Pass-Through) ---
    # Strategy I logic
    taxable_consulting_annual_llc = inputs.consulting_rev * (1 - inputs.statutory_deduction_consulting)
    taxable_consulting_monthly_llc = taxable_consulting_annual_llc / 12
    monthly_gap_llc = max(0, inputs.max_soc_sec_cap - inputs.md_salary)
    soc_sec_taxable_monthly_llc = min(taxable_consulting_monthly_llc, monthly_gap_llc)
    soc_sec_due_llc = soc_sec_taxable_monthly_llc * 12 * inputs.soc_sec_rate
    consulting_tax_llc = taxable_consulting_annual_llc * inputs.bg_income_tax
    
    # Strategy II & Passive
    trading_tax_llc = (0.0 if inputs.is_eu_trading else 
                       (inputs.trading_profits * (1 - inputs.statutory_deduction_trading)) * inputs.bg_income_tax)

    total_tax_llc = (soc_sec_due_llc + consulting_tax_llc + 
                     src_us_withholding + src_intl_div_tax + 
                     src_bg_subsidiary_wht + trading_tax_llc)
    net_wealth_llc = total_gross - total_tax_llc - inputs.llc_expenses

    # --- MODEL B: BVI COMPANY (Corporate Blocker) ---
    # Strategy I CIT risk (POEM)
    consulting_cit_bvi = 0.0 if inputs.solve_management_risk else (inputs.consulting_rev * inputs.bg_income_tax)
    
    # Entity-wide Corporate Income Tax
    pre_tax_profit_bvi = total_gross - src_us_withholding - src_bg_subsidiary_wht - inputs.bvi_expenses
    corporate_tax_bvi = 0.0 if inputs.solve_management_risk else max(0, pre_tax_profit_bvi * inputs.bg_income_tax)
    
    # Distribution/Payout logic
    net_retained_bvi = pre_tax_profit_bvi - corporate_tax_bvi
    payout_amount_bvi = max(0, net_retained_bvi * (inputs.bvi_payout_ratio / 100.0))
    bg_dividend_tax_bvi = payout_amount_bvi * inputs.bg_dividend_tax
    
    total_tax_bvi = src_us_withholding + src_bg_subsidiary_wht + corporate_tax_bvi + bg_dividend_tax_bvi
    trapped_in_bvi = max(0, net_retained_bvi - payout_amount_bvi)
    personal_wealth_bvi = payout_amount_bvi - bg_dividend_tax_bvi
    total_net_wealth_bvi = trapped_in_bvi + personal_wealth_bvi

    # --- Privacy Logic ---
    privacy_llc = "HIGH (Shielded)"
    privacy_bvi = "HIGH (Shielded)" if inputs.solve_management_risk else "MODERATE (POEM Trail)"

    if inputs.bg_company_dividends > 0:
        privacy_llc = "[red]LOW (UBO Disclosure)[/red]"
        privacy_bvi = "[red]LOW (UBO Disclosure)[/red]"

    return TaxResults(
        total_gross=total_gross,
        consulting_tax_llc=consulting_tax_llc,
        soc_sec_due_llc=soc_sec_due_llc,
        consulting_cit_bvi=consulting_cit_bvi,
        bg_subsidiary_wht_llc=src_bg_subsidiary_wht,
        bg_subsidiary_wht_bvi=src_bg_subsidiary_wht,
        total_tax_llc=total_tax_llc,
        net_wealth_llc=net_wealth_llc,
        privacy_llc=privacy_llc,
        total_tax_bvi=total_tax_bvi,
        personal_wealth_bvi=personal_wealth_bvi,
        trapped_in_bvi=trapped_in_bvi,
        total_net_wealth_bvi=total_net_wealth_bvi,
        privacy_bvi=privacy_bvi,
        trading_tax_llc=trading_tax_llc,
        intl_div_tax_llc=src_intl_div_tax + src_us_withholding,
        us_withholding_bvi=src_us_withholding,
        corporate_tax_bvi=corporate_tax_bvi,
        payout_amount_bvi=payout_amount_bvi,
        bg_dividend_tax_bvi=bg_dividend_tax_bvi,
        effective_rate_llc=(total_tax_llc/total_gross*100) if total_gross > 0 else 0,
        effective_rate_bvi=(total_tax_bvi/total_gross*100) if total_gross > 0 else 0
    )
