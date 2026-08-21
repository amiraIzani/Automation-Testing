"""
pages/safety_emergency_drill_recap_page.py
==============================
Page object: Safety > Reporting > EMERGENCY DRILL Recap
(Reporting/Timesheet/YearlyReport/View?Id=1325).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/03_emergency_drill_recap.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyEmergencyDrillRecapPage(HssSafetyPage):
    KUNCI = "emergency_drill_recap"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Month": "Month",
        "CompanyID": "CompanyID",
        "Tanggal": "Tanggal",
        "JenisSimulasi": "JenisSimulasi",
        "RingkasanSkenario": "RingkasanSkenario",
        "LessonLearned": "LessonLearned",
        "FollowupPlan": "FollowupPlan",
    }

    def buka(self):
        """Buka halaman EMERGENCY DRILL Recap (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
