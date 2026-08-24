"""Reproduksi MWT: Create polos (tinggalkan draft) lalu Create with
Form manual dengan dump baris di SETIAP sub-langkah (debug sementara).

    python tools/cek_mwt_kombinasi.py
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

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
        "  contoh: ins.slice(0, 5)};"
    )
    print(f"[{judul}] {i}")


try:
    page.buka_halaman("mwt_daily")
    info("awal")

    # 1) Create polos (persis helper)
    url_awal = driver.current_url
    page.click_js_saat_tampil(page.BTN_CREATE)
    page.pace(1.0)
    info("setelah klik Create")
    page.click_js_saat_tampil(page.BTN_CANCEL_GRID)
    page.jawab_konfirmasi()
    page.tunggu_processing_selesai()
    driver.get(url_awal)
    page._tunggu_tabel()
    page.tunggu_processing_selesai()
    info("setelah Cancel + reload")

    # 2) PERCOBAAN: hapus draft kosong dari DOM (JS) TANPA reload,
    #    langsung lanjut create w/ form -- apakah create lalu tersimpan?
    dihapus_dom = driver.execute_script(
        f"const t = {page.JS_GRID};"
        "if (!t) return 0;"
        "const trs = [...t.querySelectorAll('tbody tr')].filter(r => {"
        "  const ins = [...r.querySelectorAll('input')];"
        "  return ins.length > 0 && ins.every(i => i.value === '');"
        "});"
        "trs.forEach(r => r.remove());"
        "return trs.length;"
    )
    print("draft dihapus dari DOM:", dihapus_dom)
    info("setelah hapus DOM")

    # 3) Create with Form manual
    penanda = "Dummy " + time.strftime("%H%M%S")
    page.buka_form_create()
    page.pace(1.0)
    page.isi_form_create_otomatis(penanda=penanda)
    print("form terisi, penanda:", penanda)
    page.simpan_form()
    info("setelah Save")
    page.submit_changes()
    info("setelah Submit")
    driver.get(url_awal)
    for _ in range(60):
        ok = driver.execute_script(
            "const ts = [...document.querySelectorAll('table.reportData')];"
            "return ts.some(t => t.querySelectorAll('tbody tr').length > 0);"
        )
        if ok:
            break
        time.sleep(1)
    info("setelah reload")
    ok = page.tabel_berisi(penanda, timeout=config.DEFAULT_TIMEOUT)
    print("tabel_berisi(penanda):", ok)
    info("akhir")
except Exception as exc:
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
