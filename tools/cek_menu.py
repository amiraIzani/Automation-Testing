"""
tools/cek_menu.py
=================
Cek cara klik yang bisa men-expand submenu HSS > Safety di sidebar.
Target yang dicoba berurutan: <b class=collapse-sign> (element.click),
<li> HSS (element.click), lalu ActionChains (mouse asli) ke anchor.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from config import config


def log(teks):
    print(teks, flush=True)


def state(driver):
    """Return dict kondisi submenu HSS."""
    return driver.execute_script(
        "const s = [...document.querySelectorAll('nav span')]"
        ".filter(e => (e.innerText || '').trim() === 'HSS')[0];"
        "if (!s) return {error: 'span HSS tidak ada'};"
        "const li = s.closest('li');"
        "const safety = [...li.querySelectorAll('a')]"
        ".find(a => (a.title || '') === 'Safety');"
        "const cs = window.getComputedStyle(safety || document.body);"
        "const r = (safety || document.body).getBoundingClientRect();"
        "return {"
        "  liClass: li.className,"
        "  liOpen: li.className.includes('open'),"
        "  safetyVisible: safety ? cs.display !== 'none'"
        "    && cs.visibility !== 'hidden' && r.height > 0 : false,"
        "  signClass: (li.querySelector('.collapse-sign em') || {}).className,"
        "};"
    )


opt = Options()
opt.add_argument("--start-maximized")
opt.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
opt.add_experimental_option("excludeSwitches", ["enable-automation"])
driver = webdriver.Chrome(options=opt)
driver.implicitly_wait(0)
driver.get(config.BASE_URL + "My/Dashboard")
time.sleep(8)
log("URL: " + driver.current_url)
log("awal: " + str(state(driver)))

# 1) klik <b class=collapse-sign> via element.click()
try:
    el = driver.find_element(By.CSS_SELECTOR, "nav a[title='HSS'] b.collapse-sign")
    el.click()
    log("klik collapse-sign (element.click)")
except Exception as exc:
    log("gagal klik collapse-sign: " + repr(exc))
time.sleep(3)
log("stlh collapse-sign: " + str(state(driver)))

# 2) klik <li> HSS via element.click()
try:
    el = driver.find_element(By.XPATH, "//nav//span[normalize-space(text())='HSS']/ancestor::li[1]")
    el.click()
    log("klik li HSS (element.click)")
except Exception as exc:
    log("gagal klik li: " + repr(exc))
time.sleep(3)
log("stlh klik li: " + str(state(driver)))

# 3) ActionChains mouse asli ke anchor HSS
try:
    el = driver.find_element(By.CSS_SELECTOR, "nav a[title='HSS']")
    ActionChains(driver).move_to_element(el).click().perform()
    log("klik anchor HSS (ActionChains)")
except Exception as exc:
    log("gagal ActionChains: " + repr(exc))
time.sleep(3)
log("stlh ActionChains: " + str(state(driver)))

# 4) ActionChains ke collapse-sign
try:
    el = driver.find_element(By.CSS_SELECTOR, "nav a[title='HSS'] b.collapse-sign")
    ActionChains(driver).move_to_element(el).click().perform()
    log("klik collapse-sign (ActionChains)")
except Exception as exc:
    log("gagal ActionChains sign: " + repr(exc))
time.sleep(3)
log("stlh AC sign: " + str(state(driver)))

# 5) kalau masih belum kebuka, coba kirim event mousedown/mouseup asli
try:
    el = driver.find_element(By.CSS_SELECTOR, "nav a[title='HSS']")
    ActionChains(driver).move_to_element(el).click_and_hold().pause(0.3).release().perform()
    log("klik anchor (click_and_hold+release)")
except Exception as exc:
    log("gagal hold: " + repr(exc))
time.sleep(3)
log("stlh hold: " + str(state(driver)))

driver.quit()
print("selesai")
