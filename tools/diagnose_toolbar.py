"""Diagnosa sementara: struktur toolbar halaman Incident Investigation (hapus nanti)."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import config
from pages.safety_incident_investigation_form_page import SafetyIncidentInvestigationFormPage

options = Options()
options.add_argument("--start-maximized")
options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
options.add_argument("--disable-notifications")
options.add_argument("--disable-infobars")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-session-crashed-bubble")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.set_capability("unhandledPromptBehavior", "accept")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(0)

try:
    page = SafetyIncidentInvestigationFormPage(driver).buka()

    print("\n===== SEMUA <button> (teks | id | class | JS visible) =====")
    btns = driver.execute_script(
        "return [...document.querySelectorAll('button')].map(b => {"
        "  const s = window.getComputedStyle(b);"
        "  const r = b.getBoundingClientRect();"
        "  return {teks: (b.innerText||'').trim(), id: b.id, cls: b.className,"
        "          vis: s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0};"
        "});"
    )
    for b in btns:
        print(f"  teks={b['teks']!r:40} id={b['id']!r:20} vis={b['vis']}  cls={b['cls'][:60]}")

    print("\n===== LINK role=button / title=Filling =====")
    links = driver.execute_script(
        "return [...document.querySelectorAll('a')].filter(a => a.getAttribute('role')==='button' || a.title==='Filling instructions').map(a => {"
        "  const s = window.getComputedStyle(a);"
        "  const r = a.getBoundingClientRect();"
        "  return {teks: (a.innerText||'').trim(), id: a.id, title: a.title,"
        "          vis: s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0};"
        "});"
    )
    for l in links:
        print(f"  teks={l['teks']!r:30} id={l['id']!r:15} title={l['title']!r} vis={l['vis']}")

    print("\n===== btnReloadData detail =====")
    info = driver.execute_script(
        "const el = document.getElementById('btnReloadData');"
        "if (!el) return {ada: false};"
        "const s = window.getComputedStyle(el);"
        "const r = el.getBoundingClientRect();"
        "let anc = []; let p = el.parentElement; let depth = 0;"
        "while (p && depth < 6) { anc.push({tag: p.tagName, id: p.id, cls: (p.className||'').toString().slice(0,50), "
        "   disp: window.getComputedStyle(p).display}); p = p.parentElement; depth++; }"
        "return {ada: true, disp: s.display, vis: s.visibility, w: r.width, h: r.height, "
        "        isDisplayed: el.isConnected, ancestors: anc};"
    )
    print(" ", info)

    print("\n===== fullscreen-button / panel =====")
    fs = driver.execute_script(
        "const b = document.querySelector('.fullscreen-button');"
        "if (!b) return {ada: false};"
        "const p = b.closest('.panel');"
        "return {ada: true, btnCls: b.className, panelCls: p ? p.className : null,"
        "        panelId: p ? p.id : null};"
    )
    print(" ", fs)

    print("\n===== klik FullScreen lalu cek class panel =====")
    before = driver.execute_script(
        "const b = document.querySelector('.fullscreen-button');"
        "const p = b.closest('.panel');"
        "return p ? p.className : null;"
    )
    print("  sebelum klik:", before)
    page.toggle_fullscreen()
    after = driver.execute_script(
        "const b = document.querySelector('.fullscreen-button');"
        "const p = b.closest('.panel');"
        "return p ? p.className : null;"
    )
    print("  sesudah klik:", after)
    after2 = driver.execute_script(
        "return {fullscreenElement: !!document.fullscreenElement,"
        "  panelsFullscreen: [...document.querySelectorAll('.panel-fullscreen')].length,"
        "  bodyCls: document.body.className};"
    )
    print("  state:", after2)

    print("\n===== tombol di panel footer (Submit/Cancel) =====")
    footer = driver.execute_script(
        "return [...document.querySelectorAll('.panel')].map(p => {"
        "  const btns = [...p.querySelectorAll('button,a')].filter(b => (b.innerText||'').trim())"
        "    .map(b => (b.innerText||'').trim());"
        "  return {panelId: p.id, cls: (p.className||'').toString().slice(0,40), btns: btns.slice(0,12)};"
        "});"
    )
    for p in footer:
        print(" ", p)

finally:
    driver.quit()
