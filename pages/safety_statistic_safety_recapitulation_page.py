"""
pages/safety_statistic_safety_recapitulation_page.py
==============================
Page object: Safety > Transaction > Lagging Indicator > Statistic Safety Recapitulation
(Reporting/Timesheet/MonthlyReport/Edit?Id=1317).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/17_statistic_safety_recapitulation.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyStatisticSafetyRecapitulationPage(HssSafetyPage):
    KUNCI = "statistic_safety_recapitulation"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "Month": "Month",
        "TipePegawai": "TipePegawai",
        "FirstAidCase": "FirstAidCase",
        "MedicalTreatment": "MedicalTreatment",
        "Nearmiss": "Nearmiss",
        "KejadianBerbahaya": "KejadianBerbahaya",
        "TindakanTidakAman": "TindakanTidakAman",
        "KondisiTidakAman": "KondisiTidakAman",
        "PropertyDamage": "PropertyDamage",
        "JumlahTenagakerja": "JumlahTenagakerja",
        "JumlahJamKerjaKumulatif": "JumlahJamKerjaKumulatif",
        "JumlahHarikerjaHilang": "JumlahHarikerjaHilang",
        "FrequencyRate": "FrequencyRate",
        "SeverityRate": "SeverityRate",
        "AkibatPenyakitTenagaKerja": "AkibatPenyakitTenagaKerja",
        "TotalRecordableInjuryRate": "TotalRecordableInjuryRate",
        "FatalityRate": "FatalityRate",
        "SafeManhours": "SafeManhours",
        "PenyakitAkibatKerja": "PenyakitAkibatKerja",
        "MonthInt": "MonthInt",
        "JumlahAccidentRingan": "JumlahAccidentRingan",
        "JumlahAccidentBerat": "JumlahAccidentBerat",
        "JumlahAccidentMati": "JumlahAccidentMati",
    }

    def buka(self):
        """Buka halaman Statistic Safety Recapitulation (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
