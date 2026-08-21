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
from pages.hss_safety_page import HssSafetyPage


# ------------------------------------------------------------------
# Factory halaman: kunci -> kelas page object. Dipakai test toolbar
# tombol supaya tiap halaman dibuka lewat buka() miliknya sendiri
# (Safety Recap punya alur buka custom, bukan table.reportData).
# ------------------------------------------------------------------
PAGE_OBJECTS = {
    "lagging_indicator": SafetyLaggingIndicatorPage,
    "golden_rules_recap": SafetyGoldenRulesRecapPage,
    "emergency_drill_recap": SafetyEmergencyDrillRecapPage,
    "mwt_recapitulation": SafetyMwtRecapitulationPage,
    "safety_recap": SafetyRecapPage,
    "incident_investigation_form": SafetyIncidentInvestigationFormPage,
    "initial_incident_accident_report": SafetyInitialIncidentAccidentReportPage,
    "witness_statement_report": SafetyWitnessStatementReportPage,
    "emergency_drill_daily": SafetyEmergencyDrillDailyPage,
    "master_alat_keselamatan_operasi": SafetyMasterAlatKeselamatanOperasiPage,
    "soc_recapitulation": SafetySocRecapitulationPage,
    "golden_rules": SafetyGoldenRulesPage,
    "data_rekap_statistik_k3": SafetyDataRekapStatistikK3Page,
    "safety_kkp_p2k3_committee_meeting": SafetyKkpP2k3CommitteeMeetingPage,
    "mwt_daily": SafetyMwtDailyPage,
    "leading_indicator": SafetyLeadingIndicatorPage,
    "statistic_safety_recapitulation": SafetyStatisticSafetyRecapitulationPage,
    "smk3": SafetySmk3Page,
    "smkp": SafetySmkpPage,
}

# Nama menu untuk id parametrize yang bisa dibaca (dipakai label hasil).
NAMA_HALAMAN = {
    "lagging_indicator": "Lagging Indicator",
    "golden_rules_recap": "Golden Rules Recap",
    "emergency_drill_recap": "Emergency Drill Recap",
    "mwt_recapitulation": "MWT Recapitulation",
    "safety_recap": "Safety Recap",
    "incident_investigation_form": "Incident Investigation",
    "initial_incident_accident_report": "Initial Incident/Accident",
    "witness_statement_report": "Witness Statement",
    "emergency_drill_daily": "Emergency Drill Daily",
    "master_alat_keselamatan_operasi": "Master Alat Keselamatan",
    "soc_recapitulation": "SOC Recapitulation",
    "golden_rules": "Golden Rules",
    "data_rekap_statistik_k3": "Data Rekap Statistik K3",
    "safety_kkp_p2k3_committee_meeting": "KKP/P2K3 Committee Meeting",
    "mwt_daily": "MWT Daily",
    "leading_indicator": "Leading Indicator",
    "statistic_safety_recapitulation": "Statistic Safety Recap",
    "smk3": "SMK3",
    "smkp": "SMKP",
}


def _buka_halaman(driver, kunci):
    """Buka halaman Safety `kunci` lewat page object miliknya."""
    return PAGE_OBJECTS[kunci](driver).buka()


