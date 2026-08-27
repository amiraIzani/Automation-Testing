"""Probe #16 (2026-08-27):

Lanjutan probe 15: klik collapse-sign 'HSS' TIDAK membuka submenu di
halaman smkp (YearlyReport Edit), padahal di dashboard BUKA normal.

Cek detail di smkp:
1) HTML anchor HSS + atribut body/aside (minified?)
2) klik SIGN via JS (execute_script .click()) -> terbuka?
3) klik ANCHOR via JS -> terbuka?
4) ada .modal-backdrop / overlay yang mengganggu?
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

JS_TERBUKA = (
    "const s = [...document.querySelectorAll('nav span')]"
    ".filter(e => (e.innerText || '').trim() === 'HSS')[0];"
    "return s ? s.closest('li').className : null;"
)
JS_HTML = (
    "const s = [...document.querySelectorAll('nav span')]"
    ".filter(e => (e.innerText || '').trim() === 'HSS')[0];"
    "if (!s) return null;"
    "const a = s.closest('a');"
    "const body = document.body.className;"
    "const aside = document.querySelector('#left-panel, aside');"
    "return {anchor: (a ? a.outerHTML.slice(0, 400) : null),"
    "        bodyCls: body.slice(0, 120),"
    "        asideCls: aside ? aside.className.slice(0, 120) : null,"
    "        backdrop: document.querySelectorAll('.modal-backdrop').length};"
)

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    driver.get(config.BASE_URL + "Reporting/Timesheet/YearlyReport/Edit?Id=1307")
    page.pace(5.0)
    print("[smkp] HTML:", driver.execute_script(JS_HTML), flush=True)

    # 1) klik SIGN via JS
    klik = driver.execute_script(
        "const s = [...document.querySelectorAll('nav span')]"
        ".filter(e => (e.innerText || '').trim() === 'HSS')[0];"
        "const b = s.closest('a').querySelector('b.collapse-sign');"
        "if (b) { b.click(); return true; } return false;"
    )
    page.pace(2.0)
    print(f"[smkp] klik SIGN via JS: {klik} -> li={driver.execute_script(JS_TERBUKA)}",
          flush=True)

    # 2) kalau belum terbuka, klik ANCHOR via JS
    if driver.execute_script(JS_TERBUKA) != "open":
        klik2 = driver.execute_script(
            "const s = [...document.querySelectorAll('nav span')]"
            ".filter(e => (e.innerText || '').trim() === 'HSS')[0];"
            "const a = s.closest('a');"
            "if (a) { a.click(); return true; } return false;"
        )
        page.pace(2.0)
        print(f"[smkp] klik ANCHOR via JS: {klik2} -> "
              f"li={driver.execute_script(JS_TERBUKA)}", flush=True)

    # 3) kalau masih belum, klik SPAN (mouse asli)
    if driver.execute_script(JS_TERBUKA) != "open":
        from selenium.webdriver.common.by import By
        el = page._ambil_js_visible(
            (By.XPATH, "//span[normalize-space(text())='HSS']")
        )
        from selenium.webdriver.common.action_chains import ActionChains
        ActionChains(driver).move_to_element(el).click().perform()
        page.pace(2.0)
        print(f"[smkp] klik SPAN mouse asli -> "
              f"li={driver.execute_script(JS_TERBUKA)}", flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
