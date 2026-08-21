"""Diagnosa FullScreen: kenapa klik kedua tidak mengembalikan mode (hapus nanti)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

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

    def semua_btn():
        return driver.execute_script(
            "return [...document.querySelectorAll('.fullscreen-button')].map(b => {"
            "  const s = window.getComputedStyle(b); const r = b.getBoundingClientRect();"
            "  return {teks: (b.innerText||'').trim(), vis: s.display !== 'none'"
            "          && s.visibility !== 'hidden' && r.width > 0 && r.height > 0,"
            "          rect: [Math.round(r.x), Math.round(r.y)]};"
            "});"
        )

    print("sebelum klik:", semua_btn())
    page.toggle_fullscreen()
    time.sleep(1)
    print("sesudah klik 1 (+1s):", semua_btn())

    # --- pasang counter listener di SEMUA tombol, lalu JS-click tombol pertama ---
    driver.execute_script(
        "window.__klik = {};"
        "[...document.querySelectorAll('.fullscreen-button')].forEach((b, i) => {"
        "  b.addEventListener('click', () => { window.__klik[i] = (window.__klik[i]||0)+1; });"
        "});"
    )
    js = driver.execute_script(
        "const bs = [...document.querySelectorAll('.fullscreen-button')];"
        "const idx = bs.findIndex(b => {const s = window.getComputedStyle(b);"
        "  const r = b.getBoundingClientRect();"
        "  return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0;});"
        "if (idx >= 0) { bs[idx].click(); } return idx;"
    )
    time.sleep(1)
    print(f"JS-click tombol idx={js}: counter={driver.execute_script('return window.__klik')} -> {semua_btn()}")

    # --- coba klik mouse ASLI (Actions) kalau masih Windowed ---
    st = semua_btn()
    if st and st[0]["teks"] == "Windowed":
        el = driver.find_elements("css selector", ".fullscreen-button")[0]
        ActionChains(driver).move_to_element(el).click().perform()
        time.sleep(1)
        print("klik mouse asli (+1s):", semua_btn())

    # --- coba mousedown+mouseup asli kalau masih Windowed ---
    st = semua_btn()
    if st and st[0]["teks"] == "Windowed":
        el = driver.find_elements("css selector", ".fullscreen-button")[0]
        ActionChains(driver).move_to_element(el).click_and_hold().pause(0.2).release().perform()
        time.sleep(1)
        print("mousedown+mouseup asli (+1s):", semua_btn())

finally:
    driver.quit()
