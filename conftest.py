"""
conftest.py
===========
PENTING - kenapa driver di sini scope="session":
Sesuai pola project NewDLA, Chrome HANYA dibuka 1 KALI dari test
pertama (Login) sampai test terakhir (Logout). Kalau scope-nya
"function" (default), Selenium akan buka & tutup browser di SETIAP
fungsi test -- itu yang bikin flow-nya "putus-putus" dan harus login
ulang setiap kali.

Dengan scope="session":
- Browser dibuka SEKALI oleh test pertama yang memakai fixture `driver`.
- Instance browser yang SAMA dipakai ulang oleh semua test lain sampai
  seluruh sesi pytest selesai.
- Browser memakai CHROME_PROFILE_PATH (config.py) yang sesi Azure AD
  B2C-nya sudah aktif -- lihat pages/login_page.py untuk detail alur.
- Browser ditutup OTOMATIS di akhir (tidak ada jeda "tekan ENTER").

TAMBAHKAN label modul baru ke STEP_LABELS begitu test modul OPEL lain
dibuat (mengikuti pola test_login di bawah).
"""

import json
import os
from datetime import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config


# ------------------ Ringkasan hasil per modul (kotak "AUTOMATION TESTING RESULT") ------------------
# Pemetaan: nama method test -> label modul. Tambahkan baris baru di
# sini setiap kali modul baru ditambahkan ke tests/.
STEP_LABELS = [
    ("test_login", "Login"),
    # --- HSS > Safety ---
    ("test_safety_menu_dan_landing", "Safety - Navigasi Menu"),
    ("test_safety_lagging_indicator_view", "Safety - Lagging Indicator (View)"),
    ("test_safety_golden_rules_recap_view", "Safety - Golden Rules Recap (View)"),
    ("test_safety_emergency_drill_recap_view", "Safety - Emergency Drill Recap (View)"),
    ("test_safety_mwt_recapitulation_view", "Safety - MWT Recapitulation (View)"),
    ("test_safety_recap_view", "Safety - Safety Recap (View)"),
    ("test_safety_incident_investigation_view", "Safety - Incident Investigation Form"),
    ("test_safety_incident_investigation_tab", "Safety - Incident Investigation (Tab)"),
    ("test_safety_initial_incident_view", "Safety - Initial Incident/Accident Report"),
    ("test_safety_witness_statement_view", "Safety - Witness Statement Report"),
    ("test_safety_emergency_drill_daily_view", "Safety - Emergency Drill Daily"),
    ("test_safety_master_alat_view", "Safety - Master Alat Keselamatan Operasi"),
    ("test_safety_master_alat_create", "Safety - Master Alat (Create with Form)"),
    ("test_safety_master_alat_delete", "Safety - Master Alat (Delete)"),
    ("test_safety_soc_recapitulation_view", "Safety - SOC Recapitulation"),
    ("test_safety_golden_rules_view", "Safety - Golden Rules"),
    ("test_safety_data_rekap_k3_view", "Safety - Data Rekap Statistik K3"),
    ("test_safety_kkp_p2k3_view", "Safety - SAFETY/KKP/P2K3 Committee Meeting"),
    ("test_safety_mwt_daily_view", "Safety - MWT Daily"),
    ("test_safety_leading_indicator_view", "Safety - Leading Indicator"),
    ("test_safety_statistic_safety_view", "Safety - Statistic Safety Recapitulation"),
    ("test_safety_smk3_view", "Safety - SMK3"),
    ("test_safety_smkp_view", "Safety - SMKP"),
    ("test_safety_lagging_deep", "Safety - Lagging (Semua Fitur)"),
    ("test_safety_halaman_lengkap", "Safety - Halaman Lengkap (Tabel+Tab+Tombol)"),
]

# Hasil kumulatif: label -> bool (semua step modul lulus); urutan dict = urutan eksekusi.
_step_results = {}


