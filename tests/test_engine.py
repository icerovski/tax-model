import unittest
from engine import TaxInputs, calculate_taxes, BG_INCOME_TAX, BG_DIVIDEND_TAX

class TestTaxEngine(unittest.TestCase):
    def test_default_calculation(self):
        inputs = TaxInputs()
        results = calculate_taxes(inputs)
        
        # Gross: 150k + 20k + 0 + 50k = 220k
        self.assertEqual(results.total_gross, 220000.0)
        
        # LLC checks
        # Taxable consulting: 150k * 0.75 = 112,500
        # Monthly taxable consulting: 9375
        # MD Salary: 5000. Cap: 2352. Gap: 0.
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

if __name__ == "__main__":
    unittest.main()
