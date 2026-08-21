"""
pages/hss_safety_page.py
========================
Page object untuk bagian SAFETY di menu HSS website OPEL.

Semua locator di file ini adalah hasil SCAN website langsung
(2026-08-20, OPEL v2.6.7) -- lihat reports/scan/safety/*.md untuk
data mentah lengkap per halaman, dan locators/hss_safety.md untuk
dokumentasi yang bisa dibaca manusia.

Struktur menu HSS > Safety:
    Safety
      Reporting
        - Lagging Indicator                    /Reporting/Timesheet/MonthlyReport/View?Id=1306
        - GOLDEN RULES RECAP                   /Reporting/Timesheet/YearlyReport/View?Id=1324
        - EMERGENCY DRILL Recap                /Reporting/Timesheet/YearlyReport/View?Id=1325
        - MWT RECAPITULATION                   /Reporting/Timesheet/YearlyReport/View?Id=1323
        - Safety Recap.                        /Reporting/Supersafe/HSSE/ReportingSafetyRecap
      Transaction > Leading Indicator
        - Incident Investigation Form          /Reporting/Timesheet/DailyReport/Edit?Id=1334
        - Initial Incident/Accident Report     /Reporting/Timesheet/DailyReport/Edit?Id=1335
        - Witness Statement Report             /Reporting/Timesheet/DailyReport/Edit?Id=1336
        - EMERGENCY DRILL Daily                /Reporting/Timesheet/MonthlyReport/Edit?Id=1319
        - Master Alat keselamatan Operasi      /Reporting/Timesheet/StaticReport/Edit?Id=1321
        - SOC RECAPITULATION                   /Reporting/Timesheet/YearlyReport/Edit?Id=1310
        - GOLDEN RULES                         /Reporting/Timesheet/MonthlyReport/Edit?Id=1316
        - Data Rekap Statistik K3              /Reporting/Timesheet/YearlyReport/Edit?Id=1315
        - SAFETY/KKP/P2K3 COMMITTEE MEETING    /Reporting/Timesheet/YearlyReport/Edit?Id=1313
        - MWT DAILY                            /Reporting/Timesheet/MonthlyReport/Edit?Id=1312
        - Leading Indicator                    /Reporting/Timesheet/StaticReport/Edit?Id=1309
      Transaction > Lagging Indicator
        - Statistic Safety Recapitulation      /Reporting/Timesheet/MonthlyReport/Edit?Id=1317
        - SMK3                                 /Reporting/Timesheet/YearlyReport/Edit?Id=1308
        - SMKP                                 /Reporting/Timesheet/YearlyReport/Edit?Id=1307

Catatan framework: OPEL memakai template SmartAdmin + jQuery +
DataTables (table.reportData.dataTable). Grid kolom punya atribut
STABIL data-name -> locator kolom: th[data-name='...'].
"""

import os
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
)

from config import config
from pages.base_page import BasePage


