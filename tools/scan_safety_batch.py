"""
tools/scan_safety_batch.py
==========================
Batch scanner untuk SEMUA halaman bagian Safety di menu HSS website
OPEL. Menavigasi satu per satu ke tiap halaman Reporting & Transaction
dan menyimpan hasil scan locator (md + json + screenshot) ke
reports/scan/safety/.

Daftar halaman diambil dari struktur menu HSS (hasil eksplorasi manual
via tools/opel_drive.py) -- lihat safety_pages di bawah.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.opel_drive import attach, scan_now

BASE = "https://dev-opel.antm.tech"

# Struktur menu HSS > Safety (teks menu, url, kategori).
# url relatif -> digabung dengan BASE.
SAFETY_PAGES = [
    # ---------------- Reporting ----------------
    ("Lagging Indicator",              "Reporting/Timesheet/MonthlyReport/View?Id=1306", "reporting"),
    ("GOLDEN RULES RECAP",             "Reporting/Timesheet/YearlyReport/View?Id=1324",  "reporting"),
    ("EMERGENCY DRILL Recap",          "Reporting/Timesheet/YearlyReport/View?Id=1325",  "reporting"),
    ("MWT RECAPITULATION",             "Reporting/Timesheet/YearlyReport/View?Id=1323",  "reporting"),
    ("Safety Recap.",                  "/Reporting/Supersafe/HSSE/ReportingSafetyRecap", "reporting"),
    # ---------------- Transaction > Leading Indicator ----------------
    ("Incident Investigation Form",    "Reporting/Timesheet/DailyReport/Edit?Id=1334",   "leading"),
    ("Initial Incident/Accident Report","Reporting/Timesheet/DailyReport/Edit?Id=1335",  "leading"),
    ("Witness Statement Report",       "Reporting/Timesheet/DailyReport/Edit?Id=1336",   "leading"),
    ("EMERGENCY DRILL Daily",          "Reporting/Timesheet/MonthlyReport/Edit?Id=1319", "leading"),
    ("Master Alat keselamatan Operasi","Reporting/Timesheet/StaticReport/Edit?Id=1321",  "leading"),
    ("SOC RECAPITULATION",             "Reporting/Timesheet/YearlyReport/Edit?Id=1310",  "leading"),
    ("GOLDEN RULES",                   "Reporting/Timesheet/MonthlyReport/Edit?Id=1316", "leading"),
    ("Data Rekap Statistik K3",        "Reporting/Timesheet/YearlyReport/Edit?Id=1315",  "leading"),
    ("SAFETY KKP P2K3 COMMITTEE MEETING","Reporting/Timesheet/YearlyReport/Edit?Id=1313","leading"),
    ("MWT DAILY",                      "Reporting/Timesheet/MonthlyReport/Edit?Id=1312", "leading"),
    ("Leading Indicator",              "Reporting/Timesheet/StaticReport/Edit?Id=1309",  "leading"),
    # ---------------- Transaction > Lagging Indicator ----------------
    ("Statistic Safety Recapitulation","Reporting/Timesheet/MonthlyReport/Edit?Id=1317", "lagging"),
    ("SMK3",                           "Reporting/Timesheet/YearlyReport/Edit?Id=1308",  "lagging"),
    ("SMKP",                           "Reporting/Timesheet/YearlyReport/Edit?Id=1307",  "lagging"),
]


def slug(teks):
    import re

    teks = re.sub(r"[^a-z0-9]+", "_", teks.lower()).strip("_")
    return teks[:50]


def main():
    driver = attach()
    driver.switch_to.window(driver.window_handles[-1])

    out_dir = Path(__file__).resolve().parent.parent / "reports" / "scan" / "safety"
    out_dir.mkdir(parents=True, exist_ok=True)

    ringkasan = []
    for idx, (menu, url, kategori) in enumerate(SAFETY_PAGES, start=1):
        full_url = url if url.startswith("http") else BASE.rstrip("/") + "/" + url.lstrip("/")
        print(f"\n[{idx}/{len(SAFETY_PAGES)}] {menu} -> {full_url}")
        try:
            driver.get(full_url)
            time.sleep(7)  # tunggu tabel/data render
            name = f"{idx:02d}_{slug(menu)}"
            data, navigasi = scan_now(driver, f"safety/{name}")
            ringkasan.append({
                "no": idx, "menu": menu, "url": full_url,
                "kategori": kategori, "elemen": len(data), "link": len(navigasi),
                "title": driver.title, "status": "ok",
            })
        except Exception as exc:
            print(f"  [GAGAL] {exc}")
            ringkasan.append({"no": idx, "menu": menu, "url": full_url,
                              "kategori": kategori, "status": f"gagal: {exc}"})

    import json

    (out_dir / "_ringkasan.json").write_text(
        json.dumps(ringkasan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\n" + "=" * 70)
    print("RINGKASAN")
    print("=" * 70)
    for r in ringkasan:
        print(f"{r['no']:>2}. {r['menu'][:50]:<52} {r['status']:<10} elemen={r.get('elemen','-')}")


if __name__ == "__main__":
    main()
