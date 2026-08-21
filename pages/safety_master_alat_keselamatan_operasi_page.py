"""
pages/safety_master_alat_keselamatan_operasi_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > Master Alat keselamatan Operasi
(Reporting/Timesheet/StaticReport/Edit?Id=1321 (Static Input -- tanpa filter tbDate)).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/10_master_alat_keselamatan_operasi.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyMasterAlatKeselamatanOperasiPage(HssSafetyPage):
    KUNCI = "master_alat_keselamatan_operasi"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "EquipmentNumber": "EquipmentNumber",
        "Location": "Location",
        "Type": "Type",
        "Capacity": "Capacity",
    }

    def buka(self):
        """Buka halaman Master Alat keselamatan Operasi (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
