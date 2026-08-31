"""Probe: dump isi dropdown Columns di halaman Witness Statement
(buat tahu elemen item kolom yang harus diklik)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import config
from pages.safety_witness_statement_report_page import (
    SafetyWitnessStatementReportPage,
)

options = Options()
options.add_argument("--start-maximized")
options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
options.add_argument("--disable-notifications")
options.add_experimental_option("excludeSwitches", ["enable-automation"])

d = webdriver.Chrome(options=options)
d.implicitly_wait(0)

try:
    page = SafetyWitnessStatementReportPage(d)
    page.buka_via_menu("witness_statement_report")
    page.buka_dropdown_columns()
    time.sleep(2)
    dump = d.execute_script(
        "const out = [];"
        "document.querySelectorAll('div.dt-button-collection').forEach(c => {"
        "  const r = c.getBoundingClientRect();"
        "  if (r.width <= 0 || r.height <= 0) return;"
        "  const item = [];"
        "  c.querySelectorAll('*').forEach(el => {"
        "    const er = el.getBoundingClientRect();"
        "    if (er.width <= 0 || er.height <= 0) return;"
        "    const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();"
        "    item.push({tag: el.tagName, cls: el.className.toString()"
        "      .slice(0, 70), teks: t.slice(0, 40)});"
        "  });"
        "  out.push({html: c.outerHTML.slice(0, 2500), item: item});"
        "});"
        "return out;"
    )
    for kumpulan in dump:
        print("[item yang tampil di collection]")
        for it in kumpulan["item"]:
            print("  ", it)
        print("[outerHTML]")
        print(kumpulan["html"])

    # tutup lalu ulangi SEKUENS PERSIS test: buka -> pace -> klik_item_columns
    page.tutup_dropdown_columns()
    page.buka_dropdown_columns()
    page.pace()
    snap = d.execute_script(
        "const cols = [];"
        "document.querySelectorAll('div.dt-button-collection').forEach(c => {"
        "  const r = c.getBoundingClientRect();"
        "  cols.push({cls: c.className.toString().slice(0, 60),"
        "    rect: [r.width, r.height]});"
        "});"
        "const its = [];"
        "document.querySelectorAll('div.dt-button-collection .dt-button')"
        ".forEach(a => {"
        "  const r = a.getBoundingClientRect();"
        "  const s = window.getComputedStyle(a);"
        "  its.push({teks: (a.innerText || '').trim(),"
        "    rect: [r.width, r.height], display: s.display});"
        "});"
        "return {collection: cols, item: its};"
    )
    print("[snapshot pas klik_item_columns]", snap)
    page.klik_item_columns()
    print("[sesudah klik_item_columns] modal tampil?",
          page._ada_modal_tampil())
    desc = page._deskripsi_modal()
    print("[deskripsi modal]", desc)
    page._paksa_tutup_modal()
finally:
    d.quit()
