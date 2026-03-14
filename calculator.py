from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Label, Static, Checkbox, DataTable
from textual.reactive import reactive

class TaxCalculator(App):
    """A Textual TUI for the Bulgarian/Wyoming Tax Model."""

    CSS = """
    Container {
        layout: horizontal;
    }
    VerticalScroll {
        width: 40%;
        padding: 1;
        border: solid green;
    }
    #results-pane {
        width: 60%;
        padding: 1;
        border: solid blue;
    }
    .input-group {
        margin-bottom: 1;
    }
    Label {
        margin-top: 1;
        text-style: bold;
    }
    #explanation {
        margin-top: 2;
        padding: 1;
        background: $boost;
        border: round $accent;
        height: auto;
    }
    """

    # Reactive variables for calculation inputs
    md_salary = reactive(5000.0)
    consulting_rev = reactive(150000.0)
    dividends = reactive(20000.0)
    bg_company_dividends = reactive(0.0)
    trading_profits = reactive(50000.0)
    is_us_dividend = reactive(True)
    is_eu_trading = reactive(False)
    client_withholds = reactive(True)

    # Constants (2026 Euro)
    BG_INCOME_TAX = 0.10
    BG_DIVIDEND_TAX = 0.05
    STATUTORY_DEDUCTION_CONSULTING = 0.25
    STATUTORY_DEDUCTION_TRADING = 0.10
    MAX_SOC_SEC_CAP = 2352.0  # Using the later 2026 figure
    SOC_SEC_RATE = 0.278
    LLC_EXPENSES = 1200.0

    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            with VerticalScroll():
                yield Label("VARIABLE INPUTS")
                yield Label("Monthly MD Salary (€)")
                yield Input(value=str(self.md_salary), id="md_salary", type="number")
                yield Label("Annual Consulting Revenue (€)")
                yield Input(value=str(self.consulting_rev), id="consulting_rev", type="number")
                yield Label("Annual Dividends (US/Intl) (€)")
                yield Input(value=str(self.dividends), id="dividends", type="number")
                yield Label("Annual BG Company Dividends (€)")
                yield Input(value=str(self.bg_company_dividends), id="bg_company_dividends", type="number")
                yield Label("Annual Trading Profits (€)")
                yield Input(value=str(self.trading_profits), id="trading_profits", type="number")
                
                yield Label("OPTIONS")
                yield Checkbox("US Sourced Dividends (15% US Withholding)", value=self.is_us_dividend, id="is_us_dividend")
                yield Checkbox("EU/EEA Regulated Trading (0% Tax)", value=self.is_eu_trading, id="is_eu_trading")
                yield Checkbox("BG Client Withholds 10%", value=self.client_withholds, id="client_withholds")

                yield Label("FIXED INFORMATION (2026)")
                yield Static(f"• Income Tax Rate: {self.BG_INCOME_TAX*100}%")
                yield Static(f"• Dividend Tax Rate: {self.BG_DIVIDEND_TAX*100}%")
                yield Static(f"• Social Security Cap: €{self.MAX_SOC_SEC_CAP}/mo")
                yield Static(f"• Consulting Deduction: {self.STATUTORY_DEDUCTION_CONSULTING*100}%")
                yield Static(f"• LLC Annual Expenses: €{self.LLC_EXPENSES}")

            with Vertical(id="results-pane"):
                yield Label("CALCULATION RESULTS")
                yield DataTable(id="results-table")
                yield Static(id="explanation")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Line Item", "Amount (€)", "Notes")
        self.update_calculations()

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            val = float(event.value) if event.value else 0.0
            if event.input.id == "md_salary":
                self.md_salary = val
            elif event.input.id == "consulting_rev":
                self.consulting_rev = val
            elif event.input.id == "dividends":
                self.dividends = val
            elif event.input.id == "bg_company_dividends":
                self.bg_company_dividends = val
            elif event.input.id == "trading_profits":
                self.trading_profits = val
            self.update_calculations()
        except ValueError:
            pass

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "is_us_dividend":
            self.is_us_dividend = event.value
        elif event.checkbox.id == "is_eu_trading":
            self.is_eu_trading = event.value
        elif event.checkbox.id == "client_withholds":
            self.client_withholds = event.value
        self.update_calculations()

    def update_calculations(self) -> None:
        # 1. Social Security Check
        taxable_consulting_annual = self.consulting_rev * (1 - self.STATUTORY_DEDUCTION_CONSULTING)
        taxable_consulting_monthly = taxable_consulting_annual / 12
        monthly_gap = max(0, self.MAX_SOC_SEC_CAP - self.md_salary)
        soc_sec_taxable_monthly = min(taxable_consulting_monthly, monthly_gap)
        soc_sec_due = soc_sec_taxable_monthly * 12 * self.SOC_SEC_RATE
        
        # 2. Consulting Tax
        consulting_tax_liability = taxable_consulting_annual * self.BG_INCOME_TAX
        client_withheld_amount = self.consulting_rev * self.BG_INCOME_TAX if self.client_withholds else 0.0

        # 3. Dividend Tax
        us_withholding = self.dividends * 0.15 if self.is_us_dividend else 0.0
        intl_dividend_tax = 0.0 if self.is_us_dividend else self.dividends * self.BG_DIVIDEND_TAX
        bg_div_tax_withheld = self.bg_company_dividends * self.BG_DIVIDEND_TAX

        # 4. Trading Tax
        trading_tax_due = 0.0 if self.is_eu_trading else (self.trading_profits * (1 - self.STATUTORY_DEDUCTION_TRADING)) * self.BG_INCOME_TAX

        # Totals
        total_tax_paid_or_due = (soc_sec_due + consulting_tax_liability + 
                                 (us_withholding if self.is_us_dividend else intl_dividend_tax) + 
                                 bg_div_tax_withheld + trading_tax_due)
        
        total_gross = self.consulting_rev + self.dividends + self.bg_company_dividends + self.trading_profits
        true_net_wealth = total_gross - total_tax_paid_or_due - self.LLC_EXPENSES
        effective_rate = (total_tax_paid_or_due / total_gross) * 100 if total_gross > 0 else 0

        # Update Table
        table = self.query_one("#results-table", DataTable)
        table.clear()
        table.add_rows([
            ("Gross Revenue", f"{total_gross:,.2f}", "Total structure inflows"),
            ("Social Security", f"{soc_sec_due:,.2f}", "Shielded by MD salary" if soc_sec_due == 0 else "Based on gap to cap"),
            ("Consulting Tax", f"{consulting_tax_liability:,.2f}", f"10% on 75% base"),
            ("Intl Dividend Tax", f"{us_withholding if self.is_us_dividend else intl_dividend_tax:,.2f}", "US Treaty (15%)" if self.is_us_dividend else "BG Tax (5%)"),
            ("BG Div Withheld", f"{bg_div_tax_withheld:,.2f}", "5% Tax paid by BG subsidiary"),
            ("Trading Tax", f"{trading_tax_due:,.2f}", "EU Exempt" if self.is_eu_trading else "10% on 90% base"),
            ("LLC Running Costs", f"{self.LLC_EXPENSES:,.2f}", "Fixed setup/agent costs"),
            ("Total Tax Burden", f"{total_tax_paid_or_due:,.2f}", f"Effective Rate: {effective_rate:.2f}%"),
            ("Net Wealth", f"{true_net_wealth:,.2f}", "Retained after all taxes/costs")
        ])

        # Update Explanation
        privacy_warning = ""
        if self.bg_company_dividends > 0:
            privacy_warning = "\n[red][b]PRIVACY ALERT:[/b][/red] Owning a BG company via LLC triggers [b]mandatory UBO disclosure[/b] in the BG Commercial Register."

        explanation = self.query_one("#explanation", Static)
        explanation.update(
            f"[b]Key Steps to Final Result:[/b]\n\n"
            f"1. [b]MD Shield:[/b] Social security is capped at €{self.MAX_SOC_SEC_CAP:,.2f}/mo. You pay €{soc_sec_due:,.2f}.\n"
            f"2. [b]BG Dividends:[/b] The subsidiary withholds 5%. No extra tax in US. Personal BG return shows this as 'credited'.\n"
            f"3. [b]Fixed Costs:[/b] You pay €{self.LLC_EXPENSES:,.2f} per year for the Wyoming Agent and US CPA (Form 5472).\n"
            f"4. [b]Consulting:[/b] Revenue through LLC is treated as personal income in BG with a 25% deduction."
            f"{privacy_warning}"
        )

if __name__ == "__main__":
    app = TaxCalculator()
    app.run()
