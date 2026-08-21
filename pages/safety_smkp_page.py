"""
pages/safety_smkp_page.py
==============================
Page object: Safety > Transaction > Lagging Indicator > SMKP
(Reporting/Timesheet/YearlyReport/Edit?Id=1307).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/19_smkp.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetySmkpPage(HssSafetyPage):
    KUNCI = "smkp"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "No": "No",
        "Month": "Month",
        "AuditExecutionDate": "AuditExecutionDate",
        "CompanyID": "CompanyID",
        "Deskripsi": "Deskripsi",
        "AuditKebijakan": "AuditKebijakan",
        "AuditPerencanaan": "AuditPerencanaan",
        "AuditOrganisasiPersonel": "AuditOrganisasiPersonel",
        "AuditImplementasi": "AuditImplementasi",
        "AuditEvaluasiTindakLanjut": "AuditEvaluasiTindakLanjut",
        "AuditDokumentasi": "AuditDokumentasi",
        "AuditTinjauanManajemenPeningkatanKinerja": "AuditTinjauanManajemenPeningkatanKinerja",
        "Total": "Total",
    }

    def buka(self):
        """Buka halaman SMKP (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
