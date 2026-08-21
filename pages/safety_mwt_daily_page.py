"""
pages/safety_mwt_daily_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > MWT DAILY
(Reporting/Timesheet/MonthlyReport/Edit?Id=1312 (tanpa tombol Reload Data)).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/15_mwt_daily.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyMwtDailyPage(HssSafetyPage):
    KUNCI = "mwt_daily"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Date": "Date",
        "MoFLevel": "MoFLevel",
        "MoFID": "MoFID",
        "MoFName": "MoFName",
        "JenisAktivitas": "JenisAktivitas",
        "Location": "Location",
        "StrategicalImprovement": "StrategicalImprovement",
        "Description": "Description",
        "FileImage": "FileImage",
    }

    def buka(self):
        """Buka halaman MWT DAILY (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
