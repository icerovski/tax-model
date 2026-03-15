import unittest
from engine import TaxInputs, calculate_taxes, BG_INCOME_TAX, BG_DIVIDEND_TAX

class TestTaxEngine(unittest.TestCase):
    def test_default_calculation(self):
        inputs = TaxInputs()
        results = calculate_taxes(inputs)

        # Gross: 150k consulting + 0 dividends + 0 bg dividends + 0 trading = 150k
        self.assertEqual(results.total_gross, 150000.0)

        # LLC checks
        # Taxable consulting: 150k * 0.75 = 112,500
        # Monthly taxable consulting: 9375
        # MD Salary: 11000. Cap: 2352. Gap: 0.
        # Soc Sec: 0
        self.assertEqual(results.soc_sec_due_llc, 0.0)
        self.assertAlmostEqual(results.consulting_tax_llc, 112500 * BG_INCOME_TAX)

    def test_low_salary_triggers_soc_sec(self):
        # Salary 0, Cap 2352. Gap 2352.
        inputs = TaxInputs(md_salary=0.0)
        results = calculate_taxes(inputs)
        # 2352 * 12 * 0.278 = 7847.04
        self.assertAlmostEqual(results.soc_sec_due_llc, 2352.0 * 12 * 0.278)

    def test_bvi_payout_logic(self):
        # 100% payout
        inputs = TaxInputs(bvi_payout_ratio=100.0, solve_management_risk=True)
        results = calculate_taxes(inputs)

        # If 100% payout, trapped in BVI should be 0 (excluding withholding at source)
        self.assertEqual(results.trapped_in_bvi, 0.0)

    def test_poem_risk_trigger(self):
        inputs = TaxInputs(solve_management_risk=False)
        results = calculate_taxes(inputs)
        # Corporate tax should be > 0 if POEM risk is not solved
        self.assertGreater(results.corporate_tax_bvi, 0.0)

    def test_privacy_breach_bg_subsidiary(self):
        inputs = TaxInputs(bg_company_dividends=1000.0)
        results = calculate_taxes(inputs)
        self.assertIn("LOW", results.privacy_llc)
        self.assertIn("LOW", results.privacy_bvi)

    def test_zero_revenue_edge_case(self):
        # Test to ensure effective_rate calculation doesn't throw ZeroDivisionError
        inputs = TaxInputs(consulting_rev=0.0, dividends=0.0, bg_company_dividends=0.0, trading_profits=0.0)
        results = calculate_taxes(inputs)

        self.assertEqual(results.total_gross, 0.0)
        self.assertEqual(results.effective_rate_llc, 0.0)
        self.assertEqual(results.effective_rate_bvi, 0.0)
        # Net wealth should reflect only expenses since revenue is 0
        self.assertEqual(results.net_wealth_llc, -inputs.llc_expenses)

    def test_negative_trading_profits(self):
        # Test how the model handles trading losses
        inputs = TaxInputs(trading_profits=-10000.0)
        results = calculate_taxes(inputs)

        # Gross should reflect the loss
        self.assertEqual(results.total_gross, 140000.0) # 150k consulting - 10k trading loss

        # BVI should not pay corporate tax on a net loss if overall profit is negative
        inputs_heavy_loss = TaxInputs(consulting_rev=0.0, trading_profits=-50000.0, solve_management_risk=False)
        results_heavy_loss = calculate_taxes(inputs_heavy_loss)
        self.assertEqual(results_heavy_loss.corporate_tax_bvi, 0.0)

    def test_bvi_payout_ratio_limits(self):
        # Test extreme payout ratios
        inputs = TaxInputs(bvi_payout_ratio=150.0) # User types 150% in the engine bypassing UI limit

        # In engine.py, if the UI doesn't cap it, does the engine handle it?
        # Currently, the engine just multiplies by (ratio / 100), meaning it would calculate 150% payout.
        # Let's ensure the UI is the only place it's capped, or ideally, add a cap in the engine later.
        # For now, we test the math holds true to the input.
        results = calculate_taxes(inputs)

        # Trapped in BVI is max(0, retained - payout). If payout > retained, trapped is 0.
        self.assertEqual(results.trapped_in_bvi, 0.0)

if __name__ == "__main__":
    unittest.main()