def _label_for_step(item_name):
    for prefix, label in STEP_LABELS:
        if item_name == prefix:
            return label
        # Test parametrized: nama item = "test_xxx[param]" -- tampilkan
        # param-nya (nama halaman) supaya hasil per halaman terlihat.
        if item_name.startswith(prefix + "["):
            param = item_name[len(prefix) + 1:-1]
            return f"{label} [{param}]"
    return None


# -------------------- Fixture: driver (session-scoped -> 1 browser) --------------------
@pytest.fixture(scope="session")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")

    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-session-crashed-bubble")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Dialog konfirmasi browser (mis. confirm Yes/OK saat Export)
    # otomatis dijawab Accept -- tidak bikin test hang menunggu dialog.
    chrome_options.set_capability("unhandledPromptBehavior", "accept")

    # Performance log Chrome -> berguna untuk diagnosa network kalau
    # dibutuhkan nanti (status HTTP asli request, dll).
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # File export (tombol Export) diarahkan ke folder unduhan project
    # supaya bisa diverifikasi otomatis oleh test.
    os.makedirs(config.DOWNLOAD_DIR, exist_ok=True)
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": config.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
        },
    )

    if config.HEADLESS:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")

    chrome_driver = webdriver.Chrome(options=chrome_options)
    chrome_driver.implicitly_wait(0)

    yield chrome_driver

    try:
        chrome_driver.quit()
    except Exception:
        pass


# -------------------- Fixture: test_data (dari data/test_data.json) --------------------
@pytest.fixture(scope="session")
def test_data():
    data_path = os.path.join(os.path.dirname(__file__), "data", "test_data.json")
    with open(data_path, "r", encoding="utf-8") as data_file:
        return json.load(data_file)


def _get_active_driver(test_item):
    active_driver = test_item.funcargs.get("driver")
    if active_driver is not None:
        return active_driver
    test_instance = getattr(test_item, "instance", None)
    if test_instance is not None:
        return getattr(test_instance, "driver", None)
    return None


# ------------------ Screenshot otomatis saat test gagal / di-skip ------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report_extras = getattr(report, "extra", [])

    if report.when == "call":
        label = _label_for_step(item.name)
        if label:
            ok = bool(report.passed)
            _step_results[label] = ok
            mark = "V" if ok else "X"
            ket = "berhasil" if ok else "GAGAL"
            print(f"\n{mark} [{label}] {ket}")

    if report.when == "call" and (report.failed or report.skipped):
        active_driver = _get_active_driver(item)
        if active_driver:
            os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_name = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join(config.SCREENSHOT_DIR, screenshot_name)
            try:
                active_driver.save_screenshot(screenshot_path)
                print(f"\n[SCREENSHOT SAAT GAGAL] {screenshot_path}")
                print(f"[URL SAAT GAGAL] {active_driver.current_url}")
                try:
                    from pytest_html import extras
                    relative_path = os.path.join("screenshots", screenshot_name)
                    report_extras.append(extras.image(relative_path))
                    report_extras.append(extras.url(active_driver.current_url))
                except Exception:
                    pass
            except Exception as screenshot_error:
                print(f"\n[GAGAL AMBIL SCREENSHOT] {screenshot_error}")

    report.extra = report_extras


# ------------------ Akhir sesi: cetak kotak "AUTOMATION TESTING RESULT" ------------------
def pytest_sessionfinish(session, exitstatus):
    if not _step_results:
        return

    total = len(_step_results)
    passed = sum(1 for ok in _step_results.values() if ok)
    failed = total - passed
    status = "PASSED" if failed == 0 else "FAILED"

    sep = "=" * 40
    lines = [sep, "       AUTOMATION TESTING RESULT", sep, ""]
    for label, ok in _step_results.items():
        mark = "V" if ok else "X"
        ket = "berhasil" if ok else "GAGAL"
        lines.append(f"{mark} [{label}] {ket}")
    lines += ["", sep, f"TOTAL TEST : {total}", f"PASSED     : {passed}",
              f"FAILED     : {failed}", f"STATUS     : {status}", sep]
    print("\n" + "\n".join(lines))
