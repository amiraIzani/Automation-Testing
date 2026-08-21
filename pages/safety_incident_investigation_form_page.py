"""
pages/safety_incident_investigation_form_page.py
==============================
Page object: Safety > Transaction > Leading Indicator > Incident Investigation Form
(Reporting/Timesheet/DailyReport/Edit?Id=1334. 6 tab: Data Insiden, Data Korban, Fakta & Analisis Penyebab, Kesimpulan & Usulan Investigasi, Rekomendasi & Tindakan Perbaikan, Saksi & Tim Investigasi).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/06_incident_investigation_form.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class SafetyIncidentInvestigationFormPage(HssSafetyPage):
    KUNCI = "incident_investigation_form"

    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
    KOLOM = {
        "NoInsiden": "NoInsiden",
        "Divisi": "Divisi",
        "NoUrutBukuKecelakaan": "NoUrutBukuKecelakaan",
        "PenggolonganInsiden": "PenggolonganInsiden",
        "TingkatKeparahan": "TingkatKeparahan",
        "IsNearmiss": "IsNearmiss",
        "NearmissDiinvestigasi": "NearmissDiinvestigasi",
        "AlasanNearmissTidakInvestigasi": "AlasanNearmissTidakInvestigasi",
        "KategoriInsiden": "KategoriInsiden",
        "HariKejadian": "HariKejadian",
        "TanggalKejadian": "TanggalKejadian",
        "JamKejadian": "JamKejadian",
        "Shift": "Shift",
        "Lokasi": "Lokasi",
        "AlatTerlibat": "AlatTerlibat",
        "AkibatInsiden": "AkibatInsiden",
        "PerkiraanHariKerjaHilang": "PerkiraanHariKerjaHilang",
        "BiayaLangsung": "BiayaLangsung",
        "BiayaTakLangsung": "BiayaTakLangsung",
        "TotalBiaya": "TotalBiaya",
        "LampiranBiaya": "LampiranBiaya",
        "JI_Terjatuh": "JI_Terjatuh",
        "JI_Tergilas": "JI_Tergilas",
        "JI_Terpukul": "JI_Terpukul",
        "JI_Terjepit": "JI_Terjepit",
        "JI_Tertusuk": "JI_Tertusuk",
        "JI_Terbentur": "JI_Terbentur",
        "JI_Terpotong": "JI_Terpotong",
        "JI_Tergigit": "JI_Tergigit",
        "JI_Tertimbun": "JI_Tertimbun",
        "JI_TerpelesetTergelincir": "JI_TerpelesetTergelincir",
        "JI_Terbakar": "JI_Terbakar",
        "JI_Tenggelam": "JI_Tenggelam",
        "JI_Keracunan": "JI_Keracunan",
        "JI_KemasukanBenda": "JI_KemasukanBenda",
        "JI_KejatuhanBenda": "JI_KejatuhanBenda",
        "JI_SuhuEkstrim": "JI_SuhuEkstrim",
        "JI_TersengatArusListrik": "JI_TersengatArusListrik",
        "JI_TerpaparTerkena": "JI_TerpaparTerkena",
        "JI_Lain": "JI_Lain",
        "SI_PermesinanPortable": "SI_PermesinanPortable",
        "SI_AlatAngkutOrang": "SI_AlatAngkutOrang",
        "SI_PesawatAngkatAngkut": "SI_PesawatAngkatAngkut",
        "SI_ApiTerbuka": "SI_ApiTerbuka",
        "SI_AlatAngkatDanAngkut": "SI_AlatAngkatDanAngkut",
        "SI_AlatMuatGaliAngkut": "SI_AlatMuatGaliAngkut",
        "SI_KendaraanAngkutanOrang": "SI_KendaraanAngkutanOrang",
        "SI_GasBeracunB3": "SI_GasBeracunB3",
        "SI_PeralatanFasilitasStatis": "SI_PeralatanFasilitasStatis",
        "SI_PesawatTenagaProduksi": "SI_PesawatTenagaProduksi",
        "SI_BahanAlatPeledak": "SI_BahanAlatPeledak",
        "SI_PerkakasManual": "SI_PerkakasManual",
        "SI_FaktorLingkungan": "SI_FaktorLingkungan",
        "SI_PerkakasOtomatis": "SI_PerkakasOtomatis",
        "SI_Lain": "SI_Lain",
        "KronologiKejadian": "KronologiKejadian",
        "LampiranSketsa": "LampiranSketsa",
        "TanggalPendaftaranInsiden": "TanggalPendaftaranInsiden",
        "NamaHSEAntam": "NamaHSEAntam",
        "NamaOHSManager": "NamaOHSManager",
        "NamaAMManagerTerkait": "NamaAMManagerTerkait",
        "NamaPimpinanTimInvestigasi": "NamaPimpinanTimInvestigasi",
        "NamaKTTWKTTGM": "NamaKTTWKTTGM",
    }

    # ---- tab internal halaman (klik pakai teks tab yang terlihat) ----
    TAB_DATA_INSIDEN = "Data Insiden"
    TAB_DATA_KORBAN = "Data Korban"
    TAB_FAKTA_ANALISIS = "Fakta & Analisis Penyebab"
    TAB_KESIMPULAN = "Kesimpulan & Usulan Investigasi"
    TAB_REKOMENDASI = "Rekomendasi & Tindakan Perbaikan"
    TAB_SAKSI_TIM = "Saksi & Tim Investigasi"

    def buka_tab(self, nama_tab):
        """Pindah ke tab halaman (mis. self.TAB_DATA_KORBAN)."""
        self.klik_tab(nama_tab)
        return self

    def buka(self):
        """Buka halaman Incident Investigation Form (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
