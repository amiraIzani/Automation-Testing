"""
tools/generate_safety_pages.py
==============================
Generator page object untuk SEMUA sub-halaman Safety (menu HSS) --
satu file per halaman di pages/safety_*_page.py.

Sumber data: reports/scan/safety/*.json (hasil scan website OPEL).
Jalankan ulang kalau scan diperbarui:
    python tools/generate_safety_pages.py
"""

import glob
import json
import os
import re
import textwrap

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN_DIR = os.path.join(BASE, "reports", "scan", "safety")
PAGES_DIR = os.path.join(BASE, "pages")

# (kunci, nama file scan, class name, judul menu, kategori, keterangan tambahan)
SPEC = [
    # ---------------- Reporting ----------------
    ("lagging_indicator", "01_lagging_indicator",
     "SafetyLaggingIndicatorPage", "Lagging Indicator",
     "Reporting",
     "Reporting/Timesheet/MonthlyReport/View?Id=1306"),
    ("golden_rules_recap", "02_golden_rules_recap",
     "SafetyGoldenRulesRecapPage", "GOLDEN RULES RECAP",
     "Reporting",
     "Reporting/Timesheet/YearlyReport/View?Id=1324"),
    ("emergency_drill_recap", "03_emergency_drill_recap",
     "SafetyEmergencyDrillRecapPage", "EMERGENCY DRILL Recap",
     "Reporting",
     "Reporting/Timesheet/YearlyReport/View?Id=1325"),
    ("mwt_recapitulation", "04_mwt_recapitulation",
     "SafetyMwtRecapitulationPage", "MWT RECAPITULATION",
     "Reporting",
     "Reporting/Timesheet/YearlyReport/View?Id=1323"),
    ("safety_recap", "05_safety_recap",
     "SafetyRecapPage", "Safety Recap.",
     "Reporting",
     "Reporting/Supersafe/HSSE/ReportingSafetyRecap (custom, bukan pola Timesheet)"),
    # ---------------- Transaction > Leading Indicator ----------------
    ("incident_investigation_form", "06_incident_investigation_form",
     "SafetyIncidentInvestigationFormPage", "Incident Investigation Form",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/DailyReport/Edit?Id=1334. 6 tab: Data Insiden, Data Korban, Fakta & Analisis Penyebab, Kesimpulan & Usulan Investigasi, Rekomendasi & Tindakan Perbaikan, Saksi & Tim Investigasi"),
    ("initial_incident_accident_report", "07_initial_incident_accident_report",
     "SafetyInitialIncidentAccidentReportPage", "Initial Incident/Accident Report",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/DailyReport/Edit?Id=1335"),
    ("witness_statement_report", "08_witness_statement_report",
     "SafetyWitnessStatementReportPage", "Witness Statement Report",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/DailyReport/Edit?Id=1336"),
    ("emergency_drill_daily", "09_emergency_drill_daily",
     "SafetyEmergencyDrillDailyPage", "EMERGENCY DRILL Daily",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/MonthlyReport/Edit?Id=1319"),
    ("master_alat_keselamatan_operasi", "10_master_alat_keselamatan_operasi",
     "SafetyMasterAlatKeselamatanOperasiPage", "Master Alat keselamatan Operasi",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/StaticReport/Edit?Id=1321 (Static Input -- tanpa filter tbDate)"),
    ("soc_recapitulation", "11_soc_recapitulation",
     "SafetySocRecapitulationPage", "SOC RECAPITULATION",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/YearlyReport/Edit?Id=1310. Punya tombol ekstra 'Select Finding'"),
    ("golden_rules", "12_golden_rules",
     "SafetyGoldenRulesPage", "GOLDEN RULES",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/MonthlyReport/Edit?Id=1316"),
    ("data_rekap_statistik_k3", "13_data_rekap_statistik_k3",
     "SafetyDataRekapStatistikK3Page", "Data Rekap Statistik K3",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/YearlyReport/Edit?Id=1315. 4 tab: Frequency Rate, Severity Rate, TRIR, Fatality Rate"),
    ("safety_kkp_p2k3_committee_meeting", "14_safety_kkp_p2k3_committee_meeting",
     "SafetyKkpP2k3CommitteeMeetingPage", "SAFETY/KKP/P2K3 COMMITTEE MEETING",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/YearlyReport/Edit?Id=1313"),
    ("mwt_daily", "15_mwt_daily",
     "SafetyMwtDailyPage", "MWT DAILY",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/MonthlyReport/Edit?Id=1312 (tanpa tombol Reload Data)"),
    ("leading_indicator", "16_leading_indicator",
     "SafetyLeadingIndicatorPage", "Leading Indicator",
     "Transaction > Leading Indicator",
     "Reporting/Timesheet/StaticReport/Edit?Id=1309 (Static Input -- tanpa filter tbDate)"),
    # ---------------- Transaction > Lagging Indicator ----------------
    ("statistic_safety_recapitulation", "17_statistic_safety_recapitulation",
     "SafetyStatisticSafetyRecapitulationPage", "Statistic Safety Recapitulation",
     "Transaction > Lagging Indicator",
     "Reporting/Timesheet/MonthlyReport/Edit?Id=1317"),
    ("smk3", "18_smk3",
     "SafetySmk3Page", "SMK3",
     "Transaction > Lagging Indicator",
     "Reporting/Timesheet/YearlyReport/Edit?Id=1308"),
    ("smkp", "19_smkp",
     "SafetySmkpPage", "SMKP",
     "Transaction > Lagging Indicator",
     "Reporting/Timesheet/YearlyReport/Edit?Id=1307"),
]


def ambil_kolom(nama_scan):
    """Ambil semua data-name kolom dari JSON scan."""
    path = os.path.join(SCAN_DIR, nama_scan + ".json")
    if not os.path.exists(path):
        return []
    data = json.load(open(path, encoding="utf-8"))
    kolom, seen = [], set()
    for e in data["elements"]:
        dn = e.get("data_name", "")
        if dn and dn not in seen:
            seen.add(dn)
            kolom.append(dn)
    return kolom


def buat_file(kunci, nama_scan, nama_kelas, judul, kategori, keterangan):
    kolom = ambil_kolom(nama_scan)
    nama_file = f"{kunci}_page.py" if kunci.startswith("safety_") else f"safety_{kunci}_page.py"
    header = f'''"""
pages/{nama_file}
==============================
Page object: Safety > {kategori} > {judul}
({keterangan}).

Semua locator hasil SCAN website OPEL (2026-08-20, v2.6.7):
    - data mentah : reports/scan/safety/{nama_scan}.md / .json / .png
    - dokumentasi : locators/hss_safety.md

Mewarisi locator umum dari HssSafetyPage (toolbar tbDate/cbDistrict,
tombol Export/Import/Submit, modal Import, dll).
"""

from pages.hss_safety_page import HssSafetyPage


class {nama_kelas}(HssSafetyPage):
    KUNCI = "{kunci}"

'''
    if kolom:
        # dict KOLOM: nama data-name -> data-name (1:1, dari th[data-name])
        # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{nilai}']")
        baris_kolom = ",\n".join(f'        "{dn}": "{dn}"' for dn in kolom)
        header += f'''    # Semua kolom tabel halaman ini (th[data-name], 1:1 dengan backend).
    # Locator kolom: (By.CSS_SELECTOR, "th[data-name='{{nilai}}']")
    KOLOM = {{
{baris_kolom},
    }}

'''
    # ---------- penyesuaian khusus per halaman ----------
    if kunci == "safety_recap":
        header += '''    # Halaman custom (bukan pola Timesheet): tabelnya
    # #tableBulanan / #tableTahunan (bukan table.reportData).
    TABLE_BULANAN = (By.ID, "tableBulanan")
    TABLE_TAHUNAN = (By.ID, "tableTahunan")
    LINK_BULANAN = (By.ID, "linkBulanan")
    LINK_TAHUNAN = (By.ID, "linkTahunan")

    def buka(self):
        """Buka halaman Safety Recap (tunggu tabel Bulanan tampil).
        Halaman ini kadang butuh fetch data lebih lama (pipeline
        Supersafe/HSSE) -- retry navigasi sekali kalau timeout."""
        url = config.BASE_URL.rstrip("/") + "/" + self.HALAMAN[self.KUNCI].lstrip("/")

        def _tunggu():
            self._wait(config.LONG_TIMEOUT).until(
                lambda d: self.driver.execute_script(self._js_tampil(), "#tableBulanan", 10),
                f"Tabel Bulanan tidak kunjung tampil di {url}",
            )

        self.driver.get(url)
        try:
            _tunggu()
        except TimeoutException:
            self.driver.get(url)
            _tunggu()
        return self

'''
        header = header.replace(
            "from pages.hss_safety_page import HssSafetyPage",
            "from selenium.webdriver.common.by import By\n"
            "from selenium.common.exceptions import TimeoutException\n\n"
            "from config import config\n"
            "from pages.hss_safety_page import HssSafetyPage",
        )

    if kunci == "incident_investigation_form":
        header += '''    # ---- tab internal halaman (klik pakai teks tab yang terlihat) ----
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

'''

    if kunci == "data_rekap_statistik_k3":
        header += '''    # ---- tab internal halaman ----
    TAB_FREQUENCY_RATE = "Frequency Rate"
    TAB_SEVERITY_RATE = "Severity Rate"
    TAB_TRIR = "TRIR"
    TAB_FATALITY_RATE = "Fatality Rate"

    def buka_tab(self, nama_tab):
        """Pindah ke tab statistik (mis. self.TAB_TRIR)."""
        self.klik_tab(nama_tab)
        return self

'''

    if kunci == "soc_recapitulation":
        header += '''    # Tombol khusus halaman SOC (tidak ada di halaman lain).
    BTN_SELECT_FINDING = (By.XPATH, "//button[normalize-space(.)='Select Finding']")

'''
        header = header.replace(
            "from pages.hss_safety_page import HssSafetyPage",
            "from selenium.webdriver.common.by import By\n\n"
            "from pages.hss_safety_page import HssSafetyPage",
        )

    if kunci != "safety_recap":
        header += f'''    def buka(self):
        """Buka halaman {judul} (tunggu tabel DataTables tampil)."""
        self.buka_halaman(self.KUNCI)
        return self
'''
    nama_file = os.path.join(PAGES_DIR, nama_file)
    with open(nama_file, "w", encoding="utf-8") as f:
        f.write(header)
    return nama_file, len(kolom)


def main():
    dibuat = []
    for kunci, nama_scan, nama_kelas, judul, kategori, ket in SPEC:
        nama_file, n_kolom = buat_file(kunci, nama_scan, nama_kelas, judul, kategori, ket)
        dibuat.append((nama_file, n_kolom))
        print(f"[OK] {os.path.basename(nama_file)} (kolom: {n_kolom})")
    print(f"\nTotal {len(dibuat)} file page object dibuat di pages/")


if __name__ == "__main__":
    main()
