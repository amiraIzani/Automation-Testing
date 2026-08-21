"""
pages/safety_leading_indicator_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > Leading Indicator
(Reporting/Timesheet/StaticReport/Edit?Id=1309 (Static Input -- tanpa filter tbDate)).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/16_leading_indicator.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyLeadingIndicatorPage(HssSafetyPage):
    KUNCI = "leading_indicator"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "LeadingIndicators": "LeadingIndicators",
        "Target": "Target",
        "Bobot": "Bobot",
        "YTD": "YTD",
        "Corporate": "Corporate",
        "UBPEPongkor": "UBPEPongkor",
        "UBPBKalbar": "UBPBKalbar",
        "UBPNKolaka": "UBPNKolaka",
        "UBPNMalut": "UBPNMalut",
        "UBPNKonut": "UBPNKonut",
        "UBPPLm": "UBPPLm",
        "Geomin": "Geomin",
        "CSD": "CSD",
        "ICA": "ICA",
        "GagNikel": "GagNikel",
        "Haltim": "Haltim",
        "WKMD": "WKMD",
        "SDA": "SDA",
        "NKA": "NKA",
    }

    def buka(self):
        """Buka halaman Leading Indicator (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
