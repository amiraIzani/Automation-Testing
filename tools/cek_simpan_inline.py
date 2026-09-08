"""
tools/cek_simpan_inline.py
==========================
Diagnosa: APAKAH edit inline di grid benar-benar tersimpan lewat
Submit Changes -- diuji di SEMUA halaman Safety yang punya tombol
Submit Changes (14 halaman), dengan cara yang persis sama.

KENAPA ADA (2026-09-08)
-----------------------
`reports/bugs/statistic-safety-recap-inline-edit-tidak-tersimpan.md`
melaporkan Statistic Safety Recapitulation tidak menyimpan edit inline.
Temuan itu berasal dari test otomatis 2026-08-26. Tapi pemilik produk
menyatakan secara manual penyimpanan BERHASIL -- artinya ada kemungkinan
yang salah adalah CARA TEST MEMBACA, bukan aplikasinya.

Dua kecurigaan utama pada sisi test:

  1. BACA TERLALU CEPAT. `test_safety_lagging_deep` menunggu elemen sel
     ADA (`_tunggu_anchor`), lalu langsung membaca. Padahal nilai sel
     diisi AJAX belakangan, jadi bacaan '' atau nilai lama bisa terjadi
     walau server sudah menyimpan. Alat ini menunggu nilainya STABIL,
     bukan cuma elemennya ada.

  2. DRAFT LOKAL MENGGANGGU. OPEL menyimpan perubahan yang belum
     di-submit ke localStorage dan MEMULIHKANNYA saat halaman dimuat
     ulang (fitur, bukan bug -- lihat bug report yang sudah ditutup).
     Kalau ada draft nyangkut, bacaan setelah reload bisa berasal dari
     draft, bukan dari server. Alat ini membersihkan draft dulu.

CARA PAKAI
----------
    py tools/cek_simpan_inline.py                 # uji semua halaman
    py tools/cek_simpan_inline.py --dry-run       # cuma laporkan rencana
    py tools/cek_simpan_inline.py --hanya smk3 statistic_safety_recapitulation

KEAMANAN DATA DEV
-----------------
Nilai yang diubah SELALU dikembalikan ke nilai semula (+ Submit) di
akhir tiap halaman, termasuk kalau hasilnya "tidak tersimpan". Mode
--dry-run tidak menulis apa pun.

Butuh sesi login aktif di profil Chrome (config.CHROME_PROFILE_PATH).
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage, TidakPunyaAkses

# Kolom KERANGKA -- label baris, bukan data. Tidak boleh dijadikan
# sasaran edit, tapi BOLEH dipakai sebagai anchor penunjuk baris.
KOLOM_KERANGKA = {
    "no", "#", "rownumber", "month", "monthint", "monthname",
    "tipepegawai", "date", "tahun", "year", "companyid",
}

DRY_RUN = "--dry-run" in sys.argv
if "--hanya" in sys.argv:
    HANYA = sys.argv[sys.argv.index("--hanya") + 1:]
    HANYA = [h for h in HANYA if not h.startswith("--")]
else:
    HANYA = []

# --field <NamaKolom>: paksa kolom tertentu jadi sasaran edit, bukan
# kolom pertama yang kebetulan terisi. Dipakai membandingkan perilaku
# ANTAR-KOLOM di halaman yang sama -- 2026-09-08 terlihat
# 'AkibatPenyakitTenagaKerja' tersimpan sementara 'PenyakitAkibatKerja'
# tidak, padahal keduanya di halaman Statistic Safety Recapitulation.
FIELD_PAKSA = None
if "--field" in sys.argv:
    _i = sys.argv.index("--field") + 1
    if _i < len(sys.argv) and not sys.argv[_i].startswith("--"):
        FIELD_PAKSA = sys.argv[_i]


def _angka(teks):
    """float dari isi sel, atau None kalau bukan angka."""
    teks = (teks or "").strip().replace(" ", "")
    if not teks:
        return None
    try:
        return float(teks.replace(",", "."))
    except ValueError:
        return None


def _muat_ulang(page, kunci, periode):
    """Muat ulang halaman TAPI kembalikan periodenya ke `periode`.

    INI AKAR MASALAH YANG SEBENARNYA (2026-09-08). `buka_halaman()`
    membuka URL halaman apa adanya, jadi filter periode KEMBALI KE
    DEFAULT. Kalau nilai ditulis di Agustus 2026 lalu dibaca setelah
    `buka_halaman()`, yang terbaca adalah September 2026 -- periode
    default yang KOSONG. Hasilnya dilaporkan "tidak tersimpan" padahal
    datanya aman di Agustus.

    Screenshot cek_simpan_statistic_safety_recapitulation_TIDAKJELAS_
    20260908_092618.png membuktikannya: Month terbaca 'September 2026'
    padahal alat menulis di 'August 2026'.

    Kekeliruan yang sama ada di test_safety_lagging_deep dan itulah
    yang melahirkan laporan bug palsu Statistic Safety Recapitulation.
    """
    page.buka_halaman(kunci)
    page.tunggu_processing_selesai()
    if periode and page.baca_filter_tanggal() != periode:
        page.set_filter_tanggal(periode)
        page.tunggu_processing_selesai()


def _sama(a, b):
    """Bandingkan dua isi sel. ANGKA dibandingkan sebagai angka, bukan
    string.

    Kenapa (2026-09-08): aplikasi boleh saja merender ulang angka dengan
    format berbeda dari yang diketik -- '69' bisa kembali sebagai
    '69.0', '69.00', atau ' 69 '. Pembandingan string mentah menilai itu
    "tidak sama", lalu melaporkan TIDAK JELAS padahal nilainya identik.
    Ini dugaan utama kenapa smk3 -- halaman KONTROL yang sudah terbukti
    menyimpan normal -- ikut dilaporkan TIDAK JELAS.
    """
    a, b = (a or "").strip(), (b or "").strip()
    if a == b:
        return True
    na, nb = _angka(a), _angka(b)
    return na is not None and nb is not None and na == nb


def _baca_stabil(page, field, anchor, timeout=25, jeda=1.0):
    """Baca sel berulang sampai nilainya STABIL (sama 2x berturut-turut
    dan tidak kosong), atau sampai timeout.

    Ini inti alat ini: bacaan sekali-jalan setelah reload TIDAK andal
    karena nilai sel diisi AJAX setelah elemennya dirender.
    """
    batas = time.monotonic() + timeout
    sebelumnya = None
    while time.monotonic() < batas:
        nilai = page.baca_sel_grid_anchor(field, anchor)
        if nilai and nilai == sebelumnya:
            return nilai
        sebelumnya = nilai
        time.sleep(jeda)
    return sebelumnya or ""


def _jumlah_baris_cocok(page, anchor):
    """Berapa baris di grid yang cocok dengan `anchor`.

    Anchor WAJIB menunjuk tepat satu baris. Kalau cocok ke banyak baris,
    `_ambil_elemen_sel_anchor()` mengambil yang PERTAMA -- alat bisa
    menulis ke satu baris lalu membaca dari baris lain, dan melaporkan
    'TIDAK TERSIMPAN' padahal aplikasinya benar.

    Risikonya nyata: grid Master Alat 2026-09-08 punya 8 baris yang
    Location/Type/Capacity-nya kembar (1 / 1 / 10).
    """
    return page.driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return 0;"
        "const a = arguments[0];"
        "let n = 0;"
        "for (const tr of t.querySelectorAll('tbody tr')) {"
        "  if (tr.querySelector('td.dataTables_empty')) continue;"
        "  let cocok = true;"
        "  for (const k of Object.keys(a)) {"
        "    const el = tr.querySelector("
        "      \"[data-fieldname='\" + k + \"']\");"
        "    const v = el ? (el.value != null ? el.value : el.innerText) : null;"
        "    if (v === null || (v || '').trim() !== a[k]) { cocok = false; break; }"
        "  }"
        "  if (cocok) n++;"
        "}"
        "return n;",
        anchor,
    ) or 0


def _pilih_sasaran(page):
    """Cari (anchor, nama_field, nilai_awal, nilai_uji) yang aman diuji.

    Anchor = kolom penunjuk baris. Diambil dari kolom KERANGKA kalau
    ada (Month/No/Date), TAPI banyak halaman tidak punya kolom begitu --
    Master Alat misalnya cuma EquipmentNo/Location/Type/Capacity
    (ketahuan di dry-run 2026-09-08: 'TAK ADA DATA' padahal datanya
    ADA, cuma anchornya gagal dibuat). Jadi kalau kolom kerangka tidak
    ada, anchor dibangun dari kolom lain yang terisi dan BUKAN kolom
    yang mau diedit.

    Sasaran edit boleh ANGKA (diuji nilai+1) maupun TEKS (diuji dengan
    imbuhan penanda), supaya halaman tanpa kolom angka tetap terjangkau.
    """
    baris = page.dt_baris_dict(maks_baris=40)
    for row in baris:
        terisi = {k: v for k, v in row.items() if (v or "").strip()}
        kerangka = {k: v for k, v in terisi.items()
                    if k.strip().lower() in KOLOM_KERANGKA}
        for nama, nilai in terisi.items():
            if nama.strip().lower() in KOLOM_KERANGKA:
                continue
            if FIELD_PAKSA and nama != FIELD_PAKSA:
                continue
            # anchor: pakai kolom kerangka kalau ada; kalau tidak,
            # pakai kolom terisi LAIN (maksimal 3) sebagai penunjuk baris
            anchor = dict(kerangka)
            if not anchor:
                anchor = {k: v for k, v in list(terisi.items())
                          if k != nama}
                anchor = dict(list(anchor.items())[:3])
            if not anchor:
                continue
            el = page._ambil_elemen_sel_anchor(nama, anchor)
            if el is None:
                continue
            # Lewati input TANGGAL/WAKTU. Nilai ujinya dibentuk dengan
            # menambah 'X' untuk teks, dan '2026-07-10T08:31X' jelas
            # bukan datetime yang sah -- browser menolaknya, sel jadi
            # kosong, lalu dilaporkan GAGAL BACA (kejadian di smk3,
            # field AuditExecutionDate, 2026-09-08).
            try:
                tipe = (el.get_attribute("type") or "").lower()
            except Exception:
                tipe = ""
            if tipe in ("date", "datetime-local", "month", "week", "time"):
                continue
            # anchor harus menunjuk TEPAT SATU baris -- lihat
            # _jumlah_baris_cocok() untuk alasannya
            if _jumlah_baris_cocok(page, anchor) != 1:
                continue
            asli = (nilai or "").strip()
            angka = _angka(asli)
            uji = str(int(angka) + 1) if angka is not None else (asli + "X")[:60]
            if uji == asli:
                continue
            return anchor, nama, asli, uji
    return None


def _coba_periode_lain(page, kunci):
    """Kalau periode aktif kosong, coba periode dari data/test_data.json
    (`hss_safety.filter_bulan`, mis. '2026-08') lalu tahun saja.

    Perlu karena periode DEFAULT beberapa halaman memang kosong --
    Statistic Safety Recap di September 2026 kosong, padahal Agustus
    2026 ada datanya (dry-run 2026-09-08 melaporkan 'TAK ADA DATA'
    hanya karena itu).
    """
    import json
    import os

    path = os.path.join(os.path.dirname(__file__), "..", "data",
                        "test_data.json")
    try:
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)["hss_safety"]
    except Exception:
        return None
    kandidat = [cfg.get("filter_bulan"), cfg.get("filter_tahun")]
    for periode in [p for p in kandidat if p]:
        try:
            sekarang = page.baca_filter_tanggal()
            if not sekarang or sekarang == periode:
                continue
            # filter bulan ('2026-08') tidak cocok untuk halaman tahunan
            # yang formatnya '2026' -- samakan panjangnya dulu
            if len(sekarang) != len(periode):
                periode = periode[:len(sekarang)]
                if periode == sekarang:
                    continue
            page.set_filter_tanggal(periode)
            page.tunggu_processing_selesai()
        except Exception:
            continue
        sasaran = _pilih_sasaran(page)
        if sasaran:
            return periode, sasaran
    return None


def _uji_halaman(driver, kunci):
    """Uji satu halaman. Kembalikan dict hasil."""
    hasil = {"kunci": kunci, "status": "?", "detail": ""}
    page = HssSafetyPage(driver)
    try:
        page.buka_halaman(kunci)
    except TidakPunyaAkses as e:
        hasil["status"] = "TIDAK PUNYA AKSES"
        hasil["detail"] = str(e)[:120]
        return hasil
    except Exception as e:
        hasil["status"] = "GAGAL DIBUKA"
        hasil["detail"] = f"{type(e).__name__}: {e}"[:120]
        return hasil

    # Buang draft lokal yang mungkin nyangkut, supaya yang dibaca nanti
    # benar-benar berasal dari server, bukan pemulihan draft.
    if page.ada_pending_lokal():
        hasil["detail"] = "ada draft pending saat dibuka -> dibersihkan; "
        try:
            page.reload_data()
        except Exception:
            pass

    page.reset_cari_grid()
    page.tunggu_processing_selesai()

    sasaran = _pilih_sasaran(page)
    if not sasaran:
        # Periode aktif kosong -- coba periode lain sebelum menyerah.
        lain = _coba_periode_lain(page, kunci)
        if lain:
            periode, sasaran = lain
            hasil["detail"] += f"periode diganti ke '{periode}'; "
    if not sasaran:
        # Halaman DailyReport disaring ke SATU TANGGAL (input dd/mm/yyyy).
        # Kalau tanggalnya belum diisi, grid pasti 0 baris -- dan itu
        # BUKAN bukti halamannya kosong. Periode cadangan yang dipakai
        # alat ini ('2026-08' / '2026') tidak cocok formatnya, jadi
        # tanggalnya memang tidak pernah terisi.
        #
        # Dibedakan statusnya (2026-09-08) supaya laporan tidak
        # menyesatkan: screenshot ketiga halaman DailyReport
        # memperlihatkan filter Date kosong 'dd/mm/yyyy' dengan
        # 'Showing 0 to 0 of 0 entries' -- belum diuji, bukan kosong.
        url = HssSafetyPage.HALAMAN.get(kunci, "")
        tanggal = page.baca_filter_tanggal()
        if "DailyReport" in url and not tanggal:
            hasil["status"] = "BUTUH TANGGAL"
            hasil["detail"] += (
                "halaman DailyReport dan filter Date masih kosong "
                "(dd/mm/yyyy) -- grid 0 baris karena belum ditanya, "
                "BUKAN karena datanya tidak ada. Belum teruji."
            )
        else:
            hasil["status"] = "TAK ADA DATA"
            hasil["detail"] += (
                f"tidak ada baris terisi di periode '{tanggal}' "
                "maupun periode cadangan"
            )
        # Klaim apa pun di sini WAJIB dibuktikan -- status saja tidak
        # cukup untuk menyimpulkan (permintaan user 2026-09-08).
        hasil["shot"] = page.take_screenshot(
            f"cek_simpan_{kunci}_{hasil['status'].replace(' ', '')}"
        )
        return hasil

    anchor, field, nilai_awal, nilai_uji = sasaran
    # Periode tempat nilai ini BENAR-BENAR ditulis. Wajib dipulihkan
    # sebelum membaca ulang -- lihat _muat_ulang().
    periode_pakai = page.baca_filter_tanggal()
    hasil["detail"] += (
        f"periode='{periode_pakai}' field={field} anchor={anchor} "
        f"'{nilai_awal}'->'{nilai_uji}'"
    )

    if DRY_RUN:
        hasil["status"] = "DRY RUN"
        hasil["shot"] = page.take_screenshot(f"cek_simpan_{kunci}_SASARAN")
        return hasil

    # --- tulis -> submit -> reload -> baca STABIL ---
    page.isi_sel_grid_anchor(field, nilai_uji, anchor)
    # Catat URL sebelum/sesudah Submit. Pengamatan manual 2026-09-08:
    # setelah konfirmasi Submit Changes, halaman Statistic dilaporkan
    # BERPINDAH dari Monthly Input ke Yearly Input lalu memuat ulang
    # terus-menerus. Kalau benar, penyimpanan terputus di tengah dan
    # itu bug aplikasi -- bukan soal kolomnya. URL-nya direkam supaya
    # perpindahan itu jadi bukti, bukan kesan.
    url_sebelum = driver.current_url
    info_submit = page.submit_changes()
    url_sesudah = driver.current_url
    if url_sebelum != url_sesudah:
        hasil["detail"] += (
            f" | URL BERPINDAH saat submit: '{url_sebelum}' -> "
            f"'{url_sesudah}'"
        )
        hasil["shot_submit"] = page.take_screenshot(
            f"cek_simpan_{kunci}_PINDAH_URL"
        )
    if isinstance(info_submit, dict):
        if not info_submit.get("konfirmasi_dijawab"):
            hasil["detail"] += " | KONFIRMASI SUBMIT TIDAK TERJAWAB"
        if info_submit.get("modal_ditutup_paksa"):
            hasil["detail"] += " | modal submit ditutup PAKSA"

    # Verifikasi WAJIB lewat Reload Data, bukan buka_halaman().
    #
    # AKAR MASALAH KEDUA (2026-09-08): OPEL memulihkan draft lokal saat
    # halaman dimuat ulang. Jadi `buka_halaman()` mengembalikan nilai
    # yang BARU SAJA DIKETIK -- bukan nilai dari server -- dan
    # pembacaan itu "membuktikan" penyimpanan yang belum tentu terjadi.
    # Ketahuan dari test_safety_lagging_deep[statistic]: dibaca lewat
    # buka_halaman() hasilnya 4 lalu 3 (nilai uji sendiri), tapi setelah
    # Reload Data nilainya 1 -- itulah nilai server sebenarnya.
    # Hanya Reload Data yang membuang draft dan menarik ulang dari
    # server, jadi hanya itu yang sah untuk memverifikasi penyimpanan.
    _muat_ulang(page, kunci, periode_pakai)
    try:
        page.reload_data()
    except Exception as e:
        hasil["detail"] += f" | reload_data error: {type(e).__name__}"
    # reload_data() bisa MENAVIGASI ulang (driver.get) kalau tombolnya
    # tidak kunjung tampil -- dan navigasi mengembalikan periode ke
    # default. Terbukti di golden_rules & mwt_daily 2026-09-08: periode
    # dipakai '2026-08' tapi setelah reload_data terbaca '2026-09',
    # anchor cocok 0 baris. Jadi periodenya dipulihkan LAGI di sini.
    if periode_pakai and page.baca_filter_tanggal() != periode_pakai:
        page.set_filter_tanggal(periode_pakai)
        page.tunggu_processing_selesai()
    terbaca = _baca_stabil(page, field, anchor)

    if not (terbaca or "").strip():
        # Sel tidak terbaca sama sekali. Ini kegagalan ALAT (anchor
        # tidak lagi cocok setelah reload, atau nilai belum ter-render),
        # BUKAN bukti aplikasi tidak menyimpan. Dibedakan statusnya
        # supaya tidak pernah lagi disalahartikan sebagai temuan
        # aplikasi -- persis kekeliruan yang melahirkan laporan bug
        # Statistic Safety Recap.
        hasil["status"] = "GAGAL BACA"
        # Sebutkan SEBABNYA, jangan ditebak: berapa baris yang masih
        # cocok dengan anchor, dan berapa baris yang dirender grid.
        cocok = _jumlah_baris_cocok(page, anchor)
        hasil["detail"] += (
            f" | sel tidak terbaca setelah reload. Baris yang cocok anchor "
            f"sekarang: {cocok}; baris dirender: {page.dt_jumlah_baris_dom()}; "
            f"periode: '{page.baca_filter_tanggal()}'"
        )
    elif _sama(terbaca, nilai_uji):
        hasil["status"] = "TERSIMPAN"
        if terbaca != nilai_uji:
            hasil["detail"] += f" | terbaca '{terbaca}' (format beda, nilai sama)"
    elif _sama(terbaca, nilai_awal):
        hasil["status"] = "TIDAK TERSIMPAN"
        hasil["detail"] += f" | setelah reload kembali ke '{terbaca}'"
    else:
        hasil["status"] = "TIDAK JELAS"
        hasil["detail"] += (
            f" | setelah reload terbaca '{terbaca}', bukan '{nilai_uji}' "
            f"maupun '{nilai_awal}'"
        )

    # Bukti visual keadaan grid SETELAH submit+reload -- supaya
    # kesimpulan TERSIMPAN / TIDAK TERSIMPAN bisa diperiksa mata,
    # bukan cuma dipercaya dari status (permintaan user 2026-09-08).
    hasil["shot"] = page.take_screenshot(
        f"cek_simpan_{kunci}_{hasil['status'].replace(' ', '')}"
    )

    # --- kembalikan data DEV apa pun hasilnya ---
    try:
        sekarang = page.baca_sel_grid_anchor(field, anchor)
        if not _sama(sekarang, nilai_awal):
            page.isi_sel_grid_anchor(field, nilai_awal, anchor)
            page.submit_changes()
            _muat_ulang(page, kunci, periode_pakai)
            try:
                page.reload_data()
            except Exception:
                pass
            if periode_pakai and page.baca_filter_tanggal() != periode_pakai:
                page.set_filter_tanggal(periode_pakai)
                page.tunggu_processing_selesai()
            balik = _baca_stabil(page, field, anchor)
            if not _sama(balik, nilai_awal):
                hasil["detail"] += f" | REVERT GAGAL, sekarang '{balik}'"
    except Exception as e:
        hasil["detail"] += f" | revert error: {type(e).__name__}"
    return hasil


def main():
    sasaran = [
        k for k, tombol in HssSafetyPage.TOMBOL_HALAMAN.items()
        if "Submit Changes" in tombol
    ]
    if HANYA:
        sasaran = [k for k in sasaran if k in HANYA]
    if not sasaran:
        sys.exit("Tidak ada halaman yang cocok.")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0)

    print(f"Menguji {len(sasaran)} halaman"
          + (" (DRY RUN -- tidak menulis apa pun)" if DRY_RUN else "")
          + "\n")
    hasil = []
    try:
        for i, kunci in enumerate(sasaran, 1):
            print(f"[{i}/{len(sasaran)}] {kunci} ...", flush=True)
            try:
                r = _uji_halaman(driver, kunci)
            except Exception as e:
                r = {"kunci": kunci, "status": "ERROR",
                     "detail": f"{type(e).__name__}: {e}"[:160]}
            hasil.append(r)
            print(f"        -> {r['status']}  {r['detail']}", flush=True)
            if r.get("shot_submit"):
                print(f"           bukti saat submit: {r['shot_submit']}",
                      flush=True)
            if r.get("shot"):
                print(f"           bukti: {r['shot']}", flush=True)
    finally:
        driver.quit()

    print("\n" + "=" * 72)
    print("RINGKASAN: apakah edit inline tersimpan lewat Submit Changes?")
    print("=" * 72)
    for r in hasil:
        print(f"{r['status']:18} {r['kunci']}")
        if r.get("shot"):
            print(f"{'':18} bukti: {Path(r['shot']).name}")
    print("=" * 72)
    for status in ("TERSIMPAN", "TIDAK TERSIMPAN", "TIDAK JELAS",
                   "GAGAL BACA", "TAK ADA DATA", "BUTUH TANGGAL",
                   "DRY RUN", "TIDAK PUNYA AKSES", "GAGAL DIBUKA", "ERROR"):
        n = sum(1 for r in hasil if r["status"] == status)
        if n:
            print(f"  {status:18} : {n}")


if __name__ == "__main__":
    main()
