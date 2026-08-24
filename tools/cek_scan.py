"""Dump hasil scan JS_FIELD_FORM mentah di modal Incident (debug
sementara -- hapus setelah hijau)."""
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
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

page.buka_halaman("incident_investigation_form")
page.buka_form_create()
time.sleep(1.5)
fields = driver.execute_script(page.JS_FIELD_FORM)
print("scan JS_FIELD_FORM:")
for f in fields:
    print(f"  label={f['label']!r} type={f['type']!r} lookup={f['lookup']} "
          f"upload={f['upload']} kosong={f['kosong']} "
          f"selectOptions={f['selectOptions'][:6]}")
try:
    page.batal_form()
except Exception:
    pass
driver.quit()
