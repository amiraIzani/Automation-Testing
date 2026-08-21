"""
pages/safety_golden_rules_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > GOLDEN RULES
(Reporting/Timesheet/MonthlyReport/Edit?Id=1316).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/12_golden_rules.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyGoldenRulesPage(HssSafetyPage):
    KUNCI = "golden_rules"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Date": "Date",
        "VId": "VId",
        "VName": "VName",
        "CriticalControlVerification": "CriticalControlVerification",
        "Location": "Location",
        "ComplianceScore": "ComplianceScore",
        "FUTemporaryStopWorking": "FUTemporaryStopWorking",
        "FUAllNCFollowedUp": "FUAllNCFollowedUp",
        "FileImage": "FileImage",
    }

    def buka(self):
        """Buka halaman GOLDEN RULES (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
