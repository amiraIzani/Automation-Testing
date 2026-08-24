"""
tools/cek_hapus.py
==================
Cek kolom aksi baris grid di halaman SMKP, SMK3, Statistic, dan Master
Alat: tombol apa saja yang ada (Edit/Hapus) + kelasnya, untuk
merancang test hapus yang aman (klik hapus -> dialog konfirmasi ->
tolak).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage

out = []


def log(t):
    print(t, flush=True)
    out.append(str(t))


opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

for kunci in ("smkp", "smk3", "statistic_safety_recapitulation",
              "master_alat_keselamatan_operasi"):
    try:
        page.buka_halaman(kunci)
        info = driver.execute_script(
            "const t = " + page.JS_GRID + ";"
            "if (!t) return 'tidak ada grid';"
            "const tr = t.querySelector('tbody tr');"
            "if (!tr) return 'tidak ada baris';"
            "const tds = [...tr.querySelectorAll('td')];"
            "const terakhir = tds[tds.length - 1];"
            "return {"
            "  jumlahTd: tds.length,"
            "  htmlAksi: terakhir ? terakhir.outerHTML.slice(0, 600) : null,"
            "  tombol: terakhir ? [...terakhir.querySelectorAll('a,button')]"
            "    .map(b => ({cls: b.className.slice(0, 80),"
            "      title: b.getAttribute('title'),"
            "      teks: (b.innerText || '').trim().slice(0, 20)})) : []"
            "};"
        )
        log(f"\n===== {kunci} =====")
        log(str(info))
    except Exception as exc:
        log(f"\n===== {kunci} ERROR: {exc!r}")

driver.quit()
with open(os.path.join(config.REPORTS_DIR, "cek_hapus.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("selesai")
