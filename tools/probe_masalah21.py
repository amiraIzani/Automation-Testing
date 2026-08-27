"""Probe #21 (2026-08-27): diagnose modal Create with Form tidak
terbuka di halaman Incident (probe 20 gagal 2x, padahal probe 17-19
lancar). Dump: tombol Create with Form (ada/tampil?), klik JS, modal
setelah klik, console error, screenshot."""
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

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    page.buka_halaman("incident_investigation_form")
    page.pace(2.0)
    info = driver.execute_script(
        "const out = {tombol: [], modal: document.querySelectorAll"
        "('.modal.show').length, url: location.href};"
        "document.querySelectorAll('button').forEach(b => {"
        "  const t = (b.innerText || '').trim();"
        "  if (t.indexOf('Create') === 0) {"
        "    const r = b.getBoundingClientRect();"
        "    const s = window.getComputedStyle(b);"
        "    out.tombol.push({teks: t, tampil: r.width > 0"
        "      && s.display !== 'none', rect: [r.x, r.y, r.width, r.height]});"
        "  }"
        "});"
        "return out;"
    )
    print("[hal] ", info, flush=True)

    # klik JS langsung
    driver.execute_script(
        "const bs = [...document.querySelectorAll('button')];"
        "const b = bs.find(x => (x.innerText || '').trim()"
        "  === 'Create with Form');"
        "if (b) { b.click(); return true; } return false;"
    )
    page.pace(5.0)
    print("[klik] modal .show setelah klik JS:",
          driver.execute_script(
              "return document.querySelectorAll('.modal.show').length;"),
          flush=True)
    print("[klik] console error:",
          [e.get("message", "")[:150] for e in
           driver.get_log("browser")[-8:]], flush=True)
    driver.save_screenshot(str(Path(__file__).resolve().parent.parent
                               / "reports" / "screenshots"
                               / "_probe21_gagal.png"))
    print("[SELESAI]", flush=True)
finally:
    driver.quit()
