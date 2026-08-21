"""
tests/test_safety.py
====================
Test smoke (view) untuk SEMUA halaman bagian Safety di menu HSS OPEL.

Setiap test: buka halaman lewat page object -> pastikan tabel
DataTables tampil (berarti halaman + data berhasil dirender).
Locator yang dipakai adalah hasil scan website (2026-08-20) --
lihat locators/hss_safety.md dan pages/safety_*_page.py.

Jalankan:
    pytest -k safety                          # semua test safety
    pytest -k safety_smk3                     # satu halaman saja
    pytest tests/test_safety.py -m safety_view
"""

import time

import pytest

from selenium.webdriver.common.by import By

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


@pytest.mark.e2e
@pytest.mark.safety
class TestSafetyHss:

    # ------------------------------------------------------------------
    # Navigasi menu sidebar HSS > Safety
    # ------------------------------------------------------------------
    @pytest.mark.safety
    def test_safety_menu_dan_landing(self, driver):
        """Klik menu sidebar HSS -- pastikan submenu Safety (dengan
        anak Reporting & Transaction) muncul di sidebar."""
        from pages.hss_safety_page import HssSafetyPage

        page = HssSafetyPage(driver)
        page.buka_menu_hss_safety()
        # submenu Safety punya 2 anak: Reporting & Transaction
        assert page.is_any_visible(
            (By.XPATH, "//span[normalize-space(text())='Reporting']"), timeout=5
        ), "Submenu Reporting tidak muncul setelah klik HSS > Safety"
        assert page.is_any_visible(
            (By.XPATH, "//span[normalize-space(text())='Transaction']"), timeout=5
        ), "Submenu Transaction tidak muncul setelah klik HSS > Safety"

    # ------------------------------------------------------------------
    # Reporting (view / read-only)
    # ------------------------------------------------------------------
    @pytest.mark.safety_view
    def test_safety_lagging_indicator_view(self, driver):
        page = SafetyLaggingIndicatorPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Lagging Indicator tidak tampil"
        assert page.is_visible(page.FILTER_TANGGAL), "Filter tanggal tidak tampil"
        assert page.is_visible(page.FILTER_UNIT), "Filter unit tidak tampil"

    @pytest.mark.safety_view
    def test_safety_golden_rules_recap_view(self, driver):
        page = SafetyGoldenRulesRecapPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel GOLDEN RULES RECAP tidak tampil"

    @pytest.mark.safety_view
    def test_safety_emergency_drill_recap_view(self, driver):
        page = SafetyEmergencyDrillRecapPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel EMERGENCY DRILL Recap tidak tampil"

    @pytest.mark.safety_view
    def test_safety_mwt_recapitulation_view(self, driver):
        page = SafetyMwtRecapitulationPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel MWT RECAPITULATION tidak tampil"

    @pytest.mark.safety_view
    def test_safety_recap_view(self, driver):
        page = SafetyRecapPage(driver).buka()
        assert driver.execute_script(page._js_tampil(), "#tableBulanan", 10), \
            "Tabel Safety Recap (Bulanan) tidak tampil"
        assert page.is_visible(page.FILTER_BULAN), "Filter bulan tidak tampil"
        assert page.is_visible(page.FILTER_TAHUN), "Filter tahun tidak tampil"

    # ------------------------------------------------------------------
    # Transaction - Leading Indicator
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_incident_investigation_view(self, driver):
        page = SafetyIncidentInvestigationFormPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Incident Investigation tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_incident_investigation_tab(self, driver):
        page = SafetyIncidentInvestigationFormPage(driver).buka()
        page.buka_tab(page.TAB_DATA_KORBAN)
        tab = page.find((page.TAB[0], page.TAB[1].format(teks_tab=page.TAB_DATA_KORBAN)))
        assert "active" in (tab.get_attribute("class") or ""), "Tab Data Korban tidak aktif"

    @pytest.mark.safety_transaction
    def test_safety_initial_incident_view(self, driver):
        page = SafetyInitialIncidentAccidentReportPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Initial Incident/Accident tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_witness_statement_view(self, driver):
        page = SafetyWitnessStatementReportPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Witness Statement tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_emergency_drill_daily_view(self, driver):
        page = SafetyEmergencyDrillDailyPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel EMERGENCY DRILL Daily tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_master_alat_view(self, driver):
        page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Master Alat tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_master_alat_create(self, driver, test_data):
        """Create with Form: field diisi OTOMATIS dengan data dummy
        (combo lookup pilih baris pertama, Capacity angka, Equipment
        No unik per run) -> Save -> Submit Changes -> baris baru harus
        muncul di tabel."""
        data = test_data["hss_safety"]["master_alat"]
        equip = data["equipment_prefix"] + time.strftime("%H%M%S")
        page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        page.buka_form_create()
        page.isi_form_create_otomatis(tambahan={"Equipment No": equip})
        page.simpan_form()
        # Save menutup modal & memasukkan baris ke grid sebagai draft --
        # Submit Changes untuk benar2 menyimpan, lalu tunggu grid reload.
        page.submit_changes()
        page.tunggu_processing_selesai()
        # Baris baru bisa jatuh di halaman lain (pagination) -- cari via
        # DataTables API yang query-nya sampai ke server.
        page.cari_di_grid(equip)
        assert page.tabel_berisi(equip), (
            f"Data '{equip}' tidak muncul di tabel setelah Save + Submit"
        )

    @pytest.mark.safety_transaction
    def test_safety_master_alat_export(self, driver, test_data):
        """Filter unit -> Reload Data -> Export: file unduhan harus
        muncul di folder unduhan project (config.DOWNLOAD_DIR)."""
        page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        page.pilih_unit(test_data["hss_safety"]["filter_unit_default"])
        page.reload_data()
        file_unduh = page.export_dan_tunggu_file()
        assert file_unduh, "File export tidak muncul di folder unduhan"

    @pytest.mark.safety_transaction
    def test_safety_soc_recapitulation_view(self, driver):
        page = SafetySocRecapitulationPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel SOC RECAPITULATION tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_golden_rules_view(self, driver):
        page = SafetyGoldenRulesPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel GOLDEN RULES tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_data_rekap_k3_view(self, driver):
        page = SafetyDataRekapStatistikK3Page(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Data Rekap Statistik K3 tidak tampil"
        page.buka_tab(page.TAB_TRIR)
        tab = page.find((page.TAB[0], page.TAB[1].format(teks_tab=page.TAB_TRIR)))
        assert "active" in (tab.get_attribute("class") or ""), "Tab TRIR tidak aktif"

    @pytest.mark.safety_transaction
    def test_safety_kkp_p2k3_view(self, driver):
        page = SafetyKkpP2k3CommitteeMeetingPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel SAFETY/KKP/P2K3 tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_mwt_daily_view(self, driver):
        page = SafetyMwtDailyPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel MWT DAILY tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_leading_indicator_view(self, driver):
        page = SafetyLeadingIndicatorPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Leading Indicator tidak tampil"

    # ------------------------------------------------------------------
    # Transaction - Lagging Indicator
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_statistic_safety_view(self, driver):
        page = SafetyStatisticSafetyRecapitulationPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel Statistic Safety tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_smk3_view(self, driver):
        page = SafetySmk3Page(driver).buka()
        assert page.tabel_report_tampil(), "Tabel SMK3 tidak tampil"
        assert page.is_visible(page.BTN_SUBMIT), "Tombol Submit Changes tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_smkp_view(self, driver):
        page = SafetySmkpPage(driver).buka()
        assert page.tabel_report_tampil(), "Tabel SMKP tidak tampil"

    # ------------------------------------------------------------------
    # Modal Import (pola sama di semua halaman transaction)
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_import_modal(self, driver):
        page = SafetySmk3Page(driver).buka()
        page.click(page.BTN_IMPORT)
        assert page.is_visible(page.MODAL_IMPORT), "Modal Import tidak terbuka"
        assert page.is_visible(page.LINK_DOWNLOAD_TEMPLATE), "Link Download Template tidak ada"
        # input file Bootstrap custom-file sengaja transparan (opacity 0)
        # -- cek PRESENCE, bukan visibility
        assert page.is_present(page.INPUT_FILE_IMPORT), "Input file import tidak ada"
        page.tutup_modal()
        assert not page.is_visible(page.MODAL_IMPORT, timeout=2), "Modal Import tidak tertutup"
