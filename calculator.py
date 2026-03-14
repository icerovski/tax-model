from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Input, Label, Static, Checkbox, DataTable
from textual.reactive import reactive

class TaxCalculator(App):
    """A Textual TUI for the Bulgarian Global Entity Tax Model."""

    CSS = """
    Container {
        layout: horizontal;
    }
    VerticalScroll {
        width: 35%;
        padding: 1;
        border: solid green;
    }
    #results-pane {
        width: 65%;
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

    # General Reactive variables
    md_salary = reactive(5000.0)
    consulting_rev = reactive(150000.0)
    dividends = reactive(20000.0)
    bg_company_dividends = reactive(0.0)
    trading_profits = reactive(50000.0)
    is_us_dividend = reactive(True)
    is_eu_trading = reactive(False)
    client_withholds = reactive(True)

    # BVI Specific Reactive variables
    bvi_expenses = reactive(2500.0)
    bvi_payout_ratio = reactive(0.0) # Percentage 0-100

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
                yield Label("VARIABLE INPUTS (GENERAL)")
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
                
                yield Label("VARIABLE INPUTS (BVI)")
                yield Label("BVI Annual Expenses (€)")
                yield Input(value=str(self.bvi_expenses), id="bvi_expenses", type="number")
                yield Label("BVI Dividend Payout Ratio (%)")
                yield Input(value=str(self.bvi_payout_ratio), id="bvi_payout_ratio", type="number")

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
                yield Label("CALCULATION RESULTS: LLC vs BVI")
                yield DataTable(id="results-table")
                yield Static(id="explanation")

        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.add_columns("Line Item", "Wyoming LLC (€)", "BVI Company (€)", "Explanation / Notes")
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
            elif event.input.id == "bvi_expenses":
                self.bvi_expenses = val
            elif event.input.id == "bvi_payout_ratio":
                self.bvi_payout_ratio = max(0.0, min(100.0, val))
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
        # GROSS CALCULATION
        total_gross = self.consulting_rev + self.dividends + self.bg_company_dividends + self.trading_profits

        # --- MODEL A: WYOMING LLC (Flow-Through) ---
        # 1. Social Security Check
        taxable_consulting_annual_llc = self.consulting_rev * (1 - self.STATUTORY_DEDUCTION_CONSULTING)
        taxable_consulting_monthly_llc = taxable_consulting_annual_llc / 12
        monthly_gap_llc = max(0, self.MAX_SOC_SEC_CAP - self.md_salary)
        soc_sec_taxable_monthly_llc = min(taxable_consulting_monthly_llc, monthly_gap_llc)
        soc_sec_due_llc = soc_sec_taxable_monthly_llc * 12 * self.SOC_SEC_RATE
        
        # 2. Consulting Tax
        consulting_tax_liability_llc = taxable_consulting_annual_llc * self.BG_INCOME_TAX

        # 3. Dividend Tax
        us_withholding_llc = self.dividends * 0.15 if self.is_us_dividend else 0.0
        intl_dividend_tax_llc = 0.0 if self.is_us_dividend else self.dividends * self.BG_DIVIDEND_TAX
        bg_div_tax_withheld_llc = self.bg_company_dividends * self.BG_DIVIDEND_TAX
        total_div_tax_llc = (us_withholding_llc if self.is_us_dividend else intl_dividend_tax_llc) + bg_div_tax_withheld_llc

        # 4. Trading Tax
        trading_tax_due_llc = 0.0 if self.is_eu_trading else (self.trading_profits * (1 - self.STATUTORY_DEDUCTION_TRADING)) * self.BG_INCOME_TAX

        # Totals LLC
        total_tax_llc = soc_sec_due_llc + consulting_tax_liability_llc + total_div_tax_llc + trading_tax_due_llc
        total_expenses_llc = self.LLC_EXPENSES
        net_wealth_llc = total_gross - total_tax_llc - total_expenses_llc
        effective_rate_llc = (total_tax_llc / total_gross) * 100 if total_gross > 0 else 0


        # --- MODEL B: BVI COMPANY (Corporate Blocker) ---
        # Assuming "Effective Management" risk is completely solved, yielding 0% BG Corporate Tax.
        
        # Corporate level taxes & costs
        corporate_tax_bvi = 0.0
        soc_sec_due_bvi = 0.0 # Corporate revenue doesn't trigger BG Social Security
        
        # US/Intl Dividends Withholding at source (still happens to the BVI)
        us_withholding_bvi = self.dividends * 0.15 if self.is_us_dividend else 0.0
        # BG Dividends Withheld at source
        bg_div_tax_withheld_bvi = self.bg_company_dividends * self.BG_DIVIDEND_TAX
        
        # Pre-Distribution Corporate Net
        gross_retained_bvi = total_gross - us_withholding_bvi - bg_div_tax_withheld_bvi - self.bvi_expenses
        
        # Distribution Logic
        payout_amount_bvi = max(0, gross_retained_bvi * (self.bvi_payout_ratio / 100.0))
        bg_dividend_tax_bvi = payout_amount_bvi * self.BG_DIVIDEND_TAX
        
        # Totals BVI
        total_tax_bvi = us_withholding_bvi + bg_div_tax_withheld_bvi + bg_dividend_tax_bvi
        total_expenses_bvi = self.bvi_expenses
        trapped_in_bvi = gross_retained_bvi - payout_amount_bvi
        personal_wealth_bvi = payout_amount_bvi - bg_dividend_tax_bvi
        total_net_wealth_bvi = trapped_in_bvi + personal_wealth_bvi
        effective_rate_bvi = (total_tax_bvi / total_gross) * 100 if total_gross > 0 else 0


        # --- Update Table ---
        table = self.query_one("#results-table", DataTable)
        table.clear()
        table.add_rows([
            ("Gross Revenue", f"{total_gross:,.2f}", f"{total_gross:,.2f}", "Total structure inflows"),
            ("Fixed Expenses", f"{total_expenses_llc:,.2f}", f"{total_expenses_bvi:,.2f}", "Agent / ES Filings / CPA"),
            ("Social Security", f"{soc_sec_due_llc:,.2f}", f"{soc_sec_due_bvi:,.2f}", "LLC flows through to individual"),
            ("Consulting Tax (BG)", f"{consulting_tax_liability_llc:,.2f}", "0.00", "LLC gets 25% deduction; BVI is 0% corp"),
            ("Trading Tax (BG)", f"{trading_tax_due_llc:,.2f}", "0.00", "LLC gets 10% deduction; BVI is 0% corp"),
            ("Source Div Withholding", f"{total_div_tax_llc:,.2f}", f"{us_withholding_bvi + bg_div_tax_withheld_bvi:,.2f}", "US/BG source taxes applying to entity"),
            ("Dividend Payout to BG", "N/A (Flow)", f"{payout_amount_bvi:,.2f}", f"BVI Payout Ratio: {self.bvi_payout_ratio}%"),
            ("BG Dividend Tax", "0.00", f"{bg_dividend_tax_bvi:,.2f}", "5% Tax on distributed BVI profits"),
            ("Total Tax Burden", f"{total_tax_llc:,.2f}", f"{total_tax_bvi:,.2f}", f"Combined tax paid/withheld"),
            ("Net Tax Rate (%)", f"{effective_rate_llc:.2f}%", f"{effective_rate_bvi:.2f}%", "Total Tax / Total Gross"),
            ("Wealth: Personal", f"{net_wealth_llc:,.2f}", f"{personal_wealth_bvi:,.2f}", "Post-tax wealth in BG account"),
            ("Wealth: Corporate", "0.00", f"{trapped_in_bvi:,.2f}", "Untaxed funds retained in BVI"),
            ("TOTAL NET WEALTH", f"{net_wealth_llc:,.2f}", f"{total_net_wealth_bvi:,.2f}", "Total wealth across all accounts")
        ])

        # --- Update Explanation ---
        winner = "Wyoming LLC" if net_wealth_llc > total_net_wealth_bvi else "BVI Company"
        difference = abs(net_wealth_llc - total_net_wealth_bvi)

        privacy_warning = ""
        if self.bg_company_dividends > 0:
            privacy_warning = "\n\n[red][b]PRIVACY ALERT:[/b][/red] Owning a BG subsidiary triggers [b]mandatory UBO disclosure[/b] in the BG Commercial Register, exposing the structure."

        explanation = self.query_one("#explanation", Static)
        explanation.update(
            f"[b]STRATEGIC ANALYSIS[/b]\n\n"
            f"[b]Optimal Structure (Current Inputs):[/b] [green]{winner}[/green] by €{difference:,.2f}\n\n"
            f"1. [b]The Compounding Advantage:[/b] By keeping the BVI Payout Ratio at {self.bvi_payout_ratio}%, you trap €{trapped_in_bvi:,.2f} in a 0% tax environment for reinvestment. Wyoming forces immediate taxation on all revenue.\n"
            f"2. [b]The Consulting Penalty:[/b] Wyoming benefits from the 25% statutory deduction on consulting revenue (€{consulting_tax_liability_llc:,.2f} tax vs 5% on pure distribution). The BVI lacks this personal tax shield.\n"
            f"3. [b]The Social Security Factor:[/b] Your MD Salary shields €{self.md_salary:,.2f}/mo. You pay €{soc_sec_due_llc:,.2f} in Wyoming vs €0 in BVI.\n"
            f"4. [b]Compliance Drag:[/b] The BVI costs €{total_expenses_bvi:,.2f} vs Wyoming's €{total_expenses_llc:,.2f}, eroding small tax advantages."
            f"{privacy_warning}"
        )

if __name__ == "__main__":
    app = TaxCalculator()
    app.run()