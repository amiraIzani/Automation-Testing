"""Mimik test coba semua tombol PERSIS urutannya + log tiap langkah
(debug sementara -- hapus setelah hijau).

    python tools/cek_urutan.py mwt_daily
    python tools/cek_urutan.py master_alat_keselamatan_operasi

Untuk tiap tombol toolbar: cetak langkah, jumlah baris grid sebelum/
sesudah, jumlah baris draft kosong, dan state modal. Fokusnya cari
kenapa create w/ form gagal di pytest padahal probe langsung sukses.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

KUNCI = sys.argv[1] if len(sys.argv) > 1 else "mwt_daily"

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
opt.set_capability("unhandledPromptBehavior", "accept")
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)


def info(judul=""):
    i = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return {baris: -1};"
        "const trs = [...t.querySelectorAll('tbody tr')];"
        "const kosong = trs.filter(r => {"
        "  const ins = [...r.querySelectorAll('input')];"
        "  return ins.length > 0 && ins.every(x => x.value === '');"
        "}).length;"
        "const ins = [...t.querySelectorAll('tbody tr input')]"
        "  .map(x => x.value).filter(v => v);"
        "return {baris: trs.length, draftKosong: kosong,"
        "  adaPenanda: ins.some(v => v.includes('Dummy')),"
        "  contoh: ins.slice(0, 4)};"
    )
    print(f"    [{judul}] {i}")


try:
    page.buka_halaman(KUNCI)
    print("HALAMAN:", driver.current_url)
    info("awal")
    daftar = HssSafetyPage.TOMBOL_HALAMAN[KUNCI]
    print("URUTAN TOMBOL:", daftar)
    for nama in daftar:
        print(f"\n>>> {nama}")
        try:
            page.coba_tombol(nama)
            print(f"    {nama}: OK")
        except Exception as exc:
            print(f"    {nama}: GAGAL {type(exc).__name__}: {str(exc)[:150]}")
            # cek state pasca gagal
            info("pasca-gagal")
            print("    modal:", page._ada_modal_tampil())
            try:
                page.tutup_modal()
                print("    (modal ditutup)")
            except Exception:
                pass
            raise
        info(nama)
except Exception as exc:
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