def _ids_halaman(kunci_list):
    """List id yang bisa dibaca untuk parametrize (nama menu)."""
    return [NAMA_HALAMAN[k] for k in kunci_list]


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
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        [k for k, v in HssSafetyPage.TOMBOL_HALAMAN.items() if "Import" in v],
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_import_modal(self, driver, kunci_halaman):
        """Klik Import -> modal Import terbuka (link Download Template +
        input file) -> tutup -> modal hilang."""
        page = _buka_halaman(driver, kunci_halaman)
        page.buka_modal_import()
        assert page._ada_modal_tampil(), (
            f"Modal Import tidak terbuka di '{kunci_halaman}'"
        )
        assert page.is_visible(page.LINK_DOWNLOAD_TEMPLATE), (
            f"Link Download Template tidak ada di '{kunci_halaman}'"
        )
        # input file Bootstrap custom-file sengaja transparan (opacity 0)
        # -- cek PRESENCE, bukan visibility
        assert page.is_present(page.INPUT_FILE_IMPORT), (
            f"Input file import tidak ada di '{kunci_halaman}'"
        )
        page.tutup_modal()
        assert not page._ada_modal_tampil(), (
            f"Modal Import tidak tertutup di '{kunci_halaman}'"
        )

    # ------------------------------------------------------------------
    # Toolbar tombol per halaman ("bagian tombol pada fitur")
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        sorted(PAGE_OBJECTS),
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_tombol_toolbar(self, driver, kunci_halaman):
        """Semua tombol toolbar yang diharapkan tampil di halaman
        (daftar per halaman: HssSafetyPage.TOMBOL_HALAMAN -- hasil scan
        OPEL 2026-08-20)."""
        page = _buka_halaman(driver, kunci_halaman)
        hasil = page.cek_tombol_toolbar(kunci_halaman)
        hilang = [nama for nama, ok in hasil.items() if not ok]
        assert not hilang, (
            f"Halaman '{kunci_halaman}': tombol toolbar tidak tampil -> {hilang}"
        )

    @pytest.mark.safety
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        [k for k, v in HssSafetyPage.TOMBOL_HALAMAN.items() if "Reload Data" in v],
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_reload_data(self, driver, kunci_halaman):
        """Klik Reload Data -> overlay Processing hilang -> tabel tetap
        tampil (grid selesai dimuat ulang)."""
        page = _buka_halaman(driver, kunci_halaman)
        page.reload_data()
        assert page.tabel_report_tampil(), (
            f"Tabel tidak tampil setelah Reload Data di '{kunci_halaman}'"
        )

    @pytest.mark.safety
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        [k for k, v in HssSafetyPage.TOMBOL_HALAMAN.items() if "Create with Form" in v],
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_create_with_form_modal(self, driver, kunci_halaman):
        """Klik 'Create with Form' -> modal form terbuka -> Cancel ->
        modal tertutup (TANPA menyimpan data apa pun)."""
        page = _buka_halaman(driver, kunci_halaman)
        page.buka_form_create()
        assert page._ada_modal_tampil(), (
            f"Modal Create with Form tidak terbuka di '{kunci_halaman}'"
        )
        page.batal_form()
        assert not page._ada_modal_tampil(), (
            f"Modal tidak tertutup setelah Cancel di '{kunci_halaman}'"
        )

    @pytest.mark.safety
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        [k for k, v in HssSafetyPage.TOMBOL_HALAMAN.items() if "Columns" in v],
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_columns_dropdown(self, driver, kunci_halaman):
        """Klik Columns -> dropdown daftar kolom DataTables
        (div.dt-button-collection) muncul."""
        page = _buka_halaman(driver, kunci_halaman)
        page.buka_dropdown_columns()
        assert page.is_present(page.DROPDOWN_COLUMNS), (
            f"Dropdown Columns tidak muncul di '{kunci_halaman}'"
        )

    @pytest.mark.safety
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        [k for k, v in HssSafetyPage.TOMBOL_HALAMAN.items() if "FullScreen" in v],
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_fullscreen_toggle(self, driver, kunci_halaman):
        """Klik FullScreen -> panel grid jadi fullscreen (class
        panel-fullscreen); klik lagi -> kembali normal."""
        page = _buka_halaman(driver, kunci_halaman)
        page.toggle_fullscreen()
        assert page.tunggu_fullscreen(True), (
            f"Panel tidak fullscreen setelah klik FullScreen di '{kunci_halaman}'"
        )
        page.toggle_fullscreen()
        assert page.tunggu_fullscreen(False), (
            f"Panel tidak kembali normal setelah toggle kedua di '{kunci_halaman}'"
        )
