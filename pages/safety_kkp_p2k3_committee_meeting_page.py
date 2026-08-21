"""
pages/safety_kkp_p2k3_committee_meeting_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > SAFETY/KKP/P2K3 COMMITTEE MEETING
(Reporting/Timesheet/YearlyReport/Edit?Id=1313).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/14_safety_kkp_p2k3_committee_meeting.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyKkpP2k3CommitteeMeetingPage(HssSafetyPage):
    KUNCI = "safety_kkp_p2k3_committee_meeting"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Month": "Month",
        "Unit": "Unit",
        "Date": "Date",
        "MLLevel": "MLLevel",
        "MLID": "MLID",
        "MLName": "MLName",
        "NumberofAttendee": "NumberofAttendee",
        "Topic": "Topic",
        "StrategicalImprovement": "StrategicalImprovement",
        "MOMMeeting": "MOMMeeting",
        "PdfLink": "PdfLink",
        "Description": "Description",
    }

    def buka(self):
        """Buka halaman SAFETY/KKP/P2K3 COMMITTEE MEETING (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
