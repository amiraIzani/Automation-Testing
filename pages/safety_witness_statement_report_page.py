"""
pages/safety_witness_statement_report_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > Witness Statement Report
(Reporting/Timesheet/DailyReport/Edit?Id=1336).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/08_witness_statement_report.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyWitnessStatementReportPage(HssSafetyPage):
    KUNCI = "witness_statement_report"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "NoInsiden": "NoInsiden",
        "JenisSaksi": "JenisSaksi",
        "NamaSaksi": "NamaSaksi",
        "NIK": "NIK",
        "NomorID": "NomorID",
        "Jabatan": "Jabatan",
        "Perusahaan": "Perusahaan",
        "DepartemenDivisi": "DepartemenDivisi",
        "TempatTanggalLahir": "TempatTanggalLahir",
        "Umur": "Umur",
        "JenisKelamin": "JenisKelamin",
        "LamanyaBekerjaPadaJabatan": "LamanyaBekerjaPadaJabatan",
        "PengalamanBekerja": "PengalamanBekerja",
        "Tupoksi": "Tupoksi",
        "LokasiKerja": "LokasiKerja",
        "GiliranShift": "GiliranShift",
        "AlamatDapatDihubungi": "AlamatDapatDihubungi",
        "NamaPengawasLangsung": "NamaPengawasLangsung",
        "HariTanggalKejadian": "HariTanggalKejadian",
        "TanggalWaktuWawancara": "TanggalWaktuWawancara",
        "NomorUrutWawancara": "NomorUrutWawancara",
        "RingkasanInsiden": "RingkasanInsiden",
        "KeteranganRingkas": "KeteranganRingkas",
        "KondisiKesehatanSaksi": "KondisiKesehatanSaksi",
        "TempatPernyataan": "TempatPernyataan",
        "TanggalPernyataan": "TanggalPernyataan",
        "NamaPewawancara": "NamaPewawancara",
        "NIKPewawancara": "NIKPewawancara",
        "JabatanPewawancara": "JabatanPewawancara",
        "LampiranTandaTangan": "LampiranTandaTangan",
    }

    def buka(self):
        """Buka halaman Witness Statement Report (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
