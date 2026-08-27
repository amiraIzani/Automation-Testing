"""Probe #15 (2026-08-27):

test_safety_menu_dan_landing gagal di full run 27-08: browser start
me-restore tab smkp (YearlyReport Edit), klik collapse-sign 'HSS'
SUKSES tapi submenu tidak pernah terbaca terbuka (timeout).

Cek:
1) di halaman smkp (restore): ada berapa <nav>? span 'HSS' di mana?
   klik sign -> li.open muncul?
2) di dashboard: sama -> perbandingan.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config
from pages.hss_safety_page import HssSafetyPage
from pages.login_page import LoginPage

opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_argument("--disable-notifications")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

JS_STATE = (
    "const out = {nav: document.querySelectorAll('nav').length,"
    " spans: []};"
    "document.querySelectorAll('span').forEach(s => {"
    "  if ((s.innerText||'').trim() === 'HSS') {"
    "    const li = s.closest('li');"
    "    const r = s.getBoundingClientRect();"
    "    out.spans.push({liCls: li ? li.className : null,"
    "      w: r.width, h: r.height});"
    "  }"
    "});"
    "return out;"
)

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    for nama, url in [
        ("dashboard", config.BASE_URL),
        ("smkp", config.BASE_URL + "Reporting/Timesheet/YearlyReport/Edit?Id=1307"),
    ]:
        driver.get(url)
        page.pace(4.0)
        print(f"[{nama}] {driver.execute_script(JS_STATE)}", flush=True)
        page.buka_submenu("HSS")
        print(f"[{nama}] SETELAH klik sign: "
              f"{driver.execute_script(JS_STATE)}", flush=True)
        page.buka_submenu("Safety")
        print(f"[{nama}] SETELAH klik Safety: "
              f"{driver.execute_script(JS_STATE)}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
