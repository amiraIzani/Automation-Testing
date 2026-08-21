"""
pages/safety_smk3_page.py
==============================
Page object: Safety > Transaction > Lagging Indicator > SMK3
(Reporting/Timesheet/YearlyReport/Edit?Id=1308).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/18_smk3.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetySmk3Page(HssSafetyPage):
    KUNCI = "smk3"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "No": "No",
        "Month": "Month",
        "CompanyID": "CompanyID",
        "AuditExecutionDate": "AuditExecutionDate",
        "TotalScore": "TotalScore",
        "PPkomKetidaksesuaianMaj": "PPkomKetidaksesuaianMaj",
        "PPkomKetidaksesuaianMin": "PPkomKetidaksesuaianMin",
        "PPkomKesesuaian": "PPkomKesesuaian",
        "PPrenKetidaksesuaianMaj": "PPrenKetidaksesuaianMaj",
        "PPrenKetidaksesuaianMin": "PPrenKetidaksesuaianMin",
        "PPrenKesesuaian": "PPrenKesesuaian",
        "PPpenKetidaksesuaianMaj": "PPpenKetidaksesuaianMaj",
        "PPpenKetidaksesuaianMin": "PPpenKetidaksesuaianMin",
        "PPpenKesesuaian": "PPpenKesesuaian",
        "PdokKetidaksesuaianMaj": "PdokKetidaksesuaianMaj",
        "PdokKetidaksesuaianMin": "PdokKetidaksesuaianMin",
        "PdokKesesuaian": "PdokKesesuaian",
        "PPprodKetidaksesuaianMaj": "PPprodKetidaksesuaianMaj",
        "PPprodKetidaksesuaianMin": "PPprodKetidaksesuaianMin",
        "PPprodKesesuaian": "PPprodKesesuaian",
        "KBBsmkKetidaksesuaianMaj": "KBBsmkKetidaksesuaianMaj",
        "KBBsmkKetidaksesuaianMin": "KBBsmkKetidaksesuaianMin",
        "KBBsmkKesesuaian": "KBBsmkKesesuaian",
        "SpemKetidaksesuaianMaj": "SpemKetidaksesuaianMaj",
        "SpemKetidaksesuaianMin": "SpemKetidaksesuaianMin",
        "SpemKesesuaian": "SpemKesesuaian",
        "PPkekKetidaksesuaianMaj": "PPkekKetidaksesuaianMaj",
        "PPkekKetidaksesuaianMin": "PPkekKetidaksesuaianMin",
        "PPkekKesesuaian": "PPkekKesesuaian",
        "PMperpKetidaksesuaianMaj": "PMperpKetidaksesuaianMaj",
        "PMperpKetidaksesuaianMin": "PMperpKetidaksesuaianMin",
        "PMperpKesesuaian": "PMperpKesesuaian",
        "PPdatKetidaksesuaianMaj": "PPdatKetidaksesuaianMaj",
        "PPdatKetidaksesuaianMin": "PPdatKetidaksesuaianMin",
        "PPdatKesesuaian": "PPdatKesesuaian",
        "PSmkKetidaksesuaianMaj": "PSmkKetidaksesuaianMaj",
        "PSmkKetidaksesuaianMin": "PSmkKetidaksesuaianMin",
        "PSmkKesesuaian": "PSmkKesesuaian",
        "PKkemKetidaksesuaianMaj": "PKkemKetidaksesuaianMaj",
        "PKkemKetidaksesuaianMin": "PKkemKetidaksesuaianMin",
        "PKkemKesesuaian": "PKkemKesesuaian",
    }

    def buka(self):
        """Buka halaman SMK3 (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
