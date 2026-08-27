# Automation Testing OPEL

Automation Selenium untuk aplikasi **OPEL** di `https://dev-opel.antm.tech/`
(diadaptasi dari project NewDLA).

## Yang beda dari NewDLA

| Aspek | NewDLA | OPEL |
|---|---|---|
| Login | Google SSO | **Auto-auth di DEV** (cookie ASP.NET langsung diterbitkan, 1 redirect ke `/My/Dashboard`). Form Azure AD B2C tidak pernah muncul di DEV -- locator B2C hanya cadangan deteksi |
| Framework front-end | ExtJS | **SmartAdmin (Bootstrap 4) + jQuery + DataTables** (`table.reportData.dataTable`) |
| Modul teruji | 14 modul lengkap | Login + **HSS Safety (19 halaman)** |

## Struktur folder

- `config/config.py` — BASE_URL, CHROME_PROFILE_PATH, timeout (override lewat env `OPEL_*`)
- `pages/base_page.py` — helper Selenium generic (klik, ketik, tunggu elemen, screenshot)
- `pages/login_page.py` — alur login + topbar (avatar, notifikasi, logout)
- `pages/hss_safety_page.py` — locator umum halaman Safety (toolbar, tabel, tab, modal)
- `pages/safety_*_page.py` — **19 page object**, satu per sub-halaman Safety
- `tests/test_e2e_opel.py` — `test_login`
- `tests/test_safety.py` — test smoke SEMUA halaman Safety + modal Import
- `locators/login.md`, `locators/hss_safety.md` — dokumentasi locator hasil scan
- `reports/scan/` — hasil scan mentah per halaman (md/json/png)
- `tools/` — scanner & helper eksplorasi (lihat bawah)

## Tools eksplorasi (scan locator)

Pola NewDLA: Chrome dibuka manual dengan remote debugging, lalu
scanner menempel ke sesi yang sama:

1. Tutup semua Chrome, lalu buka:
   `chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\selenium-chrome-profile-opel"`
2. Login manual sekali ke OPEL (kalau diminta).
3. Jalankan scanner:
   - `python tools/scan_locators_opel.py --name <nama>` — scan halaman aktif
   - `python tools/scan_safety_batch.py` — scan ulang SEMUA 19 halaman Safety
   - `python tools/locator.py` — ringkasan ID stabil per halaman
   - `python tools/generate_safety_pages.py` — regenerate page object dari hasil scan
   - `python tools/opel_drive.py` — helper navigasi interaktif (eksplorasi)

## Menjalankan test

```bash
pip install -r requirements.txt
pytest                          # seluruh alur
pytest -k safety                # hanya modul Safety
pytest -k safety_smk3           # satu halaman saja
pytest -m safety_view           # hanya halaman view/reporting
```

## Catatan hasil scan (2026-08-20, v2.6.7)

- **Kolom tabel paling stabil**: `th[data-name='...']` (1:1 dengan backend) --
  daftar lengkap di dict `KOLOM` tiap `pages/safety_*_page.py`.
- **Modal Import** punya id stabil (`#modalImport`, `#linkDownloadTemplate`,
  `#imgFileImport`, `#btnImport`).
- **Modal Create with Form** id-nya auto-generate (`input_NNNNN`) --
  field dicari lewat teks label (helper `isi_field_modal()`).
- **Navigasi cepat antar halaman** kadang bikin SPA stuck di loading
  overlay -- `buka_halaman()` sudah retry 1x + LONG_TIMEOUT 60s.
- Detail lengkap: `locators/hss_safety.md` dan `locators/login.md`.

## Catatan tambahan (2026-08-26)

- Tombol **Reload Data** kini hanya ditampilkan aplikasi di halaman
  Master Alat Keselamatan Operasi -- di halaman lain tombolnya
  dirender di dalam `div.panel-tag.d-none` (tersembunyi, 0x0 px).
  Daftar harapan toolbar per halaman (`TOMBOL_HALAMAN` di
  `hss_safety_page.py`) sudah disesuaikan.
- Halaman **Statistic Safety Recapitulation** (template MonthlyReport)
  tidak menyimpan perubahan inline lewat Submit Changes (ketikan masuk
  sel tapi nilai kembali ke awal setelah reload) -- beda dari SMK3/SMKP
  (YearlyReport) yang menyimpan normal. Test edit di halaman itu
  memverifikasi data TIDAK rusak, bukan tersimpan.
- Eksport & buka modal kadang tidak terpicu saat sesi panjang (SPA
  stuck) -- `export_dan_tunggu_file()` retry 3x dan
  `_klik_dan_tunggu_modal()` fallback navigasi ulang.

## Catatan tambahan (2026-08-27)

- **Anchor edit lagging smk3/smkp**: field target di baris Juli ternyata
  KOSONG di data DEV (PPkomKetidaksesuaianMaj SMK3 & Deskripsi SMKP,
  dicek tools/probe_masalah14.py) -- test sekarang pindah OTOMATIS ke
  bulan lain yang field-nya terisi (`cari_anchor_field_terisi()`),
  edit tetap dites sungguhan lalu di-revert.
- **Menu sidebar di halaman Timesheet**: klik `b.collapse-sign` native
  TIDAK mempan di halaman YearlyReport Edit (padahal di dashboard
  mempan) -- `buka_submenu()` sekarang klik MOUSE asli (ActionChains)
  berurutan sign -> span, dan test menu mulai dari dashboard dulu
  (Chrome me-restore tab sesi lama dari profil).
- **Export Incident Investigation** memang tidak menghasilkan file
  (probe 12) -- tombol Export tetap diklik, verifikasi file dilewati
  lewat `EXPORT_TANPA_FILE` (sekarang benar-benar dipakai di
  `coba_tombol()`).
- Hasil full suite 2026-08-27: **67/68 hijau**; sisa 1 (menu) sudah
  diperbaiki & diverifikasi terpisah.

## Langkah selanjutnya

1. Jalankan `pytest -k safety` untuk memvalidasi semua page object.
2. Lengkapi test aksi (Create/Import/Export) per halaman sesuai
   `TestCase Web OPEL SAFETY.xlsx`.
3. Isi data uji riil di `data/test_data.json` untuk test negatif/positif.
