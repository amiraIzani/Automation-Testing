"""
pages/safety_data_rekap_statistik_k3_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > Data Rekap Statistik K3
(Reporting/Timesheet/YearlyReport/Edit?Id=1315. 4 tab: Frequency Rate, Severity Rate, TRIR, Fatality Rate).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/13_data_rekap_statistik_k3.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyDataRekapStatistikK3Page(HssSafetyPage):
    KUNCI = "data_rekap_statistik_k3"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Month": "Month",
        "Target": "Target",
        "Actual": "Actual",
    }

    # ---- tab internal halaman ----
    TAB_FREQUENCY_RATE = "Frequency Rate"
    TAB_SEVERITY_RATE = "Severity Rate"
    TAB_TRIR = "TRIR"
    TAB_FATALITY_RATE = "Fatality Rate"

    def buka_tab(self, nama_tab):
        """Pindah ke tab statistik (mis. self.TAB_TRIR)."""
        self.klik_tab(nama_tab)
        return self

    def buka(self):
        """Buka halaman Data Rekap Statistik K3 (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
