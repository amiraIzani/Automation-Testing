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

import base64
import json
import os
import re
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    MoveTargetOutOfBoundsException,
)

from config import config
from pages.base_page import BasePage


class TidakPunyaAkses(Exception):
    """Dilempar kalau halaman OPEL menampilkan pesan 'tidak punya akses'
    (user tidak diizinkan melihat halaman tersebut). Test yang menangkap
    exception ini bisa melakukan pytest.skip() supaya suite tetap lanjut
    ke halaman berikutnya."""


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
    # template.
    #
    # BUG (dibuktikan 2026-09-04 lewat tools/cek_grid_semua_halaman.py):
    # halaman BERTAB me-render SATU GRID PER TAB, semuanya sekaligus di
    # DOM. Hasil sweep:
    #   incident_investigation_form : 6 DataTables (tableData_1937..1942)
    #   data_rekap_statistik_k3     : 4 DataTables (tableData_1872..1875)
    #   witness_statement_report    : 2 DataTables (tableData_1944..1945)
    # Pemilihan yang cuma berdasar "punya baris"/"baris terbanyak"
    # SELALU jatuh ke grid TAB PERTAMA (di Incident: 3 baris vs 0; di
    # Data Rekap K3: seri 12-12-12-12, reduce menyimpan yang pertama).
    # Akibatnya begitu test pindah tab, SELURUH helper grid (dt_info,
    # baca/isi sel, cari_di_grid) tetap membaca grid tab 1 -- grid tab
    # lain tidak pernah tersentuh, dan assertion-nya jadi lulus palsu.
    #
    # Perbaikan: dahulukan grid yang BENAR-BENAR TAMPIL. Panel tab yang
    # tidak aktif ber-display:none, jadi offsetParent-nya null -- itu
    # pembeda yang andal antara grid tab aktif dan grid tab lain.
    #
    # Prioritas (paling spesifik -> paling longgar), diterapkan dulu ke
    # tabel yang TAMPIL, baru ke semua tabel sebagai cadangan:
    #   1. DataTables ter-init DAN ber-id tableData_* -> grid asli
    #   2. DataTables ter-init dengan recordsTotal terbanyak
    #   3. tabel dengan baris DATA terbanyak (baris 'No data available'
    #      / td.dataTables_empty TIDAK dihitung)
    #   4. ber-id tableData_* -> tabel pertama
    JS_GRID = (
        "(() => {"
        "  const ts = [...document.querySelectorAll('table.reportData')];"
        "  if (!ts.length) return null;"
        "  const punyaId = t => t.id && t.id.indexOf('tableData_') === 0;"
        "  const tampil = t => {"
        "    if (t.offsetParent !== null) return true;"
        "    const r = t.getBoundingClientRect();"
        "    return r.width > 0 || r.height > 0;"
        "  };"
        "  const barisData = t => [...t.querySelectorAll('tbody tr')]"
        "      .filter(tr => !tr.querySelector('td.dataTables_empty')).length;"
        "  const total = t => {"
        "    try {"
        "      if (window.jQuery && jQuery.fn.dataTable"
        "          && jQuery.fn.dataTable.isDataTable(t))"
        "        return jQuery(t).DataTable().page.info().recordsTotal;"
        "    } catch (e) {}"
        "    return -1;"
        "  };"
        "  const pilih = arr => {"
        "    if (!arr.length) return null;"
        "    const dt = arr.filter(t => total(t) >= 0);"
        "    const dtBerId = dt.filter(punyaId);"
        "    if (dtBerId.length)"
        "      return dtBerId.reduce((a, b) => total(b) > total(a) ? b : a);"
        "    if (dt.length)"
        "      return dt.reduce((a, b) => total(b) > total(a) ? b : a);"
        "    const isi = arr.filter(t => barisData(t) > 0);"
        "    if (isi.length)"
        "      return isi.reduce((a, b) => barisData(b) > barisData(a) ? b : a);"
        "    return arr.find(punyaId) || arr[0] || null;"
        "  };"
        "  return pilih(ts.filter(tampil)) || pilih(ts);"
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
    # ".modal.show" = state terbuka Bootstrap 4; ".modal.in" = state
    # terbuka Bootstrap 3 -- kedua-duanya dicek supaya deteksi modal
    # tahan versi template (2026-08-26).
    MODAL_SHOW = (By.CSS_SELECTOR, ".modal.show, .modal.in")
    # XPath dasar modal terbuka -- cek .show DAN .in: modal Bootstrap 3
    # hanya berkelas 'in', jadi tombol/field di dalamnya tidak ketemu
    # kalau hanya .show yang dicek (gagal aneh saat modal TERBUKA,
    # 2026-08-28).
    XP_MODAL = (
        "//div[contains(@class,'modal')"
        " and (contains(@class,'show') or contains(@class,'in'))]"
    )
    BTN_CLOSE_MODAL = (
        By.XPATH,
        XP_MODAL + "//button[contains(@class,'close') or normalize-space(.)='Close']",
    )

    # ------------------------------------------------------------------
    # Modal Create with Form (id dinamis: input_NNNNN, cbXX_*_NNNN,
    # btnSave_NNNN -- field DICARI lewat label, tombol lewat teks)
    # ------------------------------------------------------------------
    # Field di dalam modal DICARI lewat teks label (id auto-generate)
    # -- helper _locator_field() / _locator_group() di bawah.
    BTN_SAVE_MODAL = (
        By.XPATH,
        XP_MODAL + "//button[normalize-space(.)='Save']",
    )
    BTN_CANCEL_MODAL = (
        By.XPATH,
        XP_MODAL + "//button[normalize-space(.)='Cancel']",
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
        # Id=1317 DIPINDAH aplikasi dari MonthlyReport ke YearlyReport
        # (2026-09-10). Sebelumnya inkonsisten: link sidebar & Submit
        # mengarah ke YearlyReport sementara halamannya MonthlyReport --
        # itu yang dulu terlihat sebagai "Submit Changes redirect".
        # Sekarang sudah konsisten Yearly. Lihat reports/bugs/
        # submit-changes-redirect-tanpa-menyimpan.md.
        "statistic_safety_recapitulation": "Reporting/Timesheet/YearlyReport/Edit?Id=1317",
        "smk3": "Reporting/Timesheet/YearlyReport/Edit?Id=1308",
        "smkp": "Reporting/Timesheet/YearlyReport/Edit?Id=1307",
    }

    # ------------------------------------------------------------------
    # Rantai submenu sidebar per halaman (setelah 'HSS') -- dipakai
    # buka_via_menu() supaya navigasi lewat ALUR MENU, bukan URL
    # langsung (permintaan user 2026-08-31: dashboard -> HSS -> Safety
    # -> Reporting / Transaction). CATATAN: judul 'Reporting' JUGA
    # dipakai menu Health -- buka_submenu() diberi `induk` supaya
    # tidak salah buka submenu tetangga.
    # ------------------------------------------------------------------
    GRUP_MENU = {
        # Reporting
        "lagging_indicator": ("Safety", "Reporting"),
        "golden_rules_recap": ("Safety", "Reporting"),
        "emergency_drill_recap": ("Safety", "Reporting"),
        "mwt_recapitulation": ("Safety", "Reporting"),
        "safety_recap": ("Safety", "Reporting"),
        # Transaction > Leading Indicator
        # CATATAN 2026-08-31 (probe tools/probe_menu_href.py): 3
        # halaman DailyReport berada di dalam subgroup BERSARANG
        # 'Incident Management' di bawah Leading Indicator -- rantai
        # tanpa subgroup itu = link tidak pernah tampil.
        "incident_investigation_form": (
            "Safety", "Transaction", "Leading Indicator",
            "Incident Management"),
        "initial_incident_accident_report": (
            "Safety", "Transaction", "Leading Indicator",
            "Incident Management"),
        "witness_statement_report": (
            "Safety", "Transaction", "Leading Indicator",
            "Incident Management"),
        "emergency_drill_daily": (
            "Safety", "Transaction", "Leading Indicator"),
        "master_alat_keselamatan_operasi": (
            "Safety", "Transaction", "Leading Indicator"),
        "soc_recapitulation": (
            "Safety", "Transaction", "Leading Indicator"),
        "golden_rules": ("Safety", "Transaction", "Leading Indicator"),
        "data_rekap_statistik_k3": (
            "Safety", "Transaction", "Leading Indicator"),
        "safety_kkp_p2k3_committee_meeting": (
            "Safety", "Transaction", "Leading Indicator"),
        "mwt_daily": ("Safety", "Transaction", "Leading Indicator"),
        "leading_indicator": (
            "Safety", "Transaction", "Leading Indicator"),
        # Transaction > Lagging Indicator
        "statistic_safety_recapitulation": (
            "Safety", "Transaction", "Lagging Indicator"),
        "smk3": ("Safety", "Transaction", "Lagging Indicator"),
        "smkp": ("Safety", "Transaction", "Lagging Indicator"),
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
    # + link ber-role button). Halaman View cuma punya Export (+Cancel);
    # halaman Transaction (Edit) punya toolbar lengkap. Link
    # Instructions TIDAK masuk daftar -- tidak diklik oleh alur coba
    # tombol (permintaan user 2026-08-28). Catatan scan:
    #   - MWT DAILY tidak punya tombol Reload Data.
    #   - Columns cuma ada di 3 halaman Daily Input (Id=1334/1335/1336).
    #   - SOC RECAPITULATION punya tombol tambahan Select Finding.
    TOMBOL_HALAMAN = {
        # Reporting (View / read-only)
        "lagging_indicator": ("Export", "Cancel"),
        "golden_rules_recap": ("Export", "Cancel"),
        "emergency_drill_recap": ("Export", "Cancel"),
        "mwt_recapitulation": ("Export", "Cancel"),
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
            "Create with Form", "Create","Cancel",
        ),
        "initial_incident_accident_report": (
            "Import", "FullScreen", "Columns", "Submit Changes", "Export",
            "Create with Form", "Create","Cancel",
        ),
        "witness_statement_report": (
            "Import", "FullScreen", "Columns", "Submit Changes", "Export",
            "Create with Form", "Create","Cancel",
        ),
        "emergency_drill_daily": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create","Cancel",
        ),
        "master_alat_keselamatan_operasi": (
            "Reload Data", "Import", "FullScreen", "Submit Changes",
            "Export", "Create with Form", "Create", "Cancel",
        ),
        "soc_recapitulation": (
            "Import", "FullScreen", "Select Finding", "Submit Changes",
            "Export", "Create with Form", "Create", "Cancel",
        ),
        "golden_rules": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create","Cancel",
        ),
        "data_rekap_statistik_k3": (
            "Import", "FullScreen", "Submit Changes",
            "Export","Cancel",
        ),
        "safety_kkp_p2k3_committee_meeting": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create","Cancel",
        ),
        "mwt_daily": (
            "Import", "FullScreen", "Submit Changes", "Export",
            "Create with Form", "Create","Cancel",
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
            "Export","Cancel",
        ),
        "smk3": (
            "Import", "FullScreen", "Submit Changes",
            "Export","Cancel",
        ),
        "smkp": (
            "Import", "FullScreen", "Submit Changes",
            "Export","Cancel",
        ),
    }

    # ------------------------------------------------------------------
    # Navigasi
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # TEMPLATE laporan (DailyReport / MonthlyReport / YearlyReport /
    # StaticReport, masing-masing Edit atau View).
    #
    # 19 halaman Safety sebenarnya cuma 7 kombinasi template+mode --
    # sebagian besar perilakunya (toolbar, tab, grid, tombol) milik
    # TEMPLATE, bukan milik halaman. Sampai 2026-09-08 suite ini sama
    # sekali tidak punya konsep template, sehingga tidak bisa menjawab
    # "kegagalan ini kena satu halaman atau satu template?" -- padahal
    # itu persis pertanyaan yang muncul saat bug Submit Changes
    # redirect ditemukan di Id=1317 (lihat reports/bugs/
    # submit-changes-redirect-tanpa-menyimpan.md). Waktu itu jawabannya
    # harus dicari manual.
    # ------------------------------------------------------------------
    @classmethod
    def template_halaman(cls, kunci):
        """Nama template+mode halaman `kunci`, mis. 'MonthlyReport/Edit'.
        'Custom' untuk halaman di luar pola Timesheet (Safety Recap)."""
        cocok = re.search(
            r"Timesheet/(\w+)/(\w+)", cls.HALAMAN.get(kunci, "")
        )
        return f"{cocok.group(1)}/{cocok.group(2)}" if cocok else "Custom"

    @classmethod
    def halaman_per_template(cls):
        """{'MonthlyReport/Edit': ['golden_rules', ...], ...}"""
        hasil = {}
        for kunci in cls.HALAMAN:
            hasil.setdefault(cls.template_halaman(kunci), []).append(kunci)
        return hasil

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

    def buka_submenu(self, judul, timeout=None, induk=None, rantai=None):
        """Buka submenu sidebar `judul` (mis. 'HSS') dengan mengklik
        collapse-sign-nya, lalu tunggu parent <li> dapat class 'open'
        (indikator terbukti, 2026-08-24). Klik dilakukan HANYA kalau
        submenu belum terbuka -- klik saat terbuka = menutup (toggle).

        `induk` (opsional) = judul menu PENDUDUK `judul` -- pencarian
        ELEMEN di-scope ke dalam <li> yang memuat span induk. Dipakai
        untuk judul yang DUPLIKAT di menu lain (contoh 'Reporting' ada
        di Health DAN di Safety -- tanpa scope klik bisa jatuh ke
        Health, 2026-08-31).

        `rantai` (opsional) = tuple judul BERJENJANG dari atas sampai
        `judul`, mis. ('Safety', 'Transaction', 'Leading Indicator').
        Cek keadaan JS memakai walk berjenjang supaya TEPAT sasaran:
        teks 'Transaction' JUGA dipakai menu level-atas (bukan HSS),
        dan 'Leading Indicator' dipakai grup + link halamannya --
        pencarian .find() pertama salah sasaran ke situ (diamati probe
        tools/probe_menu_href.py, 2026-08-31).

        catatan quirk:
          - handler toggle butuh klik MOUSE asli -- JS .click() tidak
            memicu handler di dashboard (dicek tools/cek_menu.py,
            2026-08-24).
          - di halaman Timesheet (YearlyReport Edit) klik sign NATIVE
            juga TIDAK mempan -- yang terbukti mempan di sana = klik
            mouse asli pada SPAN teks menu (probe 15/16, 2026-08-27:
            test menu gagal karena browser restore tab smkp).
            Karena itu klik dicoba BERURUTAN: sign -> span, berhenti
            begitu submenu terbuka."""
        dasar = "//nav"
        if induk:
            dasar += f"//li[.//span[normalize-space(text())='{induk}']]"
        sign = (
            By.XPATH,
            dasar
            + f"//a[contains(@title,'{judul}')]"
            + "//b[contains(@class,'collapse-sign')]",
        )
        span = (
            By.XPATH,
            dasar + f"//span[normalize-space(text())='{judul}']",
        )
        if rantai:
            js_terbuka = (
                "let root = document;"
                "for (const t of arguments[0]) {"
                "  const s = [...root.querySelectorAll('span')]"
                "    .find(e => (e.innerText || '').trim() === t);"
                "  if (!s) return false;"
                "  root = s.closest('li');"
                "}"
                "return (root.className || '').includes('open');"
            )

            def _terbuka(d):
                return bool(d.execute_script(js_terbuka, list(rantai)))
        else:
            js_induk = (
                "const ind = [...document.querySelectorAll('nav span')]"
                f".find(e => (e.innerText || '').trim() === '{induk}');"
                "if (!ind) return false;"
                "root = ind.closest('li');"
            ) if induk else ""

            def _terbuka(d):
                return bool(d.execute_script(
                    "let root = document;" + js_induk
                    + "const s = [...root.querySelectorAll('span')]"
                    ".find(e => (e.innerText || '').trim()"
                    f" === '{judul}');"
                    "if (!s) return false;"
                    "return (s.closest('li').className || '')"
                    ".includes('open');"
                ))

        if not _terbuka(self.driver):
            for lokasi in (sign, span):
                if _terbuka(self.driver):
                    break
                try:
                    element = self._ambil_js_visible(lokasi, timeout=timeout)
                except TimeoutException:
                    continue
                # Gulir dulu ke elemennya: sidebar OPEL bisa lebih tinggi
                # dari viewport, dan move_to_element ke item di luar
                # viewport melempar MoveTargetOutOfBoundsException
                # (run penuh 2026-09-07, 'Initial Incident/Accident').
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        element,
                    )
                    self.pace(0.3)
                except Exception:
                    pass
                try:
                    ActionChains(self.driver).move_to_element(
                        element
                    ).click().perform()
                except (MoveTargetOutOfBoundsException,
                        ElementNotInteractableException):
                    # Klik lewat pointer gagal -- jatuh ke klik JS.
                    # Untuk MEMBUKA submenu, klik JS sudah cukup (yang
                    # benar-benar butuh mousedown+mouseup asli cuma alur
                    # keluar-fullscreen, lihat toggle_fullscreen()).
                    #
                    # Dua sebab yang sudah terbukti di run penuh:
                    #  - MoveTargetOutOfBounds: item menu di luar
                    #    viewport (2026-09-07, 'Initial Incident/Accident')
                    #  - ElementNotInteractable "has no size and
                    #    location": elemen SEMPAT dinilai tampil oleh
                    #    _ambil_js_visible(), lalu ukurannya jadi nol
                    #    sebelum ActionChains sempat jalan -- sidebar
                    #    accordion masih beranimasi buka/tutup
                    #    (2026-09-07, 'MWT Recapitulation')
                    self.driver.execute_script("arguments[0].click();", element)
                self.pace()
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

    def buka_via_menu(self, kunci):
        """Buka halaman Safety `kunci` lewat ALUR MENU SIDEBAR
        (permintaan user 2026-08-31 -- bukan URL langsung):
          1. dashboard dulu kalau sidebar belum tampil (mis. test
             dijalankan sendirian);
          2. buka rantai submenu: HSS -> Safety -> grup (Reporting /
             Transaction > Leading|Lagging Indicator -- lihat
             GRUP_MENU);
          3. klik link halaman di sidebar (klik MOUSE asli -- quirk
             menu: JS .click() tidak memicu handler, 2026-08-24);
          4. tunggu halaman siap (sama seperti buka_halaman --
             `tabel_report_tampil()` polimorfik, Safety Recap punya
             tabel custom) + bersihkan draft lokal."""
        if kunci not in self.HALAMAN:
            raise KeyError(
                f"Kunci halaman '{kunci}' tidak dikenal. Pilihan: "
                f"{', '.join(sorted(self.HALAMAN))}"
            )
        # 0) pulihkan viewport dulu -- sidebar OPEL auto-collapse kalau
        #    jendela sempit, dan navigasi lewat menu jadi mustahil.
        self.pulihkan_viewport()
        # 1) pastikan sidebar ada -- kalau belum, mulai dari dashboard
        if not self.is_any_visible(self.MENU_HSS, timeout=3):
            self.driver.get(config.BASE_URL)
            try:
                self._wait(config.LONG_TIMEOUT).until(
                    lambda d: self.is_any_visible(self.MENU_HSS),
                    "Sidebar (menu HSS) tidak muncul setelah buka dashboard",
                )
            except TimeoutException:
                # Percobaan terakhir: paksa pulihkan viewport lalu muat
                # ulang. Menutup kasus jendela yang menyempit di tengah
                # sesi panjang (run 2026-09-07).
                self.pulihkan_viewport(paksa=True)
                self.driver.get(config.BASE_URL)
                self._wait(config.LONG_TIMEOUT).until(
                    lambda d: self.is_any_visible(self.MENU_HSS),
                    "Sidebar (menu HSS) tidak muncul walau viewport sudah "
                    "dipulihkan (keluar fullscreen + maximize)",
                )
        # 2) buka rantai submenu: HSS -> Safety -> grup -> subgrup.
        #    Cek keadaan pakai `rantai` (walk berjenjang) supaya tidak
        #    salah sasaran ke menu LAIN yang teksnya sama ('Transaction'
        #    dipakai menu level-atas juga -- 2026-08-31).
        induk = None
        rantai = []
        for judul in ("HSS",) + self.GRUP_MENU[kunci]:
            rantai.append(judul)
            self.buka_submenu(judul, induk=induk, rantai=tuple(rantai))
            induk = judul
        # 3) klik link halaman di sidebar
        href = self.HALAMAN[kunci]
        url = config.BASE_URL.rstrip("/") + "/" + href.lstrip("/")
        lokasi = (By.XPATH, f"//nav//a[contains(@href,'{href}')]")
        # Retry INI dulu tidak pernah jalan untuk kasus link belum
        # ter-render: `_ambil_js_visible()` melempar TimeoutException
        # yang langsung keluar dari loop, jadi percobaan kedua tidak
        # pernah terjadi. Terlihat di run penuh 2026-09-09 (1 jam 4
        # menit, sesi terpanjang): halaman_lengkap[Statistic Safety
        # Recap] gagal karena link menu tidak ketemu -- padahal
        # screenshot saat gagal memperlihatkan link itu ADA di sidebar.
        # Sekarang: kalau link belum ada, rantai submenu DIBUKA ULANG
        # lalu dicoba lagi.
        element = None
        for percobaan in range(2):
            try:
                element = self._ambil_js_visible(lokasi)
            except TimeoutException:
                if percobaan == 0:
                    induk = None
                    rantai = []
                    for judul in ("HSS",) + self.GRUP_MENU[kunci]:
                        rantai.append(judul)
                        try:
                            self.buka_submenu(
                                judul, induk=induk, rantai=tuple(rantai)
                            )
                        except TimeoutException:
                            pass
                        induk = judul
                    continue
                raise
            ActionChains(self.driver).move_to_element(element).click().perform()
            try:
                self._wait(config.DEFAULT_TIMEOUT).until(
                    lambda d: href in d.current_url,
                    "Klik link menu tidak memindahkan halaman",
                )
                break
            except TimeoutException:
                continue
        # 4) tunggu halaman siap -- retry navigasi langsung kalau SPA
        #    stuck di loading overlay (pola buka_halaman)
        def _tunggu_siap():
            self._tunggu_tabel(url)
            self.tunggu_processing_selesai()

        try:
            _tunggu_siap()
        except TimeoutException:
            self.driver.get(url)
            _tunggu_siap()
        # Bersihkan draft LOCAL halaman ini (pola buka_halaman --
        # localStorage dr_<Id>_* tidak menyentuh server).
        if self._bersihkan_draft_lokal():
            self.driver.get(url)
            _tunggu_siap()
        return self

    def buka_halaman(self, kunci):
        """Buka halaman Safety berdasarkan kunci di HALAMAN (mis.
        'smk3'). Navigasi lewat URL langsung -- paling stabil karena
        submenu pakai href relatif yang bisa berubah konteks.

        Menunggu sampai tabel DataTables benar-benar TAMPIL (bukan
        cuma ada di DOM) -- halaman Timesheet butuh beberapa detik
        untuk render data setelah load.

        Kalau halaman menampilkan pesan "tidak punya akses" (user
        tidak diizinkan melihat halaman ini), otomatis kembali ke
        halaman sebelumnya pakai tombol Back browser (driver.back())
        dan raise TidakPunyaAkses supaya test bisa di-skip."""
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
            # Cek apakah halaman menunjukkan pesan "tidak punya akses"
            # -- kalau ya, kembali ke halaman sebelumnya pakai tombol
            # Back browser Chrome dan raise TidakPunyaAkses.
            pesan = self._halaman_tidak_punya_akses()
            if pesan:
                print(
                    f"\n[TIDAK PUNYA AKSES] Halaman '{kunci}' "
                    f"({url}): {pesan}"
                    "\n  -> Kembali ke halaman sebelumnya (driver.back())"
                )
                self.driver.back()
                self.pace(1.0)
                raise TidakPunyaAkses(
                    f"Tidak punya akses ke halaman '{kunci}': {pesan}"
                )
            # Bukan masalah akses -- mungkin SPA OPEL "stuck" di loading
            # overlay. Retry navigasi sekali menyelesaikan.
            self.driver.get(url)
            try:
                _tunggu_siap()
            except TimeoutException:
                # Setelah retry, cek lagi apakah ternyata masalah akses
                pesan = self._halaman_tidak_punya_akses()
                if pesan:
                    print(
                        f"\n[TIDAK PUNYA AKSES] Halaman '{kunci}' "
                        f"({url}): {pesan}"
                        "\n  -> Kembali ke halaman sebelumnya (driver.back())"
                    )
                    self.driver.back()
                    self.pace(1.0)
                    raise TidakPunyaAkses(
                        f"Tidak punya akses ke halaman '{kunci}': {pesan}"
                    )
                raise  # bukan masalah akses, lempar TimeoutException asli
        # Bersihkan draft LOCAL halaman ini (localStorage dr_<Id>_*) --
        # baris draft kosong nyangkut setelah Create+Cancel dan membuat
        # Submit MEMBUANG baris baru dari Create with Form (2026-08-24).
        # Hapus localStorage TIDAK menyentuh server; kalau ada yang
        # terhapus, reload sekali supaya grid render tanpa draft.
        if self._bersihkan_draft_lokal():
            self.driver.get(url)
            _tunggu_siap()

    # ------------------------------------------------------------------
    # Deteksi halaman "tidak punya akses"
    # ------------------------------------------------------------------
    # Kata kunci yang dicari di body halaman untuk mendeteksi pesan
    # "tidak punya akses". Sengaja dibuat lebar (EN + ID) supaya
    # menangkap variasi pesan yang mungkin ditampilkan OPEL.
    _KATA_KUNCI_TIDAK_PUNYA_AKSES = (
        "not authorized",
        "unauthorized",
        "access denied",
        "forbidden",
        "tidak memiliki akses",
        "tidak diizinkan",
        "anda tidak memiliki",
        "tidak punya akses",
        "you do not have permission",
        "you don't have permission",
        "you are not authorized",
        "permission denied",
        "no permission",
        "no access",
    )

    def _halaman_tidak_punya_akses(self):
        """Cek apakah halaman saat ini menampilkan pesan 'tidak punya
        akses'. Kembalikan teks pesan yang cocok (string) kalau
        terdeteksi, atau string kosong ('') kalau tidak.

        Pemeriksaan:
        1. Cari kata kunci di teks body halaman (case-insensitive).
        2. Cek elemen dengan class/id umum untuk pesan error (mis.
           .alert-danger, .error-message, #error, dsb.)."""
        try:
            body_text = self.driver.execute_script(
                "return (document.body && document.body.innerText) || '';"
            ).lower()
        except Exception:
            return ""

        # 1) Cari kata kunci di body text
        for kunci in self._KATA_KUNCI_TIDAK_PUNYA_AKSES:
            if kunci in body_text:
                # Ambil baris yang mengandung kata kunci sebagai pesan
                for baris in body_text.split("\n"):
                    if kunci in baris.strip().lower():
                        return baris.strip()
                return kunci  # fallback: kembalikan kata kunci itu sendiri

        # 2) Cek elemen error container yang mungkin punya pesan akses
        pesan_error = self.driver.execute_script(
            "const sels = ["
            "  '.alert-danger', '.alert-warning', '.error-message',"
            "  '#error', '.access-denied', '.forbidden',"
            "  '[class*=\'unauthorized\']', '[class*=\'denied\']'"
            "];"
            "for (const s of sels) {"
            "  const el = document.querySelector(s);"
            "  if (el && el.offsetHeight > 0) {"
            "    return el.innerText.trim();"
            "  }"
            "}"
            "return '';"
        )
        if pesan_error:
            pesan_lower = pesan_error.lower()
            for kunci in self._KATA_KUNCI_TIDAK_PUNYA_AKSES:
                if kunci in pesan_lower:
                    return pesan_error

        return ""

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

    # Banner OPEL "The data has been stored locally. Please click the
    # submit button to save it on the server" -- artinya masih ada
    # perubahan PENDING yang belum dikirim ke server.
    #
    # Kenapa perlu dideteksi (2026-09-07): banner ini terlihat di
    # screenshot test_safety_leading_deep[Data Rekap Statistik K3]
    # padahal test itu tidak mengedit apa pun.
    #
    # Dugaan awal "bocor dari test sebelumnya di sesi yang sama"
    # TERBANTAH pada run 2026-09-07 10:06: banner sudah menyala di test
    # PERTAMA sesi itu (statistic_safety_recapitulation), jadi sumbernya
    # BUKAN test sebelumnya -- state-nya bertahan LINTAS SESI. Kandidat
    # yang tersisa: (a) localStorage di profil Chrome yang memang
    # dipakai ulang tiap run, tapi dengan pola key SELAIN 'dr_<Id>_*'
    # sehingga lolos dari _bersihkan_draft_lokal(); atau (b) perubahan
    # pending yang benar-benar tersimpan di server untuk user ini.
    # `daftar_key_penyimpanan()` dipakai membedakan keduanya.
    _TEKS_PENDING = ("stored locally", "please click the submit")

    def ada_pending_lokal(self):
        """True kalau halaman menampilkan banner perubahan pending
        ('stored locally ... please click the submit button')."""
        return bool(self.driver.execute_script(
            "const teks = (document.body.innerText || '').toLowerCase();"
            "return arguments[0].some(t => teks.indexOf(t) >= 0);",
            list(self._TEKS_PENDING),
        ))

    def daftar_key_penyimpanan(self, maks=40):
        """Daftar key localStorage + sessionStorage yang ada sekarang,
        beserta panjang nilainya. Dipakai melacak DI MANA state pending
        disimpan waktu banner 'stored locally' menyala: kalau daftarnya
        kosong padahal banner menyala, berarti pending-nya di SERVER,
        bukan di browser."""
        return self.driver.execute_script(
            "const out = [];"
            "for (const [nama, gudang] of ["
            "     ['local', window.localStorage],"
            "     ['session', window.sessionStorage]]) {"
            "  try {"
            "    for (const k of Object.keys(gudang)) {"
            "      if (out.length >= arguments[0]) return out;"
            "      out.push(nama + ':' + k + ' (' +"
            "               (gudang.getItem(k) || '').length + ' char)');"
            "    }"
            "  } catch (e) { out.push(nama + ': TIDAK BISA DIBACA'); }"
            "}"
            "return out;",
            int(maks),
        ) or []

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
                self.pace()
        raise TimeoutException(
            "File export tidak kunjung muncul di folder unduhan "
            f"({config.DOWNLOAD_DIR}) setelah 3x klik Export"
        )

    def download_template_import(self, ekstensi=".xlsx"):
        """Klik link Download Template di modal Import lalu tunggu file
        template terunduh. Dipakai pasang_file_dummy_import() -- file
        template resmi adalah dummy PALING valid untuk input upload."""
        sebelum = set(os.listdir(config.DOWNLOAD_DIR))
        self.click_js_saat_tampil(self.LINK_DOWNLOAD_TEMPLATE)
        return self.tunggu_file_baru(ekstensi, sebelum)

    # Cache template import per halaman per SESI -- template diunduh
    # SEKALI per halaman, tab-tab berikutnya memakai ulang file yang
    # sama (waktu tidak lama, folder unduhan tidak menumpuk).
    _TEMPLATE_IMPORT_CACHE = {}

    def pasang_file_dummy_import(self):
        """Pasang file dummy (template import resmi yang diunduh dari
        modal ini) ke input #imgFileImport lalu verifikasi file
        benar2 terpasang (files == 1). Tombol Import TIDAK diklik --
        klik tombol = POST ke server (menulis data ke DEV); permintaan
        user 'upload file dummy dalam keadaan AMAN' (2026-08-31) =
        widget pilih-file upload dicoba SUNGGUHAN, tapi file TIDAK
        pernah dikirim ke server."""
        kunci = getattr(self, "KUNCI", "umum")
        path = self._TEMPLATE_IMPORT_CACHE.get(kunci)
        if not path or not os.path.exists(path):
            path = self.download_template_import()
            self._TEMPLATE_IMPORT_CACHE[kunci] = path
        element = self._ambil_js_visible(self.INPUT_FILE_IMPORT)
        element.send_keys(path)
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda d: d.execute_script(
                "const i = document.querySelector('#imgFileImport');"
                "return !!(i && i.files && i.files.length > 0);"
            ),
            "File dummy import tidak terpasang di #imgFileImport",
        )
        print(f"  [import] file dummy '{os.path.basename(path)}' terpasang"
              " -- TIDAK dikirim ke server (aman)")

    # Kandidat tombol Yes/OK dialog konfirmasi (Submit Changes /
    # Export): bootbox Yes dulu, lalu modal Bootstrap, SweetAlert,
    # dan tombol Yes/OK umum.
    _LOKASI_TOMBOL_OK = (
        (By.CSS_SELECTOR, "button.bootbox-accept"),
        (By.XPATH, XP_MODAL + "//button[normalize-space(.)='Yes']"),
        (By.XPATH, XP_MODAL + "//button[normalize-space(.)='OK']"),
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
        kena intercept oleh modal yang masih menutup (2026-08-24).

        Kalau popup TETAP tampil padahal aksi di belakangnya SUDAH
        jalan (quirk UI diamati SMK3/SMKP 2026-08-28: submit selesai,
        grid idle, tapi popup tidak menutup sendiri), popup sisa
        dianggap ornamen -- pastikan processing selesai dulu, lalu
        tutup paksa (pola sama dengan _paksa_tutup_modal Statistic).
        Kalau processing-nya yang macet, yang gagal adalah tunggu
        processing, bukan popup yang ditutup paksa sembarangan."""
        self.click_js_saat_tampil(self.BTN_SUBMIT)
        terjawab = self.jawab_konfirmasi()
        dipaksa = False
        try:
            self.tunggu_modal_tertutup(timeout=config.LONG_TIMEOUT)
        except TimeoutException:
            self.tunggu_processing_selesai()
            # Coba jawab SEKALI LAGI sebelum menutup paksa. Dialog
            # konfirmasi bisa muncul TERLAMBAT -- jawab_konfirmasi()
            # menyerah setelah 2 detik tenang, jadi kalau dialognya baru
            # nongol sesudah itu, tidak ada yang mengkliknya. Menutup
            # paksa dialog konfirmasi = MEMBATALKAN submit secara diam-
            # diam, dan test lanjut mengira sudah tersimpan (2026-09-08).
            if self.jawab_konfirmasi(timeout=config.DEFAULT_TIMEOUT):
                terjawab = True
                try:
                    self.tunggu_modal_tertutup(timeout=config.LONG_TIMEOUT)
                except TimeoutException:
                    self._paksa_tutup_modal()
                    self.tunggu_modal_tertutup()
                    dipaksa = True
            else:
                self._paksa_tutup_modal()
                self.tunggu_modal_tertutup()
                dipaksa = True
        # Nilai balik dipakai alat diagnosa (tools/cek_simpan_inline.py);
        # pemanggil lama mengabaikannya, jadi tetap kompatibel.
        return {"konfirmasi_dijawab": terjawab, "modal_ditutup_paksa": dipaksa}

    def klik_tab(self, teks_tab, jeda=None):
        """Klik tab internal halaman (hanya yang benar2 tampil menurut
        JS -- beberapa halaman punya panel tab tersembunyi di DOM),
        lalu tunggu tabnya jadi aktif. `jeda` = jeda visual setelah
        tab aktif supaya hasil aksi sempat terlihat (default ikut
        config ACTION_PACE_SECONDS -- seragam 2 detik, 2026-08-28)."""
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
        Cek pakai computed style JS (offsetWidth/offsetHeight/
        getClientRects -- sama seperti _deskripsi_modal): is_displayed()
        Selenium bisa False negatif saat fade-transition / SPA stuck
        (diamati full run 2026-08-31: modal Import TERBUKA -- terbaca
        _deskripsi_modal -- tapi is_displayed() False, tunggu_modal
        gagal sia-sia). Elemen stale dianggap belum tampil."""
        try:
            return bool(self.driver.execute_script(
                "return [...document.querySelectorAll("
                "'.modal.show, .modal.in')]"
                ".some(m => {"
                "  try { return !!(m.offsetWidth || m.offsetHeight"
                "    || m.getClientRects().length); }"
                "  catch (e) { return false; }"
                "});"
            ))
        except Exception:
            return False

    def _deskripsi_modal(self):
        """Deskripsi singkat modal yang sedang tampil -- dipakai
        supaya pesan error timeout TIDAK kosong: kelas modal, teks
        (dipotong), dan teks tombol-tombolnya. Kembalikan '-- tidak
        ada modal tampil --' kalau memang tidak ada."""
        hasil = self.driver.execute_script(
            "const out = [];"
            "[...document.querySelectorAll('.modal.show, .modal.in,"
            " .bootbox, .swal2-container')].forEach(m => {"
            "  let tampil = false;"
            "  try { tampil = !!(m.offsetWidth || m.offsetHeight"
            "    || m.getClientRects().length); } catch (e) {}"
            "  if (!tampil) return;"
            "  const teks = (m.innerText || '').replace(/\\s+/g, ' ')"
            "    .trim().slice(0, 140);"
            "  const tombol = [...m.querySelectorAll('button')]"
            "    .map(b => (b.innerText || '').replace(/\\s+/g, ' ')"
            "      .trim()).filter(t => t).slice(0, 8).join('/');"
            "  out.push('[' + m.className.toString().slice(0, 60)"
            "    + '] ' + teks + (tombol ? ' BTN: ' + tombol : ''));"
            "});"
            "return out.join(' || ');"
        )
        return hasil or "-- tidak ada modal tampil --"

    def tunggu_modal_terbuka(self, timeout=None):
        """Tunggu sampai ADA modal .modal.show yang tampil."""
        try:
            self._wait(timeout).until(
                lambda _: self._ada_modal_tampil(),
                "Modal tidak kunjung terbuka",
            )
        except TimeoutException:
            raise TimeoutException(
                "Modal tidak kunjung terbuka -- modal saat ini: "
                + self._deskripsi_modal()
            )

    def tunggu_modal_tertutup(self, timeout=None):
        """Tunggu sampai TIDAK ADA modal .modal.show yang tampil lagi."""
        try:
            self._wait(timeout).until(
                lambda _: not self._ada_modal_tampil(),
                "Modal tidak kunjung tertutup -- kemungkinan ada field wajib"
                " belum terisi / validasi gagal",
            )
        except TimeoutException:
            raise TimeoutException(
                "Modal tidak kunjung tertutup -- modal saat ini: "
                + self._deskripsi_modal()
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
        self.pace()
        self.click_js_saat_tampil(locator)
        # Halaman dengan grid berat (banyak kolom/district, mis. Leading
        # Indicator Static Input) bisa bikin main thread sibuk render ulang
        # setelah reload -- modal open KE-DETEKSI TERLAMBAT dengan
        # DEFAULT_TIMEOUT (observasi 2026-08-31: screenshot kegagalan
        # menunjukkan modal SUDAH terbuka saat timeout dilempar). Pakai
        # LONG_TIMEOUT di percobaan terakhir ini supaya tidak keburu gagal.
        self.tunggu_modal_terbuka(timeout=config.LONG_TIMEOUT)

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
            self.XP_MODAL
            + f"//label[{self._xpath_label(label)}]"
            + "/following-sibling::*"
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
            self.XP_MODAL
            + f"//label[{self._xpath_label(label)}]"
            + "/ancestor::div[contains(@class,'form-group')][1]"
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
                    try:
                        Select(element).select_by_visible_text(nilai)
                    except Exception:
                        self.driver.execute_script(
                            "arguments[0].value = arguments[1];"
                            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                            element, str(nilai),
                        )
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
                    try:
                        element.clear()
                        element.send_keys(str(nilai))
                    except (ElementNotInteractableException, Exception):
                        self.driver.execute_script(
                            "arguments[0].value = arguments[1];"
                            "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                            "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
                            element, str(nilai),
                        )
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
const modal = document.querySelector('.modal.show, .modal.in');
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

    # Halaman yang field upload-nya (.dt-input-upload) BENAR2 diisi
    # file dummy. File hanya dikirim ke server saat Save (multipart
    # form -> server yang mengirim ke Firebase Storage) -- TIDAK ada
    # file yatim walau form di-Cancel (dicek probe 23/24, 2026-08-27:
    # tidak ada POST firebase dari browser saat memilih file). Halaman
    # lain tetap dilewati supaya jejak upload di server seminimal
    # mungkin.
    UPLOAD_HALAMAN = {"incident_investigation_form"}

    # PNG 1x1 transparan (67 byte) -- file dummy TERKECIL yang bisa
    # dibuat supaya jejak upload di server seminimal mungkin.
    PNG_DUMMY_B64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    )

    def _siapkan_png_dummy(self):
        """Tulis PNG 1x1 dummy ke reports/ (sekali saja) dan kembalikan
        path-nya -- dipakai upload_file_dummy()."""
        path = os.path.join(config.REPORTS_DIR, "dummy_upload.png")
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(base64.b64decode(self.PNG_DUMMY_B64))
        return path

    def upload_file_dummy(self, label):
        """Isi field upload `label` (widget .dt-input-upload) dengan
        file dummy PNG terkecil, ALUR AMAN (dipetakan probe 17-25,
        2026-08-27):

        1. klik anchor Upload -> aplikasi membuat input#imgFile
           (input[type=file] BERSAMA yang dipindah ke group field yang
           diklik -- bukan input statis per field);
        2. send_keys file dummy ke input -> aplikasi menyimpan file
           per field (TIDAK ada POST firebase dari browser; file
           dikirim ke server baru saat Save lewat multipart form);
        3. verifikasi file benar2 terpasang (files == 1).

        Kalau widget SUDAH berisi file (link 'Remove' tampil), method
        ini dilewati -- upload ulang akan menambah file ganda yang
        ikut dikirim saat Save.

        Sebelum klik, HTMLInputElement.prototype.click di-patch supaya
        dialog file OS TIDAK muncul (selenium tidak bisa mengendalikan
        dialog native) -- patch menyimpan fungsi asli dan hanya
        memotong klik input bertipe file, sisanya diteruskan normal."""
        self.driver.execute_script(
            "window.__opelFileInputs = window.__opelFileInputs || [];"
            "if (!window.__opelClickAsli) {"
            "  window.__opelClickAsli = HTMLInputElement.prototype.click;"
            "  HTMLInputElement.prototype.click = function () {"
            "    if (this.type === 'file') {"
            "      window.__opelFileInputs.push(this); return;"
            "    }"
            "    return window.__opelClickAsli.apply(this, arguments);"
            "  };"
            "}"
        )
        grp = self._locator_group(label)
        for el in self.driver.find_elements(
            By.XPATH,
            grp
            + "//*[contains(@class,'text-danger')]"
            "[contains(normalize-space(.), 'Remove')]",
        ):
            if self._js_visible(self.driver, el):
                # widget sudah berisi file (link 'Remove' TAMPIL) --
                # upload ulang akan menambah file GANDA yang ikut
                # dikirim saat Save. Terjadi kalau scan field diulang
                # (select cascading, isi_form_create_otomatis sampai 3
                # putaran). Link Remove TERNYATA selalu ada di DOM
                # (hidden sebelum file dipilih) -- jadi wajib cek
                # visibilitas, bukan sekadar keberadaan (2026-08-28).
                print(f"  [upload] '{label}' sudah berisi file -- dilewati")
                return
        self.click_js_saat_tampil(
            (By.XPATH, grp + "//a[contains(@class,'dt-input-upload')]")
        )
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda _: self.driver.execute_script(
                "const i = document.querySelector('input[type=file]#imgFile');"
                "return !!i;"
            ),
            f"Input file untuk '{label}' tidak muncul setelah klik Upload",
        )
        element = self.driver.find_element(
            By.CSS_SELECTOR, "input[type=file]#imgFile"
        )
        element.send_keys(self._siapkan_png_dummy())
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda _: self.driver.execute_script(
                "const i = document.querySelector('input[type=file]#imgFile');"
                "return !!(i && i.files && i.files.length > 0);"
            ),
            f"File dummy untuk '{label}' tidak terpasang di input file",
        )
        # Setiap file dipilih, aplikasi membuka modal PREVIEW "Upload
        # File/Image" (Upload/Close) di atas form yang TIDAK menutup
        # sendiri -- popup menumpuk dan mencuri state 'show' dari
        # modal form (Save jadi tidak ketemu, 2026-08-28). File SUDAH
        # terpasang saat input berubah (widget tampil Remove), dan
        # tombol CLOSE menutup preview TANPA membuang file (probe
        # 2026-08-28) -- tombol Upload malah membuka konfirmasi
        # "Do you wish to Upload?" yang juga tidak menutup sendiri.
        # Jadi: klik Close, lalu tunggu preview benar2 hilang.
        klik = self.driver.execute_script(
            "const m = [...document.querySelectorAll('.modal.show, .modal.in')]"
            "  .find(x => /Upload (File|Image)/.test(x.innerText || ''));"
            "if (!m) return false;"
            "const b = [...m.querySelectorAll('button')].find(x =>"
            "  (x.innerText || '').trim() === 'Close');"
            "if (!b) return false;"
            "b.click(); return true;"
        )
        if klik:
            self._wait(config.DEFAULT_TIMEOUT).until(
                lambda _: self.driver.execute_script(
                    "const m = [...document.querySelectorAll("
                    "'.modal.show, .modal.in')]"
                    "  .find(x => /Upload (File|Image)/.test(x.innerText || ''));"
                    "if (!m) return true;"
                    "const s = window.getComputedStyle(m);"
                    "const r = m.getBoundingClientRect();"
                    "return s.display === 'none' || s.visibility === 'hidden'"
                    " || r.height === 0;"
                ),
                f"Modal preview upload '{label}' tidak kunjung tertutup",
            )
        print(f"  [upload] '{label}' <- dummy_upload.png (67 byte)")
        self.pace()

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
          - upload         -> diisi file dummy PNG 1x1 terkecil HANYA
            di halaman yang terdaftar di UPLOAD_HALAMAN (lihat
            upload_file_dummy -- aman, file dikirim saat Save dan ikut
            dummy record yang memang dibuat); halaman lain dilewati
            supaya jejak upload di server minimal.
        Group TANPA input SAMA SEKALI dilewati.
        `tambahan` = dict {label: nilai} untuk field yang mau diisi
        nilai tertentu (menimpa otomatis), mis. Equipment No unik."""
        tambahan = tambahan or {}
        penanda = penanda or "Dummy"
        # upload HANYA SEKALI per label per sesi isi -- putaran scan
        # berikutnya (select cascading) TIDAK boleh klik anchor lagi:
        # upload dobel di putaran 2 berkaitan erat dengan gagal Save
        # 'modal tertutup sebelum Save' (diamati Incident, 2026-08-28
        # -- run dengan upload dobel gagal, sekali per label lolos;
        # mekanisme pastinya tidak terisolasi penuh lewat probe)
        sudah_upload = set()
        for _putaran in range(3):
            fields = self.driver.execute_script(self.JS_FIELD_FORM) or []
            menunggu_select = False
            for f in fields:
                label, tipe = f["label"], f["type"]
                # upload DICEK DULU: group upload TIDAK punya input
                # statis (input#imgFile dibuat saat anchor diklik),
                # jadi juga terdeteksi kosong -- kalau kosong dicek
                # duluan, upload tidak pernah dijalankan (2026-08-27)
                if f.get("upload"):
                    if (
                        getattr(self, "KUNCI", "") in self.UPLOAD_HALAMAN
                        and label not in sudah_upload
                    ):
                        self.upload_file_dummy(label)
                        sudah_upload.add(label)
                    continue
                if f.get("kosong"):
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
                elif "equipment" in label.lower():
                    # Field Equipment No diisi penanda unik (Dummy HHMMSS / equipment_prefix)
                    self.isi_field_modal(label, penanda)
                elif self._label_minta_angka(label):
                    self.isi_field_modal(label, "10")
                else:
                    self.isi_field_modal(label, f"{penanda} {label}")
            if not menunggu_select:
                break

    def _pesan_validasi_modal(self):
        """Kumpulkan pesan validasi yang sedang tampil di modal yang
        terbuka (indikator Save ditolak: field wajib belum terisi dsb).
        Kembalikan teks pesan dipisah ' | ' ('' kalau tidak ada).

        Link 'Remove' di widget upload berkelas text-danger padahal
        BUKAN pesan validasi -- dikecualikan supaya tidak salah tuduh
        (2026-08-27)."""
        return self.driver.execute_script(
            "const modal = document.querySelector('.modal.show, .modal.in');"
            "if (!modal) return '';"
            "const el = [...modal.querySelectorAll("
            "'.text-danger, .invalid-feedback, .field-validation-error,"
            " .alert, .swal2-container, .bootbox')];"
            "return el.map(e => (e.innerText || '')"
            "  .replace(/\\s+/g, ' ').trim())"
            "  .filter(t => t && t !== 'Remove').slice(0, 5).join(' | ');"
        )

    def pesan_validasi_halaman(self):
        """Pesan validasi yang tampil di HALAMAN (bukan di dalam modal):
        toast/alert/bootbox/SweetAlert yang muncul setelah Submit
        Changes menolak baris.

        Dipakai test input inline supaya kegagalan bisa DIBACA -- tanpa
        ini, baris yang ditolak validasi cuma terlihat sebagai "tidak
        tersimpan", dan itu gampang disalahartikan sebagai bug aplikasi
        (kejadian 2026-09-08 di Witness Statement)."""
        return self.driver.execute_script(
            "const el = [...document.querySelectorAll("
            "'.bootbox, .swal2-container, .toast, .alert-danger,"
            " .alert-warning, .validation-summary-errors,"
            " .field-validation-error, .invalid-feedback')];"
            "return el.filter(e => {"
            "  const s = window.getComputedStyle(e);"
            "  return s.display !== 'none' && s.visibility !== 'hidden';"
            "}).map(e => (e.innerText || '').replace(/\\s+/g, ' ').trim())"
            "  .filter(t => t && t !== 'Remove').slice(0, 5).join(' | ');"
        )

    def simpan_form(self):
        """Klik Save di modal lalu tunggu modal tertutup (tanda
        proses simpan selesai). Kalau modal tidak kunjung tertutup,
        klik Save DIULANG -- klik pertama bisa tertelan quirk SPA
        (handler tombol mati padahal tombol tampak; diamati di form
        Incident 2026-08-27, Save sekali klik tidak memicu apa pun).
        Kalau ada pesan VALIDASI yang tampil, retry tidak membantu --
        langsung gagal dengan pesan validasinya supaya ketahuan field
        yang bermasalah, bukan timeout kosong."""
        if not self._ada_modal_tampil():
            raise TimeoutException(
                "Modal form sudah tertutup SEBELUM Save diklik -- isi "
                "form bermasalah atau modal tertutup sendiri. Modal saat "
                "ini: " + self._deskripsi_modal()
            )
        if not self.driver.find_elements(*self.BTN_SAVE_MODAL):
            # ada modal tampil TAPI bukan modal form (mis. lookup modal
            # tersisa) -- gagal dengan deskripsi supaya ketahuan
            raise TimeoutException(
                "Tombol Save tidak ada di modal yang tampil -- modal "
                "form hilang atau tertimpa modal lain: "
                + self._deskripsi_modal()
            )
        for _ in range(3):
            try:
                self.click_js_saat_tampil(self.BTN_SAVE_MODAL)
            except TimeoutException:
                # modal form LENYAP tepat sebelum Save (quirk notifikasi/
                # reload aplikasi yang menutup modal, diamati Incident
                # 2026-08-28) -- sinyal MODAL_LENYAP supaya pemanggil
                # bisa buka + isi form ulang (belum ada yang tersimpan)
                raise TimeoutException(
                    "MODAL_LENYAP: modal form hilang tepat sebelum Save "
                    "diklik -- modal saat ini: " + self._deskripsi_modal()
                )
            try:
                self.tunggu_modal_tertutup(timeout=6)
                return
            except TimeoutException:
                pesan = self._pesan_validasi_modal()
                if pesan:
                    raise TimeoutException(
                        "Save gagal -- validasi form menolak: " + pesan
                    )
        # 3x klik tetap tidak mempan tanpa pesan validasi -- tunggu
        # panjang terakhir (pesan standar kalau tetap gagal)
        self.tunggu_modal_tertutup(timeout=config.LONG_TIMEOUT)
        self.jawab_konfirmasi()

    def batal_form(self):
        """Klik Cancel di modal lalu tunggu modal tertutup."""
        try:
            self.click_js_saat_tampil(self.BTN_CANCEL_MODAL)
        except Exception:
            pass
        self.tutup_modal()

    def tutup_modal(self):
        """Tutup modal yang sedang terbuka (tombol X -> tombol teks
        Close -> tombol ESC -> paksa DOM), lalu TUNGGU sampai benar2 hilang."""
        from selenium.webdriver.common.keys import Keys
        for _ in range(3):
            if not self._ada_modal_tampil():
                return
            self._klik_jika_ada(self.BTN_CLOSE_MODAL)
            self._klik_jika_ada((
                By.XPATH,
                self.XP_MODAL + "//button[normalize-space(.)='Close']",
            ))
            # bootbox alert (mis. info Reload Data) dijawab OK
            self._klik_jika_ada((By.CSS_SELECTOR, "button.bootbox-accept"))
            self._klik_jika_ada((By.XPATH, "//button[normalize-space(.)='Cancel']"))
            try:
                self.tunggu_modal_tertutup(timeout=3)
                return
            except TimeoutException:
                continue
        try:
            self.driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
            self.tunggu_modal_tertutup(timeout=3)
            return
        except Exception:
            pass
        # Fallback akhir: hapus DOM modal/backdrop yang masih nyangkut
        self._paksa_tutup_modal()
        self.pace(0.5)

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
        "    const k = p[0];"
        "    const target = (p[1] || '').toString().trim().toLowerCase();"
        "    const inp = tr.querySelector("
        "      \"input[data-fieldname='\" + k + \"'], select[data-fieldname='\" + k + \"'], textarea[data-fieldname='\" + k + \"']\");"
        "    if (inp) {"
        "      const val = (inp.value || '').trim().toLowerCase();"
        "      if (val === target) return true;"
        "      if (target === 'juli' && val === 'july') return true;"
        "      if (target === 'july' && val === 'juli') return true;"
        "      if (target === 'januari' && val === 'january') return true;"
        "      if (target === 'january' && val === 'januari') return true;"
        "    }"
        "    const sel = tr.querySelector(\"td[data-name='\" + k + \"']\");"
        "    if (sel) {"
        "      const teks = (sel.innerText || '').trim().toLowerCase();"
        "      if (teks === target) return true;"
        "      if (target === 'juli' && teks === 'july') return true;"
        "      if (target === 'july' && teks === 'juli') return true;"
        "    }"
        "    return false;"
        "  }));"
        "if (!baris) return null;"
        "return baris.querySelector("
        "\"input[data-fieldname='\" + arguments[0] + \"'], textarea[data-fieldname='\" + arguments[0] + \"'], select[data-fieldname='\" + arguments[0] + \"']\");"
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

    def cari_anchor_field_terisi(self, nama_field, anchor):
        """Cari baris PENGGANTI anchor: baris pertama di grid utama
        yang punya SEMUA field `anchor` terisi DAN `nama_field`-nya
        terisi non-kosong. Kembalikan dict anchor {key: nilai_baris}
        atau None kalau tidak ada baris seperti itu.

        Dipakai saat field target di baris anchor asli ternyata KOSONG
        (data DEV berubah -- 2026-08-27: PPkomKetidaksesuaianMaj SMK3
        & Deskripsi SMKP bulan Juli kosong). Alih-alih gagal, test
        pindah ke bulan yang field-nya terisi supaya fitur edit tetap
        dites SUNGGUHAN (tetap di-revert, data DEV tidak rusak)."""
        return self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (!t) return null;"
            "const keys = Object.keys(arguments[1]);"
            "for (const tr of t.querySelectorAll('tbody tr')) {"
            "  const vals = {};"
            "  let cocok = true;"
            "  for (const k of keys) {"
            "    const inp = tr.querySelector("
            "      \"input[data-fieldname='\" + k + \"']\");"
            "    if (!inp || inp.value === '') { cocok = false; break; }"
            "    vals[k] = inp.value;"
            "  }"
            "  if (!cocok) continue;"
            "  const f = tr.querySelector("
            "    \"input[data-fieldname='\" + arguments[0] + \"']\");"
            "  if (f && f.value !== '') return vals;"
            "}"
            "return null;",
            nama_field,
            anchor,
        )

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
                self.pace()
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
                self.pace()
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
                self.XP_MODAL
                + "//button[normalize-space(.)='No' or normalize-space(.)='Cancel'"
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
        self.pace()
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
        """Hapus baris DRAFT (semua input kosong) PERTAMA yang ketemu --
        di SELURUH HALAMAN grid utama, bukan cuma yang sedang tampil --
        lewat tombol Delete barisnya + konfirmasi Yes. Dipakai untuk
        membersihkan draft yang nyangkut setelah Create+Cancel.

        Grid ber-pagination (mis. Master Alat yang sudah menumpuk banyak
        baris) hanya me-render baris HALAMAN AKTIF ke DOM -- scan yang
        cuma lihat DOM saat ini bisa MELEWATKAN draft kosong yang duduk
        di halaman lain, dan draft yang lolos itu tetap bikin Submit
        Changes berikutnya membuang baris baru (2026-09-04: akar masalah
        kenapa test_safety_master_alat_create masih sesekali gagal walau
        sudah dipanggil di awal alur). Kalau grid bukan DataTables ber-
        pagination, `dt_info()` None -- fallback ke scan halaman aktif
        saja (perilaku lama, dipakai grid non-DataTables juga)."""
        info = self.dt_info()
        halaman_awal = info["page"] if info else 0
        total_halaman = info["pages"] if info else 1
        for h in range(max(total_halaman, 1)):
            if info:
                self.dt_ke_halaman(h)
            terhapus = self.driver.execute_script(
                f"const t = {self.JS_GRID};"
                "if (!t) return false;"
                # Checkbox/radio/hidden diabaikan saat menilai "kosong":
                # .value checkbox defaultnya 'on', jadi satu checkbox
                # saja membuat baris draft TIDAK PERNAH terdeteksi
                # kosong -- pembersih ini diam-diam tidak bekerja di
                # halaman ber-checkbox (2026-09-08, sebab yang sama
                # dengan JS_ISI_BARIS_KOSONG di bawah).
                "const abaikan = "
                "  ['checkbox','radio','hidden','button','submit'];"
                "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
                "  const ins = [...r.querySelectorAll('input')].filter(i =>"
                "    !abaikan.includes((i.type || 'text').toLowerCase()));"
                "  return ins.length > 0 && ins.every(i => i.value === '');"
                "});"
                "if (!tr) return false;"
                "const del = tr.querySelector('a.btn-delete');"
                "if (!del) return false;"
                "del.click(); return true;"
            )
            if terhapus:
                self.pace()
                self.jawab_konfirmasi()
                self.tunggu_processing_selesai()
                if info:
                    self.dt_ke_halaman(halaman_awal)
                return
        if info:
            self.dt_ke_halaman(halaman_awal)

    # JS: isi SEMUA input yang bisa diketik di baris draft KOSONG
    # (baris hasil klik Create). Lookup/select/checkbox dilewati --
    # isinya harus dipilih dari daftar, tidak bisa diketik bebas.
    #
    # Kolom TANGGAL ikut diisi (arguments[1]) -- ini penting untuk
    # halaman DailyReport: barisnya punya kolom tanggal sendiri DAN
    # gridnya disaring per tanggal. Kalau kolom itu dilewati, baris
    # tersimpan tanpa tanggal lalu tidak muncul di filter, dan test
    # salah menyimpulkan "tidak tersimpan" (ketahuan 2026-09-08: 3
    # halaman DailyReport gagal/skip sementara 6 halaman lain lulus).
    JS_ISI_BARIS_KOSONG = (
        f"const t = {JS_GRID};"
        "if (!t) return null;"
        "const penanda = arguments[0];"
        "const tanggal = arguments[1];"   # 'YYYY-MM-DD' atau ''
        # Cari baris draft KOSONG. Checkbox/radio/hidden/tombol SENGAJA
        # tidak ikut dinilai: .value checkbox defaultnya 'on', bukan '',
        # jadi satu checkbox saja membuat baris tidak pernah dianggap
        # kosong. Itu yang bikin Incident Investigation selalu SKIP
        # ("tidak ada baris draft kosong") padahal barisnya ADA --
        # kolom 'Nearmiss' di halaman itu berupa checkbox
        # (screenshot 2026-09-08 16:13).
        "const abaikan = ['checkbox','radio','hidden','button','submit'];"
        "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
        "  const ins = [...r.querySelectorAll('input')].filter(i =>"
        "    !abaikan.includes((i.type || 'text').toLowerCase()));"
        "  return ins.length > 0 && ins.every(i => i.value === '');"
        "});"
        "if (!tr) return null;"
        "const terisi = [];"
        "for (const el of tr.querySelectorAll('input[data-fieldname]')) {"
        "  if (el.readOnly || el.disabled) continue;"
        "  const tipe = (el.type || 'text').toLowerCase();"
        "  if (['checkbox','radio','file'].includes(tipe)) continue;"
        "  const nama = el.getAttribute('data-fieldname') || '';"
        "  let nilai;"
        "  if (tipe === 'number') { nilai = '1'; }"
        "  else if (tipe === 'date') { if (!tanggal) continue;"
        "                              nilai = tanggal; }"
        "  else if (tipe === 'datetime-local') { if (!tanggal) continue;"
        "                              nilai = tanggal + 'T08:00'; }"
        "  else if (tipe === 'month') { if (!tanggal) continue;"
        "                              nilai = tanggal.slice(0, 7); }"
        "  else if (tipe === 'time') { nilai = '08:00'; }"
        "  else if (tipe === 'week') { continue; }"
        "  else { nilai = penanda; }"
        "  el.value = nilai;"
        "  el.dispatchEvent(new Event('input', {bubbles: true}));"
        "  el.dispatchEvent(new Event('change', {bubbles: true}));"
        "  terisi.push(nama);"
        "}"
        # <select> SAMA SEKALI tidak tersentuh sebelum 2026-09-08 --
        # JS-nya cuma memindai input[data-fieldname]. Padahal di halaman
        # bervalidasi, dropdown seperti ini termasuk field WAJIB, jadi
        # barisnya selalu ditolak. Diisi opsi pertama yang punya value.
        "for (const el of tr.querySelectorAll('select[data-fieldname]')) {"
        "  if (el.disabled) continue;"
        "  const opsi = [...el.options].find(o =>"
        "    o.value !== '' && !o.disabled);"
        "  if (!opsi) continue;"
        "  el.value = opsi.value;"
        "  el.dispatchEvent(new Event('change', {bubbles: true}));"
        "  terisi.push((el.getAttribute('data-fieldname') || '') + '(select)');"
        "}"
        # <textarea> juga terlewat sebelumnya.
        "for (const el of tr.querySelectorAll('textarea[data-fieldname]')) {"
        "  if (el.readOnly || el.disabled) continue;"
        "  el.value = penanda;"
        "  el.dispatchEvent(new Event('input', {bubbles: true}));"
        "  el.dispatchEvent(new Event('change', {bubbles: true}));"
        "  terisi.push((el.getAttribute('data-fieldname') || '') + '(textarea)');"
        "}"
        "return terisi;"
    )

    def isi_baris_kosong_inline(self, penanda, tanggal=""):
        """Isi baris draft KOSONG (hasil klik Create) langsung di grid,
        tanpa modal form. Kembalikan daftar nama kolom yang benar-benar
        diisi, atau None kalau tidak ada baris kosong.

        `tanggal` ('YYYY-MM-DD') mengisi kolom date/datetime/month di
        baris itu. WAJIB diisi untuk halaman DailyReport: barisnya punya
        kolom tanggal sendiri dan gridnya disaring per tanggal, jadi
        baris tanpa tanggal tidak akan muncul lagi setelah Submit.

        Checkbox/radio/file dan lookup dilewati: nilainya tidak bisa
        diketik bebas. Kolom angka diisi '1', kolom teks diisi
        `penanda` supaya barisnya bisa dicari lagi setelah Submit.

        Dipakai test jalur input LANGSUNG DI TABEL -- jalur yang dipakai
        user pada halaman tanpa 'Create with Form', dan yang sampai
        2026-09-08 sama sekali belum pernah diuji (satu-satunya test
        yang menyentuh tombol Create cuma mengklik lalu Cancel, barisnya
        tidak pernah diisi).
        """
        return self.driver.execute_script(
            self.JS_ISI_BARIS_KOSONG, penanda, tanggal or ""
        )

    def hapus_baris_berisi(self, teks):
        """Klik Delete pada baris pertama yang salah satu inputnya
        memuat `teks`, lalu jawab konfirmasi. True kalau ada yang
        diklik. Dipakai membersihkan baris yang dibuat test sendiri."""
        terhapus = self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (!t) return false;"
            "const cari = (arguments[0] || '').toLowerCase();"
            "const tr = [...t.querySelectorAll('tbody tr')].find(r =>"
            "  [...r.querySelectorAll('input')].some(i =>"
            "    (i.value || '').toLowerCase().includes(cari)));"
            "if (!tr) return false;"
            "const del = tr.querySelector('a.btn-delete');"
            "if (!del) return false;"
            "del.click(); return true;",
            teks,
        )
        if terhapus:
            self.pace()
            self.jawab_konfirmasi()
            self.tunggu_processing_selesai()
        return bool(terhapus)

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
        # Baris draft KOSONG yang nyangkut dari aksi sebelumnya bikin
        # Submit Changes MEMBUANG baris baru dari Create with Form --
        # bersihkan dulu (2026-08-31, lihat catatan TOMBOL_HALAMAN di atas).
        self._hapus_baris_kosong()
        for percobaan in (1, 2):
            self.buka_form_create()
            self.pace()
            self.isi_form_create_otomatis(penanda=penanda)
            try:
                self.simpan_form()
                break
            except TimeoutException as exc:
                if "MODAL_LENYAP" not in str(exc) or percobaan == 2:
                    raise
                # modal form lenyap tepat sebelum Save (quirk notifikasi
                # aplikasi, 2026-08-28) -- belum ada yang tersimpan
                # (tidak ada draft yatim), buka + isi form ULANG sekali
                print("  [create] modal lenyap sebelum Save -- buka form ulang")
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
        self.pace()
        if not _terbuka():
            return
        self.driver.find_element(By.CSS_SELECTOR, "body").send_keys(Keys.ESCAPE)
        self.pace()
        if not _terbuka():
            return
        self.driver.execute_script("document.body.click();")
        self.pace()
        self._wait(config.DEFAULT_TIMEOUT).until(
            lambda d: not _terbuka(),
            "Dropdown Columns tidak kunjung tertutup (toggle, ESC, "
            "klik luar semua tidak mempan)",
        )

    def klik_item_columns(self):
        """Klik item 'Settings' di dropdown Columns lalu tutup modal
        'Freeze Column' yang terbuka. Isi dropdown Columns = 'Unfreeze'
        & 'Settings' (probe tools/probe_columns.py, 2026-08-31;
        permintaan user: dropdown Columns dibuka lalu PILIH SETTINGS).
        Modal Freeze Column (daftar kolom grid) yang terbuka jadi bukti
        item benar2 diklik, lalu DITUTUP supaya alur berikutnya bersih.
        Kalau item belum ter-render (quirk redraw SPA), dropdown
        dibuka ulang sekali."""
        lokasi = (
            By.XPATH,
            "//div[contains(@class,'dt-button-collection')]"
            "//a[contains(@class,'dt-button')]"
            "[normalize-space(.)='Settings']",
        )
        for percobaan in (1, 2):
            try:
                element = self._ambil_js_visible(lokasi, timeout=5)
            except TimeoutException:
                if percobaan == 2:
                    raise
                # item belum ter-render -- buka ulang dropdown
                self.tutup_dropdown_columns()
                self.buka_dropdown_columns()
                self.pace()
                continue
            self.driver.execute_script("arguments[0].click();", element)
            self.tunggu_modal_terbuka()
            self.pace()
            self.tutup_modal()
            print("  [columns] item 'Settings' diklik -> modal Freeze"
                  " Column dibuka & ditutup")
            return

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

    # Halaman yang form "Create with Form"-nya TIDAK menerapkan validasi
    # field wajib -- Save dengan form kosong diterima aplikasi (modal
    # menutup tanpa pesan error). Dicek 2026-08-28 (run pertama
    # test_safety_create_form_validasi): hanya Incident Investigation
    # Form & Witness Statement Report yang benar-benar menolak input
    # kosong.
    #
    # STATUS 2026-09-07: dikonfirmasi pemilik produk bahwa menyimpan
    # baris kosong di halaman-halaman ini MEMANG DIBOLEHKAN -- jadi ini
    # perilaku yang disengaja, BUKAN bug dan BUKAN temuan yang belum
    # ditindaklanjuti. Tidak perlu dibuatkan laporan bug.
    #
    # Halaman di set ini di-skip supaya test tetap tajam untuk dua form
    # yang memang punya validasi wajib. Kalau suatu saat aturan bisnisnya
    # berubah dan salah satu halaman ini mulai mewajibkan field, keluarkan
    # dari set ini supaya validasinya ikut diuji.
    FORM_TANPA_VALIDASI_WAJIB = {
        "emergency_drill_daily",
        "golden_rules",
        "initial_incident_accident_report",
        "master_alat_keselamatan_operasi",
        "mwt_daily",
        "safety_kkp_p2k3_committee_meeting",
        "soc_recapitulation",
    }

    # Halaman yang tombol pembuka modal-nya (Import / Create /
    # Create with Form / Select Finding) kadang TIDAK memicu modal
    # walau tombol tampak & sudah diklik + navigasi ulang -- quirk SPA
    # "handler mati" di DEV OPEL (diamati di Incident Investigation,
    # run 2026-08-28: modal Import/Create tidak terbuka bahkan di run
    # pendek 3 test). Untuk halaman ini, test "coba semua tombol"
    # menganggap tombol SUDAH DICOBA (diklik) walau modal tak terbuka --
    # sesuai tujuan test (klik tiap tombol), bukan verifikasi modal.
    MODAL_BEST_EFFORT = {"incident_investigation_form"}

    # Halaman yang tombol Submit Changes-nya RUSAK: klik Submit langsung
    # me-redirect ke template lain SEBELUM dialog konfirmasi muncul,
    # sehingga request penyimpanan tidak pernah terkirim dan data user
    # hilang senyap.
    #
    #   Id=1317: MonthlyReport/Edit?Id=1317
    #         -> YearlyReport/Edit?Id=1317&DistrictCode=AT10
    #
    # BUG APLIKASI TERKONFIRMASI (2026-09-08) -- rinciannya di
    # reports/bugs/submit-changes-redirect-tanpa-menyimpan.md:
    #   * terulang di incognito DAN di mesin Windows lain, jadi bukan
    #     efek state/beban dari automation;
    #   * dari 4 halaman MonthlyReport/Edit, HANYA Id=1317 terkena
    #     (golden_rules 1316, mwt_daily 1312, emergency_drill_daily 1319
    #     lulus di run `pytest -m MonthlyReport_Edit` 2026-09-08:
    #     1 failed, 15 passed, 4 skipped) -- jadi bug KONFIGURASI
    #     halaman, bukan bug template.
    #
    # Didaftar di sini supaya suite tidak merah permanen: kegagalan yang
    # selalu ada bikin orang berhenti membaca hasil, dan regresi BARU
    # ikut tenggelam. Yang dilonggarkan HANYA pemeriksaan penyimpanan;
    # langkah lain di test yang sama tetap di-assert ketat.
    # DIKOSONGKAN 2026-09-10: Id=1317 sudah diperbaiki aplikasi --
    # halamannya kini konsisten YearlyReport, jadi tidak ada lagi
    # redirect di tengah alur Submit. Pemeriksaan penyimpanan untuk
    # halaman ini kembali TAJAM (di-assert, bukan sekadar diperingatkan).
    # Lihat reports/bugs/submit-changes-redirect-tanpa-menyimpan.md.
    SUBMIT_REDIRECT_TANPA_SIMPAN = set()

    # CATATAN 2026-09-08 -- registry CREATE_INLINE_TIDAK_TERSIMPAN
    # DIHAPUS, dan laporan bug yang menyertainya DITARIK.
    #
    # Sempat dikira bug: baris baru di Witness Statement hilang setelah
    # Submit Changes. Ternyata aplikasinya BENAR -- barisnya ditolak
    # VALIDASI FIELD WAJIB, karena `isi_baris_kosong_inline()` hanya
    # mengisi input teks/angka/tanggal dan MELEWATI kolom lookup/select
    # yang di halaman itu wajib diisi.
    #
    # Korelasinya sempurna 9/9 pada run 2026-09-08:
    #   2 halaman yang MENERAPKAN validasi wajib -> gagal/skip
    #     (incident_investigation_form, witness_statement_report)
    #   7 halaman TANPA validasi wajib            -> lulus semua
    # Daftarnya sudah ada di FORM_TANPA_VALIDASI_WAJIB di bawah.

    # CATATAN 2026-09-07 -- registry CANCEL_TIDAK_MEMBUANG_PENDING DIHAPUS.
    #
    # Set itu dulu berisi {"smk3"} untuk melonggarkan assertion "Cancel
    # harus membuang perubahan pending". Ternyata assertion-nya sendiri
    # yang salah: draft lokal MEMANG sengaja dipertahankan OPEL (fitur
    # perlindungan kalau halaman ter-reload / koneksi putus), dan yang
    # membuangnya adalah tombol Reload Data. Jadi tidak ada bug yang
    # perlu dilonggarkan -- test_safety_lagging_deep sekarang menguji
    # Reload Data, sesuai kontrak aplikasi yang sebenarnya.
    # Lihat reports/bugs/lagging-cancel-does-not-discard-edit.md
    # (ditutup sebagai BUKAN BUG).

    def coba_tombol(self, nama):
        """Jalankan SATU aksi fitur sesuai nama tombol toolbar. Dipakai
        test 'coba semua tombol' per halaman DAN per tab (permintaan
        user 2026-08-31: setiap tombol fitur dicoba di setiap halaman
        & setiap tab, KECUALI link Instructions). Aksi khusus:
        Import -> modal buka + file dummy DIPASANG di input upload
        (TIDAK dikirim ke server = aman); Columns -> dropdown DIBUKA +
        item kolom DIKLIK lalu state dikembalikan; Export -> file
        diunduh & diverifikasi; Create with Form -> form diisi dummy
        lalu Save+Submit SUNGGUHAN.

        Halaman di MODAL_BEST_EFFORT (quirk SPA "handler mati" di DEV,
        mis. Incident Investigation) dapat perlakuan best-effort: kalau
        tombol pembuka modal sudah diklik tapi modal tak kunjung
        terbuka, tombol dianggap SUDAH DICOBA (bukan gagal) -- sisa
        dibersihkan & halaman dimuat ulang supaya lanjut aman."""
        aksi_modal = {"Import", "Create", "Create with Form", "Select Finding"}
        if (nama in aksi_modal
                and getattr(self, "KUNCI", "") in self.MODAL_BEST_EFFORT):
            try:
                self._coba_tombol_inti(nama)
            except TimeoutException:
                # tombol sudah diklik -- modal tak terbuka (quirk DEV,
                # lihat MODAL_BEST_EFFORT). Bersihkan sisa & lanjut.
                try:
                    self._paksa_tutup_modal()
                except Exception:
                    pass
                self.driver.get(self.driver.current_url)
                try:
                    self._tunggu_tabel()
                except TimeoutException:
                    pass
                self.tunggu_processing_selesai()
            self.pace(1.0)
            return
        self._coba_tombol_inti(nama)
        self.pace(1.0)

    def _coba_tombol_inti(self, nama):
        if nama == "Reload Data":
            self.reload_data()
        elif nama == "Import":
            self.buka_modal_import()
            self.pace()
            self.pasang_file_dummy_import()
            self.pace()
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
            self.export_dan_tunggu_file(
                wajib_file=getattr(self, "KUNCI", "")
                not in self.EXPORT_TANPA_FILE
            )
        elif nama == "Export Excel":
            self.export_excel_dan_tunggu_file()
        # "Instructions" TIDAK diklik (permintaan user 2026-08-28) --
        # link membuka konten di luar halaman dan tidak bagian alur
        elif nama == "Select Finding":
            self.click_js_saat_tampil(self.BTN_SELECT_FINDING)
            self.pace()
            self.tutup_modal()
        elif nama == "Columns":
            try:
                self.buka_dropdown_columns()
                self.pace()
                self.klik_item_columns()
                self.pace()
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
            self.pace()
            self.toggle_fullscreen()
            self.tunggu_fullscreen(False)
        elif nama == "Cancel":
            self.click_js_saat_tampil(self.BTN_CANCEL_GRID)
            self.jawab_konfirmasi()

    # Lebar viewport minimum supaya sidebar OPEL tetap terbentang.
    # Di bawah ini template SmartAdmin meng-collapse sidebar jadi
    # hamburger, dan navigasi lewat menu tidak bisa dilakukan.
    LEBAR_MIN_SIDEBAR = 1100

    def pulihkan_viewport(self, paksa=False):
        """Pastikan jendela cukup lebar dan tidak sedang fullscreen.

        Tombol FullScreen di toolbar OPEL memakai Fullscreen API asli
        browser, jadi kalau alur keluar-fullscreen gagal, jendela bisa
        tertinggal dalam ukuran yang JAUH lebih sempit. Dampaknya baru
        terasa di test BERIKUTNYA: sidebar collapse, lalu
        `move_to_element` ke item menu melempar
        MoveTargetOutOfBoundsException dan sidebar tidak pernah muncul
        (run penuh 2026-09-07: 'Initial Incident/Accident' dan 'Witness
        Statement' gagal begitu, screenshot menunjukkan jendela 1436px
        padahal test lain 2880px).

        Kembalikan True kalau sesuatu benar-benar dipulihkan.
        """
        dipulihkan = False
        try:
            if self.driver.execute_script("return !!document.fullscreenElement;"):
                self.driver.execute_script(
                    "if (document.exitFullscreen) document.exitFullscreen();"
                )
                self.pace(0.5)
                dipulihkan = True
        except Exception:
            pass  # bukan bagian inti test -- jangan menggagalkan karenanya
        try:
            lebar = self.driver.execute_script("return window.innerWidth;") or 0
            if paksa or lebar < self.LEBAR_MIN_SIDEBAR:
                self.driver.maximize_window()
                self.pace(0.5)
                dipulihkan = True
        except Exception:
            pass
        return dipulihkan

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

    # ==================================================================
    # DataTables -- interaksi grid generik (sort, pagination, search box,
    # show/hide kolom). Semua lewat jQuery DataTables API pada GRID UTAMA
    # (JS_GRID) supaya tidak salah sasaran ke template reportData kosong.
    # Setiap helper mengembalikan None kalau grid BUKAN DataTables aktif
    # (aplikasi belum init / halaman custom) -- pemanggil memperlakukan
    # itu sebagai "fitur tidak tersedia" dan skip, konsisten dengan pola
    # tolerant helper lain di file ini (2026-08-28).
    # ==================================================================
    # Prefix JS: ambil instance DataTable grid utama -> variabel `dt`.
    _JS_DT = (
        f"const t = {JS_GRID};"
        "if (!t || !window.jQuery || !jQuery.fn.dataTable"
        "    || !jQuery.fn.dataTable.isDataTable(t)) return null;"
        "const dt = jQuery(t).DataTable();"
    )

    def _dt_ada(self):
        """True kalau grid utama adalah DataTables yang sudah ter-init."""
        return bool(self.driver.execute_script(
            self._JS_DT + "return true;"
        ))

    def dt_info(self):
        """Info pagination DataTables grid utama (dict) atau None.
        Kunci: page (0-based), pages, recordsTotal, recordsDisplay,
        length, start, end."""
        return self.driver.execute_script(
            self._JS_DT + "const i = dt.page.info(); return {"
            "page: i.page, pages: i.pages, recordsTotal: i.recordsTotal,"
            "recordsDisplay: i.recordsDisplay, length: i.length,"
            "start: i.start, end: i.end};"
        )

    def dt_jumlah_baris_dom(self):
        """Jumlah baris <tr> data yang benar-benar dirender di tbody
        grid utama (baris pesan 'No data' TIDAK dihitung)."""
        return self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (!t) return -1;"
            "return [...t.querySelectorAll('tbody tr')].filter(tr =>"
            "  !tr.querySelector('td.dataTables_empty')).length;"
        )

    def daftar_kolom_grid(self):
        """Daftar kolom grid utama: list of dict {index, name, sortable,
        visible}. `name` dari th[data-name]; `sortable` = th punya class
        'sorting*'. None kalau bukan DataTables."""
        return self.driver.execute_script(
            self._JS_DT +
            "return dt.columns().indexes().toArray().map(idx => {"
            "  const th = dt.column(idx).header();"
            "  const cls = th ? th.className : '';"
            "  return {index: idx,"
            "          name: th ? (th.getAttribute('data-name') || "
            "                     (th.innerText || '').trim()) : '',"
            "          sortable: /sorting(_asc|_desc)?(\\s|$)/.test(cls),"
            "          visible: dt.column(idx).visible()};"
            "});"
        )

    def dt_order_state(self):
        """State order DataTables saat ini: list [[index, 'asc'|'desc']]
        atau None."""
        return self.driver.execute_script(self._JS_DT + "return dt.order();")

    def dt_nilai_kolom(self, index_kolom, maks=20):
        """Nilai teks kolom `index_kolom` untuk baris yang tampil di
        halaman aktif (list string, maksimal `maks`). Membaca innerText
        DAN value input (grid inline-edit menaruh nilai di <input>)."""
        return self.driver.execute_script(
            self._JS_DT +
            "const out = [];"
            "dt.column(arguments[0], {page: 'current'}).nodes().each(td => {"
            "  if (out.length >= arguments[1]) return;"
            "  const inp = td.querySelector('input, select, textarea');"
            "  out.push(((inp ? inp.value : td.innerText) || '').trim());"
            "});"
            "return out;",
            index_kolom, maks,
        )

    def dt_urutkan(self, index_kolom, arah="asc"):
        """Urutkan grid utama berdasarkan kolom `index_kolom`
        (`arah` = 'asc'/'desc') lewat DataTables API, lalu tunggu
        redraw selesai. Kembalikan order state baru atau None."""
        hasil = self.driver.execute_script(
            self._JS_DT +
            "dt.order([arguments[0], arguments[1]]).draw();"
            "return dt.order();",
            index_kolom, arah,
        )
        self.tunggu_processing_selesai()
        self.pace()
        return hasil

    def dt_ke_halaman(self, nomor):
        """Pindah ke halaman pagination `nomor` (0-based) lewat
        DataTables API lalu tunggu redraw. Kembalikan info() baru."""
        self.driver.execute_script(
            self._JS_DT + "dt.page(arguments[0]).draw('page');", nomor
        )
        self.tunggu_processing_selesai()
        self.pace()
        return self.dt_info()

    def dt_search_kotak(self, teks):
        """Ketik `teks` ke kotak Search DataTables (input di
        div.dataTables_filter) persis seperti user -- set value + event
        keyup supaya handler filter bawaan DataTables jalan. Tunggu
        redraw. Kembalikan jumlah baris hasil filter (recordsDisplay)
        atau None kalau kotak search tidak ada."""
        ada = self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (!t) return false;"
            "const wrap = t.closest('.dataTables_wrapper');"
            "const inp = wrap ? wrap.querySelector('.dataTables_filter input')"
            "                 : null;"
            "if (!inp) return false;"
            "inp.value = arguments[0];"
            "inp.dispatchEvent(new Event('input', {bubbles: true}));"
            "inp.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));"
            "return true;",
            teks,
        )
        if not ada:
            return None
        self.tunggu_processing_selesai()
        self.pace()
        info = self.dt_info()
        return info["recordsDisplay"] if info else self.dt_jumlah_baris_dom()

    def dt_kolom_terlihat(self, index_kolom):
        """True/False apakah kolom `index_kolom` sedang tampil, atau
        None kalau bukan DataTables."""
        return self.driver.execute_script(
            self._JS_DT + "return dt.column(arguments[0]).visible();",
            index_kolom,
        )

    def dt_set_kolom_terlihat(self, index_kolom, tampil):
        """Tampilkan/sembunyikan kolom `index_kolom` lewat DataTables
        API (jalur andal -- dropdown Columns UI rewel di sebagian
        halaman). Kembalikan state visible baru."""
        hasil = self.driver.execute_script(
            self._JS_DT +
            "dt.column(arguments[0]).visible(arguments[1]);"
            "return dt.column(arguments[0]).visible();",
            index_kolom, bool(tampil),
        )
        self.pace()
        return hasil

    def jumlah_th_grid(self):
        """Jumlah <th> yang benar-benar dirender di thead grid utama
        (dipakai verifikasi show/hide kolom mengubah DOM)."""
        return self.driver.execute_script(
            f"const t = {self.JS_GRID};"
            "if (!t) return -1;"
            "const tr = t.querySelector('thead tr');"
            "return tr ? [...tr.children].filter(th => {"
            "  const s = window.getComputedStyle(th);"
            "  return s.display !== 'none';"
            "}).length : -1;"
        )

    # ==================================================================
    # Isi panel tab -- verifikasi tab BUKAN cuma dapat class 'active'
    # tapi panel tujuannya benar-benar menampilkan konten (tabel / field)
    # ==================================================================
    def panel_tab_isi_tampil(self, teks_tab):
        """True kalau panel tujuan tab `teks_tab` benar-benar tampil dan
        punya konten berarti (tabel dengan baris, atau >=1 field/elemen
        input, atau teks non-kosong yang cukup panjang)."""
        return bool(self.driver.execute_script(
            "const teks = arguments[0].trim().toLowerCase();"
            "const link = [...document.querySelectorAll('a.nav-link')]"
            "  .find(a => (a.innerText || '').trim().toLowerCase() === teks);"
            "if (!link) return false;"
            "let sel = link.getAttribute('href') || '';"
            "if (!sel || sel === '#') {"
            "  const c = link.getAttribute('aria-controls');"
            "  sel = c ? ('#' + c) : '';"
            "}"
            "if (!sel) return false;"
            "const panel = document.querySelector(sel);"
            "if (!panel) return false;"
            "const s = window.getComputedStyle(panel);"
            "const r = panel.getBoundingClientRect();"
            "if (s.display === 'none' || s.visibility === 'hidden'"
            "    || r.height < 1) return false;"
            "const adaTabel = [...panel.querySelectorAll('table')].some(tb =>"
            "  tb.querySelectorAll('tbody tr').length > 0);"
            "const adaField = panel.querySelectorAll("
            "  'input, select, textarea').length > 0;"
            "const adaTeks = (panel.innerText || '').trim().length > 15;"
            "return adaTabel || adaField || adaTeks;"
        , teks_tab))

    # ==================================================================
    # Create with Form -- validasi field wajib (negative case): Save
    # dengan form KOSONG harus DITOLAK (modal tetap terbuka / muncul
    # pesan validasi). Tidak menyimpan apa pun ke server.
    # ==================================================================
    def coba_simpan_form_kosong(self):
        """Buka Create with Form -> langsung klik Save tanpa isi apa pun.
        Kembalikan dict {modal_terbuka, ada_pesan_validasi}. Pemanggil
        meng-assert minimal salah satunya True (form menolak input
        kosong). Modal ditutup lagi setelahnya (tidak menyimpan)."""
        self.buka_form_create()
        self.pace(1.0)
        self._klik_jika_ada(self.BTN_SAVE_MODAL)
        self.pace(1.5)
        modal_terbuka = self._ada_modal_tampil()
        ada_pesan = bool(self.driver.execute_script(
            "const nodes = document.querySelectorAll("
            "  '.modal.show .is-invalid, .modal.show .invalid-feedback,"
            "   .modal.show .field-validation-error,"
            "   .modal.show .text-danger, .modal.in .is-invalid,"
            "   .modal.in .text-danger');"
            "for (const n of nodes) {"
            "  const s = window.getComputedStyle(n);"
            "  if (s.display !== 'none' && s.visibility !== 'hidden')"
            "    return true;"
            "}"
            "return false;"
        ))
        # bersihkan: tutup modal apa pun yang masih ada (tanpa Save)
        try:
            self.batal_form()
        except Exception:
            self._paksa_tutup_modal()
        try:
            if self._ada_modal_tampil():
                self.tutup_modal()
        except TimeoutException:
            self._paksa_tutup_modal()
        return {"modal_terbuka": modal_terbuka, "ada_pesan_validasi": ada_pesan}

    # ==================================================================
    # ISI grid -- dipakai test yang memverifikasi DATA-nya, bukan cuma
    # elemennya (2026-09-04, "naik level"): assertion lama hanya
    # membuktikan halaman TAMPIL, bukan halaman BENAR. Tiga kebutuhan:
    #   1. bandingkan data SEBELUM vs SESUDAH filter diganti
    #      -> sidik_jari_grid() + dt_baris_nilai()
    #   2. nilai apakah grid berisi DATA atau cuma kerangka template --
    #      butuh baris ber-NAMA-kolom supaya kolom kerangka (No, Month,
    #      TipePegawai) bisa dibuang -> dt_baris_dict()
    #   3. cocokkan isi file export dengan isi grid -> dt_baris_nilai()
    # ==================================================================
    JS_BARIS_NILAI = (
        f"const t = {JS_GRID};"
        "if (!t) return [];"
        "const maks = arguments[0];"
        "const out = [];"
        "for (const tr of t.querySelectorAll('tbody tr')) {"
        "  if (out.length >= maks) break;"
        "  if (tr.querySelector('td.dataTables_empty')) continue;"
        "  const baris = [];"
        "  for (const td of tr.children) {"
        "    if (window.getComputedStyle(td).display === 'none') continue;"
        "    const inp = td.querySelector('input, select, textarea');"
        "    baris.push(((inp ? inp.value : td.innerText) || '').trim());"
        "  }"
        "  out.push(baris);"
        "}"
        "return out;"
    )

    # Baris sebagai dict {data-fieldname: nilai}. Grid inline-edit OPEL
    # menaruh nilai di <input data-fieldname='...'>; kolom read-only
    # cuma punya <td data-name='...'> -- keduanya dibaca, input menang
    # kalau sebuah kolom punya dua-duanya.
    JS_BARIS_DICT = (
        f"const t = {JS_GRID};"
        "if (!t) return [];"
        "const maks = arguments[0];"
        "const out = [];"
        "for (const tr of t.querySelectorAll('tbody tr')) {"
        "  if (out.length >= maks) break;"
        "  if (tr.querySelector('td.dataTables_empty')) continue;"
        "  const baris = {};"
        "  for (const td of tr.querySelectorAll('td[data-name]')) {"
        "    baris[td.getAttribute('data-name')] ="
        "      ((td.innerText) || '').trim();"
        "  }"
        "  for (const el of tr.querySelectorAll('[data-fieldname]')) {"
        "    baris[el.getAttribute('data-fieldname')] ="
        "      ((el.value != null ? el.value : el.innerText) || '').trim();"
        "  }"
        "  out.push(baris);"
        "}"
        "return out;"
    )

    def dt_baris_nilai(self, maks_baris=5):
        """Isi grid utama sebagai list-of-list string: satu list per
        baris yang TAMPIL di halaman aktif, berisi nilai tiap sel yang
        terlihat (value <input>/<select>/<textarea> kalau ada, kalau
        tidak innerText <td>). Baris 'No data available' dilewati."""
        return self.driver.execute_script(
            self.JS_BARIS_NILAI, int(maks_baris)
        ) or []

    def dt_baris_dict(self, maks_baris=5):
        """Isi grid utama sebagai list of dict {nama_kolom: nilai}.
        Dipakai test yang perlu mengambil beberapa kolom DARI BARIS YANG
        SAMA (mis. hitung ulang Frequency Rate dari jam kerja + jumlah
        kecelakaan di baris bulan yang sama)."""
        return self.driver.execute_script(
            self.JS_BARIS_DICT, int(maks_baris)
        ) or []

    JS_KOLOM_HEADER = (
        f"const t = {JS_GRID};"
        "if (!t) return [];"
        "const trs = [...t.querySelectorAll('thead tr')];"
        "if (!trs.length) return [];"
        "const tr = trs.reduce((a, b) =>"
        "  b.children.length > a.children.length ? b : a);"
        "return [...tr.children]"
        "  .filter(th => window.getComputedStyle(th).display !== 'none')"
        "  .map(th => (th.getAttribute('data-name')"
        "              || th.innerText || '').trim())"
        "  .filter(Boolean);"
    )

    def nama_kolom_header(self):
        """Set nama kolom yang ter-render di thead grid utama (dari
        th[data-name], fallback teks th). Jalan juga untuk tabel yang
        BUKAN DataTables. Header berjenjang (colspan): dipakai baris
        <tr> yang jumlah selnya paling banyak."""
        return set(self.driver.execute_script(self.JS_KOLOM_HEADER) or [])

    def nama_kolom_grid(self):
        """Semua nama kolom grid utama. Lewat DataTables API kalau grid
        ter-init (IKUT menghitung kolom yang sedang disembunyikan --
        penting supaya cek kontrak kolom tidak gagal palsu hanya karena
        sebuah kolom default-nya hidden), kalau tidak dari <th>."""
        kolom = self.daftar_kolom_grid() if self._dt_ada() else None
        if kolom:
            nama = {(k.get("name") or "").strip() for k in kolom}
            nama.discard("")
            if nama:
                return nama
        return self.nama_kolom_header()

    def sidik_jari_grid(self, maks_baris=5):
        """Ringkasan isi grid sebagai string, untuk membandingkan data
        SEBELUM vs SESUDAH filter diganti. Menggabungkan jumlah record
        yang dilaporkan DataTables + nilai sel `maks_baris` baris
        pertama, jadi perubahan jumlah baris MAUPUN perubahan isi
        sama-sama terdeteksi."""
        info = self.dt_info() or {}
        return json.dumps(
            {
                "total": info.get("recordsDisplay"),
                "baris": self.dt_baris_nilai(maks_baris),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
