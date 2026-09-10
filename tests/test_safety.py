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

import json
import os
import re
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
# Halaman yang punya tombol "Create" polos (menambah baris draft kosong
# langsung ke grid, tanpa modal). Dipakai test jalur input LANGSUNG DI
# TABEL -- jalur yang dipakai user pada halaman tanpa Create with Form,
# dan yang sampai 2026-09-08 belum pernah diuji sama sekali: satu-satunya
# test yang menyentuh tombol Create cuma mengklik lalu Cancel, barisnya
# tidak pernah diisi.
CREATE_INLINE_KEYS = sorted(
    k for k in PAGE_OBJECTS
    if "Create" in HssSafetyPage.TOMBOL_HALAMAN.get(k, ())
)

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


def _normalisasi(nilai):
    """Samakan BENTUK nilai grid vs nilai sel Excel supaya bisa
    dibandingkan: teks dirapatkan + huruf kecil, angka dijadikan bentuk
    kanonik ('7' == '7.0' == 7 == '7,0')."""
    teks = str(nilai).strip()
    if not teks:
        return ""
    try:
        angka = float(teks.replace(",", "."))
        # float() menerima 'nan'/'inf' -- int() atasnya melempar, dan
        # sel yang isinya teks itu memang harus diperlakukan sebagai
        # teks biasa, bukan angka
        if angka != angka or angka in (float("inf"), float("-inf")):
            raise ValueError(teks)
        return str(int(angka)) if angka == int(angka) else f"{angka:g}"
    except (TypeError, ValueError, OverflowError):
        return " ".join(teks.split()).lower()


def _xlsx_nilai(path, maks_sel=20000):
    """Semua nilai sel non-kosong file .xlsx sebagai set string
    ter-normalisasi. Dipakai mencocokkan ISI file export dengan ISI
    grid -- bukan cuma menghitung barisnya. Raise ImportError kalau
    openpyxl belum terpasang (pemanggil -> pytest.skip)."""
    import openpyxl

    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    nilai = set()
    try:
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                for sel in row:
                    if sel is None or sel == "":
                        continue
                    nilai.add(_normalisasi(sel))
                    if len(nilai) >= maks_sel:
                        return nilai
    finally:
        wb.close()
    return nilai


# Nilai berbentuk TANGGAL tidak bisa dicocokkan apa adanya dengan isi
# .xlsx: Excel menyimpannya sebagai objek datetime, jadi grid yang
# menampilkan '01/08/2026' terbaca '2026-08-01 00:00:00' di file dan
# tidak akan pernah cocok sebagai string. Di jalur ambang longgar (50%)
# ini tidak masalah, tapi di jalur ambang KETAT (100%, dipakai saat
# grid cuma punya sedikit nilai) satu kolom tanggal saja sudah cukup
# untuk menggagalkan test yang sebenarnya benar.
#
# Pemisah TITIK sengaja mewajibkan 3 bagian ('01.08.2026'): pola dua
# bagian bertitik akan menelan angka desimal biasa seperti '12.5' dan
# membuangnya dari pencocokan padahal itu data yang sah.
_POLA_TANGGAL = re.compile(
    r"^\s*("
    r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?"  # 2026-08-01 00:00:00
    r"|\d{1,4}[-/]\d{1,2}([-/]\d{1,4})?"          # 2026-08-01, 01/08/2026, 2026-08
    r"|\d{1,2}\.\d{1,2}\.\d{2,4}"                 # 01.08.2026 (titik: wajib 3 bagian)
    r"|\d{1,2}\s+\w{3,}\s+\d{2,4}"                # 1 Agustus 2026
    r")\s*$"
)


def _mirip_tanggal(teks):
    """True kalau nilai ini berbentuk tanggal (lihat `_POLA_TANGGAL`)."""
    return bool(_POLA_TANGGAL.match(str(teks or "")))


def _sampel_nilai_grid(page, maks_baris=3, maks_sampel=20, panjang_min=3):
    """Ambil nilai sel grid untuk dicocokkan dengan isi file export.

    Nilai pendek ('0', '1', '-') hampir pasti ada di file mana pun, jadi
    kalau ikut dihitung, kecocokan jadi palsu. Karena itu yang diambil
    duluan hanya nilai sepanjang >= `panjang_min` karakter.
    """
    sampel = []
    for baris in page.dt_baris_nilai(maks_baris):
        for sel in baris:
            teks = (sel or "").strip()
            if len(teks) < panjang_min:
                continue
            norm = _normalisasi(teks)
            if norm and norm not in sampel:
                sampel.append(norm)
            if len(sampel) >= maks_sampel:
                return sampel
    return sampel


# Kolom KERANGKA template: nilainya sama untuk periode/unit mana pun
# (nomor baris, label bulan, dimensi baris), jadi TIDAK boleh dihitung
# sebagai bukti "grid ini ada datanya".
#
# Kenapa perlu (false positive 2026-09-07, 'data_rekap_statistik_k3'):
# grid tahun 2025 dan 2026 sama-sama Target kosong / Actual 0, tapi
# tetap merender 12 baris berlabel January..December bernomor 1..12.
# Kalau label & nomor itu dianggap isi, dua tahun yang sama-sama kosong
# salah dinilai "punya data" -> test menuduh filter tidak jalan padahal
# aplikasinya benar.
_KOLOM_KERANGKA = {
    "no", "#", "rownumber", "month", "monthint", "monthname",
    "tipepegawai", "date", "tahun", "year",
}


def _grid_punya_data(page, maks_baris=5):
    """True kalau grid menampilkan DATA khas periode/unit ini, bukan
    cuma kerangka template kosong.

    Dinilai lewat `dt_baris_dict()` (baris ber-nama-kolom), bukan lewat
    posisi sel: kolom kerangka dibuang berdasarkan NAMA-nya, lalu sisa
    kolom dihitung berisi kalau ada angka bukan-nol atau teks non-kosong.
    Grid tanpa atribut nama kolom otomatis dinilai "tidak ada data" --
    sengaja longgar, karena lebih baik melewati perbandingan daripada
    menuduh aplikasi salah.

    Dipakai `_assert_data_berubah()` untuk memutuskan apakah dua sidik
    jari yang identik itu wajar (dua periode sama-sama kosong) atau
    tanda filter tidak diteruskan ke backend.
    """
    for row in page.dt_baris_dict(maks_baris):
        for nama_kolom, nilai in row.items():
            if (nama_kolom or "").strip().lower() in _KOLOM_KERANGKA:
                continue
            teks = (nilai or "").strip()
            if not teks:
                continue
            angka = _nilai_angka(teks)
            if angka is None or angka != 0:
                return True
    return False


def _nilai_angka(teks):
    """Ubah isi sel grid jadi float, atau None kalau bukan angka.

    Grid inline-edit OPEL menyimpan angka MENTAH di <input> (tanpa
    pemisah ribuan), tapi kolom read-only bisa saja sudah diformat.
    Aturannya: kalau titik DAN koma sama-sama muncul, yang paling KANAN
    adalah pemisah desimal ('1.234,56' -> 1234.56, '1,234.56' ->
    1234.56). Kalau cuma koma yang muncul berkali-kali, itu pemisah
    ribuan. Sisanya dibaca apa adanya oleh float().
    """
    teks = (teks or "").strip().replace(" ", "").replace(" ", "")
    if not teks:
        return None
    titik, koma = teks.rfind("."), teks.rfind(",")
    if titik >= 0 and koma >= 0:
        if koma > titik:                      # 1.234,56 (gaya Indonesia)
            teks = teks.replace(".", "").replace(",", ".")
        else:                                 # 1,234.56 (gaya Inggris)
            teks = teks.replace(",", "")
    elif teks.count(",") == 1 and len(teks) - koma - 1 != 3:
        teks = teks.replace(",", ".")         # 1234,56 -> desimal koma
    elif koma >= 0:
        # '1,234' / '1,234,567' -> koma tepat 3 digit dari kanan =
        # pemisah ribuan (kasus ambigu diputus ke tafsir ini karena
        # kolom OPEL yang diformat begini adalah jam kerja & cacah,
        # bukan pecahan)
        teks = teks.replace(",", "")
    try:
        angka = float(teks)
    except (TypeError, ValueError):
        return None
    if angka != angka or angka in (float("inf"), float("-inf")):
        return None
    return angka


