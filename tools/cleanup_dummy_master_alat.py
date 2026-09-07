"""
tools/cleanup_dummy_master_alat.py
===================================
Bersihkan SEMUA baris dummy (Equipment No mengandung 'AUTO-TEST' atau
'Dummy', atau baris draft KOSONG) yang menumpuk di grid Master Alat
Keselamatan Operasi hasil test otomatis.

Kenapa perlu (2026-09-04, "growing debt" -- lihat README): setiap run
test_safety_master_alat_create / test_safety_halaman_lengkap membuat
baris dummy baru. Sejak Delete + Submit Changes benar2 PERSISTEN ke
server (temuan 2026-08-31), baris-baris itu sekarang BISA dibersihkan
lewat UI -- tapi tidak ada test yang melakukannya untuk SEMUA baris
(test_safety_master_alat_delete cuma hapus 1 baris per run, sekadar
contoh alur fitur Delete). Script ini untuk pembersihan MANUAL/berkala,
BUKAN bagian dari suite pytest.

-------------------------------------------------------------------
CATATAN 2026-09-04 -- KENAPA SEBELUMNYA "CUMA 1 HALAMAN":
Ternyata masalahnya BUKAN loop pagination (itu sudah benar), tapi
SALAH TABEL. Halaman Master Alat merender BEBERAPA <table
class="reportData"> sekaligus (grid asli ber-id tableData_* + tabel
template). HssSafetyPage.JS_GRID memilih "tabel PERTAMA yang punya
tbody tr" -- padahal tabel template pun punya 1 <tr> (baris
'No data available' / baris contoh). Jadi semua helper (dt_info,
dt_ke_halaman, pencarian baris) menempel ke tabel DECOY yang isinya
1 baris => "Grid punya 1 halaman", "Sisa baris di grid: 1", dan nol
baris dummy ketemu, sementara grid ASLI di sebelahnya masih penuh.

Perbaikan: JS_GRID di HssSafetyPage sudah DIBETULKAN di akarnya --
baris td.dataTables_empty tidak lagi dihitung sebagai "punya baris",
dan grid asli (DataTables ter-init, id tableData_*) diprioritaskan.
Perbaikan itu kena SEMUA halaman, bukan cuma script ini. Di sini
tinggal dicetak inventaris tabelnya biar kelihatan grid mana yang
dipakai -- tidak menebak lagi. Untuk memeriksa dampaknya ke halaman
lain, pakai tools/cek_grid_semua_halaman.py.

Selain itu pagination sekarang DIMATIKAN saja: dt.page.len(-1) bikin
SEMUA baris dirender sekaligus, jadi tidak ada lagi baris yang lolos
gara-gara logika pindah halaman. Loop halaman cuma dipakai sebagai
cadangan kalau 'show all' ditolak grid.

CATATAN: TIDAK loop ganti-ganti district -- dicek di
data/test_data.json, config "master_alat" cuma punya
"equipment_prefix", tidak pernah set district apa pun. Test create
dummy selalu pakai district yang LAGI AKTIF saat halaman dibuka, jadi
cleanup ini cukup beroperasi di district itu saja.
-------------------------------------------------------------------

Jalankan:
    python tools/cleanup_dummy_master_alat.py
    python tools/cleanup_dummy_master_alat.py --dry-run   # cuma hitung, tidak hapus
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.safety_master_alat_keselamatan_operasi_page import (
    SafetyMasterAlatKeselamatanOperasiPage,
)

DRY_RUN = "--dry-run" in sys.argv

# Inventaris SEMUA table.reportData di halaman -- id, jumlah baris DOM,
# apakah DataTables ter-init, dan recordsTotal-nya. Ini yang dicetak
# supaya salah-tabel ketahuan langsung, bukan ditebak.
JS_INVENTARIS = """
const ts = [...document.querySelectorAll('table.reportData')];
return ts.map((t, i) => {
  const barisDom = [...t.querySelectorAll('tbody tr')].filter(
    tr => !tr.querySelector('td.dataTables_empty')).length;
  let isDt = false, total = -1, pages = -1, len = -1;
  try {
    if (window.jQuery && jQuery.fn.dataTable
        && jQuery.fn.dataTable.isDataTable(t)) {
      isDt = true;
      const info = jQuery(t).DataTable().page.info();
      total = info.recordsTotal; pages = info.pages; len = info.length;
    }
  } catch (e) {}
  return {i: i, id: t.id || '(tanpa id)', barisDom: barisDom,
          isDt: isDt, total: total, pages: pages, len: len};
});
"""

# Tampilkan SEMUA baris sekaligus (matikan pagination). Kembalikan
# jumlah baris yang akhirnya dirender, atau null kalau bukan DataTables.
JS_TAMPIL_SEMUA = """
const t = {grid};
if (!t || !window.jQuery || !jQuery.fn.dataTable
    || !jQuery.fn.dataTable.isDataTable(t)) return null;
