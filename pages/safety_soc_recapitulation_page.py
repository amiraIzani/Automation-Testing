"""
pages/safety_soc_recapitulation_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > SOC RECAPITULATION
(Reporting/Timesheet/YearlyReport/Edit?Id=1310. Punya tombol ekstra 'Select Finding').

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/11_soc_recapitulation.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from selenium.webdriver.common.by import By

from pages.hss_safety_page import HssSafetyPage


class SafetySocRecapitulationPage(HssSafetyPage):
    KUNCI = "soc_recapitulation"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "No": "No",
        "Month": "Month",
        "MonthInt": "MonthInt",
        "Category": "Category",
        "Description": "Description",
        "Location": "Location",
        "Status": "Status",
        "CompanyID": "CompanyID",
        "ObserverID": "ObserverID",
        "ObserverLevel": "ObserverLevel",
        "ObserverName": "ObserverName",
    }

    # Tombol khusus halaman SOC (tidak ada di halaman lain).
    BTN_SELECT_FINDING = (By.XPATH, "//button[normalize-space(.)='Select Finding']")

    def buka(self):
        """Buka halaman SOC RECAPITULATION (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
