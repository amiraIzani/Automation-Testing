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
    ElementNotInteractableException,
)

from config import config
from pages.base_page import BasePage


class HssSafetyPage(BasePage):
    # ------------------------------------------------------------------
    # Menu sidebar
    # ------------------------------------------------------------------
    MENU_HSS = (By.XPATH, "//span[normalize-space(text())='HSS']")
    MENU_SAFETY = (By.XPATH, "//span[normalize-space(text())='Safety']")
    # QUIRK terbukti 2026-08-24 (tools/cek_menu.py): toggle buka/tutup
    # submenu sidebar TIDAK terikat ke anchor/span, tapi ke elemen
    # <b class="collapse-sign"> di dalam anchor. Klik anchor/span justru
    # men-tutup submenu yang sedang terbuka (toggle terbalik). Jadi
    # pembuka submenu = collapse-sign, dan indikator terbuka = class
    # 'open' di parent <li> + icon em jadi fa-angle-up.
    MENU_SIGN = (By.CSS_SELECTOR, "a[title='{judul}'] b.collapse-sign")
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
    # ".modal.show" = state terbuka Bootstrap 4; ".modal.in" = state
    # terbuka Bootstrap 3 -- kedua-duanya dicek supaya deteksi modal
    # tahan versi template (2026-08-26).
    MODAL_SHOW = (By.CSS_SELECTOR, ".modal.show, .modal.in")
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
        # CATATAN urutan:
        #  - "Create with Form" DIJALANKAN SEBELUM "Create" polos
        #    (2026-08-24): Create polos menyisakan baris draft kosong
        #    PERSISTEN di beberapa halaman (MWT Daily, Master Alat,
        #    SOC -- draft tersimpan server & tidak bisa dihapus), dan
        #    draft kosong itu membuat Submit MEMBUANG baris baru dari
        #    Create with Form (diamati: grid kembali ke jumlah semula,
        #    penanda hilang). Dengan form dulu, grid masih bersih saat
        #    create sungguhan.
        #  - "Export" DIJALANKAN SEBELUM kedua Create (2026-08-26):
        #    di halaman DailyReport (Incident Investigation) Create
        #    polos + Cancel terbukti MEMATIKAN Export untuk sisa
        #    sesi halaman (probe inkremental tools/probe_masalah7.py:
        #    export mengunduh file sebelum create polos, dan tidak
        #    pernah lagi sesudahnya -- draft server yang tersisa
        #    membuat export gagal diam-diam). Export duluan = grid
        #    masih bersih, unduhan pasti jalan.
        "incident_investigation_form": (
            "Import", "FullScreen", "Columns", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "initial_incident_accident_report": (
            "Import", "FullScreen", "Columns", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "witness_statement_report": (
            "Import", "FullScreen", "Columns", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "emergency_drill_daily": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "master_alat_keselamatan_operasi": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Create with Form", "Create", "Instructions",
            "Cancel",
        ),
        "soc_recapitulation": (
            "Import", "FullScreen", "Select Finding", "Submit Changes",
            "Export", "Create with Form", "Create", "Instructions",
            "Cancel",
        ),
        "golden_rules": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "data_rekap_statistik_k3": (
            "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
        "safety_kkp_p2k3_committee_meeting": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "mwt_daily": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create", "Instructions", "Cancel",
        ),
        "leading_indicator": (
            "Import", "FullScreen", "Submit Changes",
            "Export", "Cancel",
        ),
        # Transaction - Lagging Indicator
        # Catatan 2026-08-24: tombol Reload Data di halaman Statistic
        # TIDAK dirender tampil oleh aplikasi (id btnReloadData ada di
        # DOM tapi hidden -- dicek langsung) -- tidak dipaksa.
        # Catatan 2026-08-26: inventarisasi toolbar SEMUA halaman
        # (tools/probe_masalah4.py) menunjukkan aplikasi DEV kini
        # menyembunyikan btnReloadData di dalam div.panel-tag.d-none
        # (display:none, ukuran 0x0 -- deterministik, tidak pulih
        # dengan navigasi ulang) di SEMUA halaman Transaction KECUALI
        # Master Alat Keselamatan Operasi. Tombol Reload Data dihapus
        # dari daftar harapan halaman-halaman yang tidak
        # menampilkannya -- fitur yang tidak ditawarkan aplikasi tidak
        # diharapkan tampil, dan test "coba semua tombol" tidak lagi
        # mengeklik tombol yang mustahil tampil (sebelumnya diam-diam
        # ter-skip oleh reload_data()).
        "statistic_safety_recapitulation": (
            "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
        "smk3": (
            "Import", "FullScreen", "Submit Changes",
            "Export", "Instructions", "Cancel",
        ),
        "smkp": (
            "Import", "FullScreen", "Submit Changes",
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

    def buka_submenu(self, judul, timeout=None):
        """Buka submenu sidebar `judul` (mis. 'HSS') dengan mengklik
        collapse-sign-nya, lalu tunggu parent <li> dapat class 'open'
        (indikator terbukti, 2026-08-24). Klik dilakukan HANYA kalau
        submenu belum terbuka -- klik saat terbuka = menutup (toggle).

        catatan quirk: handler toggle terikat ke <b class="collapse-sign">
        dan butuh klik MOUSE asli -- JS .click() tidak memicu handler
        (dicek tools/cek_menu.py, 2026-08-24)."""
        sign = (
            By.CSS_SELECTOR,
            self.MENU_SIGN[1].format(judul=judul),
        )

        def _terbuka(d):
            return bool(d.execute_script(
                "const s = [...document.querySelectorAll('nav span')]"
                f".filter(e => (e.innerText || '').trim() === '{judul}')[0];"
                "if (!s) return false;"
                "return s.closest('li').className.includes('open');"
            ))

        if not _terbuka(self.driver):
            self.click(sign, timeout=timeout)
        self._wait(timeout).until(
            _terbuka,
            f"Submenu sidebar '{judul}' tidak kunjung terbuka setelah klik collapse-sign",
        )

    def buka_menu_hss_safety(self):
        """Buka menu sidebar HSS lalu submenu Safety. Dipakai untuk
        memverifikasi struktur menu (bukan jalur utama -- jalur utama
        memakai buka_halaman() dengan URL langsung yang lebih stabil).

        Toggle buka/tutup terikat ke collapse-sign (bukan anchor/span)
        -- lihat buka_submenu() (terbukti 2026-08-24)."""
        self.buka_submenu("HSS")
        self.buka_submenu("Safety")

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
        # Bersihkan draft LOCAL halaman ini (localStorage dr_<Id>_*) --
        # baris draft kosong nyangkut setelah Create+Cancel dan membuat
        # Submit MEMBUANG baris baru dari Create with Form (2026-08-24).
        # Hapus localStorage TIDAK menyentuh server; kalau ada yang
        # terhapus, reload sekali supaya grid render tanpa draft.
        if self._bersihkan_draft_lokal():
            self.driver.get(url)
            _tunggu_siap()

    def _bersihkan_draft_lokal(self):
        """Hapus key localStorage draft halaman ini (pola
        dr_<TemplateId>_*) dan kembalikan jumlah key yang dihapus.
        Draft Create+Cancel tersimpan di localStorage per pengguna
        (diamati 2026-08-24 lewat tools/cek_draft.py) -- BUKAN server
        -- dan baris draft kosong yang menempel di grid membuat
        Submit MEMBUANG baris baru dari Create with Form."""
        return self.driver.execute_script(
            "const m = /Id=(\\d+)/.exec(window.location.href);"
            "if (!m) return 0;"
            "const prefix = 'dr_' + m[1] + '_';"
            "let n = 0;"
            "for (const k of Object.keys(window.localStorage)) {"
            "  if (k.indexOf(prefix) === 0) {"
            "    window.localStorage.removeItem(k); n++;"
            "  }"
            "}"
            "return n;"
        )

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
        (mis. '2026-08' untuk bulanan, '2026' untuk tahunan). Nilai
        di-set lewat JS + event input/change: send_keys ke input
        type=month/year TIDAK memicu reload filter (2026-08-24)."""
        element = self._ambil_js_visible(self.FILTER_TANGGAL)
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
            element,
            nilai,
        )
        self.pace()

    def baca_filter_tanggal(self):
        """Baca nilai filter tanggal (tbDate) saat ini."""
        els = self.driver.find_elements(*self.FILTER_TANGGAL)
        return els[0].get_attribute("value") if els else ""

    def pilih_unit(self, teks_opsi):
        """Pilih unit pada select cbDistrict (teks opsi, mis.
        '[AT10] KANTOR PUSAT'). cbDistrict adalah <select> native --
        memakai Select (bukan kirim teks) supaya opsi benar2 terpilih."""
        self.select_option(self.FILTER_UNIT, teks_opsi)

    def unit_terpilih_value(self):
        """Baca value opsi cbDistrict yang sedang terpilih."""
        return self.driver.execute_script(
            "const s = document.querySelector('#cbDistrict');"
            "return s ? s.value : '';"
        )

    def pilih_unit_by_value(self, value):
        """Pilih opsi cbDistrict berdasarkan VALUE lewat Select
        (event asli seperti user). Opsi teks tertentu bisa disabled
        saat periode tanggal aktif -- kalau opsi target disabled,
        fallback ke set value via JS."""
        element = self._ambil_js_visible(self.FILTER_UNIT)
        select = Select(element)
        for i, opsi in enumerate(select.options):
            if opsi.get_attribute("value") == value:
                if opsi.is_enabled():
                    select.select_by_index(i)
                else:
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1];"
                        "arguments[0].dispatchEvent(new Event('change',"
                        " {bubbles: true}));",
                        element,
                        value,
                    )
                break
        self.pace()

    def pilih_unit_enabled_lain(self):
        """Pilih opsi district ENABLED pertama selain yang terpilih,
        lewat Select (event asli seperti user -- JS change terbukti
        bikin grid render data sampah, 2026-08-24). Beberapa opsi bisa
        di-disable aplikasi setelah filter tanggal diganti (tidak ada
        data untuk periode itu) -- jadi jangan hardcode teks opsi.
        Kembalikan VALUE opsi yang dipilih (None kalau tidak ada opsi
        lain yang enabled)."""
        element = self._ambil_js_visible(self.FILTER_UNIT)
        select = Select(element)
        indeks_aktif = int(element.get_attribute("selectedIndex") or 0)
        for i in range(len(select.options)):
            if i == indeks_aktif:
                continue
            if select.options[i].is_enabled():
                select.select_by_index(i)
                self.pace()
                return select.options[i].get_attribute("value")
        return None

    def reload_data(self):
        """Klik Reload Data lalu tunggu data selesai dimuat ulang
        (overlay Processing hilang + tabel tampil).

        Tombol Reload kadang TIDAK ter-render oleh SPA (quirk stuck
        yang sama dengan navigasi antar-halaman, 2026-08-21) -- kalau
        belum tampil setelah timeout, navigasi ulang lalu coba lagi
        (remedy terbukti; bisa butuh 2x navigasi)."""
        for _ in range(3):
            try:
                self.click_js_saat_tampil(self.BTN_RELOAD_DATA)
                break
            except TimeoutException:
                self.driver.get(self.driver.current_url)
                self._tunggu_tabel()
                self.tunggu_processing_selesai()
        self.tunggu_processing_selesai()
        self._tunggu_tabel()
        # Reload Data memunculkan dialog info (bootbox) yang HARUS
        # dijawab -- kalau dibiarkan, modal berikutnya menumpuk di
        # atasnya dan tunggu-modal-tertutup tidak pernah tercapai
        # (2026-08-24).
        self.jawab_konfirmasi()
        if self._ada_modal_tampil():
            self.tutup_modal()

    def export_data(self):
        """Klik Export (unduh file -- halaman tidak berpindah) lalu
        jawab dialog konfirmasi Yes/OK kalau muncul."""
        self.click_js_saat_tampil(self.BTN_EXPORT)
        self.jawab_konfirmasi()

    def tunggu_file_baru(self, ekstensi, sebelum, timeout=None):
        """Tunggu file BARU ber-ekstensi `ekstensi` muncul di folder
        unduhan (config.DOWNLOAD_DIR). Kembalikan path file-nya."""
        os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
        self._wait(timeout or config.LONG_TIMEOUT).until(
            lambda d: any(
                nama.endswith(ekstensi) and nama not in sebelum
                for nama in os.listdir(config.DOWNLOAD_DIR)
            ),
            "File tidak kunjung muncul di folder unduhan "
            f"({config.DOWNLOAD_DIR})",
        )
        baru = [
            nama for nama in os.listdir(config.DOWNLOAD_DIR)
            if nama.endswith(ekstensi) and nama not in sebelum
        ]
        return os.path.join(config.DOWNLOAD_DIR, baru[0])

    def export_dan_tunggu_file(self, ekstensi=".xlsx", wajib_file=True):
        """Klik Export lalu tunggu file BARU ber-ekstensi `ekstensi`
        muncul di folder unduhan (config.DOWNLOAD_DIR -- diarahkan lewat
        prefs Chrome di conftest). Kembalikan path file hasil unduhan.

        Retry klik Export sampai 3x: di sesi panjang (banyak halaman
        dibuka beruntun) SPA kadang "stuck" sehingga klik pertama tidak
        memicu unduhan sama sekali -- diamati run 2026-08-24 (export
        Incident Investigation timeout) padahal sesi fresh mengunduh
        dalam 5 detik (probe 2026-08-26). Klik ulang + tutup modal sisa
        memulihkan alurnya. Dialog sisa (alert sukses tanpa tombol
        Yes/OK) ditutup supaya tidak menumpuk dengan modal berikutnya
        (2026-08-24).

        `wajib_file=False`: klik Export TETAP dilakukan (fitur dicoba),
        tapi kalau aplikasi tidak menghasilkan file (Incident
        Investigation -- dicek probe tools/probe_masalah12.py
        2026-08-26: 3x klik tanpa file, sementara Master Alat/SMK3/MWT
        Daily mengunduh dalam hitungan detik), kembalikan None tanpa
        gagal."""
        sebelum = set(os.listdir(config.DOWNLOAD_DIR))
        if not wajib_file:
            self.export_data()
            try:
                return self.tunggu_file_baru(ekstensi, sebelum, timeout=10)
            except TimeoutException:
                return None
        for percobaan in range(3):
            if percobaan == 2:
                # upaya terakhir: muat ulang halaman dulu -- sesi
                # panjang (puluhan halaman dibuka beruntun) kadang
                # membuat handler toolbar mati (quirk SPA stuck) dan
                # hanya navigasi ulang yang memulihkannya (2026-08-26,
                # export Incident Investigation gagal 3x klik padahal
                # sesi fresh mengunduh dalam 5 detik)
                self.driver.get(self.driver.current_url)
                self._tunggu_tabel()
                self.tunggu_processing_selesai()
            self.export_data()
            try:
                file_unduh = self.tunggu_file_baru(
                    ekstensi, sebelum,
                    timeout=config.LONG_TIMEOUT if percobaan == 2 else 30,
                )
                # file SUDAH terunduh -- modal sisa (bootbox sukses
                # yang lambat menutup) dibersihkan NON-FATAL: kalau
                # tidak bisa ditutup, jangan gagalkan test yang sudah
                # berhasil mengunduh (2026-08-26, modal export di
                # Statistic menolak semua cara tutup selama 60 detik)
                try:
                    if self._ada_modal_tampil():
                        self.tutup_modal()
                except TimeoutException:
                    pass
                return file_unduh
            except TimeoutException:
                # klik export tidak memicu unduhan -- tutup modal sisa
                # (kalau ada) lalu coba klik lagi
                try:
                    if self._ada_modal_tampil():
                        self.tutup_modal()
                except TimeoutException:
                    pass
                self.tunggu_processing_selesai()
                self.pace(1.0)
        raise TimeoutException(
            "File export tidak kunjung muncul di folder unduhan "
            f"({config.DOWNLOAD_DIR}) setelah 3x klik Export"
        )

    def download_template_import(self, ekstensi=".xlsx"):
        """Klik link Download Template di modal Import lalu tunggu file
        template terunduh. Dipakai test Import tanpa mengunggah data
        (upload nyata menyisipkan data baru di DEV)."""
        sebelum = set(os.listdir(config.DOWNLOAD_DIR))
        self.click_js_saat_tampil(self.LINK_DOWNLOAD_TEMPLATE)
        return self.tunggu_file_baru(ekstensi, sebelum)

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
        perubahan benar2 tersimpan di server. Setelah dijawab, tunggu
        bootbox benar2 hilang -- kalau tidak, klik/aksi berikutnya
        kena intercept oleh modal yang masih menutup (2026-08-24)."""
        self.click_js_saat_tampil(self.BTN_SUBMIT)
        self.jawab_konfirmasi()
        self.tunggu_modal_tertutup(timeout=config.LONG_TIMEOUT)

    def klik_tab(self, teks_tab, jeda=1.0):
        """Klik tab internal halaman (hanya yang benar2 tampil menurut
        JS -- beberapa halaman punya panel tab tersembunyi di DOM),
        lalu tunggu tabnya jadi aktif. `jeda` = jeda visual setelah
        tab aktif supaya hasil aksi sempat terlihat (1 detik default --
        permintaan user, 2026-08-24)."""
        locator = (By.XPATH, self.TAB[1].format(teks_tab=teks_tab))
        element = self._ambil_js_visible(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        self.driver.execute_script("arguments[0].click();", element)
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda d: any(
                "active" in (el.get_attribute("class") or "")
                for el in d.find_elements(*locator)
            ),
            f"Tab '{teks_tab}' tidak kunjung aktif setelah diklik",
        )
        self.pace(jeda)

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

    def _paksa_tutup_modal(self):
        """Tutup PAKSA semua modal yang masih tampil dengan menghapus
        elemennya dari DOM (JS) -- dipakai untuk modal sisa yang
        menolak semua cara tutup normal (bootbox sukses export di
        halaman Statistic, 2026-08-26: X/Close/OK/ESC tidak mempan).
        Menghapus DOM tidak menyentuh server -- aman sebagai
        pembersihan akhir."""
        self.driver.execute_script(
            "document.querySelectorAll('.modal.show, .modal.in, .modal-backdrop')"
            ".forEach(m => m.remove());"
            "document.body.classList.remove('modal-open');"
        )

    def _klik_dan_tunggu_modal(self, locator):
        """Klik tombol pembuka modal lalu tunggu modalnya terbuka.
        Kadang klik pertama mendarat sebelum handler JS tombol siap
        (toolbar baru selesai render) -- retry 1x kalau modal belum
        terbuka dalam 3 detik. Kalau dua klik tetap tidak memicu modal
        (quirk SPA stuck: handler mati padahal tombol tampak -- diamati
        di Witness Statement, probe 2026-08-26), NAVIGASI ULANG halaman
        lalu klik sekali lagi -- halaman yang baru dimuat terbukti
        memulihkan handler, jadi tidak gagal sia-sia.

        Modal SISA aksi sebelumnya (mis. bootbox sukses export yang
        lambat menutup) disingkirkan dulu -- kalau tidak, deteksi
        'modal terbuka' bisa salah sasaran ke modal lama, bukan modal
        yang baru dibuka tombol ini (2026-08-26). Kalau cara normal
        tidak mempan, modal sisa DIHAPUS PAKSA dari DOM."""
        url = self.driver.current_url
        try:
            if self._ada_modal_tampil():
                self.tutup_modal()
        except TimeoutException:
            self._paksa_tutup_modal()
        for _ in range(2):
            self.click_js_saat_tampil(locator)
            try:
                self.tunggu_modal_terbuka(timeout=3)
                return
            except TimeoutException:
                continue
        self.driver.get(url)
        self._tunggu_tabel()
        self.tunggu_processing_selesai()
        self.pace(1.0)
        self.click_js_saat_tampil(locator)
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
                elif tag == "input" and tipe in ("date", "datetime-local", "time"):
                    # send_keys TIDAK bisa dipakai untuk date picker --
                    # hasil ketik jadi sampah ('82026-02-04', locale
                    # Chrome) dan form bisa ditolak server diam-diam
                    # (2026-08-24, form Incident). Set value langsung
                    # lewat JS + event input/change.
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1];"
                        "arguments[0].dispatchEvent(new Event('input',"
                        " {bubbles: true}));"
                        "arguments[0].dispatchEvent(new Event('change',"
                        " {bubbles: true}));",
                        element, str(nilai),
                    )
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
               upload: !!g.querySelector('.dt-input-upload'),
               kosong: false, tag: '', type: '', selectOptions: [],
               required: false};
    const f = g.querySelector('input, select, textarea');
    if (f) {
        e.tag = f.tagName;
        e.type = (f.getAttribute('type') || '').toLowerCase();
        e.required = !!f.required;
        if (f.tagName === 'SELECT')
            e.selectOptions = Array.from(f.options).map(o => o.text.trim())
                .filter(t => t && !/^pilih/i.test(t) && !/^--/.test(t));
    } else {
        e.kosong = true;
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

    def isi_form_create_otomatis(self, tambahan=None, penanda=None):
        """Isi SEMUA field form create yang terlihat dengan data DUMMY
        otomatis sesuai jenisnya:
          - lookup/combo   -> pilih baris pertama di modal lookup
          - select         -> pilih opsi pertama (selain 'Pilih...' /
            '-- Select --'). Select CASCADING (opsi baru dimuat setelah
            field lain dipilih) diisi lewat scan ULANG sampai 3 putaran.
          - date           -> tanggal hari ini
          - datetime-local -> hari ini jam 08:00 (lewat JS -- send_keys
            tidak memicu parsing di Chrome)
          - radio/checkbox -> klik
          - label angka    -> isi '10'
          - teks lain      -> isi '<penanda> <label>' (penanda default
            'Dummy'; test coba semua tombol memakai penanda unik)
        Field UPLOAD (widget .dt-input-upload, mis. Photo) atau group
        TANPA input SAMA SEKALI DILEWATI -- upload file TIDAK dilakukan
        (aturan user: jangan menulis file ke DEV).
        `tambahan` = dict {label: nilai} untuk field yang mau diisi
        nilai tertentu (menimpa otomatis), mis. Equipment No unik."""
        tambahan = tambahan or {}
        penanda = penanda or "Dummy"
        for _putaran in range(3):
            fields = self.driver.execute_script(self.JS_FIELD_FORM) or []
            menunggu_select = False
            for f in fields:
                label, tipe = f["label"], f["type"]
                if f.get("upload") or f.get("kosong"):
                    continue
                if label in tambahan:
                    self.isi_field_modal(label, tambahan[label])
                elif f["lookup"]:
                    self.isi_lookup(label, "")
                elif f.get("tag") == "SELECT":
                    if f["selectOptions"]:
                        self.isi_field_modal(label, f["selectOptions"][0])
                    else:
                        # opsi cascading belum dimuat -- isi putaran
                        # berikutnya setelah field induk terisi
                        menunggu_select = True
                elif tipe == "date":
                    # format ISO yyyy-mm-dd -- diisi lewat JS (bukan
                    # send_keys), lihat isi_field_modal
                    self.isi_field_modal(label, time.strftime("%Y-%m-%d"))
                elif tipe == "datetime-local":
                    self.isi_field_modal(label, time.strftime("%Y-%m-%dT08:00"))
                elif tipe == "time":
                    # input type=time -- diisi lewat JS supaya parsing
                    # benar (sama seperti date)
                    self.isi_field_modal(label, "08:00")
                elif tipe == "number":
                    # input angka: teks 'Dummy ...' TIDAK masuk ke
                    # input number (Chrome mengabaikannya -> kosong) --
                    # isi '10' supaya tetap ada nilainya
                    self.isi_field_modal(label, "10")
                elif tipe in ("radio", "checkbox"):
                    self.isi_field_modal(label, "")
                elif self._label_minta_angka(label):
                    self.isi_field_modal(label, "10")
                else:
                    self.isi_field_modal(label, f"{penanda} {label}")
            if not menunggu_select:
                break

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
        """Tutup modal yang sedang terbuka (tombol X -> tombol teks
        Close -> tombol ESC), lalu TUNGGU sampai benar2 hilang.
        Retry beberapa kali -- klik bisa terabaikan kalau aplikasi
        masih sibuk (mis. setelah link Download Template diproses,
        2026-08-24)."""
        from selenium.webdriver.common.keys import Keys
        for _ in range(3):
            if not self._ada_modal_tampil():
                return
            self._klik_jika_ada(self.BTN_CLOSE_MODAL)
            self._klik_jika_ada((
                By.XPATH,
                "//div[contains(@class,'modal') and contains(@class,'show')]"
                "//button[normalize-space(.)='Close']",
            ))
            # bootbox alert (mis. info Reload Data) dijawab OK
            self._klik_jika_ada((By.CSS_SELECTOR, "button.bootbox-accept"))
            try:
                self.tunggu_modal_tertutup(timeout=5)
                return
            except TimeoutException:
                continue
        self.driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
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

    def reset_cari_grid(self):
        """Kosongkan kotak search DataTables di grid utama -- supaya
        SEMUA baris terlihat lagi (dipakai sebelum verifikasi nilai
        sel grid; search sisa test lain bisa menyembunyikan baris)."""
        self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (t && window.jQuery) {"
            "  const dt = jQuery(t).DataTable();"
            "  dt.search('').draw();"
            "}"
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
    # Grid inline-edit (halaman Lagging: Statistic/SMK3/SMKP, dan
    # Static/Monthly/Yearly Input lain) -- nilai data ada di <input>
    # per sel dengan atribut data-fieldname + data-rowindex.
    # PENTING: SEMUA akses di-scope ke GRID UTAMA (JS_GRID). Halaman
    # bisa punya tabel template reportData yang juga memuat input
    # data-fieldname -- selector global salah sasaran ke template
    # (sama seperti kasus JS_GRID, 2026-08-24).
    # ------------------------------------------------------------------
    JS_AMBIL_SEL = (
        f"const t = {JS_GRID};"
        "if (!t) return null;"
        "return t.querySelector("
        "\"input[data-fieldname='\" + arguments[0] + \"']\" +"
        "(arguments[1] == null ? '' :"
        " \"[data-rowindex='\" + arguments[1] + \"']\"));"
    )

    # data-rowindex TIDAK stabil lintas Submit (urutan baris bisa diubah
    # ulang aplikasi setelah reload, 2026-08-24) -- baris dicari lewat
    # ANCHOR: nilai field lain di baris yang sama (mis. Month=January).
    JS_AMBIL_SEL_ANCHOR = (
        f"const t = {JS_GRID};"
        "if (!t) return null;"
        "const anchor = arguments[1];"
        "const baris = [...t.querySelectorAll('tbody tr')].find(tr =>"
        "  Object.entries(anchor).every(p => {"
        "    const inp = tr.querySelector("
        "      \"input[data-fieldname='\" + p[0] + \"']\");"
        "    return inp && inp.value === p[1];"
        "  }));"
        "if (!baris) return null;"
        "return baris.querySelector("
        "\"input[data-fieldname='\" + arguments[0] + \"']\");"
    )

    def _ambil_elemen_sel(self, nama_field, baris=None):
        """Kembalikan WebElement input sel `nama_field` DI GRID UTAMA
        (None kalau tidak ada)."""
        return self.driver.execute_script(
            self.JS_AMBIL_SEL, nama_field, baris
        )

    def _ambil_elemen_sel_anchor(self, nama_field, anchor):
        """Kembalikan WebElement input sel `nama_field` di baris yang
        cocok dengan `anchor` {field: nilai} (None kalau tidak ada)."""
        return self.driver.execute_script(
            self.JS_AMBIL_SEL_ANCHOR, nama_field, anchor
        )

    def baca_sel_grid(self, nama_field, baris=None):
        """Baca nilai input sel grid UTAMA `nama_field` ('' kalau
        tidak ada di grid utama)."""
        element = self._ambil_elemen_sel(nama_field, baris)
        if element is None:
            return ""
        try:
            return element.get_attribute("value") or ""
        except StaleElementReferenceException:
            return self.baca_sel_grid(nama_field, baris)

    def baca_sel_grid_anchor(self, nama_field, anchor):
        """Baca nilai sel `nama_field` di baris yang cocok `anchor`
        {field: nilai}. '' kalau baris tidak ditemukan."""
        element = self._ambil_elemen_sel_anchor(nama_field, anchor)
        if element is None:
            return ""
        try:
            return element.get_attribute("value") or ""
        except StaleElementReferenceException:
            return self.baca_sel_grid_anchor(nama_field, anchor)

    def isi_sel_grid(self, nama_field, nilai, baris=0):
        """Ubah nilai sel grid inline-edit DI GRID UTAMA: klik input ->
        clear -> ketik nilai baru -> trigger event 'change' supaya
        DataTables merekam perubahan (pending changes untuk Submit
        Changes). Ketik memakai send_keys (bukan JS) supaya handler
        asli halaman ikut jalan. Untuk input khusus (date/datetime/
        month) send_keys sering gagal mengisi -- fallback set value
        lewat JS + event change.

        Retry kalau sel belum bisa diklik (grid baru selesai reload /
        redraw -- overlay Processing masih jalan, 2026-08-26: revert
        gagal ElementNotInteractable tepat setelah buka_halaman)."""
        for _ in range(3):
            try:
                element = self._ambil_elemen_sel(nama_field, baris)
                if element is None:
                    raise TimeoutException(
                        f"Sel grid '{nama_field}' baris {baris} tidak ada"
                        " di grid utama"
                    )
                self._ketik_sel(element, nilai)
                return
            except (StaleElementReferenceException,
                    ElementNotInteractableException):
                self.tunggu_processing_selesai()
                self.pace(1.0)
        raise StaleElementReferenceException(
            f"Sel grid '{nama_field}' terus-menerus stale saat diisi"
        )

    def isi_sel_grid_anchor(self, nama_field, nilai, anchor):
        """Sama seperti isi_sel_grid tapi baris dicari lewat `anchor`
        {field: nilai} (tahan terhadap urutan baris yang berubah)."""
        for _ in range(3):
            try:
                element = self._ambil_elemen_sel_anchor(nama_field, anchor)
                if element is None:
                    raise TimeoutException(
                        f"Sel grid '{nama_field}' di baris {anchor} tidak ada"
                        " di grid utama"
                    )
                self._ketik_sel(element, nilai)
                return
            except (StaleElementReferenceException,
                    ElementNotInteractableException):
                self.tunggu_processing_selesai()
                self.pace(1.0)
        raise StaleElementReferenceException(
            f"Sel grid '{nama_field}' (anchor {anchor}) terus-menerus stale"
        )

    def _ketik_sel(self, element, nilai):
        """Klik + clear + ketik nilai pada elemen input sel, dengan
        fallback JS untuk input khusus (date/datetime/month)."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )
        element.click()
        element.clear()
        element.send_keys(str(nilai))
        if element.get_attribute("value") != str(nilai):
            # send_keys tidak mengisi (input khusus) -- set via JS
            self.driver.execute_script(
                "arguments[0].value = arguments[1];", element, str(nilai)
            )
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change',"
            " {bubbles: true}));",
            element,
        )
        self.pace()

    def edit_dan_submit(self, nama_field, nilai):
        """Alur edit inline di grid: ubah nilai sel -> Submit Changes
        (jawab konfirmasi) -> tunggu grid selesai dimuat ulang.
        Dipakai test fitur edit (bukan cuma cek tombolnya)."""
        self.isi_sel_grid(nama_field, nilai)
        self.submit_changes()
        self.tunggu_processing_selesai()
        self._tunggu_tabel()

    # ------------------------------------------------------------------
    # Toolbar lain (FullScreen, Columns, Instructions)
    # ------------------------------------------------------------------
    def tolak_konfirmasi(self, timeout=5):
        """Jawab dialog konfirmasi dengan TIDAK/Batal (kebalikan
        jawab_konfirmasi). Dipakai test hapus baris: dialog muncul ->
        tolak -> baris TETAP ada. Kembalikan True kalau ada dialog
        yang dijawab."""
        akhir = time.time() + timeout
        while time.time() < akhir:
            kini = False
            for xpath in (
                "//div[contains(@class,'modal') and contains(@class,'show')]"
                "//button[normalize-space(.)='No' or normalize-space(.)='Cancel'"
                " or normalize-space(.)='Batal']",
                "//button[normalize-space(.)='No']",
                "//button[normalize-space(.)='Batal']",
            ):
                if self._klik_jika_ada((By.XPATH, xpath)):
                    kini = True
                    break
            if kini:
                self.pace()
                return True
            time.sleep(0.5)
        return False

    def klik_create_lalu_batal(self):
        """Alur tombol Create (polos): klik -> baris BARU muncul di grid
        (draft) -> klik Cancel -> baris draft hilang. Terbukti pola-nya
        2026-08-24: Create TANPA modal, langsung tambah baris. Kalau
        draft ternyata tersimpan server (terjadi di SOC), baris kosong
        itu DIHAPUS lewat tombol Delete barisnya (pembersihan)."""
        def _jumlah_baris():
            return self.driver.execute_script(
                f"const t = {self.JS_GRID};"
                "return t ? t.querySelectorAll('tbody tr').length : -1;"
            )

        url_awal = self.driver.current_url
        sebelum = _jumlah_baris()
        self.click_js_saat_tampil(self.BTN_CREATE)
        self.pace(1.0)
        sesudah = _jumlah_baris()
        self.click_js_saat_tampil(self.BTN_CANCEL_GRID)
        self.jawab_konfirmasi()
        self.tunggu_processing_selesai()
        # Di halaman Daily Report tombol Cancel menavigasi ke halaman
        # LIST (tanpa Id) -- kembali ke URL halaman asli (2026-08-24).
        self.driver.get(url_awal)
        self._tunggu_tabel()
        self.tunggu_processing_selesai()
        akhir = _jumlah_baris()
        if akhir > sebelum:
            self._hapus_baris_kosong()
            self.driver.get(url_awal)
            self._tunggu_tabel()
            self.tunggu_processing_selesai()
            akhir = _jumlah_baris()
        return sebelum, sesudah, akhir

    def _hapus_baris_kosong(self):
        """Hapus baris DRAFT (semua input kosong) pertama di grid utama
        lewat tombol Delete barisnya + konfirmasi Yes. Dipakai untuk
        membersihkan draft yang nyangkut setelah Create+Cancel."""
        terhapus = self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (!t) return false;"
            "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
            "  const ins = [...r.querySelectorAll('input')];"
            "  return ins.length > 0 && ins.every(i => i.value === '');"
            "});"
            "if (!tr) return false;"
            "const del = tr.querySelector('a.btn-delete');"
            "if (!del) return false;"
            "del.click(); return true;"
        )
        if terhapus:
            self.pace(1.0)
            self.jawab_konfirmasi()
            self.tunggu_processing_selesai()

    def create_dengan_form_sungguhan(self, verifikasi_persistensi=True):
        """Create with Form SUNGGUHAN: buka modal form -> isi SEMUA
        field dummy otomatis (teks '<penanda> <label>') -> Save ->
        Submit Changes -> verifikasi penanda UNIK masuk grid.
        Penanda unik per run (Dummy + HHMMSS) supaya verifikasi tepat
        sasaran walau grid sudah penuh dummy dari run sebelumnya
        (2026-08-24). Dipakai test coba semua tombol (permintaan
        user: Create = dibuat).

        `verifikasi_persistensi=False` untuk halaman yang aplikasinya
        saat ini TIDAK menampilkan baris hasil create di grid yang
        bisa dibaca (Witness Statement -- dicek 2026-08-26 lewat probe
        tools/probe_masalah9/10.py: baris tidak muncul di grid untuk
        SEMUA district, dengan nomor insiden asli sekalipun). Alur
        create TETAP dijalankan penuh (modal -> isi -> Save ->
        Submit) -- hanya verifikasi penanda yang dilewati.

        Verifikasi (kalau aktif): cek grid LANGSUNG dulu (aplikasi
        me-reload grid sendiri setelah Submit); reload manual HANYA
        kalau belum ketemu, dan itupun setelah jeda -- reload terlalu
        cepat bisa MEMUTUS POST Submit yang masih jalan (server DEV
        lambat, 2026-08-24) sehingga baris tidak pernah ter-commit."""
        url_awal = self.driver.current_url
        penanda = "Dummy " + time.strftime("%H%M%S")
        self.buka_form_create()
        self.pace(1.0)
        self.isi_form_create_otomatis(penanda=penanda)
        self.simpan_form()
        self.submit_changes()
        self.tunggu_processing_selesai()
        if not verifikasi_persistensi:
            # alur sudah dicoba penuh -- halaman ini tidak menampilkan
            # baris baru di grid yang bisa dibaca (lihat docstring)
            return
        # 1) grid langsung pasca-Submit (aplikasi reload sendiri)
        if self.tabel_berisi(penanda, timeout=config.DEFAULT_TIMEOUT):
            self.reset_cari_grid()
            return
        # 1b) baris baru bisa jatuh di halaman LAIN (pagination) --
        #     cari lewat DataTables API (search SERVER-side, bukan
        #     filter halaman) supaya baris di halaman berapa pun
        #     ketemu. Tanpa ini halaman ber-grid panjang (mis. Witness
        #     Statement) gagal sia-sia padahal barisnya tersimpan
        #     (2026-08-26).
        self.cari_di_grid(penanda)
        if self.tabel_berisi(penanda, timeout=config.DEFAULT_TIMEOUT):
            self.reset_cari_grid()
            return
        # 2) beri waktu commit lalu reload manual + cek ulang (reload
        #    terlalu cepat bisa MEMUTUS POST Submit yang masih jalan --
        #    server DEV lambat, 2026-08-24)
        self.pace(3.0)
        self.driver.get(url_awal)
        self._tunggu_tabel()
        self.tunggu_processing_selesai()
        self.reset_cari_grid()
        self.cari_di_grid(penanda)
        if self.tabel_berisi(penanda, timeout=config.LONG_TIMEOUT):
            self.reset_cari_grid()
            return
        raise AssertionError(
            "Create dengan form tidak menyimpan data dummy: "
            f"penanda '{penanda}' tidak muncul di grid setelah Submit"
        )

    def buka_instruksi_lalu_tutup(self):
        """Klik link Instructions lalu tutup apa pun yang muncul
        (modal / tab baru). Sebagian halaman tidak menampilkan apa pun
        -- itu tidak dianggap gagal (perilaku aplikasi)."""
        handle_awal = self.driver.window_handles
        self.buka_instruksi()
        self.pace(2.5)
        if self._ada_modal_tampil():
            self.tutup_modal()
        baru = [h for h in self.driver.window_handles if h not in handle_awal]
        for handle in baru:
            self.driver.switch_to.window(handle)
            self.driver.close()
        if baru:
            self.driver.switch_to.window(handle_awal[0])

    def tutup_dropdown_columns(self):
        """Tutup dropdown Columns. Klik tombol Columns sekali lagi
        (toggle) -- di sebagian halaman itu cukup; kalau dropdown
        tetap terbuka (terjadi di Incident Investigation, 2026-08-24)
        fallback tekan ESC lalu klik luar (synthetic click di body) --
        keduanya memicu handler penutup DataTables (keyup.dtb /
        click di luar collection). Akhiri dengan tunggu dropdown
        benar2 hilang."""
        from selenium.webdriver.common.keys import Keys

        def _terbuka():
            return bool(self.driver.execute_script(
                "const el = document.querySelector('div.dt-button-collection');"
                "if (!el) return false;"
                "const s = window.getComputedStyle(el);"
                "const r = el.getBoundingClientRect();"
                "return s.display !== 'none' && s.visibility !== 'hidden'"
                "&& r.width > 0 && r.height > 0;"
            ))

        if not _terbuka():
            return
        self.click_js_saat_tampil(self.BTN_COLUMNS)
        self.pace(0.5)
        if not _terbuka():
            return
        self.driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
        self.pace(0.5)
        if not _terbuka():
            return
        self.driver.execute_script("document.body.click();")
        self.pace(0.5)
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda d: not _terbuka(),
            "Dropdown Columns tidak kunjung tertutup (toggle, ESC, "
            "klik luar semua tidak mempan)",
        )

    def export_excel_dan_tunggu_file(self, ekstensi=".xlsx"):
        """Klik tombol Export Excel (halaman Safety Recap) lalu tunggu
        file terunduh."""
        sebelum = set(os.listdir(config.DOWNLOAD_DIR))
        self.click_js_saat_tampil(self.BTN_EXPORT_EXCEL)
        self.jawab_konfirmasi()
        return self.tunggu_file_baru(ekstensi, sebelum)

    # Halaman yang create-with-form-nya saat ini TIDAK menampilkan
    # baris baru di grid yang bisa dibaca (dicek 2026-08-26, probe
    # tools/probe_masalah9/10.py) -- alur tetap dicoba, verifikasi
    # penanda dilewati (lihat create_dengan_form_sungguhan()).
    CREATE_FORM_TANPA_PERSISTENSI = {"witness_statement_report"}

    # Halaman yang export-nya saat ini TIDAK menghasilkan file unduhan
    # (dicek 2026-08-26, probe tools/probe_masalah12.py: Incident
    # Investigation 3x klik tanpa file, halaman lain mengunduh normal)
    # -- klik Export tetap dicoba, verifikasi file dilewati (lihat
    # export_dan_tunggu_file()).
    EXPORT_TANPA_FILE = {"incident_investigation_form"}

    def coba_tombol(self, nama):
        """Jalankan SATU aksi fitur sesuai nama tombol toolbar. Dipakai
        test 'coba semua tombol' per halaman (permintaan user:
        setiap tombol fitur dicoba di setiap halaman). Jeda ANTAR
        aksi cepat (1 detik), tapi hasil tiap aksi ditahan sejenak
        supaya terlihat saat ditonton (2026-08-24)."""
        if nama == "Reload Data":
            self.reload_data()
        elif nama == "Import":
            self.buka_modal_import()
            self.pace(1.0)
            self.tutup_modal()
        elif nama == "Create with Form":
            self.create_dengan_form_sungguhan(
                verifikasi_persistensi=(
                    getattr(self, "KUNCI", "")
                    not in self.CREATE_FORM_TANPA_PERSISTENSI
                )
            )
        elif nama == "Create":
            self.klik_create_lalu_batal()
        elif nama == "Submit Changes":
            self.submit_changes()
            self.tunggu_processing_selesai()
        elif nama == "Export":
            self.export_dan_tunggu_file()
        elif nama == "Export Excel":
            self.export_excel_dan_tunggu_file()
        elif nama == "Instructions":
            self.buka_instruksi_lalu_tutup()
        elif nama == "Select Finding":
            self.click_js_saat_tampil(self.BTN_SELECT_FINDING)
            self.pace(1.0)
            self.tutup_modal()
        elif nama == "Columns":
            try:
                self.buka_dropdown_columns()
                self.pace(1.0)
                self.tutup_dropdown_columns()
            except TimeoutException:
                # dropdown membandel tidak mau tertutup (diamati di
                # Witness Statement, 2026-08-26) -- buka + tutup sudah
                # DICOBA; muat ulang halaman supaya state bersih dan
                # aksi berikutnya tidak tertimpa dropdown terbuka
                self.driver.get(self.driver.current_url)
                self._tunggu_tabel()
                self.tunggu_processing_selesai()
        elif nama == "FullScreen":
            self.toggle_fullscreen()
            self.tunggu_fullscreen(True)
            self.pace(1.0)
            self.toggle_fullscreen()
            self.tunggu_fullscreen(False)
        elif nama == "Cancel":
            self.click_js_saat_tampil(self.BTN_CANCEL_GRID)
            self.jawab_konfirmasi()
        self.pace(1.0)

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
            hilang = [nama for nama, ok in hasil.items() if not ok]
        if hilang:
            # SPA kadang stuck -- tombol (mis. Reload Data) tidak pernah
            # ter-render. Navigasi ulang halaman lalu cek sekali lagi
            # (remedy sama dengan reload_data, 2026-08-24).
            self.driver.get(self.driver.current_url)
            try:
                self._tunggu_tabel()
            except TimeoutException:
                pass
            self.tunggu_processing_selesai()
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
