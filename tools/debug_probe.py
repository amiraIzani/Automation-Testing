"""Probe sementara: alur LENGKAP create + export halaman Master Alat. (hapus nanti)"""
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.hss_safety_page import HssSafetyPage

options = Options()
options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Chrome(options=options)
driver.switch_to.window(driver.window_handles[-1])

page = HssSafetyPage(driver)
stamp = time.strftime("%H%M%S")
EQUIP = f"AUTO-TEST-{stamp}"
print("Equipment No test:", EQUIP)

page.buka_halaman("master_alat_keselamatan_operasi")
page.buka_form_create()

# --- 1. Equipment No: input teks ---
page.isi_field_modal("Equipment No", EQUIP)
print("[1] Equipment No terisi")

# --- 2. Location: lookup -> cari -> klik baris ---
page.click_js_saat_tampil(
    ("xpath",
     "//div[contains(@class,'modal') and contains(@class,'show')]"
     "//div[contains(@class,'form-group')][.//label[normalize-space(.)='Location']]"
     "//a[contains(@class,'dt-input-lookup-search')]")
)
page.tunggu_modal_terbuka()
judul = driver.execute_script(
    "return document.querySelector('#lookupModalTitle').innerText;")
print("[2] lookup Location terbuka, judul:", judul)
page.type_text_visible(("css selector", "#lookupModal input[aria-controls='vLookup']"), "Forklift Mitsubishi")
page.tunggu_processing_selesai()
time.sleep(1)
page.click_js_saat_tampil(("css selector", "#lookupModal tr.row-lookup"))
page.tunggu_modal_tertutup()
nilai_loc = driver.execute_script(r"""
const l = [...document.querySelectorAll('.modal.show label')]
    .find(x => (x.innerText||'').trim() === 'Location');
const grp = l.closest('.form-group');
return {hidden: grp.querySelector('.dt-input-lookup-hidden').value,
        tampil: grp.querySelector('.dt-input-lookup').value};
""")
print("[3] Location terpilih:", nilai_loc)

# --- 3. Type: lookup kedua ---
page.click_js_saat_tampil(
    ("xpath",
     "//div[contains(@class,'modal') and contains(@class,'show')]"
     "//div[contains(@class,'form-group')][.//label[normalize-space(.)='Type']]"
     "//a[contains(@class,'dt-input-lookup-search')]")
)
page.tunggu_modal_terbuka()
judul2 = driver.execute_script(
    "return document.querySelector('#lookupModalTitle').innerText;")
print("[4] lookup Type terbuka, judul:", judul2)
page.type_text_visible(("css selector", "#lookupModal input[aria-controls='vLookup']"), "Chain Hoist KITO")
page.tunggu_processing_selesai()
time.sleep(1)
page.click_js_saat_tampil(("css selector", "#lookupModal tr.row-lookup"))
page.tunggu_modal_tertutup()
nilai_typ = driver.execute_script(r"""
const l = [...document.querySelectorAll('.modal.show label')]
    .find(x => (x.innerText||'').trim() === 'Type');
const grp = l.closest('.form-group');
return {hidden: grp.querySelector('.dt-input-lookup-hidden').value,
        tampil: grp.querySelector('.dt-input-lookup').value};
""")
print("[5] Type terpilih:", nilai_typ)

# --- 4. Capacity: input teks ---
page.isi_field_modal("Capacity", "5 Ton")
print("[6] Capacity terisi")

# --- 5. Save ---
page.simpan_form()
print("[7] Modal tertutup setelah Save")

# --- 6. Verifikasi data muncul di tabel ---
ada = page.tabel_berisi(EQUIP)
print("[8] Data muncul di tabel:", ada)

# --- 7. Export ---
page.export_data()
time.sleep(3)
modal_export = driver.execute_script(
    "return [...document.querySelectorAll('.modal.show')].map(m => m.id);")
print("[9] Modal terbuka setelah Export:", modal_export)
downloads = list(Path.home() / "Downloads" / "*.xlsx")
print("[10] xlsx terakhir di Downloads:", max(downloads, key=lambda p: p.stat().st_mtime) if downloads else "-")

driver.quit()
