# Locator HSS > Safety — LENGKAP

Hasil scan website OPEL (2026-08-20, v2.6.7). Data mentah per halaman:
`reports/scan/safety/*.md / *.json / *.png`.

## Struktur menu HSS > Safety

```
HSS
└─ Safety
   ├─ Reporting
   │  ├─ Lagging Indicator                  /Reporting/Timesheet/MonthlyReport/View?Id=1306
   │  ├─ GOLDEN RULES RECAP                 /Reporting/Timesheet/YearlyReport/View?Id=1324
   │  ├─ EMERGENCY DRILL Recap              /Reporting/Timesheet/YearlyReport/View?Id=1325
   │  ├─ MWT RECAPITULATION                 /Reporting/Timesheet/YearlyReport/View?Id=1323
   │  └─ Safety Recap.                      /Reporting/Supersafe/HSSE/ReportingSafetyRecap  (custom)
   └─ Transaction
      ├─ Leading Indicator
      │  ├─ Incident Management (SUBGROUP -- 2026-08-31, probe menu_href)
      │  │  ├─ Incident Investigation Form     /Reporting/Timesheet/DailyReport/Edit?Id=1334
      │  │  ├─ Initial Incident/Accident Report/Reporting/Timesheet/DailyReport/Edit?Id=1335
      │  │  └─ Witness Statement Report        /Reporting/Timesheet/DailyReport/Edit?Id=1336
      │  ├─ EMERGENCY DRILL Daily           /Reporting/Timesheet/MonthlyReport/Edit?Id=1319
      │  ├─ Master Alat keselamatan Operasi /Reporting/Timesheet/StaticReport/Edit?Id=1321
      │  ├─ SOC RECAPITULATION              /Reporting/Timesheet/YearlyReport/Edit?Id=1310
      │  ├─ GOLDEN RULES                    /Reporting/Timesheet/MonthlyReport/Edit?Id=1316
      │  ├─ Data Rekap Statistik K3         /Reporting/Timesheet/YearlyReport/Edit?Id=1315
      │  ├─ SAFETY/KKP/P2K3 COMMITTEE MTG   /Reporting/Timesheet/YearlyReport/Edit?Id=1313
      │  ├─ MWT DAILY                       /Reporting/Timesheet/MonthlyReport/Edit?Id=1312
      │  └─ Leading Indicator               /Reporting/Timesheet/StaticReport/Edit?Id=1309
      └─ Lagging Indicator
         ├─ Statistic Safety Recapitulation /Reporting/Timesheet/MonthlyReport/Edit?Id=1317
         ├─ SMK3                            /Reporting/Timesheet/YearlyReport/Edit?Id=1308
         └─ SMKP                            /Reporting/Timesheet/YearlyReport/Edit?Id=1307
```

CATATAN navigasi menu (2026-08-31, tools/probe_menu_href.py):
- Sidebar pakai ACCORDION: membuka satu submenu menutup submenu lain.
- Teks menu DUPLIKAT: 'Reporting' dipakai Health DAN Safety; 'Transaction'
  dipakai menu level-atas DAN HSS>Safety. Cek state pakai rantai
  berjenjang (buka_submenu(..., rantai=...)).
- Link halaman di sidebar href-nya RELATIF ('Reporting/...') kecuali
  halaman Supersafe (Safety Recap) yang ABSOLUT ('/Reporting/...').

Page object: satu file per halaman di `pages/safety_*_page.py`
(generated dari scan oleh `tools/generate_safety_pages.py`).

## Locator universal (hampir semua halaman)

### Toolbar / filter

| Nama | Locator | Catatan |
|---|---|---|
| FILTER_TANGGAL | `#tbDate` | Input tanggal. Format bulanan `2026-08`, tahunan `2026`. TIDAK ada di halaman Static Input (Master Alat, Leading Indicator) |
| FILTER_UNIT | `#cbDistrict` | Select unit/distrik (opsi seperti `[AT10] KANTOR PUSAT`) |
| BTN_RELOAD_DATA | `#btnReloadData` | Tombol "Reload Data". CATATAN 2026-08-26: aplikasi DEV kini merender tombol ini di dalam `div.panel-tag.d-none` (display:none) di hampir semua halaman -- hanya Master Alat Keselamatan Operasi yang masih menampilkannya. Halaman yang tidak menampilkan tombol ini TIDAK dimasukkan daftar harapan toolbar (lihat `TOMBOL_HALAMAN`) |
| BTN_EXPORT | `#btnExport` | Tombol "Export" |
| BTN_SUBMIT | `#btnSubmit` | Tombol "Submit Changes" (halaman Edit) |
| BTN_CANCEL_GRID | `#btnCancel` | Tombol "Cancel" grid |
| BTN_CREATE | `//button[normalize-space(.)='Create']` | Teks saja, tanpa id |
| BTN_CREATE_FORM | `//button[normalize-space(.)='Create with Form']` | idem |
| BTN_IMPORT | `//button[normalize-space(.)='Import']` | idem |
| BTN_FULLSCREEN | `//button[normalize-space(.)='FullScreen']` | idem |
| BTN_COLUMNS | `//button[normalize-space(.)='Columns']` | idem |