class HssSafetyPage(BasePage):
    # ------------------------------------------------------------------
    # Menu sidebar
    # ------------------------------------------------------------------
    MENU_HSS = (By.XPATH, "//span[normalize-space(text())='HSS']")
    MENU_SAFETY = (By.XPATH, "//span[normalize-space(text())='Safety']")
    # Submenu item Safety punya href asli (bukan '#'), jadi bisa klik
    # langsung lewat href. Teks dipakai sebagai fallback.
    SUBMENU_ITEM = (
        By.XPATH,
        "//a[normalize-space(.)='{teks}'] | //span[normalize-space(text())='{teks}']",
    )

    # ------------------------------------------------------------------
    # Toolbar UNIVERSAL (ada di hampir semua halaman Safety)
    # ------------------------------------------------------------------
    FILTER_TANGGAL = (By.ID, "tbDate")          # input tanggal (month/year picker)
    FILTER_UNIT = (By.ID, "cbDistrict")         # select unit/distrik
    BTN_RELOAD_DATA = (By.ID, "btnReloadData")  # tombol Reload Data
    BTN_EXPORT = (By.ID, "btnExport")           # tombol Export
    BTN_SUBMIT = (By.ID, "btnSubmit")           # tombol Submit Changes
    BTN_CANCEL_GRID = (By.ID, "btnCancel")      # tombol Cancel (grid)
    # Tombol yang hanya punya teks (tanpa id stabil):
    BTN_CREATE = (By.XPATH, "//button[normalize-space(.)='Create']")
    BTN_CREATE_FORM = (By.XPATH, "//button[normalize-space(.)='Create with Form']")
    BTN_IMPORT = (By.XPATH, "//button[normalize-space(.)='Import']")
    # Tombol FullScreen toolbar: teksnya BERUBAH antara 'FullScreen' dan
    # 'Windowed' setiap kali diklik -- jadi locator pakai class stabil
    # .fullscreen-button, BUKAN teks (terbukti 2026-08-21).
    BTN_FULLSCREEN = (By.XPATH, "//button[contains(@class,'fullscreen-button')]")
    BTN_COLUMNS = (By.XPATH, "//button[normalize-space(.)='Columns']")
    # Link Instructions (bukan button): title='Filling instructions'
    BTN_INSTRUCTIONS = (By.XPATH, "//a[@title='Filling instructions']")
    # Tombol khusus halaman SOC RECAPITULATION:
    BTN_SELECT_FINDING = (By.XPATH, "//button[normalize-space(.)='Select Finding']")
    # Dropdown DataTables buttons-collection (muncul setelah klik Columns)
    DROPDOWN_COLUMNS = (By.CSS_SELECTOR, "div.dt-button-collection")

    # ------------------------------------------------------------------
    # Tabel DataTables
    # ------------------------------------------------------------------
    TABLE_REPORT = (By.CSS_SELECTOR, "table.reportData.dataTable")
    # Overlay "Processing..." DataTables yang muncul saat load/reload/save
    PROCESSING = (By.CSS_SELECTOR, ".dataTables_processing")
    # Kolom tabel: th[data-name='<nama kolom>'] -- data-name stabil
    # (dipakai backend), JANGAN pakai aria-label/posisi.
    KOLOM = (By.CSS_SELECTOR, "th[data-name='{nama_kolom}']")
    # Baris data (tbody dari table.reportData)
    BARIS = (By.CSS_SELECTOR, "table.reportData tbody tr")

    # Ekspresi JS pemilih GRID UTAMA. Beberapa halaman (mis. Master
    # Alat) me-render grid asli ber-id tableData_XXX BERSAMA template
    # table.reportData kosong -- querySelector biasa salah sasaran ke
    # template. Prioritas: tabel yang PUNYA baris -> yang ber-id
    # tableData_* -> yang pertama.
    JS_GRID = (
        "(() => {"
        "  const ts = [...document.querySelectorAll('table.reportData')];"
        "  const ada = ts.find(t => t.querySelectorAll('tbody tr').length > 0);"
        "  return ada || ts.find(t => t.id && t.id.indexOf('tableData_') === 0)"
        "      || ts[0] || null;"
        "})()"
    )

    # ------------------------------------------------------------------
    # Tab internal halaman (id linkTab-<DataTemplateId> -- dinamis,
    # klik pakai teks tab yang terlihat)
    # ------------------------------------------------------------------
    TAB = (By.XPATH, "//a[contains(@class,'nav-link')][normalize-space(.)='{teks_tab}']")
    # Tab Incident Investigation Form (Id=1334):
    TAB_DATA_INSIDEN = "Data Insiden"
    TAB_DATA_KORBAN = "Data Korban"
    TAB_FAKTA_ANALISIS = "Fakta & Analisis Penyebab"
    TAB_KESIMPULAN = "Kesimpulan & Usulan Investigasi"
    TAB_REKOMENDASI = "Rekomendasi & Tindakan Perbaikan"
    TAB_SAKSI_TIM = "Saksi & Tim Investigasi"

    # ------------------------------------------------------------------
    # Modal Import (id STABIL, sama di semua halaman transaction)
    # ------------------------------------------------------------------
    MODAL_IMPORT = (By.ID, "modalImport")
    MODAL_IMPORT_FORM = (By.ID, "importForm")
    LINK_DOWNLOAD_TEMPLATE = (By.ID, "linkDownloadTemplate")  # Download Template
    INPUT_FILE_IMPORT = (By.ID, "imgFileImport")              # <input type=file> .xlsx
    BTN_IMPORT_CONFIRM = (By.ID, "btnImport")                 # tombol Import di modal
    BTN_CLOSE_MODAL = (
        By.XPATH,
        "//div[contains(@class,'modal') and contains(@class,'show')]"
        "//button[contains(@class,'close') or normalize-space(.)='Close']",
    )

    # ------------------------------------------------------------------
    # Modal Create with Form (id dinamis: input_NNNNN, cbXX_*_NNNN,
    # btnSave_NNNN -- field DICARI lewat label, tombol lewat teks)
    # ------------------------------------------------------------------
    MODAL_SHOW = (By.CSS_SELECTOR, ".modal.show")
    # Field di dalam modal DICARI lewat teks label (id auto-generate)
    # -- helper _locator_field() / _locator_group() di bawah.
    BTN_SAVE_MODAL = (
        By.XPATH,
        "//div[contains(@class,'modal') and contains(@class,'show')]"
        "//button[normalize-space(.)='Save']",
    )
    BTN_CANCEL_MODAL = (
        By.XPATH,
        "//div[contains(@class,'modal') and contains(@class,'show')]"
        "//button[normalize-space(.)='Cancel']",
    )

    # ------------------------------------------------------------------
    # Halaman Safety Recap (custom, BUKAN pola Timesheet)
    # ------------------------------------------------------------------
    FILTER_BULAN = (By.ID, "cbMonths")   # select bulan (January..December)
    FILTER_TAHUN = (By.ID, "cbYears")    # select tahun (2020..2026)
    SEARCH_SAFETY_RECAP = (By.CSS_SELECTOR, "input[placeholder='Search']")
    BTN_EXPORT_EXCEL = (By.XPATH, "//button[normalize-space(.)='Export Excel']")

    # ------------------------------------------------------------------
    # Daftar halaman Safety (nama -> url relatif BASE_URL)
    # ------------------------------------------------------------------
    HALAMAN = {
        # Reporting
        "lagging_indicator": "Reporting/Timesheet/MonthlyReport/View?Id=1306",
        "golden_rules_recap": "Reporting/Timesheet/YearlyReport/View?Id=1324",
        "emergency_drill_recap": "Reporting/Timesheet/YearlyReport/View?Id=1325",
        "mwt_recapitulation": "Reporting/Timesheet/YearlyReport/View?Id=1323",
        "safety_recap": "Reporting/Supersafe/HSSE/ReportingSafetyRecap",
        # Transaction - Leading Indicator
        "incident_investigation_form": "Reporting/Timesheet/DailyReport/Edit?Id=1334",
        "initial_incident_accident_report": "Reporting/Timesheet/DailyReport/Edit?Id=1335",
        "witness_statement_report": "Reporting/Timesheet/DailyReport/Edit?Id=1336",
        "emergency_drill_daily": "Reporting/Timesheet/MonthlyReport/Edit?Id=1319",
        "master_alat_keselamatan_operasi": "Reporting/Timesheet/StaticReport/Edit?Id=1321",
        "soc_recapitulation": "Reporting/Timesheet/YearlyReport/Edit?Id=1310",
        "golden_rules": "Reporting/Timesheet/MonthlyReport/Edit?Id=1316",
        "data_rekap_statistik_k3": "Reporting/Timesheet/YearlyReport/Edit?Id=1315",
        "safety_kkp_p2k3_committee_meeting": "Reporting/Timesheet/YearlyReport/Edit?Id=1313",
        "mwt_daily": "Reporting/Timesheet/MonthlyReport/Edit?Id=1312",
        "leading_indicator": "Reporting/Timesheet/StaticReport/Edit?Id=1309",
        # Transaction - Lagging Indicator
        "statistic_safety_recapitulation": "Reporting/Timesheet/MonthlyReport/Edit?Id=1317",
        "smk3": "Reporting/Timesheet/YearlyReport/Edit?Id=1308",
        "smkp": "Reporting/Timesheet/YearlyReport/Edit?Id=1307",
    }

    # ------------------------------------------------------------------
    # Toolbar tombol per halaman ("bagian tombol pada fitur")
    # ------------------------------------------------------------------
    # Registri tombol toolbar: nama -> locator. Nama dipakai test &
    # dokumentasi; locator hasil scan website OPEL (2026-08-20, v2.6.7).
    TOMBOL_TOOLBAR = {
        "Reload Data": BTN_RELOAD_DATA,
        "Export": BTN_EXPORT,
        "Submit Changes": BTN_SUBMIT,
        "Cancel": BTN_CANCEL_GRID,
        "Create": BTN_CREATE,
        "Create with Form": BTN_CREATE_FORM,
        "Import": BTN_IMPORT,
        "FullScreen": BTN_FULLSCREEN,
        "Columns": BTN_COLUMNS,
        "Select Finding": BTN_SELECT_FINDING,
        "Instructions": BTN_INSTRUCTIONS,
        "Export Excel": BTN_EXPORT_EXCEL,
    }

    # Tombol toolbar yang diharapkan TAMPIL di tiap halaman (hasil scan
    # website OPEL 2026-08-20 -- reports/scan/safety/*.md, bagian BUTTON
    # + link ber-role button). Halaman View cuma punya Export
    # (+Instructions/Cancel); halaman Transaction (Edit) punya toolbar
    # lengkap. Catatan scan:
    #   - MWT DAILY tidak punya tombol Reload Data.
    #   - Leading Indicator tidak punya link Instructions.
    #   - Columns cuma ada di 3 halaman Daily Input (Id=1334/1335/1336).
    #   - SOC RECAPITULATION punya tombol tambahan Select Finding.
    TOMBOL_HALAMAN = {
        # Reporting (View / read-only)
        "lagging_indicator": ("Export", "Instructions", "Cancel"),
        "golden_rules_recap": ("Export", "Instructions", "Cancel"),
        "emergency_drill_recap": ("Export", "Instructions", "Cancel"),
        "mwt_recapitulation": ("Export", "Instructions", "Cancel"),
        "safety_recap": ("Export Excel",),
        # Transaction - Leading Indicator
        "incident_investigation_form": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Columns", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "initial_incident_accident_report": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Columns", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "witness_statement_report": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Columns", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "emergency_drill_daily": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "master_alat_keselamatan_operasi": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "soc_recapitulation": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Select Finding", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "golden_rules": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "data_rekap_statistik_k3": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
        "safety_kkp_p2k3_committee_meeting": (
            "Reload Data", "Create", "Create with Form", "Import",
            "FullScreen", "Submit Changes", "Export",
            "Instructions", "Cancel",
        ),
        "mwt_daily": (
            "Create", "Create with Form", "Import", "FullScreen",
            "Submit Changes", "Export", "Instructions", "Cancel",
        ),
        "leading_indicator": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Cancel",
        ),
        # Transaction - Lagging Indicator
        "statistic_safety_recapitulation": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
        "smk3": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
        "smkp": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
    }

    # ------------------------------------------------------------------
    # Navigasi
    # ------------------------------------------------------------------
    @staticmethod
    def _js_tampil():
        """JS: True kalau ADA elemen yang cocok dan benar-benar tampil
        (computed style bukan display:none/visibility:hidden + tinggi
        rect >= min_tinggi). Dipakai sebagai kondisi 'halaman siap'
        karena WebElement.is_displayed() Selenium bisa False negatif
        saat DataTables/fade-transition masih berjalan (terbukti saat
        validasi: tabel punya tinggi nyata tapi is_displayed() False).

        Argumen saat execute_script:
            arguments[0] = css selector, arguments[1] = tinggi minimum.
        """
        return (
            "let ok = false;"
            "document.querySelectorAll(arguments[0]).forEach(el => {"
            "  const s = window.getComputedStyle(el);"
            "  const r = el.getBoundingClientRect();"
            "  if (s.display !== 'none' && s.visibility !== 'hidden'"
            "      && r.height >= arguments[1]) ok = true;"
            "});"
            "return ok;"
        )

    def tabel_report_tampil(self, min_tinggi=10):
        """True kalau tabel reportData sudah benar-benar tampil (JS)."""
        return self.driver.execute_script(
            self._js_tampil(), self.TABLE_REPORT[1], min_tinggi
        )

    def buka_menu_hss_safety(self):
        """Klik menu sidebar HSS lalu submenu Safety. Dipakai untuk
        memverifikasi struktur menu (bukan jalur utama -- jalur utama
        memakai buka_halaman() dengan URL langsung yang lebih stabil).

        Catatan: menu sidebar SmartAdmin bersifat TOGGLE -- kalau HSS
        sudah terbuka dan diklik lagi malah menutup, jadi ada cek
        fallback: kalau Safety belum muncul setelah klik pertama,
        klik HSS sekali lagi (toggle balik)."""
        self.click_visible_among(self.MENU_HSS)
        if not self.is_any_visible(self.MENU_SAFETY, timeout=3):
            self.click_visible_among(self.MENU_HSS)
        self.click_visible_among(self.MENU_SAFETY)

    def buka_halaman(self, kunci):
        """Buka halaman Safety berdasarkan kunci di HALAMAN (mis.
        'smk3'). Navigasi lewat URL langsung -- paling stabil karena
        submenu pakai href relatif yang bisa berubah konteks.

        Menunggu sampai tabel DataTables benar-benar TAMPIL (bukan
        cuma ada di DOM) -- halaman Timesheet butuh beberapa detik
        untuk render data setelah load."""
        if kunci not in self.HALAMAN:
            raise KeyError(
                f"Kunci halaman '{kunci}' tidak dikenal. Pilihan: "
                f"{', '.join(sorted(self.HALAMAN))}"
            )
        url = config.BASE_URL.rstrip("/") + "/" + self.HALAMAN[kunci].lstrip("/")

        def _tunggu_siap():
            self._tunggu_tabel(url)
            self.tunggu_processing_selesai()

        self.driver.get(url)
        try:
            _tunggu_siap()
        except TimeoutException:
            # Navigasi cepat antar-halaman kadang bikin SPA OPEL "stuck"
            # di loading overlay -- retry navigasi sekali menyelesaikan.
            self.driver.get(url)
            _tunggu_siap()

    def _tunggu_tabel(self, url=None):
        """Tunggu tabel reportData benar-benar TAMPIL (JS check)."""
        self._wait(config.LONG_TIMEOUT).until(
            lambda d: self.tabel_report_tampil(),
            f"Tabel reportData tidak kunjung tampil di {url or self.driver.current_url}",
        )

    def tunggu_processing_selesai(self, timeout=None):
        """Tunggu overlay 'Processing...' DataTables hilang -- penting
        sebelum klik/ketik di tabel supaya tidak kena elemen setengah
        jalan saat load/reload/save data."""
        timeout = timeout or config.LONG_TIMEOUT
        self._wait(timeout).until(
            lambda d: d.execute_script(
                "let ok = true;"
                "document.querySelectorAll('.dataTables_processing').forEach(el => {"
                "  const s = window.getComputedStyle(el);"
                "  const r = el.getBoundingClientRect();"
                "  if (s.display !== 'none' && s.visibility !== 'hidden'"
                "      && r.height > 0) ok = false;"
                "});"
                "return ok;"
            )
        )

    # ------------------------------------------------------------------
    # Aksi umum
    # ------------------------------------------------------------------
    def set_filter_tanggal(self, nilai):
        """Isi filter tanggal (tbDate) -- format mengikuti halaman
        (mis. '2026-08' untuk bulanan, '2026' untuk tahunan)."""
        self.type_text_visible(self.FILTER_TANGGAL, nilai)

    def pilih_unit(self, teks_opsi):
        """Pilih unit pada select cbDistrict (teks opsi, mis.
        '[AT10] KANTOR PUSAT'). cbDistrict adalah <select> native --
        memakai Select (bukan kirim teks) supaya opsi benar2 terpilih."""
        self.select_option(self.FILTER_UNIT, teks_opsi)

    def reload_data(self):
        """Klik Reload Data lalu tunggu data selesai dimuat ulang
        (overlay Processing hilang + tabel tampil).

        Tombol Reload kadang TIDAK ter-render oleh SPA (quirk stuck
        yang sama dengan navigasi antar-halaman, 2026-08-21) -- kalau
        belum tampil setelah timeout, navigasi ulang 1x lalu coba
        lagi (remedy terbukti)."""
        try:
            self.click_js_saat_tampil(self.BTN_RELOAD_DATA)
        except TimeoutException:
            self.driver.get(self.driver.current_url)
            self._tunggu_tabel()
            self.tunggu_processing_selesai()
            self.click_js_saat_tampil(self.BTN_RELOAD_DATA)
        self.tunggu_processing_selesai()
        self._tunggu_tabel()

    def export_data(self):
        """Klik Export (unduh file -- halaman tidak berpindah) lalu
        jawab dialog konfirmasi Yes/OK kalau muncul."""
        self.click_js_saat_tampil(self.BTN_EXPORT)
        self.jawab_konfirmasi()

    def export_dan_tunggu_file(self, ekstensi=".xlsx"):
        """Klik Export lalu tunggu file BARU ber-ekstensi `ekstensi`
        muncul di folder unduhan (config.DOWNLOAD_DIR -- diarahkan lewat
        prefs Chrome di conftest). Kembalikan path file hasil unduhan."""
        os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
        sebelum = set(os.listdir(config.DOWNLOAD_DIR))
        self.export_data()
        self._wait(config.LONG_TIMEOUT).until(
            lambda d: any(
                nama.endswith(ekstensi) and nama not in sebelum
                for nama in os.listdir(config.DOWNLOAD_DIR)
            ),
            "File export tidak kunjung muncul di folder unduhan "
            f"({config.DOWNLOAD_DIR})",
        )
        baru = [
            nama for nama in os.listdir(config.DOWNLOAD_DIR)
            if nama.endswith(ekstensi) and nama not in sebelum
        ]
        return os.path.join(config.DOWNLOAD_DIR, baru[0])

    # Kandidat tombol Yes/OK dialog konfirmasi (Submit Changes /
    # Export): bootbox Yes dulu, lalu modal Bootstrap, SweetAlert,
    # dan tombol Yes/OK umum.
    _LOKASI_TOMBOL_OK = (
        (By.CSS_SELECTOR, "button.bootbox-accept"),
        (
            By.XPATH,
            "//div[contains(@class,'modal') and contains(@class,'show')]"
            "//button[normalize-space(.)='Yes']",
        ),
        (
            By.XPATH,
            "//div[contains(@class,'modal') and contains(@class,'show')]"
            "//button[normalize-space(.)='OK']",
        ),
        (By.XPATH, "//div[contains(@class,'swal2')]//button[normalize-space(.)='OK']"),
        (By.XPATH, "//button[normalize-space(.)='Yes']"),
        (By.XPATH, "//button[normalize-space(.)='OK']"),
    )

    def _klik_jika_ada(self, locator):
        """Klik elemen pertama yang ADA & tampil (JS) TANPA menunggu.
        Kembalikan True kalau berhasil diklik."""
        try:
            for el in self.driver.find_elements(*locator):
                try:
                    if self._js_visible(self.driver, el):
                        self.driver.execute_script("arguments[0].click();", el)
                        return True
                except StaleElementReferenceException:
                    continue
        except Exception:
            pass
        return False

    def jawab_konfirmasi(self, timeout=8):
        """Jawab dialog konfirmasi Yes/OK yang muncul setelah Submit/
        Export -- kalau tidak dijawab, perubahan TIDAK tersimpan.
        Menangani: native confirm(), bootbox (`button.bootbox-accept`),
        tombol Yes/OK di modal Bootstrap, dan SweetAlert. Terus dijawab
        sampai dialog tidak muncul lagi (menangani dialog beruntun,
        mis. konfirmasi -> pesan sukses). Kembalikan True kalau ada
        dialog yang dijawab."""
        akhir = time.time() + timeout
        tenang_sejak = time.time()
        terjawab = False
        while time.time() < akhir:
            kini_terjawab = False
            try:  # native confirm / alert
                self.driver.switch_to.alert.accept()
                kini_terjawab = True
            except Exception:
                pass
            for locator in self._LOKASI_TOMBOL_OK:
                if self._klik_jika_ada(locator):
                    kini_terjawab = True
                    break
            if kini_terjawab:
                self.pace()
                terjawab = True
                tenang_sejak = time.time()
            elif time.time() - tenang_sejak > 2:
                return terjawab
            time.sleep(0.5)
        return terjawab

    def submit_changes(self):
        """Klik Submit Changes lalu jawab dialog konfirmasi OK supaya
        perubahan benar2 tersimpan di server."""
        self.click_js_saat_tampil(self.BTN_SUBMIT)
        self.jawab_konfirmasi()

    def klik_tab(self, teks_tab):
        """Klik tab internal halaman (hanya yang benar2 tampil menurut
        JS -- beberapa halaman punya panel tab tersembunyi di DOM),
        lalu tunggu tabnya jadi aktif."""
        locator = (By.XPATH, self.TAB[1].format(teks_tab=teks_tab))
        element = self._ambil_js_visible(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        self.driver.execute_script("arguments[0].click();", element)
        self.pace()
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda d: any(
                "active" in (el.get_attribute("class") or "")
                for el in d.find_elements(*locator)
            ),
            f"Tab '{teks_tab}' tidak kunjung aktif setelah diklik",
        )

    def klik_kolom(self, nama_kolom):
        """Klik header kolom tabel (untuk sort)."""
        self.click((By.CSS_SELECTOR, self.KOLOM[1].format(nama_kolom=nama_kolom)))

    # ------------------------------------------------------------------
    # Modal Create with Form (alur isi data)
    # ------------------------------------------------------------------
    def _ada_modal_tampil(self):
        """True kalau ADA modal .modal.show yang benar2 terlihat.
        Elemen stale (sedang diganti DOM) dianggap belum tampil."""
        for el in self.driver.find_elements(*self.MODAL_SHOW):
            try:
                if el.is_displayed():
                    return True
            except StaleElementReferenceException:
                continue
        return False

    def tunggu_modal_terbuka(self, timeout=None):
        """Tunggu sampai ADA modal .modal.show yang tampil."""
        self._wait(timeout).until(
            lambda _: self._ada_modal_tampil(),
            "Modal tidak kunjung terbuka",
        )

    def tunggu_modal_tertutup(self, timeout=None):
        """Tunggu sampai TIDAK ADA modal .modal.show yang tampil lagi."""
        self._wait(timeout).until(
            lambda _: not self._ada_modal_tampil(),
            "Modal tidak kunjung tertutup -- kemungkinan ada field wajib"
            " belum terisi / validasi gagal",
        )

    def _klik_dan_tunggu_modal(self, locator):
        """Klik tombol pembuka modal lalu tunggu modalnya terbuka.
        Kadang klik pertama mendarat sebelum handler JS tombol siap
        (toolbar baru selesai render) -- retry 1x kalau modal belum
        terbuka dalam 3 detik, supaya tidak gagal sia-sia."""
        for _ in range(2):
            self.click_js_saat_tampil(locator)
            try:
                self.tunggu_modal_terbuka(timeout=3)
                return
            except TimeoutException:
                continue
        self.tunggu_modal_terbuka()

    def buka_modal_import(self):
        """Klik Import lalu tunggu modal Import terbuka."""
        self._klik_dan_tunggu_modal(self.BTN_IMPORT)

    def buka_form_create(self):
        """Klik 'Create with Form' lalu tunggu modal form-nya terbuka."""
        self._klik_dan_tunggu_modal(self.BTN_CREATE_FORM)

    @staticmethod
    def _xpath_label(teks):
        """Predikat `normalize-space(.)=<teks>` yang aman walau label
        mengandung tanda kutip satu (XPath 1.0 tidak punya escape --
        dipakai concat())."""
        if "'" not in teks:
            return f"normalize-space(.)='{teks}'"
        bagian = [f"'{b}'" for b in teks.split("'")]
        return "concat(" + ", \"'\", ".join(bagian) + ")"

    def _locator_field(self, label):
        """Locator field di dalam modal .show berdasarkan label. Field
        bisa SAUDARA LANGSUNG dari label (input teks biasa, contoh
        Equipment No / Capacity) atau berada DI DALAM container
        saudaranya (lookup, custom select). Ambil saudara pertama yang
        memuat field, lalu field pertama di dalamnya (dirinya sendiri
        dulu, baru descendant -- urutan dokumen)."""
        return (
            By.XPATH,
            "//div[contains(@class,'modal') and contains(@class,'show')]"
            f"//label[{self._xpath_label(label)}]"
            "/following-sibling::*"
            "[descendant-or-self::*[self::input or self::select"
            " or self::textarea]][1]"
            "/descendant-or-self::*[self::input or self::select"
            " or self::textarea][1]",
        )

    def _locator_group(self, label):
        """XPath ke container .form-group yang memuat label `label`
        di dalam modal .show. Dipakai untuk kontrol LOOKUP -- hidden
        input (dt-input-lookup-hidden), tombol Search/Clear, dan teks
        pilihan ada di dalam group ini."""
        return (
            "//div[contains(@class,'modal') and contains(@class,'show')]"
            f"//label[{self._xpath_label(label)}]"
            "/ancestor::div[contains(@class,'form-group')][1]"
        )

    def isi_field_modal(self, label, nilai):
        """Isi field di modal yang sedang terbuka berdasarkan teks
        label-nya (id field auto-generate, jadi label adalah cara
        paling stabil). Menyesuaikan jenis kontrol:
          - lookup (ada .dt-input-lookup-hidden di group) -> pilih
            lewat modal lookup (isi_lookup)
          - <select>   -> pilih opsi lewat Select (visible text)
          - radio/checkbox -> klik
          - lainnya (input/textarea, termasuk date picker) -> ketik"""
        if self.driver.find_elements(
            By.XPATH,
            self._locator_group(label)
            + "//*[contains(@class,'dt-input-lookup-hidden')]",
        ):
            self.isi_lookup(label, nilai)
            return
        locator = self._locator_field(label)
        for _ in range(3):
            try:
                element = self._ambil_js_visible(locator)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", element
                )
                tag = element.tag_name
                tipe = (element.get_attribute("type") or "").lower()
                if tag == "select":
                    Select(element).select_by_visible_text(nilai)
                elif tag == "input" and tipe in ("radio", "checkbox"):
                    self.driver.execute_script("arguments[0].click();", element)
                else:
                    element.clear()
                    element.send_keys(str(nilai))
                self.pace()
                return
            except StaleElementReferenceException:
                # field diganti DOM (redraw modal) -- cari ulang
                continue
        raise StaleElementReferenceException(
            f"Field '{label}' terus-menerus stale saat diisi"
        )

    def isi_lookup(self, label, nilai):
        """Isi field lookup berdasarkan label: klik tombol Search di
        group field -> modal lookup (#lookupModal) terbuka -> (kalau
        `nilai` tidak kosong) ketik `nilai` di kotak pencarian -> klik
        baris yang cocok (atau baris PERTAMA kalau nilai kosong) ->
        modal lookup tertutup otomatis dan hidden input terisi kode
        baris terpilih (ditunggu sampai benar2 terisi; retry klik 3x
        karena baris DataTables bisa ter-render ulang saat redraw)."""
        grp = self._locator_group(label)
        self.click_js_saat_tampil(
            (By.XPATH, grp + "//a[contains(@class,'dt-input-lookup-search')]")
        )
        if nilai:
            self.type_text_visible(
                (By.CSS_SELECTOR, "#lookupModal input[type='search']"), nilai
            )
            self.tunggu_processing_selesai()
            baris = (
                By.XPATH,
                f"//div[@id='lookupModal']//tr[contains(@class,'row-lookup')]"
                f"[contains(., '{nilai}')]",
            )
        else:
            baris = (By.CSS_SELECTOR, "#lookupModal tr.row-lookup")
        for _ in range(3):
            try:
                self.click_js_saat_tampil(baris)
                self._wait(config.DEFAULT_TIMEOUT).until(
                    lambda d: bool(self.baca_lookup(label))
                )
                return
            except TimeoutException:
                # baris belum dirender / kena redraw -- coba lagi
                continue
        raise TimeoutException(
            f"Lookup '{label}' tidak terisi setelah pilih '{nilai}'"
        )

    def baca_lookup(self, label):
        """Baca nilai hidden input field lookup `label` (kode baris
        yang terpilih). Kembalikan '' kalau belum ada pilihan."""
        grp = self._locator_group(label)
        els = self.driver.find_elements(
            By.XPATH, grp + "//*[contains(@class,'dt-input-lookup-hidden')]"
        )
        return els[0].get_attribute("value") if els else ""

    def isi_form_create(self, data):
        """Isi SEMUA field form create sekaligus. `data` = dict
        {label_field: nilai}. Diisi satu per satu sesuai urutan dict
        (urutan pemasukan = urutan pengisian di UI)."""
        for label, nilai in data.items():
            self.isi_field_modal(label, nilai)

    # Scan field form create yang sedang terbuka (dipakai isi_form_create_otomatis)
    JS_FIELD_FORM = r"""
const modal = document.querySelector('.modal.show');
const out = [];
modal.querySelectorAll('.form-group').forEach(g => {
    const l = g.querySelector('label');
    const teks = l ? (l.innerText || '').trim() : '';
    if (!teks) return;
    const r = g.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    const e = {label: teks, lookup: !!g.querySelector('.dt-input-lookup-hidden'),
               type: '', selectOptions: [], required: false};
    const f = g.querySelector('input, select, textarea');
    if (f) {
        e.type = (f.getAttribute('type') || '').toLowerCase();
        e.required = !!f.required;
        if (f.tagName === 'SELECT')
            e.selectOptions = Array.from(f.options).map(o => o.text.trim())
                .filter(t => t && !/^pilih/i.test(t));
    }
    out.push(e);
});
return out;
"""

    _LABEL_ANGKA = (
        "kapasitas", "capacity", "jumlah", "qty", "quantity", "berat",
        "tonase", "ton", "jam", "hari", "bulan", "tahun", "umur", "usia",
        "total", "nilai", "value", "persen", "percent", "rate",
    )

    @classmethod
    def _label_minta_angka(cls, label):
        """Heuristic: label yang menyebut satuan/kuantitas diisi ANGKA."""
        return any(k in label.lower() for k in cls._LABEL_ANGKA)

    def isi_form_create_otomatis(self, tambahan=None):
        """Isi SEMUA field form create yang terlihat dengan data DUMMY
        otomatis sesuai jenisnya:
          - lookup/combo   -> pilih baris pertama di modal lookup
          - select         -> pilih opsi pertama (selain 'Pilih...')
          - date           -> tanggal hari ini
          - radio/checkbox -> klik
          - label angka    -> isi '10'
          - teks lain      -> isi 'Dummy <label>'
        `tambahan` = dict {label: nilai} untuk field yang mau diisi
        nilai tertentu (menimpa otomatis), mis. Equipment No unik."""
        tambahan = tambahan or {}
        fields = self.driver.execute_script(self.JS_FIELD_FORM) or []
        for f in fields:
            label, tipe = f["label"], f["type"]
            if label in tambahan:
                self.isi_field_modal(label, tambahan[label])
            elif f["lookup"]:
                self.isi_lookup(label, "")
            elif f["selectOptions"]:
                self.isi_field_modal(label, f["selectOptions"][0])
            elif tipe == "date":
                self.isi_field_modal(label, time.strftime("%d-%m-%Y"))
            elif tipe in ("radio", "checkbox"):
                self.isi_field_modal(label, "")
            elif self._label_minta_angka(label):
                self.isi_field_modal(label, "10")
            else:
                self.isi_field_modal(label, f"Dummy {label}")

    def simpan_form(self):
        """Klik Save di modal lalu tunggu modal tertutup (tanda
        proses simpan selesai)."""
        self.click_js_saat_tampil(self.BTN_SAVE_MODAL)
        self.tunggu_modal_tertutup(timeout=config.LONG_TIMEOUT)

    def batal_form(self):
        """Klik Cancel di modal lalu tunggu modal tertutup."""
        self.click_js_saat_tampil(self.BTN_CANCEL_MODAL)
        self.tunggu_modal_tertutup()

    def tutup_modal(self):
        """Tutup modal yang sedang terbuka lewat tombol Close, lalu
        TUNGGU sampai modalnya benar2 hilang (sebelumnya cuma klik,
        jadi aksi berikutnya bisa kena modal yang masih setengah
        menutup)."""
        self.click_js_saat_tampil(self.BTN_CLOSE_MODAL)
        self.tunggu_modal_tertutup()

    def cari_di_grid(self, teks):
        """Cari `teks` di grid UTAMA lewat DataTables API (search
        SERVER-side, bukan cuma filter halaman) -- supaya data BARU
        tetap ketemu walaupun barisnya ada di halaman lain karena
        pagination. Grid dipilih lewat JS_GRID supaya tidak salah
        sasaran ke template reportData kosong (2026-08-21)."""
        self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (t && window.jQuery) {"
            "  const dt = jQuery(t).DataTable();"
            "  dt.search(arguments[0]).draw();"
            "}",
            teks,
        )
        self.tunggu_processing_selesai()

    def tabel_berisi(self, teks, timeout=None):
        """True kalau teks muncul di grid UTAMA (dipakai untuk
        verifikasi data BARU yang disimpan ikut tampil). Grid
        inline-editable OPEL merender nilai di dalam <input> yang
        TIDAK masuk innerText -- jadi dicek keduanya (2026-08-21)."""
        timeout = timeout or config.LONG_TIMEOUT
        try:
            self._wait(timeout).until(
                lambda d: d.execute_script(
                    f"const t = {self.JS_GRID};"
                    "if (!t) return false;"
                    "const diTeks = t.innerText.includes(arguments[0]);"
                    "const diInput = [...t.querySelectorAll('input')].some("
                    "  i => (i.value || '').includes(arguments[0]));"
                    "return diTeks || diInput;",
                    teks,
                )
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Toolbar lain (FullScreen, Columns, Instructions)
    # ------------------------------------------------------------------
    def toggle_fullscreen(self):
        """Klik tombol FullScreen pakai mousedown+mouseup ASLI (Actions).

        JS .click() terbukti hanya bisa MASUK mode fullscreen; untuk
        KELUAR (tombol 'Windowed') handler aplikasi butuh urutan
        mousedown+mouseup sungguhan (diamati 2026-08-21 lewat
        tools/diagnose_fullscreen.py)."""
        element = self._ambil_js_visible(self.BTN_FULLSCREEN)
        ActionChains(self.driver).move_to_element(element).click_and_hold().pause(0.2).release().perform()
        self.pace()

    def toggle_columns(self):
        """Klik tombol Columns (muncul dropdown pilihan kolom)."""
        self.click_js_saat_tampil(self.BTN_COLUMNS)

    def buka_instruksi(self):
        """Klik link Instructions (title='Filling instructions')."""
        self.click_js_saat_tampil(self.BTN_INSTRUCTIONS)

    # ------------------------------------------------------------------
    # Cek tombol toolbar (dipakai test "bagian tombol pada fitur")
    # ------------------------------------------------------------------
    def tombol_toolbar_tampil(self, nama, timeout=None):
        """True kalau tombol toolbar `nama` benar-benar TAMPIL (cek
        computed style JS -- konsisten dengan helper lain supaya tahan
        terhadap false-negatif is_displayed() saat fade-transition)."""
        if nama not in self.TOMBOL_TOOLBAR:
            raise KeyError(
                f"Tombol toolbar '{nama}' tidak dikenal. Pilihan: "
                f"{', '.join(sorted(self.TOMBOL_TOOLBAR))}"
            )
        try:
            self._ambil_js_visible(self.TOMBOL_TOOLBAR[nama], timeout=timeout)
            return True
        except TimeoutException:
            return False

    def cek_tombol_toolbar(self, kunci=None, timeout=None):
        """Cek SEMUA tombol toolbar yang diharapkan tampil di halaman
        (daftar per halaman di TOMBOL_HALAMAN). Kembalikan
        dict {nama_tombol: bool}. `kunci` default = KUNCI page object
        ini (kalau instance-nya page object spesifik).

        Tombol yang belum tampil dicek ulang 1x setelah jeda singkat --
        halaman Timesheet masih bisa transisi render sesaat setelah
        buka() (Reload Data terbukti kadang baru tampil beberapa detik
        kemudian, 2026-08-21)."""
        kunci = kunci or getattr(self, "KUNCI", None)
        if kunci not in self.TOMBOL_HALAMAN:
            raise KeyError(
                f"Kunci halaman '{kunci}' tidak ada di TOMBOL_HALAMAN. "
                f"Pilihan: {', '.join(sorted(self.TOMBOL_HALAMAN))}"
            )
        daftar = self.TOMBOL_HALAMAN[kunci]
        hasil = {
            nama: self.tombol_toolbar_tampil(nama, timeout=timeout)
            for nama in daftar
        }
        hilang = [nama for nama, ok in hasil.items() if not ok]
        if hilang:
            time.sleep(2)
            for nama in hilang:
                if self.tombol_toolbar_tampil(nama, timeout=timeout):
                    hasil[nama] = True
        return hasil

    def buka_dropdown_columns(self):
        """Klik Columns lalu tunggu dropdown daftar kolom DataTables
        (div.dt-button-collection) benar-benar muncul. Timeout -> gagal
        (berarti tombol Columns tidak berfungsi)."""
        self.click_js_saat_tampil(self.BTN_COLUMNS)
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda d: d.execute_script(
                "const el = document.querySelector('div.dt-button-collection');"
                "if (!el) return false;"
                "const s = window.getComputedStyle(el);"
                "const r = el.getBoundingClientRect();"
                "return s.display !== 'none' && s.visibility !== 'hidden'"
                "&& r.width > 0 && r.height > 0;"
            ),
            "Dropdown Columns tidak kunjung muncul setelah klik Columns",
        )

    def fullscreen_aktif(self):
        """True kalau grid sedang mode fullscreen -- indikator andal:
        teks tombol berubah jadi 'Windowed'. (Class 'blur' di body
        ternyata TIDAK pernah muncul saat fullscreen, dicek langsung
        2026-08-21 lewat tools/diagnose_fullscreen.py.)"""
        return bool(self.driver.execute_script(
            "const b = document.querySelector('.fullscreen-button');"
            "return b && (b.innerText || '').trim() === 'Windowed';"
        ))

    def tunggu_fullscreen(self, aktif, timeout=None):
        """Tunggu mode fullscreen berubah jadi `aktif`. Kembalikan
        True kalau tercapai, False kalau timeout -- transisi aplikasi
        butuh waktu, cek langsung setelah klik bisa melihat state lama
        (2026-08-21)."""
        try:
            self._wait(timeout).until(
                lambda d: self.fullscreen_aktif() == aktif
            )
            return True
        except TimeoutException:
            return False
