"""
tools/cek_grid_semua_halaman.py
================================
Diagnosa: buka SEMUA halaman Safety (HssSafetyPage.HALAMAN, 19 halaman)
dan laporkan setiap <table class="reportData"> yang dirender di sana --
id, jumlah baris DATA, apakah DataTables ter-init, recordsTotal, pages.

Kenapa ada (2026-09-04): bug JS_GRID lama memilih "tabel PERTAMA yang
punya tbody tr", padahal tabel TEMPLATE pun punya <tr> (baris
'No data available' / td.dataTables_empty). Akibatnya seluruh helper
grid bisa menempel ke tabel DECOY -- dt_info() melaporkan pages=1 dan
recordsDisplay=1 padahal grid asli penuh. Ini ketahuan di Master Alat,
TAPI JS_GRID ada di base class, jadi berpotensi kena 19 halaman.

Script ini membandingkan ATURAN LAMA vs ATURAN BARU per halaman dan
menandai halaman yang HASILNYA BEDA -- itulah halaman yang selama ini
diuji terhadap tabel yang salah. Read-only: tidak mengklik, mengetik,
menyimpan, atau menghapus apa pun.

-------------------------------------------------------------------
SOAL CAKUPAN -- kenapa halaman Reporting ikut diperiksa (2026-09-04):
Ini BUKAN script penghapusan. Penghapusan memang cuma ada di halaman
Transaction (TOMBOL_HALAMAN: halaman Reporting cuma punya
"Export"/"Cancel" -- tidak ada Create/Delete/Submit Changes), dan
tools/cleanup_dummy_master_alat.py memang cuma menyentuh Master Alat.

Yang diperiksa di sini adalah SALAH TABEL saat MEMBACA grid, dan itu
kena halaman Reporting juga: test_safety_datatables_interaksi
di-parametrize atas GRID_KEYS (= semua halaman KECUALI safety_recap),
jadi 4 halaman Reporting -- lagging_indicator, golden_rules_recap,
emergency_drill_recap, mwt_recapitulation -- ikut diuji pakai
dt_info() / dt_search_kotak() / dt_nilai_kolom() / jumlah_th_grid(),
yang SEMUANYA menempel ke JS_GRID. Kalau JS_GRID nyangkut di tabel
decoy, test itu "lulus" terhadap tabel kosong = lulus palsu.

Yang TIDAK kena: test view Reporting (test_safety_*_view) memakai
tabel_report_tampil(), yang pakai selector TABLE_REPORT, bukan
JS_GRID -- jadi test-test itu aman apa pun hasil sweep ini.

safety_recap DILEWATI secara default: grid-nya tabel custom
(#tableBulanan), bukan DataTables, jadi tidak ada yang bisa dibanding.
-------------------------------------------------------------------

Jalankan:
    py tools/cek_grid_semua_halaman.py                # semua halaman ber-grid
    py tools/cek_grid_semua_halaman.py --transaction  # cuma yang bisa create/delete
    py tools/cek_grid_semua_halaman.py lagging_indicator smk3   # halaman tertentu
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

# Inventaris + simulasi KEDUA aturan pemilihan grid sekaligus, supaya
# selisihnya kelihatan tanpa perlu ganti-ganti kode.
JS_DIAGNOSA = """
const ts = [...document.querySelectorAll('table.reportData')];
const punyaId = t => t.id && t.id.indexOf('tableData_') === 0;
const barisDom = t => t.querySelectorAll('tbody tr').length;
const barisData = t => [...t.querySelectorAll('tbody tr')]
    .filter(tr => !tr.querySelector('td.dataTables_empty')).length;
const total = t => {
  try {
    if (window.jQuery && jQuery.fn.dataTable
        && jQuery.fn.dataTable.isDataTable(t))
      return jQuery(t).DataTable().page.info().recordsTotal;
  } catch (e) {}
  return -1;
};
const pages = t => {
  try {
    if (window.jQuery && jQuery.fn.dataTable
        && jQuery.fn.dataTable.isDataTable(t))
      return jQuery(t).DataTable().page.info().pages;
  } catch (e) {}
  return -1;
};

// Panel tab non-aktif ber-display:none -> offsetParent null.
const tampil = t => {
  if (t.offsetParent !== null) return true;
  const r = t.getBoundingClientRect();
  return r.width > 0 || r.height > 0;
};

const pilih = arr => {
  if (!arr.length) return null;
  const dt = arr.filter(t => total(t) >= 0);
  const dtBerId = dt.filter(punyaId);
  if (dtBerId.length)
    return dtBerId.reduce((a, b) => total(b) > total(a) ? b : a);
  if (dt.length)
    return dt.reduce((a, b) => total(b) > total(a) ? b : a);
  const isi = arr.filter(t => barisData(t) > 0);
  if (isi.length)
    return isi.reduce((a, b) => barisData(b) > barisData(a) ? b : a);
  return arr.find(punyaId) || arr[0] || null;
};

// LAMA = pemilihan TANPA memperhatikan tab yang aktif.
// BARU = dahulukan grid yang benar-benar TAMPIL (JS_GRID sekarang).
const lama = pilih(ts);
const baru = pilih(ts.filter(tampil)) || pilih(ts);

