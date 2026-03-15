from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Footer, Input, Label, Static, Checkbox, DataTable

from engine import (
    TaxInputs, TaxResults, calculate_taxes,
    BG_INCOME_TAX, BG_DIVIDEND_TAX, MAX_SOC_SEC_CAP, 
    STATUTORY_DEDUCTION_CONSULTING, STATUTORY_DEDUCTION_TRADING, SOC_SEC_RATE,
    US_WITHHOLDING_RATE
)

class TaxCalculator(App):
    """A Textual TUI for the Bulgarian Global Entity Tax Model."""

    CSS = """
    Container {
        layout: horizontal;
    }
    VerticalScroll {
        width: 30%;
        padding: 1;
        border: solid green;
        overflow-x: auto;
        scrollbar-size: 1 1;
    }
    #results-pane {
        width: 70%;
        padding: 1;
        border: solid blue;
        scrollbar-size: 1 1;
    }
    .input-group {
        margin-bottom: 1;
    }
    Label {
        margin-top: 1;
        text-style: bold;
        width: auto;
    }
    #explanation {
        margin-top: 2;
        padding: 1;
        background: $boost;
        border: round $accent;
        height: auto;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Single Source of Truth
        self.inputs = TaxInputs()

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with VerticalScroll():
                yield Label("I. CONSULTING CONTRACT (BG CLIENT)")
                yield Label("Annual Consulting Revenue (€)")
                yield Input(value=str(self.inputs.consulting_rev), id="consulting_rev", type="number")
                yield Checkbox("BG Client Withholds 10% (LLC Credit)", value=self.inputs.client_withholds, id="client_withholds")
                yield Checkbox("BVI Management Risk Solved (0% BG CIT)", value=self.inputs.solve_management_risk, id="solve_management_risk")
                
                yield Label("II. BULGARIAN SUBSIDIARY")
                yield Label("Annual BG Company Dividends (€)")
                yield Input(value=str(self.inputs.bg_company_dividends), id="bg_company_dividends", type="number")

                yield Label("III. GLOBAL INVESTMENTS & PERSONAL")
                yield Label("Monthly MD Salary (€) (Tax Shield)")
                yield Input(value=str(self.inputs.md_salary), id="md_salary", type="number")
                yield Label("Annual Dividends (US/Intl) (€)")
                yield Input(value=str(self.inputs.dividends), id="dividends", type="number")
                yield Checkbox("US Sourced Dividends (15% US Tax)", value=self.inputs.is_us_dividend, id="is_us_dividend")
                yield Label("Annual Trading Profits (€)")
                yield Input(value=str(self.inputs.trading_profits), id="trading_profits", type="number")
                yield Checkbox("EU/EEA Regulated (0% Tax)", value=self.inputs.is_eu_trading, id="is_eu_trading")

                yield Label("IV. STRUCTURE OVERHEAD & POLICY")
                yield Label("LLC Annual Expenses (€)")
                yield Input(value=str(self.inputs.llc_expenses), id="llc_expenses", type="number")
                yield Label("BVI Annual Expenses (€)")
                yield Input(value=str(self.inputs.bvi_expenses), id="bvi_expenses", type="number")
                yield Label("BVI Dividend Payout Ratio (%)")
                yield Input(value=str(self.inputs.bvi_payout_ratio), id="bvi_payout_ratio", type="number")
                yield Label("SOC Security Cap (€ / mo)")
                yield Input(value=str(self.inputs.max_soc_sec_cap), id="max_soc_sec_cap", type="number")
                yield Checkbox("BG Tax Resident", value=self.inputs.is_bg_tax_resident, id="is_bg_tax_resident")

                yield Label("FIXED POLICY INFORMATION (2026)")
                yield Static(f"• BG Income Tax: {BG_INCOME_TAX*100:.0f}%")
                yield Static(f"• BG Dividend Tax: {BG_DIVIDEND_TAX*100:.0f}%")
                yield Static(f"• US Dividend Withholding: {US_WITHHOLDING_RATE*100:.0f}%")
                yield Static(f"• Soc Sec Rate: {SOC_SEC_RATE*100:.1f}%")
                yield Static(f"• Consulting Deduction: {STATUTORY_DEDUCTION_CONSULTING*100:.0f}%")
                yield Static(f"• Trading Deduction: {STATUTORY_DEDUCTION_TRADING*100:.0f}%")

            with VerticalScroll(id="results-pane"):
                yield Label("STRATEGY COMPARISON: WYOMING LLC vs BVI COMPANY")
                yield DataTable(id="results-table")
                yield Static(id="explanation")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Strategic Layer", "Wyoming LLC (€)", "BVI Company (€)", "Privacy Impact")
        self.update_calculations()

    def on_input_changed(self, event: Input.Changed) -> None:
        if not event.input.id:
            return
        try:
            val = float(event.value) if event.value else 0.0
            # Basic validation for certain fields
            if event.input.id == "bvi_payout_ratio":
                val = max(0.0, min(100.0, val))
            
            if hasattr(self.inputs, event.input.id):
                setattr(self.inputs, event.input.id, val)
                self.update_calculations()
        except ValueError:
            pass

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id and hasattr(self.inputs, event.checkbox.id):
            setattr(self.inputs, event.checkbox.id, event.value)
            self.update_calculations()

    def update_calculations(self) -> None:
        results = calculate_taxes(self.inputs)
        self._update_ui(results)

    def _update_ui(self, results: TaxResults) -> None:
        table = self.query_one("#results-table", DataTable)
        table.clear()
        
        # Privacy Status Strings
        privacy_consulting = "[green]HIGH (Private)[/green]"
        privacy_subsidiary = "[red]LOW (UBO Registry)[/red]"
        
        table.add_rows([
            ("[b]STRATEGY I: CONSULTING[/b]", "", "", ""),
            ("  • Gross Revenue", f"{self.inputs.consulting_rev:,.2f}", f"{self.inputs.consulting_rev:,.2f}", privacy_consulting),
            ("  • Consulting Tax (BG)", f"-{results.consulting_tax_llc:,.2f}", "0.00", "LLC personal tax"),
            ("  • Social Security", f"-{results.soc_sec_due_llc:,.2f}", "0.00", "LLC personal cost"),
            ("  • Corp Tax (Sofia-POEM)", "0.00", f"-{results.consulting_cit_bvi:,.2f}", "BVI Sofia-resident risk"),
            
            ("[b]STRATEGY II: SUBSIDIARY[/b]", "", "", ""),
            ("  • Dividend Gross", f"{self.inputs.bg_company_dividends:,.2f}", f"{self.inputs.bg_company_dividends:,.2f}", privacy_subsidiary),
            ("  • BG Source WHT (5%)", f"-{results.bg_subsidiary_wht_llc:,.2f}", f"-{results.bg_subsidiary_wht_bvi:,.2f}", "Taxed at source"),
            
            ("[b]GLOBAL / PASSIVE[/b]", "", "", ""),
            ("  • Trading Profits", f"{self.inputs.trading_profits:,.2f}", f"{self.inputs.trading_profits:,.2f}", "Investment layer"),
            ("  • Trading Tax", f"-{results.trading_tax_llc:,.2f}", "0.00", "10% on non-EEA profit"),
            ("  • Intl Dividends (Net)", f"{self.inputs.dividends:,.2f}", f"{self.inputs.dividends:,.2f}", "Pre-entity taxes"),
            ("  • Intl Div Tax (BG)", f"-{results.intl_div_tax_llc:,.2f}", "0.00", "BG personal tax"),
            
            ("[b]ENTITY SUMMARY[/b]", "", "", ""),
            ("  • Annual Expenses", f"-{self.inputs.llc_expenses:,.2f}", f"-{self.inputs.bvi_expenses:,.2f}", "Fixed overhead"),
            ("  • BVI Dist. Tax (5%)", "N/A", f"-{results.bg_dividend_tax_bvi:,.2f}", "Personal tax on payout"),
            ("  • Net Tax Rate (%)", f"{results.effective_rate_llc:.2f}%", f"{results.effective_rate_bvi:.2f}%", "Total Tax / Gross"),
            ("  • TOTAL NET WEALTH", f"[b]{results.net_wealth_llc:,.2f}[/b]", f"[b]{results.total_net_wealth_bvi:,.2f}[/b]", "Combined net Retained"),
            ("  • FINAL PRIVACY", results.privacy_llc, results.privacy_bvi, "Global Structure Status")
        ])

        winner = "Wyoming LLC" if results.net_wealth_llc > results.total_net_wealth_bvi else "BVI Company"
        difference = abs(results.net_wealth_llc - results.total_net_wealth_bvi)
        
        explanation = self.query_one("#explanation", Static)
        explanation.update(
            f"[b]STRATEGIC SUMMARY[/b]\n\n"
            f"• [b]Tax Winner:[/b] [green]{winner}[/green] by €{difference:,.2f}\n"
            f"• [b]Strategy I Impact:[/b] The LLC wins on consulting if you have an MD salary shield. The BVI is only better if you need to 'trap' profits offshore.\n"
            f"• [b]Strategy II Impact:[/b] Owning a BG subsidiary triggers [red]UBO Disclosure[/red]. This links your name to the structure, making the 'Privacy Shield' irrelevant for [i]both[/i] consulting and dividends.\n"
            f"• [b]The POEM Trap:[/b] If BVI management isn't solved, Strategy I incurs 10% CIT first, then 5% Div Tax, making it the most expensive option."
        )

if __name__ == "__main__":
    app = TaxCalculator()
    app.run()
