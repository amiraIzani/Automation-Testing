"""
pages/safety_emergency_drill_daily_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > EMERGENCY DRILL Daily
(Reporting/Timesheet/MonthlyReport/Edit?Id=1319).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/09_emergency_drill_daily.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyEmergencyDrillDailyPage(HssSafetyPage):
    KUNCI = "emergency_drill_daily"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Tanggal": "Tanggal",
        "JenisSimulasi": "JenisSimulasi",
        "RingkasanSkenario": "RingkasanSkenario",
        "LessonLearned": "LessonLearned",
        "FollowupPlan": "FollowupPlan",
    }

    def buka(self):
        """Buka halaman EMERGENCY DRILL Daily (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
