"""
pages/safety_initial_incident_accident_report_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > Initial Incident/Accident Report
(Reporting/Timesheet/DailyReport/Edit?Id=1335).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/07_initial_incident_accident_report.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyInitialIncidentAccidentReportPage(HssSafetyPage):
    KUNCI = "initial_incident_accident_report"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "NoInsiden": "NoInsiden",
        "NamaKorban": "NamaKorban",
        "Jabatan": "Jabatan",
        "DeptPerusahaan": "DeptPerusahaan",
        "Umur": "Umur",
        "MasaKerja": "MasaKerja",
        "Alamat": "Alamat",
        "NoUnit": "NoUnit",
        "LokasiKejadian": "LokasiKejadian",
        "TanggalKejadian": "TanggalKejadian",
        "JamKejadian": "JamKejadian",
        "Shift": "Shift",
        "Kerusakan": "Kerusakan",
        "Cidera": "Cidera",
        "KronologisKejadian": "KronologisKejadian",
        "PhotoDokumenSketsa": "PhotoDokumenSketsa",
        "TanggalPelaporan": "TanggalPelaporan",
        "SelisihHariPelaporan": "SelisihHariPelaporan",
        "NamaYangMembuatKeterangan": "NamaYangMembuatKeterangan",
        "NamaDilaporkanOleh": "NamaDilaporkanOleh",
        "NamaDiperiksaOleh": "NamaDiperiksaOleh",
        "NamaDiketahuiOleh": "NamaDiketahuiOleh",
    }

    def buka(self):
        """Buka halaman Initial Incident/Accident Report (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