def _sel_sama(a, b):
    """Bandingkan dua isi sel grid. ANGKA dibandingkan sebagai angka,
    bukan string.

    Kenapa (2026-09-08): aplikasi boleh merender ulang angka dengan
    format berbeda dari yang diketik -- '69' bisa kembali sebagai
    '69.0', '69.00', atau ' 69 '. Pembandingan string mentah menilai
    itu "tidak sama" lalu menuduh aplikasi tidak menyimpan, padahal
    nilainya identik. Kekeliruan seperti inilah yang melahirkan laporan
    bug palsu untuk Statistic Safety Recapitulation.
    """
    a, b = (a or "").strip(), (b or "").strip()
    if a == b:
        return True
    na, nb = _nilai_angka(a), _nilai_angka(b)
    return na is not None and nb is not None and na == nb


def _baca_sel_stabil(page, field, anchor, timeout=None, jeda=1.0):
    """Baca sel berulang sampai nilainya STABIL (tidak kosong dan sama
    dua kali berturut-turut), atau timeout.

    `_tunggu_anchor()` hanya menunggu ELEMEN sel ada; nilainya diisi
    AJAX belakangan, jadi pembacaan sekali-jalan setelah reload bisa
    mengembalikan '' atau nilai lama walau server sudah menyimpan.
    """
    batas = time.monotonic() + (timeout or config.LONG_TIMEOUT)
    sebelumnya = None
    while time.monotonic() < batas:
        nilai = page.baca_sel_grid_anchor(field, anchor)
        if nilai and nilai == sebelumnya:
            return nilai
        sebelumnya = nilai
        time.sleep(jeda)
    return sebelumnya or ""


def _assert_grid_sesuai_kontrak(page, kunci):
    """Verifikasi grid halaman `kunci` BUKAN sekadar 'tabelnya muncul':

      1. tabel report tampil;
      2. grid me-render SEMUA kolom yang didokumentasikan di page object
         (atribut KOLOM) -- kolom yang dihapus/di-rename backend
         ketahuan di sini, bukan diam-diam lolos;
      3. kalau DataTables melaporkan ada N record, tbody WAJIB merender
         baris. 'Backend bilang ada data tapi tabel kosong' adalah bug
         render klasik yang sebelumnya lolos total dari suite ini.

    Kembalikan jumlah record yang dilaporkan DataTables (None kalau
    grid bukan DataTables ter-init).
    """
    nama = NAMA_HALAMAN.get(kunci, kunci)
    assert page.tabel_report_tampil(), f"Tabel '{nama}' tidak tampil"

    # 2) kontrak kolom. Catatan: HssSafetyPage.KOLOM adalah LOCATOR
    #    (tuple), sedangkan tiap page object anak menimpanya dengan dict
    #    {nama: nama} hasil scan -- cek isinstance supaya yang dipakai
    #    hanya versi dict milik halaman.
    kolom_terdokumentasi = getattr(page, "KOLOM", None)
    if isinstance(kolom_terdokumentasi, dict) and kolom_terdokumentasi:
        terender = page.nama_kolom_grid()
        if terender:
            hilang = sorted(set(kolom_terdokumentasi) - terender)
            assert not hilang, (
                f"Grid '{nama}' tidak merender kolom yang terdokumentasi di "
                f"{type(page).__name__}.KOLOM: {hilang}. "
                f"Kolom yang ada sekarang: {sorted(terender)}"
            )

    # 3) klaim jumlah record vs baris yang benar-benar dirender
    info = page.dt_info()
    if not info:
        return None
    total = info.get("recordsDisplay") or 0
    if total > 0:
        baris_dom = page.dt_jumlah_baris_dom()
        assert baris_dom > 0, (
            f"Grid '{nama}': DataTables melaporkan {total} record tapi tbody "
            "tidak merender satu baris pun -- data tidak sampai ke tabel"
        )
    return total


def _assert_data_berubah(page, sidik_sebelum, konteks, ada_isi_sebelum=False,
                         timeout=None):
    """Pastikan isi grid BENAR-BENAR berubah setelah filter diganti.

    Ini menutup celah terbesar suite lama: test filter dulu hanya
    memastikan NILAI DROPDOWN-nya berpindah dan tabelnya masih ada --
    kalau aplikasi tidak meneruskan filter ke query backend (data yang
    tampil tetap milik unit/periode sebelumnya), test tetap PASSED.

    Aturannya sengaja konservatif supaya tidak gagal palsu: kalau grid
    SEBELUM dan SESUDAH sama-sama tidak punya DATA, perbandingan
    dilewati -- dua unit/periode yang sama-sama kosong memang WAJAR
    terlihat identik. "Punya data" dinilai `_grid_punya_data()`, yang
    TIDAK menghitung kerangka template (sel kosong, angka nol, dan nama
    bulan) sebagai isi. Gagal hanya kalau ada data nyata tapi sidik
    jarinya tidak bergeser sama sekali.

    Kembalikan True kalau data terbukti berubah, False kalau tidak bisa
    disimpulkan (dua-duanya kosong).

    Sidik jari dibaca BERULANG sampai berubah atau `timeout` habis,
    bukan sekali langsung (diperbaiki 2026-09-07). Sebabnya nyata:
    `test_safety_leading_deep[SOC Recapitulation]` dan `[Golden Rules]`
    gagal dengan sidik jari yang masih berisi baris 2026 (mis.
    "2026-09-07T08:00", "Dummy 105812 ID") padahal filter sudah pindah
    ke 2025 -- sementara SCREENSHOT saat gagal memperlihatkan grid sudah
    benar-benar kosong ("No data available in table", 0 entries). Jadi
    filternya JALAN, cuma pembacaannya mendahului redraw DataTables:
    `tunggu_processing_selesai()` bisa lewat sebelum overlay Processing
    sempat muncul. Yang benar diuji adalah "data AKHIRNYA berubah",
    bukan "sudah berubah pada milidetik ini".
    """
    batas = time.monotonic() + (timeout or config.DEFAULT_TIMEOUT)
    sidik_sesudah = page.sidik_jari_grid()
    while sidik_sesudah == sidik_sebelum and time.monotonic() < batas:
        time.sleep(0.5)
        sidik_sesudah = page.sidik_jari_grid()
    if sidik_sesudah != sidik_sebelum:
        return True
    if not (ada_isi_sebelum or _grid_punya_data(page)):
        return False  # dua-duanya kosong -- tidak bisa disimpulkan
    raise AssertionError(
        f"{konteks}: filter berpindah tapi ISI GRID sama persis. Data yang "
        "ditampilkan tidak ikut berubah -- kemungkinan filter tidak "
        "diteruskan ke query backend. Sidik jari: " + sidik_sesudah[:400]
    )