### Tabel DataTables

- Tabel utama : `table.reportData.dataTable`
  (DataTables membuat 2-3 tabel klon: scrollHead + scrollBody —
  gunakan yang tampil, lihat `find_visible_among()`)
- Kolom : `th[data-name='<data-name>']` ← **paling stabil**, 1:1 dengan
  backend. Daftar lengkap per halaman ada di dict `KOLOM` tiap
  `pages/safety_*_page.py` (mis. `SafetySmk3Page.KOLOM`).
- Baris data : `table.reportData tbody tr`
- Pencarian DataTables : `input[type='search']` (halaman Safety Recap
  memakai `input[placeholder='Search']`)

### Tab internal halaman

Id tab dinamis (`#linkTab-<DataTemplateId>`) — klik pakai TEKS tab
yang terlihat: `//a[contains(@class,'nav-link')][normalize-space(.)='<teks>']`

| Halaman | Tab |
|---|---|
| Incident Investigation Form | Data Insiden, Data Korban, Fakta & Analisis Penyebab, Kesimpulan & Usulan Investigasi, Rekomendasi & Tindakan Perbaikan, Saksi & Tim Investigasi |
| Data Rekap Statistik K3 | Frequency Rate, Severity Rate, TRIR, Fatality Rate |
| Witness Statement Report | Keterangan Saksi, Pertanyaan Wawancara |
| Safety Recap | Bulanan, Tahunan |

### Modal Import (id stabil — sama di semua halaman transaction)

| Nama | Locator |
|---|---|
| Modal | `#modalImport` (`.modal.show`) |
| Form | `#importForm` (POST `?handler=Import`, enctype multipart) |
| Download Template | `#linkDownloadTemplate` |
| Input file | `#imgFileImport` (accept `.xlsx`) |
| Tombol Import | `#btnImport` |
| Tombol Close | tombol teks "Close" di dalam `.modal.show` |

### Modal Create with Form (id dinamis — cari lewat LABEL)

- Modal : `.modal.show` (id `modal_<N>` auto-generate)
- Field : id `input_<N>` / `cb<...>_<N>` auto-generate →
  **cari lewat label**:
  `//div[contains(@class,'modal') and contains(@class,'show')]//label[normalize-space(.)='<Label>']/following-sibling::*//*[self::input or self::select or self::textarea]`
- Tombol Save : `#btnSave_<N>` (dinamis) → pakai teks "Save" di `.modal.show`
- Tombol Cancel : teks "Cancel" di `.modal.show`

## Halaman khusus: Safety Recap (custom, bukan pola Timesheet)

| Nama | Locator |
|---|---|
| Tabel Bulanan | `#tableBulanan` |
| Tabel Tahunan | `#tableTahunan` (hidden kalau view Bulanan aktif) |
| Link Bulanan | `#linkBulanan` |
| Link Tahunan | `#linkTahunan` |
| Filter bulan | `#cbMonths` (January..December) |
| Filter tahun | `#cbYears` (2020..2026) |
| Pencarian | `input[placeholder='Search']` |
| Export Excel | `//button[normalize-space(.)='Export Excel']` |

## Catatan penting

1. **Halaman lambat sesekali**: navigasi cepat antar halaman kadang
   bikin SPA stuck di loading overlay → `buka_halaman()` di
   `hss_safety_page.py` sudah retry 1x + `LONG_TIMEOUT` 60s.
2. **Modal field pakai label**, id field auto-generate berubah tiap
   kali modal dibuka.
3. **Grid halaman Edit vs View**: halaman View (Reporting) hanya baca;
   halaman Edit (Transaction) punya tombol Create/Import/Submit.
4. **Select Finding** hanya ada di halaman SOC RECAPITULATION.
5. Chat kolaborasi (`#collab-chat-window`) ada di SEMUA halaman
   Timesheet — bukan bagian dari konten yang diuji.
