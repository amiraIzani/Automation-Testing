"""
pages/safety_mwt_recapitulation_page.py
==============================
Page object: Safety > Reporting > MWT RECAPITULATION
(Reporting/Timesheet/YearlyReport/View?Id=1323).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/04_mwt_recapitulation.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyMwtRecapitulationPage(HssSafetyPage):
    KUNCI = "mwt_recapitulation"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Month": "Month",
        "CompanyID": "CompanyID",
        "JenisAktivitas": "JenisAktivitas",
        "Location": "Location",
        "StrategicalImprovement": "StrategicalImprovement",
        "Description": "Description",
        "FileImage": "FileImage",
        "MoFLevel": "MoFLevel",
        "MoFID": "MoFID",
        "MoFName": "MoFName",
    }

    def buka(self):
        """Buka halaman MWT RECAPITULATION (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
