"""
pages/safety_golden_rules_recap_page.py
==============================
Page object: Safety > Reporting > GOLDEN RULES RECAP
(Reporting/Timesheet/YearlyReport/View?Id=1324).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/02_golden_rules_recap.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyGoldenRulesRecapPage(HssSafetyPage):
    KUNCI = "golden_rules_recap"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Month": "Month",
        "CompanyID": "CompanyID",
        "CriticalControlVerification": "CriticalControlVerification",
        "Location": "Location",
        "ComplianceScore": "ComplianceScore",
        "VId": "VId",
        "VName": "VName",
        "FUTemporaryStopWorking": "FUTemporaryStopWorking",
        "FUAllNCFollowedUp": "FUAllNCFollowedUp",
    }

    def buka(self):
        """Buka halaman GOLDEN RULES RECAP (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
