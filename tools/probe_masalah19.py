"""Probe #19 (2026-08-27):

Klik anchor .dt-input-upload TIDAK menghasilkan input[type=file]
(probe 18). Cek mekanisme lain: setelah klik anchor, apa yang muncul?
- modal baru (dropzone?)
- iframe?
- elemen dengan class file/drop/upload baru?
- window.showOpenFilePicker tersedia?
- dump event listener? (sulit) -> cek DOM diff sederhana.
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

JS_DUMP = r"""
const modal = document.querySelector('.modal.show');
const out = {};
out.modalBaru = [...document.querySelectorAll('.modal.show')].map(
  m => (m.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 160));
out.iframe = document.querySelectorAll('iframe').length;
out.inputFile = document.querySelectorAll('input[type="file"]').length;
out.dropzone = document.querySelectorAll(
  '[class*="drop"], [class*="dz-"], [class*="fileinput"],'
  + ' [class*="file-input"], .swal2-container').length;
out.showOpenFilePicker = typeof window.showOpenFilePicker === 'function';
// semua elemen baru yang mengandung kata upload/file di class/id
const elBaru = [];
document.querySelectorAll('*').forEach(e => {
  const c = (e.className && e.className.toString ? e.className.toString() : '')
    + ' ' + (e.id || '');
  if (/dz-|dropzone|fileinput|file-input|swal2|fancybox|lightbox/i.test(c)
      && elBaru.length < 10 && e.offsetHeight > 0) {
    elBaru.push({tag: e.tagName, cls: c.slice(0, 100)});
  }
});
out.elBaru = elBaru;
return out;
"""

try:
    LoginPage(driver).login()
    print("[OK] login", flush=True)

    page.buka_halaman("incident_investigation_form")
    page.buka_form_create()
    page.pace(2.0)
    print("[form] SEBELUM klik:", driver.execute_script(JS_DUMP), flush=True)

    # klik anchor Upload pertama (native + JS, dua-duanya dicoba)
    dari = driver.execute_script(
        "const modal = document.querySelector('.modal.show');"
        "const a = modal.querySelector('.dt-input-upload');"
        "if (!a) return null;"
        "const r = a.getBoundingClientRect();"
        "return {x: r.x + r.width / 2, y: r.y + r.height / 2};"
    )
    print("[form] posisi anchor:", dari, flush=True)
    from selenium.webdriver.common.action_chains import ActionChains
    if dari:
        ActionChains(driver).move_by_offset(
            int(dari["x"]), int(dari["y"])).click().perform()
        ActionChains(driver).move_by_offset(
            -int(dari["x"]), -int(dari["y"])).perform()
    page.pace(3.0)
    print("[form] SETELAH klik native:", driver.execute_script(JS_DUMP),
          flush=True)

    print("[SELESAI]", flush=True)
finally:
    driver.quit()
