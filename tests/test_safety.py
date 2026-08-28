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
from selenium.common.exceptions import TimeoutException

from config import config

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
from pages.hss_safety_page import HssSafetyPage, TidakPunyaAkses


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
    """Buka halaman Safety `kunci` lewat page object miliknya.
    Kalau tidak punya akses, otomatis kembali (driver.back) dan skip."""
    try:
        return PAGE_OBJECTS[kunci](driver).buka()
    except TidakPunyaAkses as e:
        pytest.skip(str(e))


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
        # Chrome memakai profil dengan session-restore: tab halaman
        # terakhir bisa terbuka lagi saat browser start, dan halaman
        # Timesheet yang ter-restore bisa masih loading saat menu
        # diklik (gagal 2026-08-27). Mulai dari dashboard yang SUDAH
        # dimuat penuh dulu supaya test deterministik.
        page.driver.get(config.BASE_URL)
        page._wait(config.LONG_TIMEOUT).until(
            lambda _: page.is_any_visible(page.MENU_HSS),
            "Sidebar (menu HSS) tidak muncul setelah buka dashboard",
        )
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
        try:
            page = SafetyLaggingIndicatorPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Lagging Indicator tidak tampil"
        assert page.is_visible(page.FILTER_TANGGAL), "Filter tanggal tidak tampil"
        assert page.is_visible(page.FILTER_UNIT), "Filter unit tidak tampil"

    @pytest.mark.safety_view
    def test_safety_golden_rules_recap_view(self, driver):
        try:
            page = SafetyGoldenRulesRecapPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel GOLDEN RULES RECAP tidak tampil"

    @pytest.mark.safety_view
    def test_safety_emergency_drill_recap_view(self, driver):
        try:
            page = SafetyEmergencyDrillRecapPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel EMERGENCY DRILL Recap tidak tampil"

    @pytest.mark.safety_view
    def test_safety_mwt_recapitulation_view(self, driver):
        try:
            page = SafetyMwtRecapitulationPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel MWT RECAPITULATION tidak tampil"

    @pytest.mark.safety_view
    def test_safety_recap_view(self, driver):
        try:
            page = SafetyRecapPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert driver.execute_script(page._js_tampil(), "#tableBulanan", 10), \
            "Tabel Safety Recap (Bulanan) tidak tampil"
        assert page.is_visible(page.FILTER_BULAN), "Filter bulan tidak tampil"
        assert page.is_visible(page.FILTER_TAHUN), "Filter tahun tidak tampil"

    # ------------------------------------------------------------------
    # Transaction - Leading Indicator
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_incident_investigation_view(self, driver):
        try:
            page = SafetyIncidentInvestigationFormPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Incident Investigation tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_incident_investigation_tab(self, driver):
        try:
            page = SafetyIncidentInvestigationFormPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        page.buka_tab(page.TAB_DATA_KORBAN)
        tab = page.find((page.TAB[0], page.TAB[1].format(teks_tab=page.TAB_DATA_KORBAN)))
        assert "active" in (tab.get_attribute("class") or ""), "Tab Data Korban tidak aktif"

    # ------------------------------------------------------------------
    # Buka SEMUA tab di halaman yang punya banyak tab (1 per halaman,
    # jeda 2.5 detik per tab supaya bisa diikuti mata)
    # ------------------------------------------------------------------
    TAB_HALAMAN = {
        "incident_investigation_form": "tab_incident_investigation",
        "data_rekap_statistik_k3": "tab_data_rekap_statistik_k3",
        "witness_statement_report": "tab_witness_statement_report",
        "safety_recap": "tab_safety_recap",
    }

    @pytest.mark.safety
    @pytest.mark.parametrize(
        "kunci_halaman",
        sorted(TAB_HALAMAN),
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_buka_semua_tab(self, driver, test_data, kunci_halaman):
        """Buka SETIAP tab di halaman yang punya banyak tab dan
        pastikan tabnya jadi aktif (data panel ikut berpindah)."""
        page = _buka_halaman(driver, kunci_halaman)
        daftar_tab = test_data["hss_safety"][self.TAB_HALAMAN[kunci_halaman]]
        for teks_tab in daftar_tab:
            page.klik_tab(teks_tab)
            tab = page.find(
                (page.TAB[0], page.TAB[1].format(teks_tab=teks_tab))
            )
            assert "active" in (tab.get_attribute("class") or ""), (
                f"Tab '{teks_tab}' tidak aktif di '{kunci_halaman}'"
            )

    @pytest.mark.safety_transaction
    def test_safety_initial_incident_view(self, driver):
        try:
            page = SafetyInitialIncidentAccidentReportPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Initial Incident/Accident tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_witness_statement_view(self, driver):
        try:
            page = SafetyWitnessStatementReportPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Witness Statement tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_emergency_drill_daily_view(self, driver):
        try:
            page = SafetyEmergencyDrillDailyPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel EMERGENCY DRILL Daily tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_master_alat_view(self, driver):
        try:
            page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Master Alat tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_master_alat_create(self, driver, test_data):
        """Create with Form: field diisi OTOMATIS dengan data dummy
        (combo lookup pilih baris pertama, Capacity angka, Equipment
        No unik per run) -> Save -> Submit Changes -> baris baru harus
        muncul di tabel."""
        data = test_data["hss_safety"]["master_alat"]
        equip = data["equipment_prefix"] + time.strftime("%H%M%S")
        try:
            page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
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
    def test_safety_master_alat_delete(self, driver, test_data):
        """Contoh fitur HAPUS (hanya Master Alat yang punya tombol
        Delete per baris): klik Delete di baris dummy -> dialog
        konfirmasi muncul ('Do you wish to delete this record ?') ->
        jawab Yes -> baris HILANG dari tampilan grid (alur UI fitur
        Delete berjalan).

        CATATAN 2026-08-26 (perilaku aplikasi DEV): penghapusan TIDAK
        disimpan ke server -- setelah reload halaman baris muncul
        lagi. Dicek menyeluruh lewat probe (tools/probe_masalah6/9.py):
        klik Delete + Yes + tunggu 20 detik, maupun + Submit Changes,
        tidak mengubah data server sama sekali. Karena itu test ini
        TIDAK lagi bisa membersihkan baris dummy yang menumpuk (tidak
        mungkin lewat UI saat ini) -- test memverifikasi alur fitur
        Delete APA ADANYA, dan assert terakhir jadi ALARM kalau
        aplikasi mulai benar-benar menghapus (saat itu test diupdate
        kembali menjadi verifikasi cleanup penuh).

        Kalau tidak ada baris dummy sama sekali (test dijalankan
        SENDIRIAN), SATU baris dummy dibuat dulu lewat Create with
        Form -- test mandiri dan tidak pernah skip."""
        data = test_data["hss_safety"]["master_alat"]
        try:
            page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        page.reset_cari_grid()
        # TUNGGU baris benar2 ter-render sebelum menghitung dummy --
        # hitungan sebelum data selesai dimuat AJAX = 0 palsu (pernah
        # membuat test menciptakan dummy ekstra, 2026-08-26).
        page._wait(config.LONG_TIMEOUT).until(
            lambda _: driver.execute_script(
                f"const t = {page.JS_GRID};"
                "return t ? t.querySelectorAll('tbody tr').length > 0 : false;"
            )
        )

        def _jumlah_dummy():
            return page.driver.execute_script(
                f"const t = {page.JS_GRID};"
                "return t ? [...t.querySelectorAll('tbody tr')]"
                ".filter(tr => {"
                "  const teks = tr.innerText;"
                "  const nilai = [...tr.querySelectorAll('input')]"
                "    .map(i => i.value || '').join(' ');"
                "  return teks.includes('AUTO-TEST') || teks.includes('Dummy')"
                "    || nilai.includes('AUTO-TEST') || nilai.includes('Dummy');"
                "}).length : 0;"
            )

        def _klik_delete_dummy():
            """Klik tombol Delete baris dummy PERTAMA yang ketemu
            (cek teks + nilai input sel)."""
            return page.driver.execute_script(
                f"const t = {page.JS_GRID};"
                "if (!t) return false;"
                "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
                "  const teks = r.innerText;"
                "  const nilai = [...r.querySelectorAll('input')]"
                "    .map(i => i.value || '').join(' ');"
                "  return teks.includes('AUTO-TEST') || teks.includes('Dummy')"
                "    || nilai.includes('AUTO-TEST') || nilai.includes('Dummy');"
                "});"
                "if (!tr) return false;"
                "const b = tr.querySelector('a.btn-delete');"
                "if (b) { b.click(); return true; }"
                "return false;"
            )

        if _jumlah_dummy() == 0:
            # mandiri: buat 1 dummy dulu (alur sama dengan test create)
            equip = data["equipment_prefix"] + time.strftime("%H%M%S")
            page.buka_form_create()
            page.isi_form_create_otomatis(tambahan={"Equipment No": equip})
            page.simpan_form()
            page.submit_changes()
            page.tunggu_processing_selesai()
            page.buka_halaman("master_alat_keselamatan_operasi")
            page.reset_cari_grid()
            page._wait(config.LONG_TIMEOUT).until(
                lambda _: driver.execute_script(
                    f"const t = {page.JS_GRID};"
                    "return t ? t.querySelectorAll('tbody tr').length > 0"
                    " : false;"
                )
            )
            assert _jumlah_dummy() >= 1, (
                "Baris dummy gagal dibuat untuk contoh hapus"
            )

        sebelum = _jumlah_dummy()
        assert sebelum >= 1, "Tidak ada baris dummy untuk contoh hapus"
        assert _klik_delete_dummy(), (
            "Tombol Delete tidak ada di baris dummy"
        )
        page.pace(1.0)
        page.jawab_konfirmasi()   # Yes pada dialog konfirmasi
        # Baris HILANG dari tampilan grid (alur UI fitur Delete).
        page._wait(config.LONG_TIMEOUT).until(
            lambda _: _jumlah_dummy() < sebelum,
            "Baris dummy tidak hilang dari grid setelah Delete + Yes",
        )
        # Reload: aplikasi DEV TIDAK menyimpan penghapusan ke server
        # (dicek 2026-08-26, lihat docstring) -- baris MUNCUL lagi.
        # Assert ini jadi ALARM kalau perilaku aplikasi berubah jadi
        # benar2 menghapus -> saat itu update test jadi verifikasi
        # cleanup penuh.
        page.buka_halaman("master_alat_keselamatan_operasi")
        page.reset_cari_grid()
        page._wait(config.LONG_TIMEOUT).until(
            lambda _: driver.execute_script(
                f"const t = {page.JS_GRID};"
                "return t ? t.querySelectorAll('tbody tr').length > 0"
                " : false;"
            )
        )
        sesudah = _jumlah_dummy()
        assert sesudah >= sebelum, (
            "Perilaku delete BERUBAH: aplikasi sekarang menyimpan "
            f"penghapusan ke server ({sebelum} -> {sesudah} baris dummy). "
            "Update test ini untuk memverifikasi cleanup penuh."
        )

    @pytest.mark.safety_transaction
    def test_safety_soc_recapitulation_view(self, driver):
        try:
            page = SafetySocRecapitulationPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel SOC RECAPITULATION tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_golden_rules_view(self, driver):
        try:
            page = SafetyGoldenRulesPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel GOLDEN RULES tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_data_rekap_k3_view(self, driver):
        try:
            page = SafetyDataRekapStatistikK3Page(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Data Rekap Statistik K3 tidak tampil"
        page.buka_tab(page.TAB_TRIR)
        tab = page.find((page.TAB[0], page.TAB[1].format(teks_tab=page.TAB_TRIR)))
        assert "active" in (tab.get_attribute("class") or ""), "Tab TRIR tidak aktif"

    @pytest.mark.safety_transaction
    def test_safety_kkp_p2k3_view(self, driver):
        try:
            page = SafetyKkpP2k3CommitteeMeetingPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel SAFETY/KKP/P2K3 tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_mwt_daily_view(self, driver):
        try:
            page = SafetyMwtDailyPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel MWT DAILY tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_leading_indicator_view(self, driver):
        try:
            page = SafetyLeadingIndicatorPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Leading Indicator tidak tampil"

    # ------------------------------------------------------------------
    # Transaction - Lagging Indicator
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_statistic_safety_view(self, driver):
        try:
            page = SafetyStatisticSafetyRecapitulationPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel Statistic Safety tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_smk3_view(self, driver):
        try:
            page = SafetySmk3Page(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel SMK3 tidak tampil"
        assert page.is_visible(page.BTN_SUBMIT), "Tombol Submit Changes tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_smkp_view(self, driver):
        try:
            page = SafetySmkpPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert page.tabel_report_tampil(), "Tabel SMKP tidak tampil"

    # ------------------------------------------------------------------
    # Lagging Indicator - test MENDALAM (semua fitur per halaman)
    # ------------------------------------------------------------------
    # (kunci halaman, tanggal uji filter, field grid yang diedit,
    #  anchor baris {field: nilai}, nilai uji edit, edit_tersimpan)
    # Catatan 2026-08-24:
    #  - Baris bulan dipakai BULAN JULI (data DEV memang baru lengkap
    #    sejak Juli -- bulan-bulan awal bisa kosong).
    #  - Baris dicari lewat ANCHOR, bukan data-rowindex: urutan baris
    #    bisa diubah ulang aplikasi setelah Submit.
    #  - nilai_uji = None artinya dihitung otomatis = nilai awal + 1
    #    (field angka yang terbukti editable & bisa di-revert).
    #  - Filter unit TIDAK dites ganti nilai: select cbDistrict di
    #    halaman ini terkunci oleh aplikasi (semua opsi disabled) --
    #    cukup diverifikasi elemennya ada + punya opsi.
    # Catatan 2026-08-26 (edit_tersimpan=False untuk Statistic):
    #  - Halaman Statistic (template MonthlyReport) TIDAK menyimpan
    #    perubahan inline lewat Submit Changes -- ketikan masuk ke sel
    #    ('4' -> '5' terbaca segera), tapi setelah Submit + reload
    #    nilainya kembali ke '4' (dicek tools/probe_masalah5.py;
    #    kontrol SMK3 menyimpan '7' normal). Alur edit TETAP DICOBA
    #    di Statistic (permintaan user: semua fitur dicoba), hanya
    #    verifikasinya = data tidak rusak (tetap nilai awal).
    LAGGING_DEEP = [
        ("statistic_safety_recapitulation", "2026-07", "PenyakitAkibatKerja",
         {"Month": "July", "TipePegawai": "Pegawai"}, None, False),
        ("smk3", "2026", "PPkomKetidaksesuaianMaj", {"Month": "Juli"}, None,
         True),
        ("smkp", "2026", "Deskripsi", {"Month": "Juli"}, "AUTO-TEST", True),
    ]

    @pytest.mark.safety
    @pytest.mark.safety_transaction
    @pytest.mark.parametrize(
        "kunci, tanggal_uji, field_edit, anchor, nilai_uji, edit_tersimpan",
        LAGGING_DEEP,
        ids=[k for k, _, _, _, _, _ in LAGGING_DEEP],
    )
    def test_safety_lagging_deep(
        self, driver, test_data, kunci, tanggal_uji, field_edit,
        anchor, nilai_uji, edit_tersimpan
    ):
        """Semua fitur halaman Lagging: view tabel -> edit grid inline
        + Submit Changes (nilai uji diverifikasi masuk, lalu
        DIKEMBALIKAN ke nilai awal supaya data DEV tidak berubah) ->
        filter tanggal -> filter unit (verifikasi elemen) -> Export
        (file terunduh) -> Import (buka modal + template terunduh,
        tanpa unggah data -- upload import menulis ke DEV, sengaja
        dihindari)."""
        page = _buka_halaman(driver, kunci)
        assert page.tabel_report_tampil(), f"Tabel '{kunci}' tidak tampil"

        def _tunggu_anchor():
            """Tunggu input sel anchor benar2 ter-render di grid utama
            (baris bisa muncul dulu dengan input belum dibuat -- nilai
            diisi AJAX belakangan, bacaan '' palsu 2026-08-26)."""
            page._wait(config.LONG_TIMEOUT).until(
                lambda _: page._ambil_elemen_sel_anchor(field_edit, anchor)
                is not None,
                f"Baris {anchor} di '{kunci}' tidak kunjung ter-render",
            )

        # 1) Edit grid inline -> Submit Changes -> verifikasi -> revert
        #    (verifikasi dibaca SETELAH reload halaman: bacaan grid
        #    langsung pasca-submit tidak andal -- state sampah sementara,
        #    data asli baru terlihat setelah reload, 2026-08-24)
        page.reset_cari_grid()
        _tunggu_anchor()
        nilai_awal = page.baca_sel_grid_anchor(field_edit, anchor)
        if not nilai_awal:
            # Field target di baris anchor KOSONG (data DEV berubah --
            # 2026-08-27: PPkomKetidaksesuaianMaj SMK3 & Deskripsi SMKP
            # bulan Juli kosong). Pindah ke baris LAIN yang field-nya
            # terisi supaya fitur edit tetap dites sungguhan (tetap
            # di-revert, data DEV tidak rusak).
            anchor_baru = page.cari_anchor_field_terisi(field_edit, anchor)
            assert anchor_baru, (
                f"Field '{field_edit}' kosong di baris {anchor} dan tidak "
                f"ada baris lain yang terisi di '{kunci}'"
            )
            anchor = anchor_baru
            nilai_awal = page.baca_sel_grid_anchor(field_edit, anchor)
        assert nilai_awal, (
            f"Field '{field_edit}' di baris {anchor} tidak terbaca di '{kunci}'"
        )
        if nilai_uji is None:
            # field angka: nilai uji = nilai awal + 1 jika angka, atau '1' jika kosong
            try:
                nilai_uji = str(int(float(nilai_awal)) + 1)
            except (ValueError, TypeError):
                nilai_uji = "1"
        page.isi_sel_grid_anchor(field_edit, nilai_uji, anchor)
        page.submit_changes()
        page.buka_halaman(kunci)
        _tunggu_anchor()
        if edit_tersimpan:
            assert page.baca_sel_grid_anchor(field_edit, anchor) == nilai_uji, (
                f"Edit '{field_edit}' = '{nilai_uji}' tidak tersimpan setelah "
                "Submit Changes"
            )
            page.isi_sel_grid_anchor(field_edit, nilai_awal, anchor)
            page.submit_changes()
            page.buka_halaman(kunci)
            _tunggu_anchor()
            assert page.baca_sel_grid_anchor(field_edit, anchor) == nilai_awal, (
                f"Nilai '{field_edit}' tidak kembali ke '{nilai_awal}' "
                "setelah revert"
            )
        else:
            # halaman yang tidak menyimpan perubahan inline (template
            # MonthlyReport): alur edit + Submit tetap DICOBA, dan
            # verifikasinya = data TIDAK rusak (nilai tetap awal).
            # Kalau aplikasi suatu saat mulai menyimpan, kembalikan
            # nilainya seperti semula (2026-08-26).
            baca = page.baca_sel_grid_anchor(field_edit, anchor)
            if baca != nilai_awal:
                page.isi_sel_grid_anchor(field_edit, nilai_awal, anchor)
                page.submit_changes()
                page.buka_halaman(kunci)
                _tunggu_anchor()
                assert page.baca_sel_grid_anchor(field_edit, anchor) == nilai_awal, (
                    f"Nilai '{field_edit}' tidak kembali ke '{nilai_awal}' "
                    "setelah revert"
                )

        # 1b) Cancel: buat perubahan pending -> klik Cancel -> perubahan
        #     TIDAK tersimpan (data tetap nilai awal)
        nilai_sebelum_cancel = page.baca_sel_grid_anchor(field_edit, anchor)
        page.isi_sel_grid_anchor(field_edit, nilai_uji, anchor)
        page.click_js_saat_tampil(page.BTN_CANCEL_GRID)
        page.jawab_konfirmasi()
        page.tunggu_processing_selesai()
        page.buka_halaman(kunci)
        _tunggu_anchor()
        assert page.baca_sel_grid_anchor(field_edit, anchor) == nilai_sebelum_cancel, (
            f"Perubahan '{field_edit}' masih tersimpan padahal Cancel "
            "sudah diklik"
        )

        # 2) Filter tanggal -> value berubah & tabel tetap tampil ->
        #    kembalikan
        tanggal_awal = page.baca_filter_tanggal()
        page.set_filter_tanggal(tanggal_uji)
        page.tunggu_processing_selesai()
        assert page.baca_filter_tanggal() == tanggal_uji, (
            f"Filter tanggal tidak berubah ke '{tanggal_uji}' di '{kunci}'"
        )
        assert page.tabel_report_tampil(), (
            f"Tabel '{kunci}' tidak tampil setelah filter tanggal '{tanggal_uji}'"
        )
        page.set_filter_tanggal(tanggal_awal)
        page.tunggu_processing_selesai()
        assert page.tabel_report_tampil(), (
            f"Tabel '{kunci}' tidak tampil setelah filter tanggal dikembalikan"
        )

        # 3) Filter unit -> elemen ada + punya opsi (penggantian nilai
        #    terkunci aplikasi di halaman ini). Cek lewat _ambil_js_visible
        #    (memindai SEMUA match #cbDistrict) -- selector global bisa
        #    salah sasaran ke match pertama yang tersembunyi (2026-08-26).
        try:
            page._ambil_js_visible(page.FILTER_UNIT)
        except TimeoutException:
            raise AssertionError(f"Select unit tidak tampil di '{kunci}'")
        jumlah_opsi = driver.execute_script(
            "const sels = [...document.querySelectorAll('#cbDistrict')];"
            "const s = sels.find(el => {"
            "  const r = el.getBoundingClientRect();"
            "  return r.width > 0 && r.height > 0;"
            "}) || sels[0];"
            "return s ? s.options.length : 0;"
        )
        assert jumlah_opsi > 0, f"Select unit '{kunci}' tidak punya opsi"

        # 4) Export -> file benar2 terunduh
        file_export = page.export_dan_tunggu_file()
        assert file_export, f"File export '{kunci}' tidak terunduh"

        # 5) Import -> modal terbuka + template terunduh (tanpa unggah)
        page.buka_modal_import()
        assert page.is_visible(page.LINK_DOWNLOAD_TEMPLATE), (
            f"Link Download Template tidak ada di '{kunci}'"
        )
        file_template = page.download_template_import()
        assert file_template, f"File template import '{kunci}' tidak terunduh"
        page.tutup_modal()

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
        sorted(PAGE_OBJECTS),
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_coba_semua_tombol(self, driver, kunci_halaman):
        """SETIAP tombol fitur halaman DIKLIK satu per satu sesuai
        daftar HssSafetyPage.TOMBOL_HALAMAN (permintaan user
        2026-08-24), dengan jeda 2.5 detik antar-aksi supaya alur
        bisa diikuti mata. Aksi tiap tombol:
          Reload Data    -> klik + tunggu tabel dimuat ulang
          Import         -> modal terbuka lalu ditutup
          Create         -> baris draft bertambah lalu Cancel
          Create w/ Form -> modal form terbuka lalu Cancel
          Submit Changes -> klik (tanpa perubahan pending = aman)
          Export         -> file Excel terunduh ke folder unduhan
          Export Excel   -> (Safety Recap) file terunduh
          Instructions   -> diklik, apa pun yang muncul ditutup
          Select Finding -> (SOC) modal lookup terbuka lalu ditutup
          Columns        -> dropdown daftar kolom buka lalu tutup
          FullScreen     -> masuk fullscreen lalu kembali normal
          Cancel         -> diklik (tanpa pending = aman)"""
        page = _buka_halaman(driver, kunci_halaman)
        daftar = HssSafetyPage.TOMBOL_HALAMAN[kunci_halaman]
        for nama in daftar:
            page.coba_tombol(nama)