const dt = jQuery(t).DataTable();
dt.page.len(-1).draw();
return dt.page.info().recordsDisplay;
"""

JS_CARI_BARIS_DUMMY = (
    "const t = {grid};"
    "if (!t) return [];"
    "return [...t.querySelectorAll('tbody tr')].map((tr, idx) => {{"
    "  if (tr.querySelector('td.dataTables_empty')) return -1;"
    "  const teks = tr.innerText;"
    "  const nilai = [...tr.querySelectorAll('input')]"
    "    .map(i => i.value || '');"
    "  const gab = nilai.join(' ');"
    "  const kosong = nilai.length > 0 && nilai.every(v => v === '');"
    "  const dummy = teks.includes('AUTO-TEST') || teks.includes('Dummy')"
    "    || gab.includes('AUTO-TEST') || gab.includes('Dummy');"
    "  return (kosong || dummy) ? idx : -1;"
    "}}).filter(i => i >= 0);"
)

JS_HAPUS_BARIS_KE = (
    "const t = {grid};"
    "if (!t) return false;"
    "const tr = [...t.querySelectorAll('tbody tr')][{idx}];"
    "if (!tr) return false;"
    "const del = tr.querySelector('a.btn-delete');"
    "if (!del) return false;"
    "del.click(); return true;"
)


def lapor_grid(page, d):
    """Cetak inventaris table.reportData + tabel mana yang dipilih
    JS_GRID. Murni diagnostik -- pemilihan grid-nya sendiri sekarang
    sudah benar di HssSafetyPage.JS_GRID (diperbaiki 2026-09-04), jadi
    script ini TIDAK meng-override apa pun lagi. Kalau baris yang
    dilaporkan di sini tidak cocok dengan yang terlihat di layar,
    berarti bug pemilihan grid-nya kambuh -- cek dengan
    tools/cek_grid_semua_halaman.py.
    """
    tabel = d.execute_script(JS_INVENTARIS)
    terpilih = d.execute_script(f"return {page.JS_GRID};")
    id_terpilih = terpilih.get_attribute("id") if terpilih else None

    print(f"\nDitemukan {len(tabel)} <table class='reportData'> di halaman:")
    for t in tabel:
        jenis = "DataTables" if t["isDt"] else "bukan DT  "
        aktif = "  <== DIPAKAI" if t["id"] == (id_terpilih or "\0") else ""
        print(f"  [{t['i']}] id={t['id']:<24} {jenis} barisDOM={t['barisDom']:<4} "
              f"recordsTotal={t['total']:<5} pages={t['pages']:<4} "
              f"pageLen={t['len']}{aktif}")
    if terpilih is None:
        print("\n!! JS_GRID tidak menemukan tabel apa pun di halaman ini.")
    return tabel


def hapus_di_halaman_aktif(page, d, total_terhapus):
    """Cari + hapus semua baris dummy yang SEDANG dirender. Kembalikan
    jumlah baris yang ditandai hapus."""
    js_cari = JS_CARI_BARIS_DUMMY.format(grid=page.JS_GRID)
    indeks_dummy = d.execute_script(js_cari)
    if not indeks_dummy:
        return 0
    print(f"  {len(indeks_dummy)} baris dummy/kosong ditemukan.")
    if DRY_RUN:
        return len(indeks_dummy)
    ditandai = 0
    # Hapus dari indeks TERBESAR ke TERKECIL supaya indeks baris lain
    # tidak bergeser saat satu baris ditandai hapus (baris pending-delete
    # masih ada di DOM sampai Submit).
    for idx in sorted(indeks_dummy, reverse=True):
        js_hapus = JS_HAPUS_BARIS_KE.format(grid=page.JS_GRID, idx=idx)
        if d.execute_script(js_hapus):
            time.sleep(1.0)
            page.jawab_konfirmasi()
            page.tunggu_processing_selesai()
            ditandai += 1
    return ditandai


def main():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    d = webdriver.Chrome(options=options)
    d.implicitly_wait(0)
    total_terhapus = 0
    try:
        page = SafetyMasterAlatKeselamatanOperasiPage(d)
        page.buka_via_menu("master_alat_keselamatan_operasi")
        page._tunggu_tabel()
        page.tunggu_processing_selesai()

        print(f"District aktif: {page.unit_terpilih_value()}")
        lapor_grid(page, d)

        # Kosongkan kotak search DULU (sisa filter run sebelumnya bisa
        # menyembunyikan baris), baru hitung isinya.
        page.reset_cari_grid()
        page.tunggu_processing_selesai()

        # Tampilkan SEMUA baris sekaligus -> tidak ada baris yang lolos
        # gara-gara pindah halaman.
        jumlah = d.execute_script(JS_TAMPIL_SEMUA.format(grid=page.JS_GRID))
        if jumlah is not None:
            page.tunggu_processing_selesai()
            print(f"Pagination dimatikan (show all): {jumlah} baris dirender.")
            total_terhapus += hapus_di_halaman_aktif(page, d, total_terhapus)
        else:
            # Cadangan: grid bukan DataTables -> sapu per halaman seperti
            # sebelumnya, dengan jumlah halaman DICEK ULANG tiap iterasi.
            print("Grid bukan DataTables -- fallback sapu per halaman.")
            info = page.dt_info()
            total_halaman = info["pages"] if info else 1
            h = 0
            while h < total_halaman:
                if info:
                    page.dt_ke_halaman(h)
                    info = page.dt_info()
                    total_halaman = info["pages"]
                print(f"Halaman {h + 1}/{total_halaman}:")
                total_terhapus += hapus_di_halaman_aktif(page, d, total_terhapus)
                h += 1

        if DRY_RUN:
            print(f"\n[DRY RUN] {total_terhapus} baris AKAN dihapus kalau "
                  "dijalankan tanpa --dry-run.")
        elif total_terhapus > 0:
            print(f"\n{total_terhapus} baris ditandai hapus -- Submit "
                  "Changes untuk benar-benar persisten ke server...")
            page.submit_changes()
            page.tunggu_processing_selesai()
            print("Selesai -- reload halaman untuk verifikasi jumlah baris.")
            page.buka_halaman("master_alat_keselamatan_operasi")
            page._tunggu_tabel()
            page.tunggu_processing_selesai()
            lapor_grid(page, d)
            info_akhir = page.dt_info()
            if info_akhir:
                print(f"Sisa baris di grid: {info_akhir['recordsDisplay']}")
        else:
            print("\nTidak ada baris dummy/kosong yang perlu dibersihkan.")
    finally:
        d.quit()


if __name__ == "__main__":
    main()