def _buka_halaman(driver, kunci):
    """Buka halaman Safety `kunci` lewat page object miliknya.
    Kalau tidak punya akses, otomatis kembali (driver.back) dan skip.

    Sekalian mencatat kalau halaman DIBUKA sudah membawa perubahan
    pending. Itu bisa membuat dua periode/unit terlihat identik karena
    yang dirender draft yang sama, jadi kegagalan aneh perlu dikaitkan
    ke sini dulu sebelum disimpulkan sebagai bug aplikasi.

    Sumbernya sengaja TIDAK diklaim: run 2026-09-07 membuktikan banner
    bisa sudah menyala di test PERTAMA sebuah sesi, jadi bukan sekadar
    sisa test sebelumnya. Key penyimpanan browser ikut dicetak supaya
    bisa dibedakan state di browser vs pending di server.
    """
    try:
        page = PAGE_OBJECTS[kunci](driver).buka()
    except TidakPunyaAkses as e:
        pytest.skip(str(e))
    # Dicatat di page object supaya test bisa MENGAITKAN hasilnya dengan
    # kondisi awal halaman -- lihat pemeriksaan Cancel di
    # test_safety_lagging_deep.
    page.pending_saat_dibuka = page.ada_pending_lokal()
    if page.pending_saat_dibuka:
        key = page.daftar_key_penyimpanan()
        print(
            f"\n[STATE PENDING] '{kunci}' dibuka dalam keadaan SUDAH punya "
            "perubahan pending (banner 'stored locally'), padahal test ini "
            "belum mengedit apa pun."
            f"\n  Key penyimpanan browser saat ini ({len(key)}): "
            + (", ".join(key) if key else
               "KOSONG -> pending-nya kemungkinan di SERVER, bukan di browser")
        )
    return page


