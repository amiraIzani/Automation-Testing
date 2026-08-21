"""Debug satu halaman form create dengan traceback penuh."""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.hss_safety_page import HssSafetyPage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_form_safety import JS_SCAN  # noqa: E402

KUNCI = sys.argv[1] if len(sys.argv) > 1 else "master_alat_keselamatan_operasi"

options = Options()
options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Chrome(options=options)
driver.switch_to.window(driver.window_handles[-1])

page = HssSafetyPage(driver)
try:
    page.buka_halaman(KUNCI)
    print("[1] halaman terbuka:", driver.current_url)
    page.buka_form_create()
    print("[2] klik Create with Form + modal terbuka")
    hasil = driver.execute_script(JS_SCAN)
    print("[4] JS scan OK:", len(hasil.get("fields", [])), "field, tab:", hasil.get("tabs"))
    page.batal_form()
    print("[5] modal ditutup")
except Exception:
    traceback.print_exc()
    page.take_screenshot("debug_form")
finally:
    driver.quit()
