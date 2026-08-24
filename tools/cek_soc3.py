"""Cek apakah baris draft kosong di SOC bisa dibersihkan lewat form
edit (klik baris -> modal form -> tombol Delete?) -- debug sementara,
hapus setelah hijau.

    python tools/cek_soc3.py

TIDAK menyimpan/menghapus apa pun kecuali tombol Delete di modal form
edit memang ada dan dikonfirmasi. Semua langkah dicetak.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from config import config
from pages.hss_safety_page import HssSafetyPage

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

JS_BARIS_KOSONG = (
    "const t = " + page.JS_GRID + ";"
    "if (!t) return null;"
    "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
    "  const ins = [...r.querySelectorAll('input')];"
    "  return ins.length > 0 && ins.every(i => i.value === '');"
    "});"
    "if (!tr) return null;"
    "const td = tr.querySelector('td');"
    "if (!td) return null;"
    "const r = td.getBoundingClientRect();"
    "return {x: r.x + r.width / 2, y: r.y + r.height / 2,"
    "  teks: tr.innerText.slice(0, 120)};"
)


def modal_info():
    return driver.execute_script(
        "return [...document.querySelectorAll('.modal.show')].map(function(m) {"
        "  const s = window.getComputedStyle(m);"
        "  const r = m.getBoundingClientRect();"
        "  return {tampil: s.display !== 'none' && r.height > 0,"
        "    tombol: Array.prototype.slice.call(m.querySelectorAll('button'))"
        "      .map(function(b) { return (b.innerText || '').trim().slice(0, 25);"
        "      }).filter(Boolean)};"
        "});"
    )


try:
    page.buka_halaman("soc_recapitulation")
    time.sleep(2)
    jumlah = driver.execute_script(
        "const t = " + page.JS_GRID + ";"
        "return t ? t.querySelectorAll('tbody tr').length : -1;"
    )
    print("[1] SOC terbuka, jumlah baris:", jumlah)

    pos = driver.execute_script(JS_BARIS_KOSONG)
    print("[2] baris draft kosong:", pos)
    if not pos:
        print("    tidak ada baris kosong -> selesai")
        sys.exit(0)

    # klik SEL (bukan tombol delete) dengan mouse asli -- apakah membuka form?
    ActionChains(driver).move_by_offset(int(pos["x"]), int(pos["y"])).click().perform()
    ActionChains(driver).move_by_offset(-int(pos["x"]), -int(pos["y"])).perform()
    time.sleep(3)
    print("[3] setelah klik sel -> modal:", modal_info())
    # klik baris (tr) dengan JS click -- alternatif
    hasil = driver.execute_script(
        "const t = " + page.JS_GRID + ";"
        "const tr = [...t.querySelectorAll('tbody tr')].find(r => {"
        "  const ins = [...r.querySelectorAll('input')];"
        "  return ins.length > 0 && ins.every(i => i.value === '');"
        "});"
        "if (!tr) return false;"
        "const td = tr.querySelector('td');"
        "if (td) { td.click(); return true; }"
        "return false;"
    )
    time.sleep(3)
    print("[4] setelah td.click() -> modal:", modal_info())
except Exception as exc:
    print("GAGAL:", type(exc).__name__, exc)
finally:
    driver.quit()