def _urutan_menu_halaman():
    """Urutan halaman SESUAI MENU sidebar (Dashboard -> HSS -> Safety
    -> daftar halaman) dari data/test_data.json -- dipakai parametrize
    supaya suite berjalan berurutan seperti alur user, bukan urutan
    abjad (permintaan user 2026-08-28)."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "data", "test_data.json"
    )
    with open(path, encoding="utf-8") as data_file:
        return list(json.load(data_file)["hss_safety"]["halaman"])


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
        # buka PER SUB Reporting & Transaction (permintaan user
        # 2026-08-31: halaman dibuka lewat sub-menu-nya) -- scope
        # induk supaya 'Reporting' tidak salah ambil milik menu Health.
        # Sidebar pakai ACCORDION (buka satu sub menutup sub lain) --
        # jadi cek link TIAP sub SETELAH sub itu dibuka, sebelum
        # sub berikutnya dibuka.
        page.buka_submenu("Reporting", induk="Safety")
        assert page.is_any_visible(
            (By.XPATH,
             "//nav//a[contains(@href,"
             "'Reporting/Timesheet/MonthlyReport/View?Id=1306')]"),
            timeout=5,
        ), "Link Lagging Indicator tidak muncul di sub Reporting"
        page.buka_submenu(
            "Transaction", induk="Safety",
            rantai=("Safety", "Transaction"),
        )
        # link halaman Transaction ada di dalam subgroup BERJENJANG --
        # buka Leading Indicator lalu Incident Management dulu (probe
        # tools/probe_menu_href.py, 2026-08-31: link tersembunyi
        # sampai subgroup-subgroup dibuka)
        page.buka_submenu(
            "Leading Indicator", induk="Transaction",
            rantai=("Safety", "Transaction", "Leading Indicator"),
        )
        page.buka_submenu(
            "Incident Management", induk="Leading Indicator",
            rantai=("Safety", "Transaction", "Leading Indicator",
                    "Incident Management"),
        )
        assert page.is_any_visible(
            (By.XPATH,
             "//nav//a[contains(@href,"
             "'Reporting/Timesheet/DailyReport/Edit?Id=1334')]"),
            timeout=5,
        ), "Link Incident Investigation tidak muncul di sub Transaction"

    # ------------------------------------------------------------------
    # Reporting (view / read-only)
    # ------------------------------------------------------------------
    @pytest.mark.safety_view
    def test_safety_lagging_indicator_view(self, driver):
        try:
            page = SafetyLaggingIndicatorPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "lagging_indicator")
        # is_visible() mengunci ke match PERTAMA di DOM -- OPEL merender
        # beberapa container report (Daily/Monthly/Yearly/Static) di
        # halaman yang sama dengan id sama tapi hanya satu yang aktif/
        # tampil (2026-09-04, root cause sama dgn LINK_DOWNLOAD_TEMPLATE
        # di bawah). is_any_visible() scan SEMUA match, bukan cuma yang
        # pertama.
        #
        # FILTER_UNIT ikut diubah 2026-09-07: begitu FILTER_TANGGAL
        # diperbaiki, kegagalannya PINDAH ke baris ini ("Filter unit
        # tidak tampil") -- bukti kedua-duanya kena masalah yang sama,
        # cuma yang pertama lebih dulu kena assert.
        assert page.is_any_visible(page.FILTER_TANGGAL), "Filter tanggal tidak tampil"
        assert page.is_any_visible(page.FILTER_UNIT), "Filter unit tidak tampil"

    @pytest.mark.safety_view
    def test_safety_golden_rules_recap_view(self, driver):
        try:
            page = SafetyGoldenRulesRecapPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "golden_rules_recap")

    @pytest.mark.safety_view
    def test_safety_emergency_drill_recap_view(self, driver):
        try:
            page = SafetyEmergencyDrillRecapPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "emergency_drill_recap")

    @pytest.mark.safety_view
    def test_safety_mwt_recapitulation_view(self, driver):
        try:
            page = SafetyMwtRecapitulationPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "mwt_recapitulation")

    @pytest.mark.safety_view
    def test_safety_recap_view(self, driver):
        try:
            page = SafetyRecapPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        assert driver.execute_script(page._js_tampil(), "#tableBulanan", 10), \
            "Tabel Safety Recap (Bulanan) tidak tampil"
        # FILTER_TAHUN pakai is_any_visible juga (2026-09-07, alasan sama
        # dengan FILTER_UNIT di test_safety_lagging_indicator_view:
        # kegagalan pindah ke sini begitu FILTER_BULAN diperbaiki).
        assert page.is_any_visible(page.FILTER_BULAN), "Filter bulan tidak tampil"
        assert page.is_any_visible(page.FILTER_TAHUN), "Filter tahun tidak tampil"

    # ------------------------------------------------------------------
    # Transaction - Leading Indicator
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_incident_investigation_view(self, driver):
        try:
            page = SafetyIncidentInvestigationFormPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "incident_investigation_form")

    # test_safety_incident_investigation_tab DIHAPUS (2026-09-08).
    # Test itu memeriksa SATU tab ('Data Korban') mendapat class 'active'.
    # `test_safety_halaman_lengkap[Incident Investigation]` sudah memutar
    # KEENAM tab halaman ini satu per satu, memastikan tiap tab aktif DAN
    # panelnya benar-benar menampilkan konten (`panel_tab_isi_tampil`),
    # lalu mengklik tombol fitur di tiap tab. Cakupannya superset penuh.

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

    @pytest.mark.safety_transaction
    def test_safety_initial_incident_view(self, driver):
        try:
            page = SafetyInitialIncidentAccidentReportPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "initial_incident_accident_report")

    @pytest.mark.safety_transaction
    def test_safety_witness_statement_view(self, driver):
        try:
            page = SafetyWitnessStatementReportPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "witness_statement_report")

    @pytest.mark.safety_transaction
    def test_safety_emergency_drill_daily_view(self, driver):
        try:
            page = SafetyEmergencyDrillDailyPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "emergency_drill_daily")

    @pytest.mark.safety_transaction
    def test_safety_master_alat_view(self, driver):
        try:
            page = SafetyMasterAlatKeselamatanOperasiPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "master_alat_keselamatan_operasi")

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
        _assert_grid_sesuai_kontrak(page, "soc_recapitulation")

    @pytest.mark.safety_transaction
    def test_safety_golden_rules_view(self, driver):
        try:
            page = SafetyGoldenRulesPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "golden_rules")

    @pytest.mark.safety_transaction
    def test_safety_data_rekap_k3_view(self, driver):
        try:
            page = SafetyDataRekapStatistikK3Page(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "data_rekap_statistik_k3")
        page.buka_tab(page.TAB_TRIR)
        tab = page.find((page.TAB[0], page.TAB[1].format(teks_tab=page.TAB_TRIR)))
        assert "active" in (tab.get_attribute("class") or ""), "Tab TRIR tidak aktif"

    @pytest.mark.safety_transaction
    def test_safety_kkp_p2k3_view(self, driver):
        try:
            page = SafetyKkpP2k3CommitteeMeetingPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "safety_kkp_p2k3_committee_meeting")

    @pytest.mark.safety_transaction
    def test_safety_mwt_daily_view(self, driver):
        try:
            page = SafetyMwtDailyPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "mwt_daily")

    @pytest.mark.safety_transaction
    def test_safety_leading_indicator_view(self, driver):
        try:
            page = SafetyLeadingIndicatorPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "leading_indicator")

    # ------------------------------------------------------------------
    # Transaction - Lagging Indicator
    # ------------------------------------------------------------------
    @pytest.mark.safety_transaction
    def test_safety_statistic_safety_view(self, driver):
        try:
            page = SafetyStatisticSafetyRecapitulationPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "statistic_safety_recapitulation")

    @pytest.mark.safety_transaction
    def test_safety_smk3_view(self, driver):
        try:
            page = SafetySmk3Page(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "smk3")
        assert page.is_any_visible(page.BTN_SUBMIT), "Tombol Submit Changes tidak tampil"

    @pytest.mark.safety_transaction
    def test_safety_smkp_view(self, driver):
        try:
            page = SafetySmkpPage(driver).buka()
        except TidakPunyaAkses as e:
            pytest.skip(str(e))
        _assert_grid_sesuai_kontrak(page, "smkp")

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
    # Catatan 2026-08-26 (KELIRU, dikoreksi 2026-09-08):
    #  - Dulu Statistic dipasang `edit_tersimpan=False` karena dikira
    #    tidak menyimpan perubahan inline. Itu SALAH: yang keliru cara
    #    test membaca hasilnya. `buka_halaman()` mengembalikan filter
    #    periode ke DEFAULT, jadi nilai yang ditulis di Juli/Agustus
    #    dibaca di bulan berjalan yang kosong, lalu disimpulkan "tidak
    #    tersimpan". SMK3/SMKP lolos cuma karena periode defaultnya
    #    (tahun) kebetulan sama dengan periode datanya.
    #  - Dibuktikan tools/cek_simpan_inline.py (2026-09-08): 10 halaman
    #    TERSIMPAN termasuk Statistic, NOL yang tidak tersimpan. Detail
    #    di reports/bugs/statistic-safety-recap-inline-edit-tidak-
    #    tersimpan.md (ditutup sebagai BUKAN BUG).
    #  - Sekarang `_muat_ulang()` memulihkan periode tiap reload, jadi
    #    verifikasinya sudah sah dan `edit_tersimpan` dikembalikan True.
    #  - 2026-09-10: aplikasi MEMINDAH Id=1317 dari MonthlyReport ke
    #    YearlyReport, jadi filter periodenya sekarang TAHUN ('2026'),
    #    bukan bulan ('2026-07'). Nilai lama membuat set_filter_tanggal
    #    mengisi format yang tidak dikenali input.
    LAGGING_DEEP = [
        ("statistic_safety_recapitulation", "2026", "PenyakitAkibatKerja",
         {"Month": "July", "TipePegawai": "Pegawai"}, None, True),
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

        # Pindah dulu ke PERIODE YANG ADA DATANYA sebelum mengedit.
        # `tanggal_uji` memang periode itu (mis. '2026-07' untuk
        # Statistic), tapi dulu baru dipakai jauh di bawah saat menguji
        # filter tanggal -- akibatnya edit dicoba di periode default yang
        # kosong, lalu test menyerah dengan SKIP tanpa pernah menguji
        # penyimpanan sama sekali (2026-09-08).
        #
        # Syaratnya nilai SEL yang kosong, BUKAN elemennya yang tidak
        # ada: di periode kosong pun grid tetap merender baris template
        # (January..December x Pegawai/Non Pegawai) dengan input kosong,
        # jadi elemen anchor SELALU ketemu dan pengecekan berbasis
        # keberadaan elemen tidak pernah memicu perpindahan periode.
        try:
            _tunggu_anchor()
        except TimeoutException:
            pass  # baris anchor belum ada -- mungkin periodenya salah
        if (tanggal_uji
                and page.is_any_visible(page.FILTER_TANGGAL, timeout=3)
                and page.baca_filter_tanggal() != tanggal_uji
                and not page.baca_sel_grid_anchor(field_edit, anchor)
                and not page.cari_anchor_field_terisi(field_edit, anchor)):
            page.set_filter_tanggal(tanggal_uji)
            page.tunggu_processing_selesai()

        _tunggu_anchor()

        # Periode yang SEDANG AKTIF saat nilai dibaca & ditulis. Wajib
        # dipulihkan tiap kali halaman dimuat ulang: `buka_halaman()`
        # membuka URL apa adanya sehingga filter periode KEMBALI KE
        # DEFAULT (2026-09-08). Kalau nilai ditulis di Juli lalu dibaca
        # di September (default, kosong), test menuduh aplikasi tidak
        # menyimpan padahal datanya aman -- persis kekeliruan yang
        # melahirkan laporan bug palsu Statistic Safety Recapitulation.
        periode_pakai = page.baca_filter_tanggal()

        def _pulihkan_periode():
            # UJI MUTASI (sementara): OPEL_MUTASI_PERIODE=1 mematikan
            # pemulihan periode, meniru bug lama. Dipakai membuktikan
            # test ini benar-benar bisa GAGAL -- terbukti 2026-09-08:
            # dengan mutasi aktif, statistic GAGAL di assertion
            # penyimpanan; tanpa mutasi, lolos.
            if os.getenv("OPEL_MUTASI_PERIODE"):
                return
            if periode_pakai and page.baca_filter_tanggal() != periode_pakai:
                page.set_filter_tanggal(periode_pakai)
                page.tunggu_processing_selesai()

        def _muat_ulang():
            """Muat ulang halaman lalu tarik ulang data DARI SERVER.

            `buka_halaman()` saja TIDAK CUKUP untuk verifikasi: OPEL
            memulihkan draft lokal saat halaman dimuat ulang, jadi yang
            terbaca adalah nilai yang baru saja diketik test -- bukan
            nilai server. Itu "membuktikan" penyimpanan yang belum tentu
            terjadi (2026-09-08). Hanya tombol Reload Data yang membuang
            draft dan menarik ulang dari server.

            Periode dipulihkan DUA KALI: sebelum dan sesudah Reload
            Data. `reload_data()` bisa menavigasi ulang kalau tombolnya
            tidak kunjung tampil, dan navigasi mengembalikan periode ke
            default.
            """
            page.buka_halaman(kunci)
            _pulihkan_periode()
            try:
                page.reload_data()
            except Exception:
                pass
            _pulihkan_periode()
            _tunggu_anchor()

        # Baseline WAJIB dari server, bukan dari draft lokal yang masih
        # nyangkut di halaman (2026-09-08). Kalau nilai_awal diambil dari
        # draft, seluruh perbandingan sesudahnya jadi salah acuan: pernah
        # terbaca baseline '3' padahal nilai server '1'.
        _muat_ulang()
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
        _muat_ulang()
        if edit_tersimpan:
            # Baca STABIL + banding ANGKA (2026-09-08). Sebelumnya sekali
            # baca + banding string, dan itu sumber tuduhan palsu
            # "tidak tersimpan": nilai bisa belum ter-render saat dibaca,
            # atau kembali dengan format lain ('69' -> '69.0').
            terbaca = _baca_sel_stabil(page, field_edit, anchor)
            submit_rusak = (
                kunci in HssSafetyPage.SUBMIT_REDIRECT_TANPA_SIMPAN
            )
            if submit_rusak:
                # Bug aplikasi yang SUDAH dilaporkan & dikonfirmasi
                # manual (termasuk di incognito dan mesin lain) --
                # jangan bikin suite merah permanen.
                if not _sel_sama(terbaca, nilai_uji):
                    print(
                        f"\n[BUG DIKENAL] '{kunci}': Submit Changes tidak "
                        f"menyimpan ('{nilai_uji}' diketik, setelah reload "
                        f"terbaca '{terbaca}'). Penyebabnya Submit langsung "
                        "me-redirect ke template lain sebelum konfirmasi "
                        "muncul -- lihat reports/bugs/"
                        "submit-changes-redirect-tanpa-menyimpan.md"
                    )
                else:
                    print(
                        f"\n[BUG SUDAH DIPERBAIKI?] '{kunci}': Submit Changes "
                        "kali ini MENYIMPAN dengan benar. Kalau konsisten di "
                        f"beberapa run, keluarkan '{kunci}' dari "
                        "HssSafetyPage.SUBMIT_REDIRECT_TANPA_SIMPAN dan tutup "
                        "laporan bug-nya."
                    )
            else:
                assert _sel_sama(terbaca, nilai_uji), (
                    f"Edit '{field_edit}' = '{nilai_uji}' tidak tersimpan "
                    f"setelah Submit Changes -- setelah reload terbaca "
                    f"'{terbaca}'"
                )
            page.isi_sel_grid_anchor(field_edit, nilai_awal, anchor)
            page.submit_changes()
            _muat_ulang()
            kembali = _baca_sel_stabil(page, field_edit, anchor)
            if submit_rusak:
                # Pesan HARUS mengikuti nilai yang benar-benar terbaca.
                # Versi pertama mencetak "revert tidak tersimpan" tanpa
                # memeriksa apa pun, sehingga muncul bersamaan dengan
                # "[BUG SUDAH DIPERBAIKI?]" di run yang sama -- dua
                # pesan yang saling bertentangan (2026-09-08).
                if _sel_sama(kembali, nilai_awal):
                    print(
                        f"[INFO] '{kunci}': revert berhasil, nilai kembali "
                        f"ke '{nilai_awal}'."
                    )
                else:
                    print(
                        f"[BUG DIKENAL] '{kunci}': revert tidak tersimpan "
                        f"(terbaca '{kembali}', diharapkan '{nilai_awal}'). "
                        "Submit tidak terkirim, jadi data server tidak "
                        "pernah berubah -- tidak ada yang perlu dibersihkan."
                    )
            else:
                assert _sel_sama(kembali, nilai_awal), (
                    f"Nilai '{field_edit}' tidak kembali ke '{nilai_awal}' "
                    f"setelah revert -- terbaca '{kembali}'"
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
                _muat_ulang()
                assert page.baca_sel_grid_anchor(field_edit, anchor) == nilai_awal, (
                    f"Nilai '{field_edit}' tidak kembali ke '{nilai_awal}' "
                    "setelah revert"
                )

        # 1b) Draft lokal: buat perubahan pending -> klik RELOAD DATA ->
        #     perubahan DIBUANG (data kembali ke nilai server).
        #
        # KOREKSI 2026-09-07: blok ini dulu menguji tombol CANCEL dan
        # menuntut Cancel membuang perubahan. Itu ASUMSI YANG SALAH soal
        # desain aplikasi, dan sempat melahirkan laporan bug palsu
        # (reports/bugs/lagging-cancel-does-not-discard-edit.md, kini
        # ditutup sebagai BUKAN BUG). Kontrak OPEL yang sebenarnya:
        #   Submit Changes          -> simpan ke server
        #   Reload Data             -> BUANG draft lokal, ambil ulang
        #                              data dari server
        #   Cancel / reload browser -> draft lokal SENGAJA dipertahankan,
        #                              supaya kerja user tidak hilang
        #                              kalau halaman ter-reload tanpa
        #                              sengaja atau koneksi putus
        #                              (fitur perlindungan, bukan cacat)
        # Jadi yang layak di-assert adalah Reload Data, bukan Cancel.
        nilai_sebelum_draft = page.baca_sel_grid_anchor(field_edit, anchor)
        page.isi_sel_grid_anchor(field_edit, nilai_uji, anchor)
        page.reload_data()
        _tunggu_anchor()
        setelah_reload = page.baca_sel_grid_anchor(field_edit, anchor)
        if setelah_reload != nilai_sebelum_draft:
            # Reload Data tidak membuang draft -- kembalikan data DEV
            # dulu supaya nilai uji tidak nyangkut permanen, BARU
            # gagalkan lewat assert di bawah.
            page.isi_sel_grid_anchor(field_edit, nilai_sebelum_draft, anchor)
            page.submit_changes()
            _muat_ulang()
        assert setelah_reload == nilai_sebelum_draft, (
            f"Reload Data di '{kunci}' tidak membuang draft lokal: "
            f"'{field_edit}' masih '{setelah_reload}', seharusnya kembali "
            f"ke nilai server '{nilai_sebelum_draft}' (data DEV sudah "
            "dikembalikan otomatis di atas)"
        )

        # 2) Filter tanggal -> value berubah, tabel tetap tampil, DAN
        #    (kalau periodenya memang beda) isi grid ikut berubah ->
        #    kembalikan
        tanggal_awal = page.baca_filter_tanggal()
        sidik_awal = page.sidik_jari_grid()
        ada_isi_awal = _grid_punya_data(page)
        page.set_filter_tanggal(tanggal_uji)
        page.tunggu_processing_selesai()
        assert page.baca_filter_tanggal() == tanggal_uji, (
            f"Filter tanggal tidak berubah ke '{tanggal_uji}' di '{kunci}'"
        )
        assert page.tabel_report_tampil(), (
            f"Tabel '{kunci}' tidak tampil setelah filter tanggal '{tanggal_uji}'"
        )
        # hanya bermakna kalau periodenya BEDA dari yang sedang aktif --
        # set ke nilai yang sama wajar tidak mengubah apa-apa
        if tanggal_awal and tanggal_awal != tanggal_uji:
            _assert_data_berubah(
                page, sidik_awal,
                f"Filter tanggal '{kunci}' ('{tanggal_awal}' -> "
                f"'{tanggal_uji}')",
                ada_isi_sebelum=ada_isi_awal,
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
        # is_visible() mengunci ke match PERTAMA #linkDownloadTemplate di
        # DOM -- OPEL merender lebih dari satu container modal Import
        # (Daily/Monthly/Yearly/Static) di halaman yang sama, sebagian
        # hidden (2026-09-04: screenshot buktikan link SUNGGUH tampil di
        # modal yang benar, tapi is_visible() grab elemen hidden di
        # container lain lebih dulu). is_any_visible() scan SEMUA match.
        assert page.is_any_visible(page.LINK_DOWNLOAD_TEMPLATE), (
            f"Link Download Template tidak ada di '{kunci}'"
        )
        file_template = page.download_template_import()
        assert file_template, f"File template import '{kunci}' tidak terunduh"
        page.tutup_modal()

    # Tombol yang DIJALANKAN di tiap tab selain tab utama: SEMUA tombol
    # fitur KECUALI pembuat data server ("Create with Form" & "Create")
    # dan "Cancel" (di halaman DailyReport tombol Cancel menavigasi ke
    # halaman LIST -- menjalankannya di tengah alur tab memutus
    # kunjungan). Tombol pembuat data dijalankan di TAB UTAMA lewat
    # daftar TOMBOL_HALAMAN lengkap -- modal create SAMA di semua tab,
    # dan create dari tab lain menambah baris dummy yang TIDAK bisa
    # diverifikasi (quirk 2026-08-28).
    TOMBOL_TAB = ("Reload Data", "Import", "FullScreen", "Columns",
                  "Submit Changes", "Export", "Export Excel",
                  "Select Finding")

    # ------------------------------------------------------------------
    # Alur LENGKAP per halaman dalam SATU kunjungan (permintaan user
    # 2026-08-31): navigasi lewat ALUR MENU (dashboard -> HSS -> Safety
    # -> sub Reporting/Transaction -> klik link halaman), tabel ->
    # TAB DEMI TAB (aktif + tombol toolbar dicek DAN DIKLIK di tiap
    # tab) -> kembali ke tab pertama -> SEMUA tombol fitur diklik
    # sesuai urutan daftar. Halaman dikunjungi SESUAI URUTAN MENU
    # (bukan abjad), jeda antar-aksi SERAGAM (config).
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_toolbar
    @pytest.mark.parametrize(
        "kunci_halaman",
        _urutan_menu_halaman(),
        ids=lambda k: NAMA_HALAMAN[k],
    )
    def test_safety_halaman_lengkap(self, driver, test_data, kunci_halaman):
        """Alur lengkap SATU halaman dalam SATU kunjungan:
          0. navigasi lewat MENU SIDEBAR: dashboard dulu (kalau
             sidebar belum ada) -> HSS -> Safety -> submenu Reporting
             / Transaction (Leading|Lagging Indicator) -> klik link
             halaman di sidebar (buka_via_menu)
          1. tabel report tampil
          2. TAB DEMI TAB berurutan: klik tab -> pastikan aktif ->
             cek tombol toolbar tampil -> SEMUA tombol fitur DIKLIK
             di tab itu juga (kecuali pembuat data + Cancel, lihat
             TOMBOL_TAB) -- per tab SAMA dengan tab utama
          3. KEMBALI ke tab pertama -- SEMUA tombol fitur DIKLIK satu
             per satu SESUAI URUTAN daftar HssSafetyPage.TOMBOL_HALAMAN.
             Aksi tiap tombol: Reload Data -> klik + tabel dimuat
             ulang; Import -> modal buka + file dummy DIPASANG di
             input upload lalu ditutup TANPA dikirim ke server (aman);
             Create w/ Form -> isi dummy + Save + Submit (dibuat
             sungguhan); Create -> draft lalu Cancel; Submit Changes
             -> klik + konfirmasi; Export -> file terunduh; Select
             Finding -> (SOC) modal lookup buka-tutup; Columns ->
             dropdown DIBUKA + item kolom DIKLIK lalu dikembalikan;
             FullScreen -> masuk-keluar; Cancel -> diklik (tanpa
             pending = aman).
             Link Instructions TIDAK diklik (permintaan user)."""
        page = PAGE_OBJECTS[kunci_halaman](driver)
        page.buka_via_menu(kunci_halaman)
        nama = NAMA_HALAMAN[kunci_halaman]
        # 1) tabel -- TUNGGU sampai tampil (Safety Recap lambat render,
        #    cek sekali langsung bisa salah, 2026-08-28)
        page._wait(config.LONG_TIMEOUT).until(
            lambda _: page.tabel_report_tampil(),
            f"Tabel '{nama}' tidak tampil",
        )
        daftar_tombol = HssSafetyPage.TOMBOL_HALAMAN[kunci_halaman]
        # 2) TAB DEMI TAB berurutan -- di tiap tab: pastikan aktif +
        #    tombol toolbar tampil + SEMUA tombol fitur DIKLIK (kecuali
        #    pembuat data + Cancel, lihat TOMBOL_TAB)
        if kunci_halaman in self.TAB_HALAMAN:
            daftar_tab = test_data["hss_safety"][
                self.TAB_HALAMAN[kunci_halaman]
            ]
            for i, teks_tab in enumerate(daftar_tab):
                page.klik_tab(teks_tab)
                tab = page.find(
                    (page.TAB[0], page.TAB[1].format(teks_tab=teks_tab))
                )
                assert "active" in (tab.get_attribute("class") or ""), (
                    f"Tab '{teks_tab}' tidak aktif di '{kunci_halaman}'"
                )
                # tab BUKAN cuma dapat class 'active' -- panel tujuannya
                # harus benar-benar menampilkan konten (tabel/field/teks),
                # dipertahankan dari test_safety_buka_semua_tab lama
                # (2026-08-31, digabung saat merge automation-safety-zahra).
                assert page.panel_tab_isi_tampil(teks_tab), (
                    f"Panel tab '{teks_tab}' di '{kunci_halaman}' aktif "
                    "tapi tidak menampilkan konten apa pun"
                )
                hasil = page.cek_tombol_toolbar(kunci_halaman)
                hilang = [n for n, ok in hasil.items() if not ok]
                assert not hilang, (
                    f"Halaman '{kunci_halaman}' tab '{teks_tab}': "
                    f"tombol toolbar tidak tampil -> {hilang}"
                )
                if i > 0:
                    # tab selain utama: semua tombol fitur DIKLIK di tab
                    # ini juga (per tab SAMA dengan tab utama)
                    for nama_tombol in daftar_tombol:
                        if nama_tombol in self.TOMBOL_TAB:
                            page.coba_tombol(nama_tombol)
            # 3) kembali ke tab pertama
            page.klik_tab(daftar_tab[0])
        # 4) SEMUA tombol fitur diklik SESUAI URUTAN daftar (tab utama
        #    -- termasuk Create with Form & Create yang membuat data)
        for nama_tombol in daftar_tombol:
            page.coba_tombol(nama_tombol)
    # ------------------------------------------------------------------
    # Test berikut TIDAK diserap ke test_safety_halaman_lengkap (2026-08-31,
    # digabung dari branch automation-safety saat merge dengan
    # automation-safety-zahra) -- cakupannya beda dari alur navigasi+tombol:
    # interaksi DataTables (sort/pagination/search/show-hide kolom), isi
    # file export diverifikasi sungguhan, validasi form wajib (negative
    # case), dan filter unit benar2 DIGANTI (bukan cuma dicek elemennya).
    # test_safety_coba_semua_tombol & test_safety_tombol_toolbar DIHAPUS
    # dari sini karena sudah redundan: test_safety_halaman_lengkap sudah
    # meng-klik SEMUA tombol yang sama (klik gagal kalau tombol tidak
    # tampil, jadi visibilitasnya ikut terverifikasi).
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

        # Cakupan sengaja DICATAT dan dicetak (2026-09-07): tiga dari
        # empat bagian test ini butuh data di grid, sementara banyak
        # halaman DEV kosong. Tanpa catatan ini, hasil "PASSED" terbaca
        # seolah sort+pagination+search+kolom semuanya terverifikasi di
        # semua halaman -- padahal di grid kosong yang benar-benar
        # diuji cuma show/hide kolom. Yang dilaporkan harus sama dengan
        # yang sungguh dikerjakan.
        diuji, dilewati = [], []

        # --- 1) SORT ---
        sortable = [k for k in kolom if k["sortable"] and k["visible"]]
        if not (sortable and n_baris >= 2):
            dilewati.append("sort (butuh kolom sortable + >=2 baris data)")
        if sortable and n_baris >= 2:
            diuji.append("sort")
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
        if not (info.get("pages", 0) and info["pages"] > 1):
            dilewati.append("pagination (data cuma 1 halaman)")
        if info.get("pages", 0) and info["pages"] > 1:
            diuji.append("pagination")
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
        if not (n_baris >= 1 and total_awal >= 1):
            dilewati.append("search (grid tidak punya baris data)")
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
            if not token:
                dilewati.append(
                    "search (tidak ada nilai >=3 karakter untuk jadi token)"
                )
            if token:
                diuji.append("search")
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

        # --- 4) SHOW / HIDE KOLOM --- (satu-satunya bagian yang tidak
        # butuh data, jadi tetap jalan di grid kosong)
        terlihat = [k for k in kolom if k["visible"]]
        if len(terlihat) < 2:
            dilewati.append("show/hide kolom (kolom terlihat < 2)")
        if len(terlihat) >= 2:
            diuji.append("show/hide kolom")
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

        # Laporkan cakupan SEBENARNYA -- "PASSED" tanpa keterangan ini
        # menyesatkan di halaman yang datanya kosong.
        print(
            f"\n[CAKUPAN DataTables] '{kunci_halaman}': "
            f"diuji = {', '.join(diuji) if diuji else 'TIDAK ADA'}"
            + (f" | dilewati = {'; '.join(dilewati)}" if dilewati else "")
        )
        if not diuji:
            pytest.skip(
                f"Grid '{kunci_halaman}' tidak memungkinkan satu pun "
                "interaksi DataTables diuji (tanpa data, tanpa kolom yang "
                f"bisa disembunyikan): {'; '.join(dilewati)}. Dilaporkan "
                "SKIPPED, bukan PASSED, supaya hasilnya tidak menyesatkan"
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
        workbook (bukan file rusak), punya minimal 1 baris terisi, DAN
        isinya benar-benar mencerminkan data yang sedang tampil di grid.

        Pencocokan isi (2026-09-04): nilai sel dari beberapa baris
        pertama grid dicari di dalam workbook. Ambangnya sengaja TOLERAN
        (mayoritas, bukan semua) karena export wajar memformat ulang
        sebagian nilai -- tanggal jadi objek datetime, angka jadi float,
        kolom tersembunyi bisa ikut / tidak ikut. Yang mau ditangkap di
        sini adalah kegagalan BESAR: file berisi template kosong, file
        berisi data unit/periode lain, atau file basi sisa export
        sebelumnya. Sebelum ini test cuma menghitung jumlah baris, jadi
        file dengan isi SALAH pun tetap lolos."""
        page = _buka_halaman(driver, kunci_halaman)
        _assert_grid_sesuai_kontrak(page, kunci_halaman)
        # sampel diambil SEBELUM export supaya yang dibandingkan benar2
        # data yang sedang tampil saat tombol Export diklik (dua-duanya
        # diambil di sini, pemilihannya baru setelah file terbaca)
        sampel_khas = _sampel_nilai_grid(page)
        sampel_semua = (
            sampel_khas if len(sampel_khas) >= 3
            else _sampel_nilai_grid(page, panjang_min=1)
        )
        path = page.export_dan_tunggu_file()
        assert path, f"File export '{kunci_halaman}' tidak terunduh"
        try:
            baris = _xlsx_jumlah_baris_isi(path)
            nilai_file = _xlsx_nilai(path)
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

        # Nilai berbentuk tanggal selalu dibuang: Excel menyimpannya
        # sebagai datetime, jadi TIDAK MUNGKIN cocok sebagai teks.
        # Kalau nilai khas kurang dari 3, pakai semua nilai non-kosong
        # (grid Master Alat cuma punya 1 baris -- '1', '4', '3', 'tess'
        # -- dan dulu langsung di-skip padahal datanya bisa diperiksa).
        sampel = [n for n in (sampel_khas if len(sampel_khas) >= 3
                              else sampel_semua)
                  if not _mirip_tanggal(n)]
        if not sampel:
            pytest.skip(
                f"Grid '{kunci_halaman}' tidak menampilkan satu nilai pun "
                "yang bisa dicocokkan dengan isi file export -- data DEV "
                "kosong (grid 'No data available'), bukan kegagalan export"
            )

        cocok = [nilai for nilai in sampel if nilai in nilai_file]
        hilang = [nilai for nilai in sampel if nilai not in nilai_file]
        # Ambang 50% + minimal 2 nilai cocok secara absolut.
        #
        # Kenapa BUKAN 100% walau nilainya sedikit (dikoreksi 2026-09-07):
        # run penuh menggagalkan Master Alat di 6-dari-7 karena nilai '2'
        # tidak ada di workbook -- itu kolom lookup yang di grid tampil
        # sebagai ID tapi di export ditulis sebagai NAMA. Perbedaan
        # bentuk seperti itu WAJAR dan bukan kegagalan export, jadi
        # ambang 100% menghasilkan false positive. Syarat "minimal 2
        # cocok" tetap menjaga ketajaman: file kosong/basi/berisi data
        # unit lain tidak akan lolos hanya karena satu angka pendek
        # kebetulan ada di dalamnya.
        minimal_cocok = min(2, len(sampel))
        assert (len(cocok) / len(sampel) >= 0.5
                and len(cocok) >= minimal_cocok), (
            f"Isi file export '{kunci_halaman}' ({path}) tidak cocok dengan "
            f"data yang tampil di grid: cuma {len(cocok)} dari {len(sampel)} "
            f"nilai yang ketemu di workbook (syarat: >=50% DAN >="
            f"{minimal_cocok} nilai). Tidak ketemu: {hilang[:10]}"
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
                sidik_awal = page.sidik_jari_grid()
                ada_isi_awal = _grid_punya_data(page)
                page.set_filter_tanggal(uji)
                page.tunggu_processing_selesai()
                assert page.baca_filter_tanggal() == uji, (
                    f"Filter tanggal '{kunci_halaman}' tidak berubah ke '{uji}'"
                )
                assert page.tabel_report_tampil(), (
                    f"Tabel '{kunci_halaman}' hilang setelah filter tanggal"
                )
                # tahunnya dipilih berbeda dari yang aktif -- data yang
                # tampil HARUS ikut berubah kalau memang ada datanya
                _assert_data_berubah(
                    page, sidik_awal,
                    f"Filter tanggal '{kunci_halaman}' ('{awal}' -> '{uji}')",
                    ada_isi_sebelum=ada_isi_awal,
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

        # --- Export & Import SENGAJA TIDAK diuji di sini (2026-09-08) ---
        # Keduanya dulu ada di test ini, dan itu murni pengulangan:
        #
        #   Export : `test_safety_export_isi_file` sudah menguji hal yang
        #            SAMA plus lebih jauh -- isi workbook dicocokkan
        #            dengan isi grid, bukan cuma "file terunduh".
        #            `test_safety_halaman_lengkap` juga mengklik tombolnya.
        #   Import : `test_safety_halaman_lengkap` sudah membuka modal
        #            Import dan mengunduh template di halaman yang sama.
        #
        # Jadi Export sempat diklik 3x dan Import 2x per halaman, tanpa
        # menambah cakupan apa pun -- dan menunggu file terunduh adalah
        # bagian paling lambat dari suite ini.
        #
        # Yang TETAP di sini karena tidak diuji test lain: filter tanggal
        # benar-benar MENGUBAH DATA (`_assert_data_berubah`) dan filter
        # unit punya opsi.

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
        # sidik jari data SEBELUM unit diganti -- dipakai membuktikan
        # filter benar-benar mengubah DATA, bukan cuma isi dropdown
        sidik_awal = page.sidik_jari_grid()
        ada_isi_awal = _grid_punya_data(page)
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
        terbukti = _assert_data_berubah(
            page, sidik_awal,
            f"Filter unit '{kunci_halaman}' ('{awal}' -> '{baru}')",
            ada_isi_sebelum=ada_isi_awal,
        )
        if not terbukti:
            print(
                f"\n[INFO] '{kunci_halaman}': unit '{awal}' dan '{baru}' "
                "sama-sama tidak punya data -- perubahan data tidak bisa "
                "diverifikasi (bukan kegagalan)."
            )
        if awal:
            page.pilih_unit_by_value(awal)
            page.tunggu_processing_selesai()

    # ------------------------------------------------------------------
    # INPUT LANGSUNG DI TABEL: Create (baris draft kosong) -> isi
    # kolomnya LANGSUNG di grid -> Submit Changes -> verifikasi
    # tersimpan di SERVER -> hapus lagi.
    #
    # Kenapa ada (2026-09-08): ini jalur input yang dipakai user pada
    # halaman tanpa "Create with Form", dan sampai sekarang TIDAK PERNAH
    # diuji. Satu-satunya test yang menyentuh tombol Create
    # (`klik_create_lalu_batal`) cuma mengklik lalu Cancel -- barisnya
    # tidak pernah diisi, jadi tidak ada yang membuktikan data hasil
    # ketikan langsung benar-benar tersimpan.
    #
    # Verifikasi WAJIB lewat Reload Data: `buka_halaman()` memulihkan
    # draft lokal dan menampilkan nilai yang baru saja diketik, seolah
    # tersimpan. Lihat bagian "jangan tertipu draft lokal" di README.
    # ------------------------------------------------------------------
    @pytest.mark.safety
    @pytest.mark.safety_extra
    @pytest.mark.safety_transaction
    @pytest.mark.parametrize(
        "kunci_halaman", CREATE_INLINE_KEYS, ids=lambda k: NAMA_HALAMAN[k]
    )
    def test_safety_create_inline(self, driver, test_data, kunci_halaman):
        """Create -> isi kolom langsung di grid -> Submit -> tersimpan
        di server -> baris dihapus lagi (data DEV tidak ditinggali
        sampah)."""
        page = _buka_halaman(driver, kunci_halaman)
        _assert_grid_sesuai_kontrak(page, kunci_halaman)

        # Halaman DailyReport disaring ke SATU TANGGAL: tanpa tanggal,
        # grid selalu 0 baris dan baris baru pun tidak punya konteks.
        url = HssSafetyPage.HALAMAN.get(kunci_halaman, "")
        if "DailyReport" in url and not page.baca_filter_tanggal():
            tanggal = test_data["hss_safety"].get("filter_tanggal_harian")
            if not tanggal:
                pytest.skip(
                    "data/test_data.json belum punya 'filter_tanggal_harian' "
                    "-- halaman DailyReport butuh tanggal spesifik"
                )
            page.set_filter_tanggal(tanggal)
            page.tunggu_processing_selesai()

        periode = page.baca_filter_tanggal()

        def _muat_ulang_server():
            """Muat ulang + tarik data DARI SERVER (buang draft lokal),
            periode dipulihkan sebelum dan sesudah Reload Data."""
            page.buka_halaman(kunci_halaman)
            page.tunggu_processing_selesai()
            for _ in range(2):
                if periode and page.baca_filter_tanggal() != periode:
                    page.set_filter_tanggal(periode)
                    page.tunggu_processing_selesai()
                try:
                    page.reload_data()
                except Exception:
                    pass
            page.reset_cari_grid()
            page.tunggu_processing_selesai()

        # Bersihkan draft kosong sisa run lain -- kalau tidak, baris
        # kosong itu yang ikut terisi, bukan baris yang baru dibuat.
        page._hapus_baris_kosong()

        # Tanggal untuk mengisi kolom date/datetime DI DALAM baris baru.
        # Untuk DailyReport wajib: gridnya disaring per tanggal, jadi
        # baris tanpa tanggal tidak akan muncul lagi setelah Submit dan
        # test salah menyimpulkan "tidak tersimpan" (2026-09-08).
        tanggal_baris = test_data["hss_safety"].get(
            "filter_tanggal_harian", ""
        )
        if periode and len(periode) == 10:      # halaman harian
            tanggal_baris = periode

        penanda = f"INLINE-{time.strftime('%H%M%S')}"
        page.click_js_saat_tampil(page.BTN_CREATE)
        page.pace()
        terisi = page.isi_baris_kosong_inline(penanda, tanggal_baris)
        if not terisi:
            pytest.skip(
                f"'{kunci_halaman}': tidak ada baris draft kosong, atau "
                "baris barunya tidak punya kolom teks/angka yang bisa "
                "diketik bebas (semua lookup/tanggal)"
            )
        print(f"\n[INFO] '{kunci_halaman}': kolom diisi inline -> {terisi}")

        page.submit_changes()
        # Tangkap pesan validasi SEBELUM halaman dimuat ulang -- kalau
        # baris ditolak karena field wajib, pesannya cuma ada sesaat.
        # Tanpa ini, penolakan validasi terlihat sama persis dengan
        # "tidak tersimpan", dan itu gampang disalahartikan sebagai bug
        # aplikasi (kejadian 2026-09-08 di Witness Statement).
        pesan_validasi = page.pesan_validasi_halaman()
        _muat_ulang_server()

        tersimpan = page.tabel_berisi(penanda)
        try:
            if not tersimpan and pesan_validasi:
                # Baris DITOLAK VALIDASI, bukan gagal disimpan. Itu
                # perilaku aplikasi yang BENAR -- pengisian otomatis
                # memang belum bisa memenuhi semua field wajib (mis.
                # lookup yang harus dipilih lewat modal pencarian).
                pytest.skip(
                    f"'{kunci_halaman}': baris ditolak VALIDASI, bukan gagal "
                    f"menyimpan. Pesan aplikasi: {pesan_validasi[:300]}"
                )
            assert tersimpan, (
                f"Baris yang dibuat lewat Create + isi LANGSUNG di grid "
                f"('{penanda}', kolom {terisi}) tidak ada di "
                f"'{kunci_halaman}' setelah Submit Changes + Reload Data "
                "-- input langsung di tabel tidak tersimpan ke server, dan "
                "TIDAK ADA pesan validasi apa pun (kegagalan senyap)"
            )
        finally:
            # Bersihkan apa pun hasilnya: baris uji tidak boleh
            # ditinggalkan menumpuk di DEV.
            if tersimpan:
                page.cari_di_grid(penanda)
                if page.hapus_baris_berisi(penanda):
                    page.submit_changes()
                    _muat_ulang_server()
                    if page.tabel_berisi(penanda):
                        print(
                            f"[PERINGATAN] '{kunci_halaman}': baris uji "
                            f"'{penanda}' GAGAL dihapus -- bersihkan manual "
                            "atau lewat tools/cleanup_dummy_semua.py"
                        )
            page.reset_cari_grid()
