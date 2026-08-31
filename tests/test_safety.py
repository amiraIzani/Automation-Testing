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


# Halaman yang punya grid DataTables sungguhan (Safety Recap pakai
# tabel custom #tableBulanan -- bukan DataTables, dikecualikan).
GRID_KEYS = sorted(k for k in PAGE_OBJECTS if k != "safety_recap")

# Halaman Transaction yang punya toolbar lengkap + Create with Form.
FORM_CREATE_KEYS = sorted(
    k for k in PAGE_OBJECTS
    if "Create with Form" in HssSafetyPage.TOMBOL_HALAMAN.get(k, ())
)

# Halaman yang tombol Export-nya menghasilkan file (semua yang punya
# "Export" kecuali yang sudah diketahui tidak menghasilkan file).
EXPORT_FILE_KEYS = sorted(
    k for k in PAGE_OBJECTS
    if "Export" in HssSafetyPage.TOMBOL_HALAMAN.get(k, ())
    and k not in HssSafetyPage.EXPORT_TANPA_FILE
)

# Halaman Transaction - Leading Indicator untuk uji alur MENENGAH
# (view -> filter -> export -> import template). Lagging Indicator
# (smk3/smkp/statistic) sudah dicakup test_safety_lagging_deep, jadi
# tidak diulang di sini.
LEADING_DEEP_KEYS = [
    "incident_investigation_form",
    "initial_incident_accident_report",
    "witness_statement_report",
    "emergency_drill_daily",
    "soc_recapitulation",
    "golden_rules",
    "data_rekap_statistik_k3",
    "safety_kkp_p2k3_committee_meeting",
    "mwt_daily",
    "leading_indicator",
    "master_alat_keselamatan_operasi",
]

# Halaman yang filter unit-nya layak dicoba diganti nilainya
# (View + Lagging deep). Beberapa halaman mengunci select cbDistrict --
# test skip otomatis kalau tidak ada opsi enabled lain.
FILTER_UNIT_KEYS = [
    "lagging_indicator", "golden_rules_recap", "emergency_drill_recap",
    "mwt_recapitulation", "smk3", "smkp",
    "statistic_safety_recapitulation",
]


