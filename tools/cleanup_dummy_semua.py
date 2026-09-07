"""
tools/cleanup_dummy_semua.py
=============================
Bersihkan baris dummy sisa automation test di SEMUA halaman Safety yang
bisa membuat baris -- bukan cuma Master Alat.

Sasaran halaman (dihitung otomatis dari TOMBOL_HALAMAN: halaman yang
punya tombol "Create"). Halaman Reporting TIDAK disentuh sama sekali --
di sana cuma ada Export/Cancel, tidak ada alur create/delete. Halaman
grid inline-edit tanpa Create (leading_indicator, smk3, smkp,
statistic_safety_recapitulation, data_rekap_statistik_k3) juga dilewati:
test cuma MENGUBAH nilai sel di sana, tidak menambah baris.

Yang dianggap dummy:
  a) baris BERTANDA -- memuat 'AUTO-TEST' (data/test_data.json:
     master_alat.equipment_prefix) atau 'Dummy' (penanda default
     create_dengan_form_sungguhan / coba tombol Create, lihat
     hss_safety_page.py -- penanda = "Dummy " + HHMMSS)
  b) baris KOSONG -- semua input tanpa nilai; ini draft sisa tombol
     "Create" polos, yang terbukti membuat Submit Changes MEMBUANG baris
     baru (lihat reports/bugs/master-alat-submit-drops-new-row.md)

HALAMAN BERTAB: incident_investigation_form (6 tab) dan
witness_statement_report (2 tab) punya SATU GRID PER TAB, semuanya ada
di DOM sekaligus (dibuktikan tools/cek_grid_semua_halaman.py,
2026-09-04). Script ini PINDAH TAB satu per satu; JS_GRID sudah
diperbaiki supaya mengikuti grid yang TAMPIL, jadi tiap tab dibersihkan
terhadap grid-nya sendiri.

CATATAN district/periode: script bekerja di district + periode yang
AKTIF saat halaman dibuka -- sama persis dengan yang dipakai test saat
membuat dummy (test tidak pernah set district; lihat data/test_data.json,
tidak ada field district di config create).

Jalankan:
    py tools/cleanup_dummy_semua.py --dry-run        # hitung saja, tidak menghapus
    py tools/cleanup_dummy_semua.py                  # hapus + Submit Changes
    py tools/cleanup_dummy_semua.py --hanya-bertanda # jangan sentuh baris kosong
    py tools/cleanup_dummy_semua.py mwt_daily golden_rules   # halaman tertentu
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

DRY_RUN = "--dry-run" in sys.argv
HANYA_BERTANDA = "--hanya-bertanda" in sys.argv

# Tab per halaman -> kunci daftar tab di data/test_data.json.
# (Sama dengan TAB_HALAMAN di tests/test_safety.py.)
TAB_HALAMAN = {
    "incident_investigation_form": "tab_incident_investigation",
    "witness_statement_report": "tab_witness_statement_report",
    "data_rekap_statistik_k3": "tab_data_rekap_statistik_k3",
}

# Klasifikasi tiap baris grid AKTIF: 'kosong' | 'bertanda' | 'isi'.
# Dipisah supaya laporan dry-run menunjukkan apa yang akan dihapus dan
# kenapa -- bukan cuma satu angka gelondongan.
JS_KLASIFIKASI = (
    "const t = {grid};"
    "if (!t) return null;"
    "return [...t.querySelectorAll('tbody tr')].map((tr, idx) => {{"
    "  if (tr.querySelector('td.dataTables_empty')) return null;"
    "  const inputs = [...tr.querySelectorAll('input, select, textarea')];"
    "  const nilai = inputs.map(i => (i.value || '').trim());"
    "  const gab = nilai.join(' ');"
    "  const teks = tr.innerText || '';"
    "  const bertanda = teks.includes('AUTO-TEST') || teks.includes('Dummy')"
    "    || gab.includes('AUTO-TEST') || gab.includes('Dummy');"
    "  const kosong = nilai.length > 0 && nilai.every(v => v === '');"
    "  const adaTombolHapus = !!tr.querySelector('a.btn-delete');"
    "  return {{idx: idx,"
    "          jenis: bertanda ? 'bertanda' : (kosong ? 'kosong' : 'isi'),"
    "          bisaHapus: adaTombolHapus}};"
    "}}).filter(x => x !== null);"
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


def bersihkan_grid_aktif(page, d, label):
    """Bersihkan grid yang SEDANG TAMPIL. Kembalikan jumlah baris yang
    ditandai hapus (atau yang AKAN dihapus kalau dry-run)."""
    baris = d.execute_script(JS_KLASIFIKASI.format(grid=page.JS_GRID))
    if baris is None:
        print(f"    {label}: grid tidak ditemukan -- dilewati.")
        return 0

    target = [b for b in baris if b["jenis"] == "bertanda"]
    kosong = [b for b in baris if b["jenis"] == "kosong"]
    if not HANYA_BERTANDA:
        target += kosong

    if not target:
        print(f"    {label}: {len(baris)} baris, tidak ada dummy.")
        return 0

    n_tanda = sum(1 for b in target if b["jenis"] == "bertanda")
    n_kosong = sum(1 for b in target if b["jenis"] == "kosong")
    catatan = f"{n_tanda} bertanda"
    if not HANYA_BERTANDA:
        catatan += f", {n_kosong} kosong"
    elif kosong:
        catatan += f" ({len(kosong)} baris kosong DIABAIKAN)"
    print(f"    {label}: {len(baris)} baris -> {len(target)} dummy "
          f"({catatan}).")

    tanpa_tombol = [b for b in target if not b["bisaHapus"]]
    if tanpa_tombol:
        print(f"      !! {len(tanpa_tombol)} baris tidak punya tombol "
              "hapus (a.btn-delete) -- tidak bisa dibersihkan lewat UI.")
        target = [b for b in target if b["bisaHapus"]]

    if DRY_RUN:
        return len(target)

    # Dari indeks TERBESAR ke TERKECIL supaya indeks baris lain tidak
    # bergeser saat satu baris ditandai hapus.
    ditandai = 0
    for b in sorted(target, key=lambda x: x["idx"], reverse=True):
        js = JS_HAPUS_BARIS_KE.format(grid=page.JS_GRID, idx=b["idx"])
        if d.execute_script(js):
            time.sleep(1.0)
            page.jawab_konfirmasi()
            page.tunggu_processing_selesai()
            ditandai += 1
    return ditandai


def bersihkan_halaman(page, d, kunci, tabs):
    """Bersihkan satu halaman (semua tab kalau bertab). Kembalikan
    jumlah baris yang ditandai hapus di halaman itu."""
    page.buka_halaman(kunci)
    page._tunggu_tabel()
    page.tunggu_processing_selesai()
    print(f"  district aktif: {page.unit_terpilih_value() or '(tidak ada)'}")

    total = 0
    daftar_tab = tabs.get(TAB_HALAMAN.get(kunci, ""), [])
    if daftar_tab:
        print(f"  halaman bertab ({len(daftar_tab)} tab) -- "
              "tiap tab punya grid sendiri.")
        for teks_tab in daftar_tab:
            try:
                page.klik_tab(teks_tab)
                page.tunggu_processing_selesai()
            except Exception as e:
                print(f"    tab '{teks_tab}': gagal dibuka "
                      f"({str(e).splitlines()[0][:70]}) -- dilewati.")
                continue
            total += bersihkan_grid_aktif(page, d, f"tab '{teks_tab}'")
    else:
        total += bersihkan_grid_aktif(page, d, "grid")

    if total and not DRY_RUN:
        print(f"  {total} baris ditandai hapus -- Submit Changes...")
        page.submit_changes()
        page.tunggu_processing_selesai()
    return total


def main():
    diminta = [a for a in sys.argv[1:] if not a.startswith("-")]
    # Halaman yang PUNYA alur create -> satu-satunya sumber baris dummy.
    bisa_create = [
        k for k in HssSafetyPage.HALAMAN
        if "Create" in HssSafetyPage.TOMBOL_HALAMAN.get(k, ())
    ]
    daftar = diminta or bisa_create

    tidak_dikenal = [k for k in daftar if k not in HssSafetyPage.HALAMAN]
    if tidak_dikenal:
        print(f"Kunci halaman tidak dikenal: {', '.join(tidak_dikenal)}")
        print(f"Pilihan: {', '.join(sorted(HssSafetyPage.HALAMAN))}")
        return
    bukan_create = [k for k in daftar if k not in bisa_create]
    if bukan_create:
        print("Halaman berikut tidak punya tombol Create (tidak mungkin "
              f"punya baris dummy): {', '.join(bukan_create)}")
        daftar = [k for k in daftar if k in bisa_create]
    if not daftar:
        print("Tidak ada halaman untuk dibersihkan.")
        return

    mode = "DRY RUN (tidak menghapus apa pun)" if DRY_RUN else "HAPUS SUNGGUHAN"
    print(f"Mode   : {mode}")
    print(f"Lingkup: {len(daftar)} halaman yang punya tombol Create")
    if HANYA_BERTANDA:
        print("Filter : hanya baris bertanda AUTO-TEST/Dummy "
              "(baris kosong dibiarkan)")

    data_path = Path(__file__).resolve().parent.parent / "data" / "test_data.json"
    with open(data_path, encoding="utf-8") as f:
        tabs = json.load(f)["hss_safety"]

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    d = webdriver.Chrome(options=options)
    d.implicitly_wait(0)
    rekap = {}
    try:
        page = HssSafetyPage(d)
        for kunci in daftar:
            print(f"\n{'=' * 62}\n{kunci}\n{'=' * 62}")
            try:
                rekap[kunci] = bersihkan_halaman(page, d, kunci, tabs)
            except Exception as e:
                print(f"  !! gagal: {str(e).splitlines()[0][:110]}")
                rekap[kunci] = -1

        print(f"\n\n{'=' * 62}\nRINGKASAN ({mode})\n{'=' * 62}")
        total = 0
        for kunci, n in rekap.items():
            if n < 0:
                print(f"  {kunci:<36} GAGAL")
            elif n == 0:
                print(f"  {kunci:<36} bersih")
            else:
                kata = "akan dihapus" if DRY_RUN else "dihapus"
                print(f"  {kunci:<36} {n} baris {kata}")
                total += n
        print(f"\nTOTAL: {total} baris "
              + ("AKAN dihapus -- jalankan tanpa --dry-run untuk eksekusi."
                 if DRY_RUN else "dihapus dan di-Submit."))
    finally:
        d.quit()


if __name__ == "__main__":
    main()
