"""
tools/validasi_semua_halaman_safety.py
======================================
Buka SEMUA halaman Safety satu per satu lewat page object dan pastikan
tabelnya tampil. Output di-flush per halaman supaya kelihatan langsung
halaman mana yang macet.

    python tools/validasi_semua_halaman_safety.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.safety_lagging_indicator_page import SafetyLaggingIndicatorPage
from pages.safety_golden_rules_recap_page import SafetyGoldenRulesRecapPage
from pages.safety_emergency_drill_recap_page import SafetyEmergencyDrillRecapPage
from pages.safety_mwt_recapitulation_page import SafetyMwtRecapitulationPage
from pages.safety_recap_page import SafetyRecapPage
from pages.safety_incident_investigation_form_page import SafetyIncidentInvestigationFormPage
from pages.safety_initial_incident_accident_report_page import SafetyInitialIncidentAccidentReportPage
from pages.safety_witness_statement_report_page import SafetyWitnessStatementReportPage
from pages.safety_emergency_drill_daily_page import SafetyEmergencyDrillDailyPage
from pages.safety_master_alat_keselamatan_operasi_page import SafetyMasterAlatKeselamatanOperasiPage
from pages.safety_soc_recapitulation_page import SafetySocRecapitulationPage
from pages.safety_golden_rules_page import SafetyGoldenRulesPage
from pages.safety_data_rekap_statistik_k3_page import SafetyDataRekapStatistikK3Page
from pages.safety_kkp_p2k3_committee_meeting_page import SafetyKkpP2k3CommitteeMeetingPage
from pages.safety_mwt_daily_page import SafetyMwtDailyPage
from pages.safety_leading_indicator_page import SafetyLeadingIndicatorPage
from pages.safety_statistic_safety_recapitulation_page import SafetyStatisticSafetyRecapitulationPage
from pages.safety_smk3_page import SafetySmk3Page
from pages.safety_smkp_page import SafetySmkpPage

HALAMAN2 = [
    SafetyLaggingIndicatorPage, SafetyGoldenRulesRecapPage,
    SafetyEmergencyDrillRecapPage, SafetyMwtRecapitulationPage,
    SafetyRecapPage, SafetyIncidentInvestigationFormPage,
    SafetyInitialIncidentAccidentReportPage, SafetyWitnessStatementReportPage,
    SafetyEmergencyDrillDailyPage, SafetyMasterAlatKeselamatanOperasiPage,
    SafetySocRecapitulationPage, SafetyGoldenRulesPage,
    SafetyDataRekapStatistikK3Page, SafetyKkpP2k3CommitteeMeetingPage,
    SafetyMwtDailyPage, SafetyLeadingIndicatorPage,
    SafetyStatisticSafetyRecapitulationPage, SafetySmk3Page, SafetySmkpPage,
]


def main():
    options = Options()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=options)
    driver.switch_to.window(driver.window_handles[-1])

    hasil = []
    for cls in HALAMAN2:
        page = cls(driver)
        try:
            t0 = time.time()
            page.buka()
            if isinstance(page, SafetyRecapPage):
                ready = page.driver.execute_script(page._js_tampil(), "#tableBulanan", 10)
            else:
                ready = page.tabel_report_tampil()
            dur = round(time.time() - t0, 1)
            hasil.append((page.KUNCI, "OK" if ready else "TABEL TIDAK TAMPIL", dur))
        except Exception as exc:
            hasil.append((getattr(page, "KUNCI", "?"), "ERROR: " + str(exc)[:70], "-"))
        print(f"{'OK ' if hasil[-1][1] == 'OK' else '!! '} {hasil[-1][0]:<40} {hasil[-1][1]:<18} {hasil[-1][2]}", flush=True)

    ok = sum(1 for _, status, _ in hasil if status == "OK")
    print()
    print(f"BERHASIL: {ok}/{len(HALAMAN2)} halaman Safety terbuka dengan tabel tampil")


if __name__ == "__main__":
    main()