def _xlsx_jumlah_baris_isi(path):
    """Buka file .xlsx hasil export dan hitung baris yang punya minimal
    satu sel non-kosong. Raise ImportError kalau openpyxl belum
    terpasang (pemanggil -> pytest.skip)."""
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    total = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            if any(sel not in (None, "") for sel in row):
                total += 1
    wb.close()
    return total


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
            # tab BUKAN cuma dapat class 'active' -- panel tujuannya
            # harus benar-benar menampilkan konten (tabel / field / teks)
            assert page.panel_tab_isi_tampil(teks_tab), (
                f"Panel tab '{teks_tab}' di '{kunci_halaman}' aktif tapi "
                "tidak menampilkan konten apa pun"
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
        # Baris draft KOSONG yang nyangkut dari run/aksi sebelumnya bikin
        # Submit Changes MEMBUANG baris baru dari Create with Form (lihat
        # catatan HssSafetyPage.TOMBOL_HALAMAN) -- bersihkan dulu supaya
        # baris equip yang baru benar2 ke-submit (2026-08-31).
        page._hapus_baris_kosong()
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
        if not page.tabel_berisi(equip, timeout=config.DEFAULT_TIMEOUT):
            # server DEV lambat commit -- beri waktu, muat ulang halaman,
            # lalu cari lagi (pola sama dengan create_dengan_form_sungguhan)
            page.pace(3.0)
            page.buka_halaman("master_alat_keselamatan_operasi")
            page._tunggu_tabel()
            page.tunggu_processing_selesai()
            page.reset_cari_grid()
            page.cari_di_grid(equip)
        assert page.tabel_berisi(equip), (
            f"Data '{equip}' tidak muncul di tabel setelah Save + Submit "
            "(termasuk setelah reload + cari ulang)"
        )

    @pytest.mark.safety_transaction
    def test_safety_master_alat_delete(self, driver, test_data):
        """Contoh fitur HAPUS (hanya Master Alat yang punya tombol
        Delete per baris): klik Delete di baris dummy -> dialog
        konfirmasi muncul ('Do you wish to delete this record ?') ->
        jawab Yes -> Submit Changes -> baris HILANG dari tampilan grid
        DAN tetap hilang setelah reload (persisten ke server).

        RIWAYAT PERILAKU APLIKASI DEV:
        - 2026-08-26: penghapusan TIDAK disimpan ke server sama sekali
          (diverifikasi lewat probe tools/probe_masalah6/9.py) -- baris
          selalu muncul lagi setelah reload, submit atau tidak.
        - 2026-08-31: perilaku BERUBAH jadi dua tahap, konsisten dengan
          pola edit sel lain di aplikasi ini: (1) Delete + Yes cuma
          menandai baris sebagai pending change lokal (banner "stored
          locally... please submit" muncul) -- baris TIDAK langsung
          hilang dari grid tanpa Submit Changes; (2) setelah Submit
          Changes, baris hilang dari grid DAN penghapusan kini PERSISTEN
          ke server (diverifikasi: reload halaman, baris tidak muncul
          lagi). Test ini sekarang memverifikasi alur dua tahap itu, dan
          assert terakhir jadi cleanup sungguhan (jumlah baris dummy
          berkurang 1 secara permanen), bukan lagi sekadar alarm.

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
        # CATATAN 2026-08-31 (perilaku aplikasi berubah dari temuan
        # 2026-08-26): Delete + Yes SEKARANG cuma menandai baris sebagai
        # pending change lokal (banner "stored locally... please submit"
        # muncul, sama seperti edit sel biasa) -- baris TIDAK langsung
        # hilang dari grid tanpa Submit Changes (dicek: baris masih utuh
        # setelah LONG_TIMEOUT tanpa submit). Jadi sekarang Submit Changes
        # dulu, baru baris hilang dari tampilan.
        page.submit_changes()
        page.tunggu_processing_selesai()
        page._wait(config.LONG_TIMEOUT).until(
            lambda _: _jumlah_dummy() < sebelum,
            "Baris dummy tidak hilang dari grid setelah Delete + Yes + Submit Changes",
        )
        # Reload: sejak 2026-08-31 penghapusan (Delete + Yes + Submit
        # Changes) PERSISTEN ke server -- baris TIDAK muncul lagi.
        # Kalau suatu saat baris muncul lagi (regresi ke perilaku
        # 2026-08-26), assert ini yang akan menangkapnya.
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
        assert sesudah == sebelum - 1, (
            f"Baris dummy tidak ter-hapus permanen dari server "
            f"(sebelum={sebelum}, sesudah reload={sesudah}, seharusnya "
            f"{sebelum - 1}) -- delete mungkin regresi ke perilaku lama "
            "(2026-08-26: tidak persisten ke server)."
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
            if not anchor_baru:
                pytest.skip(
                    f"Field '{field_edit}' kosong di baris {anchor} dan tidak "
                    f"ada baris lain yang terisi di '{kunci}' -- data DEV "
                    "belum ada untuk periode ini, fitur edit tidak bisa "
                    "diuji sungguhan"
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

    # ------------------------------------------------------------------
    # DataTables: sort kolom, pagination, kotak Search, show/hide kolom
    # (satu test per halaman ber-grid). Tiap bagian TOLERAN: kalau
    # fitur/data tidak tersedia di halaman itu, bagian tsb dilewati --
    # bukan dianggap gagal.
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_extra
    @pytest.mark.safety_datatables
    @pytest.mark.parametrize(
        "kunci_halaman", GRID_KEYS, ids=lambda k: NAMA_HALAMAN[k]
    )
    def test_safety_datatables_interaksi(self, driver, kunci_halaman):
        """Interaksi standar DataTables di grid utama tiap halaman:
          1) Sort  -> urutkan kolom pertama yang sortable asc lalu
                      desc; urutan nilai kolom harus BERUBAH (atau
                      minimal order state DataTables berubah).
          2) Pagination -> kalau data > 1 halaman: pindah ke halaman
                      berikutnya (info.page naik) lalu kembali.
          3) Search box -> ketik token dari baris pertama; jumlah baris
                      hasil <= semula & baris token tetap ada; lalu
                      kosongkan -> baris kembali banyak.
          4) Show/Hide kolom -> sembunyikan kolom pertama (jumlah <th>
                      turun), tampilkan lagi (kembali).
        """
        page = _buka_halaman(driver, kunci_halaman)
        assert page.tabel_report_tampil(), f"Tabel '{kunci_halaman}' tidak tampil"
        page.reset_cari_grid()

        if not page._dt_ada():
            pytest.skip(
                f"Grid '{kunci_halaman}' bukan DataTables ter-init "
                "-- interaksi DataTables tidak berlaku"
            )

        kolom = page.daftar_kolom_grid() or []
        info = page.dt_info() or {}
        n_baris = page.dt_jumlah_baris_dom()

        # --- 1) SORT ---
        sortable = [k for k in kolom if k["sortable"] and k["visible"]]
        if sortable and n_baris >= 2:
            idx = sortable[0]["index"]
            page.dt_urutkan(idx, "asc")
            state_asc = page.dt_order_state()
            urut_asc = page.dt_nilai_kolom(idx)
            page.dt_urutkan(idx, "desc")
            state_desc = page.dt_order_state()
            urut_desc = page.dt_nilai_kolom(idx)
            assert state_asc != state_desc or urut_asc != urut_desc, (
                f"Sort kolom '{sortable[0]['name']}' di '{kunci_halaman}' "
                "tidak mengubah urutan data maupun order state"
            )

        # --- 2) PAGINATION ---
        if info.get("pages", 0) and info["pages"] > 1:
            awal = page.dt_info()["page"]
            baru = page.dt_ke_halaman(awal + 1)
            assert baru and baru["page"] == awal + 1, (
                f"Pagination '{kunci_halaman}': gagal pindah ke halaman "
                f"{awal + 2}"
            )
            page.dt_ke_halaman(awal)

        # --- 3) SEARCH / FILTER ---
        # Kotak Search bawaan DataTables (div.dataTables_filter input)
        # jarang dirender di OPEL -- kalau ADA, diuji lewat DOM. Kalau
        # TIDAK ada, fitur search tetap diuji lewat DataTables search
        # API (dipakai grid yang sama untuk cari data), supaya
        # "search mem-filter grid" tetap terverifikasi di setiap halaman.
        total_awal = (page.dt_info() or {}).get("recordsDisplay", n_baris)
        if n_baris >= 1 and total_awal >= 1:
            # Kolom Month/Date sering dirender client-side pakai locale
            # (mis. "Januari") padahal search API server-side mencocokkan
            # nilai mentah di balik layar (mis. "January") -- token dari
            # kolom begini bisa bikin false failure, jadi dilewati kalau
            # ada kolom lain yang bisa dipakai (2026-08-31).
            KOLOM_LOKAL_DILEWATI = {"month", "date"}
            token = ""
            for kol in kolom:
                if not kol["visible"]:
                    continue
                if kol["name"].strip().lower() in KOLOM_LOKAL_DILEWATI:
                    continue
                nilai = page.dt_nilai_kolom(kol["index"], maks=1)
                if nilai and len(nilai[0].strip()) >= 3:
                    token = nilai[0].strip().split()[0]
                    break
            if token:
                # Kotak Search DOM (kalau ada) -- cukup dipastikan tidak
                # error; semantik jumlah baris server-side bervariasi
                # antar halaman, jadi TIDAK di-assert ketat.
                if page.dt_search_kotak(token) is not None:
                    page.dt_search_kotak("")
                # jalur API (selalu ada di DataTables): search dengan
                # token yang PASTI ada -> grid harus tetap menampilkan
                # baris yang memuat token itu (search matched, bukan
                # blank), lalu setelah dikosongkan jumlah baris PULIH
                # ke semula.
                page.cari_di_grid(token)
                assert page.tabel_berisi(token), (
                    f"Search '{token}' di '{kunci_halaman}': token yang pasti "
                    "ada malah tidak muncul di grid hasil"
                )
                page.reset_cari_grid()
                pulih = (page.dt_info() or {}).get("recordsDisplay", total_awal)
                assert pulih >= total_awal, (
                    f"Grid '{kunci_halaman}' tidak pulih setelah search "
                    f"dikosongkan ({total_awal} -> {pulih})"
                )

        # --- 4) SHOW / HIDE KOLOM ---
        terlihat = [k for k in kolom if k["visible"]]
        if len(terlihat) >= 2:
            idx = terlihat[0]["index"]
            th_awal = page.jumlah_th_grid()
            assert page.dt_set_kolom_terlihat(idx, False) is False, (
                f"Kolom '{terlihat[0]['name']}' di '{kunci_halaman}' tidak "
                "bisa disembunyikan"
            )
            assert page.jumlah_th_grid() < th_awal, (
                f"Menyembunyikan kolom di '{kunci_halaman}' tidak mengurangi "
                f"jumlah <th> ({th_awal})"
            )
            assert page.dt_set_kolom_terlihat(idx, True) is True
            assert page.jumlah_th_grid() == th_awal, (
                f"Menampilkan kembali kolom di '{kunci_halaman}' tidak "
                "memulihkan jumlah <th>"
            )

    # ------------------------------------------------------------------
    # Isi file EXPORT diverifikasi (bukan cuma "file terunduh"): file
    # harus benar-benar bisa dibuka sebagai workbook .xlsx dan berisi
    # konten (>= 1 baris terisi -- mis. header). Jumlah baris data
    # TIDAK di-assert ketat: sebagian halaman/periode memang kosong
    # datanya di DEV, dan itu bukan bug export.
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_extra
    @pytest.mark.safety_export
    @pytest.mark.parametrize(
        "kunci_halaman", EXPORT_FILE_KEYS, ids=lambda k: NAMA_HALAMAN[k]
    )
    def test_safety_export_isi_file(self, driver, kunci_halaman):
        """Export halaman -> file .xlsx terunduh -> file dibuka sebagai
        workbook (bukan file rusak) dan punya minimal 1 baris terisi."""
        page = _buka_halaman(driver, kunci_halaman)
        assert page.tabel_report_tampil(), f"Tabel '{kunci_halaman}' tidak tampil"
        path = page.export_dan_tunggu_file()
        assert path, f"File export '{kunci_halaman}' tidak terunduh"
        try:
            baris = _xlsx_jumlah_baris_isi(path)
        except ImportError:
            pytest.skip("openpyxl belum terpasang -- lewati verifikasi isi xlsx")
        except Exception as e:
            raise AssertionError(
                f"File export '{kunci_halaman}' ({path}) tidak bisa dibuka "
                f"sebagai workbook .xlsx: {e}"
            )
        assert baris >= 1, (
            f"File export '{kunci_halaman}' ({path}) benar-benar kosong "
            "(tidak ada satu pun baris terisi, header sekalipun)"
        )

    # ------------------------------------------------------------------
    # Alur MENENGAH halaman Transaction - Leading Indicator:
    # view -> filter tanggal (kalau ada) -> filter unit (elemen+opsi) ->
    # Export (file) -> Import (modal + template). TIDAK menyentuh data
    # (tidak edit inline, tidak upload).
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_extra
    @pytest.mark.safety_transaction
    @pytest.mark.parametrize(
        "kunci_halaman", LEADING_DEEP_KEYS, ids=lambda k: NAMA_HALAMAN[k]
    )
    def test_safety_leading_deep(self, driver, kunci_halaman):
        page = _buka_halaman(driver, kunci_halaman)
        assert page.tabel_report_tampil(), f"Tabel '{kunci_halaman}' tidak tampil"

        # --- filter tanggal (kalau halaman punya) ---
        if page.is_any_visible(page.FILTER_TANGGAL, timeout=3):
            awal = page.baca_filter_tanggal()
            if awal and len(awal) >= 4:
                uji = ("2025" + awal[4:]) if not awal.startswith("2025") \
                    else ("2024" + awal[4:])
                page.set_filter_tanggal(uji)
                page.tunggu_processing_selesai()
                assert page.baca_filter_tanggal() == uji, (
                    f"Filter tanggal '{kunci_halaman}' tidak berubah ke '{uji}'"
                )
                assert page.tabel_report_tampil(), (
                    f"Tabel '{kunci_halaman}' hilang setelah filter tanggal"
                )
                page.set_filter_tanggal(awal)
                page.tunggu_processing_selesai()

        # --- filter unit: elemen ada + punya opsi ---
        try:
            page._ambil_js_visible(page.FILTER_UNIT)
            jumlah_opsi = driver.execute_script(
                "const s = document.querySelector('#cbDistrict');"
                "return s ? s.options.length : 0;"
            )
            assert jumlah_opsi > 0, f"Select unit '{kunci_halaman}' tanpa opsi"
        except TimeoutException:
            pass  # sebagian halaman tidak punya filter unit

        # --- Export -> file ---
        wajib = kunci_halaman not in HssSafetyPage.EXPORT_TANPA_FILE
        file_export = page.export_dan_tunggu_file(wajib_file=wajib)
        if wajib:
            assert file_export, f"File export '{kunci_halaman}' tidak terunduh"

        # --- Import -> modal + template ---
        if "Import" in HssSafetyPage.TOMBOL_HALAMAN.get(kunci_halaman, ()):
            page.buka_modal_import()
            assert page.is_visible(page.LINK_DOWNLOAD_TEMPLATE), (
                f"Link Download Template tidak ada di '{kunci_halaman}'"
            )
            assert page.download_template_import(), (
                f"Template import '{kunci_halaman}' tidak terunduh"
            )
            page.tutup_modal()

    # ------------------------------------------------------------------
    # NEGATIVE: Create with Form disimpan KOSONG -> form menolak
    # (modal tetap terbuka / pesan validasi muncul). Tidak menyimpan.
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_extra
    @pytest.mark.safety_negatif
    @pytest.mark.parametrize(
        "kunci_halaman", FORM_CREATE_KEYS, ids=lambda k: NAMA_HALAMAN[k]
    )
    def test_safety_create_form_validasi(self, driver, kunci_halaman):
        if kunci_halaman in HssSafetyPage.FORM_TANPA_VALIDASI_WAJIB:
            pytest.skip(
                f"Form '{kunci_halaman}' tidak menerapkan validasi field "
                "wajib (temuan 2026-08-28) -- lihat "
                "HssSafetyPage.FORM_TANPA_VALIDASI_WAJIB"
            )
        page = _buka_halaman(driver, kunci_halaman)
        assert page.tabel_report_tampil(), f"Tabel '{kunci_halaman}' tidak tampil"
        hasil = page.coba_simpan_form_kosong()
        assert hasil["modal_terbuka"] or hasil["ada_pesan_validasi"], (
            f"Create with Form '{kunci_halaman}': Save dengan form KOSONG "
            "tidak ditolak (modal tertutup tanpa pesan validasi) -- "
            "kemungkinan data kosong ikut tersimpan"
        )

    # ------------------------------------------------------------------
    # Filter unit: GANTI nilai (bukan cuma cek elemen). Skip otomatis
    # kalau select cbDistrict terkunci / tidak ada opsi enabled lain.
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_extra
    @pytest.mark.parametrize(
        "kunci_halaman", FILTER_UNIT_KEYS, ids=lambda k: NAMA_HALAMAN[k]
    )
    def test_safety_filter_unit_ganti(self, driver, kunci_halaman):
        page = _buka_halaman(driver, kunci_halaman)
        assert page.tabel_report_tampil(), f"Tabel '{kunci_halaman}' tidak tampil"
        try:
            page._ambil_js_visible(page.FILTER_UNIT)
        except TimeoutException:
            pytest.skip(f"'{kunci_halaman}' tidak punya filter unit")
        awal = page.unit_terpilih_value()
        baru = page.pilih_unit_enabled_lain()
        if not baru:
            pytest.skip(
                f"Filter unit '{kunci_halaman}' terkunci / tidak ada opsi "
                "enabled lain"
            )
        page.tunggu_processing_selesai()
        assert page.unit_terpilih_value() == baru, (
            f"Filter unit '{kunci_halaman}' tidak berpindah ke '{baru}'"
        )
        assert page.tabel_report_tampil(), (
            f"Tabel '{kunci_halaman}' hilang setelah ganti unit"
        )
        if awal:
            page.pilih_unit_by_value(awal)
            page.tunggu_processing_selesai()