return {
  jumlahTabel: ts.length,
  jumlahDt: ts.filter(t => total(t) >= 0).length,
  jumlahDtTampil: ts.filter(t => total(t) >= 0 && tampil(t)).length,
  tabel: ts.map((t, i) => ({
    i: i, id: t.id || '(tanpa id)',
    barisDom: barisDom(t), barisData: barisData(t),
    isDt: total(t) >= 0, total: total(t), pages: pages(t),
    tampil: tampil(t)
  })),
  idxLama: lama ? ts.indexOf(lama) : -1,
  idxBaru: baru ? ts.indexOf(baru) : -1
};
"""


def _halaman_bisa_ubah_data(kunci):
    """True kalau halaman punya alur ubah data (Create/Delete/Submit).
    Halaman Reporting cuma punya Export/Cancel -- lihat TOMBOL_HALAMAN."""
    tombol = HssSafetyPage.TOMBOL_HALAMAN.get(kunci, ())
    return "Submit Changes" in tombol


def main():
    diminta = [a for a in sys.argv[1:] if not a.startswith("-")]
    hanya_transaction = "--transaction" in sys.argv

    if diminta:
        daftar = diminta
    else:
        # safety_recap dikecualikan: tabelnya custom (#tableBulanan),
        # bukan DataTables -- sama seperti GRID_KEYS di tests/.
        daftar = [k for k in HssSafetyPage.HALAMAN if k != "safety_recap"]
        if hanya_transaction:
            daftar = [k for k in daftar if _halaman_bisa_ubah_data(k)]

    lingkup = ("Transaction saja (bisa create/delete)" if hanya_transaction
               else "semua halaman ber-grid DataTables")
    print(f"Lingkup: {lingkup} -- {len(daftar)} halaman.")

    tidak_dikenal = [k for k in daftar if k not in HssSafetyPage.HALAMAN]
    if tidak_dikenal:
        print(f"Kunci halaman tidak dikenal: {', '.join(tidak_dikenal)}")
        print(f"Pilihan: {', '.join(sorted(HssSafetyPage.HALAMAN))}")
        return

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    d = webdriver.Chrome(options=options)
    d.implicitly_wait(0)
    beda, banyak_tabel, gagal = [], [], []
    try:
        page = HssSafetyPage(d)
        for kunci in daftar:
            jenis = ("Transaction" if _halaman_bisa_ubah_data(kunci)
                     else "Reporting")
            print(f"\n{'=' * 66}\n{kunci}  [{jenis}]\n{'=' * 66}")
            try:
                page.buka_halaman(kunci)
                page._tunggu_tabel()
                page.tunggu_processing_selesai()
            except Exception as e:
                pesan = str(e).split("\n")[0][:110]
                print(f"  !! gagal dibuka: {pesan}")
                gagal.append(kunci)
                continue

            hasil = d.execute_script(JS_DIAGNOSA)
            n = hasil["jumlahTabel"]
            n_dt = hasil["jumlahDt"]
            print(f"  {n} <table class='reportData'>, {n_dt} di antaranya "
                  f"DataTables ({hasil['jumlahDtTampil']} tampil)")
            for t in hasil["tabel"]:
                tanda = []
                if t["i"] == hasil["idxLama"]:
                    tanda.append("<- LAMA")
                if t["i"] == hasil["idxBaru"]:
                    tanda.append("<- BARU")
                jenis = "DataTables" if t["isDt"] else "bukan DT  "
                lihat = "tampil" if t["tampil"] else "TERSEMBUNYI"
                print(f"    [{t['i']}] id={t['id']:<22} {jenis} "
                      f"barisDOM={t['barisDom']:<4} barisDATA={t['barisData']:<4} "
                      f"total={t['total']:<5} {lihat:<11} "
                      f"{' '.join(tanda)}")

            # Yang penting BUKAN jumlah table.reportData (tabel kosong
            # tanpa id itu wrapper/template, selalu ada). Yang bikin
            # helper grid salah sasaran = >1 DataTables SUNGGUHAN, yaitu
            # halaman bertab dengan satu grid per tab.
            if n_dt > 1:
                banyak_tabel.append(f"{kunci} ({n_dt} grid)")
            if hasil["idxLama"] != hasil["idxBaru"]:
                beda.append((kunci, hasil["idxLama"], hasil["idxBaru"]))
                print("  ** BEDA: aturan lama menunjuk tabel "
                      f"[{hasil['idxLama']}], aturan baru [{hasil['idxBaru']}] "
                      "-- halaman ini SELAMA INI diuji ke tabel yang SALAH.")

        print(f"\n\n{'=' * 66}\nRINGKASAN\n{'=' * 66}")
        print(f"Halaman diperiksa : {len(daftar) - len(gagal)}/{len(daftar)}")
        if gagal:
            print(f"Gagal dibuka      : {', '.join(gagal)}")
        if banyak_tabel:
            print(f"\nPunya >1 grid DataTables ({len(banyak_tabel)} halaman) "
                  "-- satu grid per tab:")
            for x in banyak_tabel:
                print(f"  - {x}")
            print("  Di halaman ini helper grid HARUS ikut tab yang aktif; "
                  "kalau tidak,\n  grid tab pertama yang selalu terbaca.")
        else:
            print("\nSemua halaman cuma punya 1 grid DataTables.")
        if beda:
            print(f"\nSALAH TABEL sebelum perbaikan ({len(beda)} halaman):")
            for kunci, lama, baru in beda:
                jenis = ("Transaction" if _halaman_bisa_ubah_data(kunci)
                         else "Reporting")
                print(f"  - {kunci:<34} [{jenis:<11}] tabel [{lama}] -> [{baru}]")
            print("\n  Transaction -> alur create/edit/delete-nya bisa "
                  "salah sasaran.\n"
                  "  Reporting   -> yang terdampak cuma "
                  "test_safety_datatables_interaksi\n"
                  "                 (test_safety_*_view pakai "
                  "TABLE_REPORT, bukan JS_GRID -- aman).")
        else:
            print("\nTidak ada halaman yang berubah pilihan grid-nya "
                  "(aturan lama & baru menunjuk tabel yang sama).")
    finally:
        d.quit()


if __name__ == "__main__":
    main()
