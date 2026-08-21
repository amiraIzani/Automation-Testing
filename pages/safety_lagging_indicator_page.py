"""
pages/safety_lagging_indicator_page.py
==============================
Page object: Safety > Reporting > Lagging Indicator
(Reporting/Timesheet/MonthlyReport/View?Id=1306).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/01_lagging_indicator.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyLaggingIndicatorPage(HssSafetyPage):
    KUNCI = "lagging_indicator"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "LaggingIndicators": "LaggingIndicators",
        "Target": "Target",
        "Bobot": "Bobot",
        "YTD": "YTD",
        "Corporate": "Corporate",
        "AT08": "AT08",
        "AT01": "AT01",
        "AT02": "AT02",
        "AT09": "AT09",
        "AT12": "AT12",
        "AT05": "AT05",
        "AT07": "AT07",
        "CSD": "CSD",
        "ICA": "ICA",
        "GAG": "GAG",
        "Haltim": "Haltim",
        "WKMD": "WKMD",
        "SDA": "SDA",
        "NKA": "NKA",
    }

    def buka(self):
        """Buka halaman Lagging Indicator (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
