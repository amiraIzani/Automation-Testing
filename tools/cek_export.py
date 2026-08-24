"""Debug tombol Export di Incident: klik, amati dialog/tab baru/XHR/
folder unduhan (debug sementara -- hapus setelah hijau).

    python tools/cek_export.py
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
os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
opt.add_experimental_option(
    "prefs",
    {
        "download.default_directory": config.DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    },
)
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
page = HssSafetyPage(driver)

page.buka_halaman("incident_investigation_form")
time.sleep(2)
print("handle awal:", len(driver.window_handles))
sebelum = set(os.listdir(config.DOWNLOAD_DIR))
print("file unduhan sebelum:", sorted(sebelum))

# klik Export JS lalu jawab konfirmasi (seperti helper)
page.export_data()
print("setelah export_data -- modal tampil:", page._ada_modal_tampil())

for detik in range(20):
    time.sleep(1)
    baru = sorted(set(os.listdir(config.DOWNLOAD_DIR)) - sebelum)
    handles = len(driver.window_handles)
    if baru:
        print(f"detik {detik+1}: FILE BARU {baru} | window: {handles}")
        break
    if detik % 5 == 4:
        print(f"detik {detik+1}: belum ada file | window: {handles}")

print("modal sekarang:", page._ada_modal_tampil())
xhr = driver.execute_script(
    "return performance.getEntriesByType('resource')"
    ".filter(e => e.initiatorType === 'xmlhttprequest' || e.initiatorType === 'fetch')"
    ".map(e => (e.name || '').slice(0, 150)).slice(-8);"
)
print("XHR terakhir:", xhr)
# dump dialog / alert yang masih ada
alert = driver.execute_script(
    "return [...document.querySelectorAll('.bootbox, .alert, .modal.show')]"
    ".map(a => ({cls: a.className.slice(0, 60),"
    " teks: (a.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 120)}));"
)
print("dialog:", alert)
driver.quit()
