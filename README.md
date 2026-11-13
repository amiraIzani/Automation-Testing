# Automation Testing OPEL

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12.10-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12.10">
  <img src="https://img.shields.io/badge/Selenium-4.47.0-43B02A?style=flat-square&logo=selenium&logoColor=white" alt="Selenium 4.47.0">
  <img src="https://img.shields.io/badge/Pytest-8.4.2-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="Pytest 8.4.2">
  <img src="https://img.shields.io/badge/Run%207%20Sep-94%20passed%20%C2%B7%2013%20skipped%20%C2%B7%200%20failed-2EA043?style=flat-square" alt="Run 7 Sep: 94 passed, 13 skipped, 0 failed">
</p>

## Gambaran Umum

Proyek ini adalah automation testing untuk modul **Safety** pada
aplikasi **OPEL** (`https://dev-opel.antm.tech/`), sebuah SPA berbasis
**SmartAdmin (Bootstrap 4) + jQuery + DataTables**, dibangun dengan
**Python** dan **Selenium WebDriver** di atas framework **Pytest**, serta
menerapkan pendekatan **Page Object Model (POM)** dan **data-driven
testing**. Seluruh alur pengujian dijalankan dalam **satu sesi browser**
tanpa perlu me-refresh halaman.

Pengujian mencakup **118 test** (117 Safety + 1 Login) yang
dikelompokkan ke dalam modul: Login, Navigasi Menu, View per Halaman,
Create/Delete, Lagging Mendalam, Halaman Lengkap, Interaksi DataTables,
Isi File Export, Validasi Form Wajib, Ganti Filter Unit, Leading, dan
Input Langsung di Tabel — untuk **19 halaman** di menu
**HSS > Safety** (5 halaman Reporting + 14 halaman Transaction).
Seluruh data uji terpusat dalam satu file sehingga mudah dipelihara dan
dapat diganti tanpa mengubah kode.

Untuk setiap halaman, alur "Halaman Lengkap" menguji halaman secara
menyeluruh: navigasi melalui menu sidebar (bukan URL langsung), tabel
data tampil, seluruh tab internal dibuka satu per satu dengan
pengecekan toolbar di setiap tab, kemudian seluruh tombol fitur
dijalankan — termasuk Export (file diverifikasi terunduh), Import
(file dummy dipasang pada input upload **tanpa dikirim ke server**),
Columns (dropdown dibuka dan item Settings diklik), FullScreen,
Create with Form (form diisi data dummy otomatis lalu disimpan), dan
Create (draft dibuat lalu dibatalkan). Data dummy yang dibuat pada
lingkungan DEV menggunakan penanda unik agar mudah diidentifikasi.

## Status Pengujian

Saat ini suite berisi **118 test** (117 Safety + 1 Login), dihitung
dengan `pytest --collect-only` pada 11 September 2026.

Run penuh terakhir yang **diarsipkan** (`pytest -m safety`) adalah
tanggal **7 September 2026** —
`reports/run_20260907_1626.txt` / `.html`, 107 test Safety:

```
========================================
       AUTOMATION TESTING RESULT
========================================
TOTAL TEST : 107
PASSED     : 94
SKIPPED    : 13
FAILED     : 0
STATUS     : PASSED
========================================
94 passed, 13 skipped, 1 deselected in 1765.44s (0:29:25)
```

Tentang **13 SKIPPED**: semuanya diverifikasi lewat screenshot dan
memang sah — grid `No data available in table` di lingkungan DEV,
periode yang datanya belum diisi, atau fitur yang tidak berlaku di
halaman tersebut. Bukan test yang menghindar dari kegagalan.

Catatan jujur soal cakupan: karena banyak halaman DEV kosong, angka
PASSED tidak berarti setiap fitur terverifikasi penuh. `pytest -m
safety_datatables` mencetak baris `[CAKUPAN DataTables]` yang menyebut
bagian mana yang benar-benar diuji per halaman dan bagian mana yang
dilewati karena tidak ada datanya.

<details>
<summary>Riwayat: hasil run 31 Agustus 2026 (45 test, sebelum merge)</summary>

```
========================================
       AUTOMATION TESTING RESULT
========================================
V [Safety - Navigasi Menu] berhasil
V [Safety - Lagging Indicator (View)] berhasil
V [Safety - Golden Rules Recap (View)] berhasil
V [Safety - Emergency Drill Recap (View)] berhasil
V [Safety - MWT Recapitulation (View)] berhasil
V [Safety - Safety Recap (View)] berhasil
V [Safety - Incident Investigation Form] berhasil
V [Safety - Incident Investigation (Tab)] berhasil
V [Safety - Initial Incident/Accident Report] berhasil
V [Safety - Witness Statement Report] berhasil
V [Safety - Emergency Drill Daily] berhasil
V [Safety - Master Alat Keselamatan Operasi] berhasil
V [Safety - Master Alat (Create with Form)] berhasil
V [Safety - Master Alat (Delete)] berhasil
V [Safety - SOC Recapitulation] berhasil
V [Safety - Golden Rules] berhasil
V [Safety - Data Rekap Statistik K3] berhasil
V [Safety - SAFETY/KKP/P2K3 Committee Meeting] berhasil
V [Safety - MWT Daily] berhasil
V [Safety - Leading Indicator] berhasil
V [Safety - Statistic Safety Recapitulation] berhasil
V [Safety - SMK3] berhasil
V [Safety - SMKP] berhasil
V [Safety - Lagging (Semua Fitur) [statistic_safety_recapitulation]] berhasil
V [Safety - Lagging (Semua Fitur) [smk3]] berhasil
V [Safety - Lagging (Semua Fitur) [smkp]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Lagging Indicator]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Golden Rules Recap]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Emergency Drill Recap]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [MWT Recapitulation]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Safety Recap]] berhasil
X [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Incident Investigation]] GAGAL
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Initial Incident/Accident]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Witness Statement]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Emergency Drill Daily]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Master Alat Keselamatan]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [SOC Recapitulation]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Golden Rules]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Data Rekap Statistik K3]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [KKP/P2K3 Committee Meeting]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [MWT Daily]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Leading Indicator]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [Statistic Safety Recap]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [SMK3]] berhasil
V [Safety - Halaman Lengkap (Tabel+Tab+Tombol) [SMKP]] berhasil
========================================
TOTAL TEST : 45
PASSED     : 44
FAILED     : 1
STATUS     : FAILED
========================================
```

Tindak lanjut dari 1 kegagalan di atas:

| Kegagalan | Akar masalah | Tindak lanjut |
|---|---|---|
| Incident Investigation — modal Import tidak terdeteksi terbuka | Deteksi modal memakai `is_displayed()` yang bernilai negatif palsu saat sesi panjang (modal sebenarnya terbuka) | Deteksi modal diganti menjadi pemeriksaan computed style JS (`_ada_modal_tampil()`), lalu test dijalankan ulang dan **lulus** (log `run_cek_incident.txt`) |
| Master Alat (Create with Form) — gagal 1 kali pada run parsial sesi panjang (flaky) | Quirk SPA pada sesi yang sangat panjang | Dijalankan ulang dan **lulus** (log `run_cek_master_alat.txt`) |

Dengan demikian seluruh **45 test saat itu terverifikasi lulus**.

</details>

## Alur Pengujian

Berikut urutan langkah pengujian sesuai isi `tests/test_e2e_opel.py`
dan `tests/test_safety.py`, dikelompokkan per modul:

| Modul | Test method | Alur / yang diperiksa |
|---|---|---|
| Login | `test_login` | Buka OPEL → sesi login dari profil Chrome (Azure AD B2C → Google SSO, login manual sekali) → halaman utama tampil. Tidak ikut `-m safety` |
| Navigasi Menu | `test_safety_menu_dan_landing` | Dashboard → klik HSS → Safety → buka sub **Reporting** dan **Transaction** → link halaman muncul di sidebar |
| View (Reporting, 5 halaman) | `test_safety_*_view` | Buka halaman → **kontrak grid** diperiksa (lihat di bawah) → filter tanggal/unit tampil |
| View (Transaction, 14 halaman) | `test_safety_*_view` | Buka halaman → **kontrak grid** diperiksa; halaman bertab → tab internal aktif |
| Master Alat | `test_safety_master_alat_create` | Create with Form → isi dummy otomatis (Equipment No unik) → Save → Submit → penanda muncul di grid |
| Master Alat | `test_safety_master_alat_delete` | Delete baris dummy → konfirmasi Yes → baris hilang dari grid |
| Lagging Mendalam (5 halaman) | `test_safety_lagging_deep` | Edit sel grid + Submit Changes → verifikasi tersimpan → **revert**; edit tanpa Submit → **Reload Data wajib membuang draft lokal**; filter tanggal (isi grid harus ikut berubah); filter unit; Export (file terunduh); Import (modal + template terunduh). Halaman: Statistic Safety Recap, SMK3, SMKP, Data Rekap Statistik K3, Leading Indicator — dua terakhir mencari baris anchor otomatis saat run |
| Halaman Lengkap (19 halaman) | `test_safety_halaman_lengkap` | Alur lengkap satu halaman dalam satu kunjungan (lihat rincian di bawah) |
| Interaksi DataTables | `test_safety_datatables_interaksi` | Sort kolom asc/desc, pagination, Search (DOM + API), show/hide kolom — per halaman ber-grid |
| Isi File Export | `test_safety_export_isi_file` | Export → workbook `.xlsx` bisa dibuka, punya ≥1 baris terisi, **dan nilai selnya cocok dengan data yang tampil di grid** |
| Validasi Form Wajib | `test_safety_create_form_validasi` | Create with Form disimpan KOSONG → form harus menolak (modal tetap terbuka / pesan validasi). Hanya berlaku di **2 dari 9** halaman — 7 sisanya memang dibolehkan menyimpan baris kosong (lihat `FORM_TANPA_VALIDASI_WAJIB`), jadi di-skip |
| Ganti Filter Unit | `test_safety_filter_unit_ganti` | Filter unit benar-benar DIGANTI ke opsi lain, **isi grid harus ikut berubah**, tabel tetap tampil, lalu dikembalikan |
| Leading (Alur Menengah) | `test_safety_leading_deep` | View → filter tanggal (**isi grid harus ikut berubah**) → filter unit (elemen+opsi). Export & Import **sengaja tidak diuji di sini** — sudah dicakup `test_safety_export_isi_file` dan `test_safety_halaman_lengkap` |
| Input Langsung di Tabel (9 halaman) | `test_safety_create_inline` | Create (baris draft kosong) → **isi kolomnya langsung di grid** (teks, angka, tanggal, select, textarea; penanda `INLINE-<HHMMSS>`) → Submit Changes → **Reload Data** → baris tersimpan di server → baris dihapus lagi. Kalau baris ditolak **validasi field wajib** (pesan aplikasi tertangkap), test di-skip — itu perilaku aplikasi yang benar, bukan gagal simpan |

**Kontrak grid** (`_assert_grid_sesuai_kontrak`, dipakai seluruh test
`*_view` dan test Export) memeriksa tiga hal, bukan sekadar "tabelnya
muncul":

1. tabel report tampil;
2. grid me-render **semua kolom** yang terdokumentasi di atribut `KOLOM`
   milik page object — kolom yang dihapus/di-rename backend langsung
   ketahuan;
3. kalau DataTables melaporkan ada *N* record, `tbody` **wajib** merender
   baris — kasus "backend bilang ada data tapi tabel kosong" sebelumnya
   lolos total dari suite ini.

Rincian alur `test_safety_halaman_lengkap` untuk setiap halaman:

1. **Navigasi menu sidebar** — dashboard → HSS → Safety → sub Reporting
   / Transaction → klik link halaman (bukan URL langsung).
2. **Tabel** — tabel report benar-benar tampil (data selesai dimuat).
3. **Tab demi tab** — setiap tab internal diklik dan dipastikan aktif;
   tombol toolbar diperiksa tampil di tab tersebut; seluruh tombol
   fitur dijalankan di tab tersebut juga (kecuali tombol pembuat data
   dan Cancel, yang hanya dijalankan di tab utama).
4. **Semua tombol fitur** — dijalankan satu per satu sesuai urutan
   daftar per halaman: Reload Data, Import (modal dibuka + file dummy
   dipasang pada input upload, **tidak dikirim**), Create with Form
   (form diisi dummy otomatis → Save → Submit → penanda diverifikasi
   muncul di grid), Create (baris draft dibuat lalu Cancel), Submit
   Changes, Export (file diunduh dan diverifikasi), Select Finding
   (SOC), Columns (dropdown dibuka → item **Settings** diklik → modal
   Freeze Column dibuka lalu ditutup), FullScreen (masuk lalu keluar),
   Cancel, dan Export Excel (Safety Recap). Link Instructions sengaja
   **tidak** diklik.

> **Catatan:** langkah-langkah berjalan berurutan sesuai urutan menu
> sidebar dalam satu sesi browser yang sama. Test Halaman Lengkap
> membuat data dummy sungguhan pada lingkungan DEV — data tersebut
> menggunakan penanda `Dummy <HHMMSS>` agar mudah dikenali.

## Arsitektur

```
conftest.py (fixture driver session + test_data + hook screenshot)
    │
    ▼
tests/test_e2e_opel.py ──memanggil──▶  page object (pages/*_page.py)
tests/test_safety.py        │                                        │
    │  data dari test_data.json                                       ▼
    ▼                                             base_page.py (helper Selenium)
Selenium WebDriver ──▶ Chrome (aplikasi OPEL, SPA SmartAdmin + DataTables)
```

1. **Page Object Model (POM)** — setiap halaman memiliki satu kelas di
   `pages/` yang berisi locator dan method aksi. Test tidak berinteraksi
   langsung dengan Selenium, melainkan hanya memanggil method tingkat
   tinggi dari page object.
2. **Inheritance bertingkat** — logika yang dipakai banyak halaman
   dinaikkan ke parent class: `BasePage` (helper umum) →
   `HssSafetyPage` (toolbar, tabel, tab, modal, alur tombol) →
   19 kelas halaman Safety. Seluruh halaman memakai locator hasil scan
   website OPEL yang terdokumentasi di `locators/hss_safety.md`.
3. **Data-driven** — seluruh data uji terpusat di
   `data/test_data.json` dan dimuat melalui fixture `test_data` di
   `conftest.py`, sehingga data uji dapat diganti tanpa mengubah kode.
4. **Satu sesi browser** — fixture `driver` ber-scope `session` di
   `conftest.py`, sehingga Chrome dibuka satu kali untuk seluruh alur.
   Hook `pytest_runtest_makereport` otomatis mengambil screenshot saat
   test gagal dan mencetak kotak "AUTOMATION TESTING RESULT" di akhir
   pengujian.
5. **Helper khusus OPEL** — karena OPEL adalah SPA dengan DataTables,
   modal yang di-render ulang, dan animasi fade, `BasePage` dan
   `HssSafetyPage` menyediakan helper seperti `find_visible_among()`
   (mencari elemen yang benar-benar tampil), `click_js_saat_tampil()`
   (klik JS setelah elemen tampil menurut computed style), deteksi
   modal berbasis computed style JS (`_ada_modal_tampil()`), penanganan
   dialog konfirmasi (`jawab_konfirmasi()`), dan navigasi menu sidebar
   dengan toleransi quirk aplikasi (`buka_submenu()`).

## Struktur Kode

### Peta Kelas (Inheritance)

```
BasePage                                   <- fondasi seluruh halaman
├── LoginPage                              <- Login (sesi profil Chrome; Azure AD B2C → Google SSO)
└── HssSafetyPage                          <- locator & alur umum seluruh halaman Safety
    ├── SafetyLaggingIndicatorPage         <- Reporting (View)
    ├── SafetyGoldenRulesRecapPage
    ├── SafetyEmergencyDrillRecapPage
    ├── SafetyMwtRecapitulationPage
    ├── SafetyRecapPage                    <- halaman custom Supersafe
    ├── SafetyIncidentInvestigationFormPage
    ├── SafetyInitialIncidentAccidentReportPage
    ├── SafetyWitnessStatementReportPage
    ├── SafetyEmergencyDrillDailyPage
    ├── SafetyMasterAlatKeselamatanOperasiPage
    ├── SafetySocRecapitulationPage
    ├── SafetyGoldenRulesPage
    ├── SafetyDataRekapStatistikK3Page
    ├── SafetyKkpP2k3CommitteeMeetingPage
    ├── SafetyMwtDailyPage
    ├── SafetyLeadingIndicatorPage
    ├── SafetyStatisticSafetyRecapitulationPage
    ├── SafetySmk3Page
    └── SafetySmkpPage
```

Kelas yang berada di bawah mewarisi seluruh method dari kelas di
atasnya. Sebagai contoh, `SafetySmk3Page` otomatis memiliki method dari
`HssSafetyPage` dan `BasePage`.

### Isi Setiap File Penting

| File | Method utama |
|---|---|
| `base_page.py` | `_wait()`, `pace()`, `find()`, `find_all()`, `find_visible_among()`, `_ambil_js_visible()`, `click_js_saat_tampil()`, `is_any_visible()`, `wait_hilang()`, `type_text_visible()`, `select_option()` |
| `hss_safety_page.py` | `buka_via_menu()`, `buka_halaman()`, `buka_submenu()`, `coba_tombol()`, `cek_tombol_toolbar()`, `klik_tab()`, `buka_modal_import()`, `pasang_file_dummy_import()`, `buka_form_create()`, `isi_form_create_otomatis()`, `upload_file_dummy()`, `simpan_form()`, `submit_changes()`, `export_dan_tunggu_file()`, `klik_item_columns()`, `toggle_fullscreen()`, `klik_create_lalu_batal()`, `isi_sel_grid_anchor()`, `jawab_konfirmasi()` |
| `login_page.py` | `login()` — buka OPEL dengan sesi profil Chrome lalu tunggu halaman utama; **tidak pernah** mengisi form login |
| `conftest.py` | Fixture `driver` (session), fixture `test_data`, marker template otomatis (`pytest_collection_modifyitems`), hook screenshot saat gagal/skip, pemetaan label hasil (`STEP_LABELS`), dan kotak "AUTOMATION TESTING RESULT" |

### Pola Alur Setiap Test

Test hanya memanggil method tingkat tinggi dari page object; method
tersebut di dalamnya menggunakan method dasar dari `BasePage`:

```
test → page method (tingkat tinggi) → BasePage method (tingkat rendah)
```

Apabila sebuah method tidak ditemukan di file page yang sedang dibaca,
method tersebut diwarisi dari parent class-nya (lihat peta kelas di
atas).

## Struktur Folder

```
Automation-Testing/
├── conftest.py                       <- driver session-scoped, marker template otomatis, ringkasan hasil
├── pytest.ini                        <- konfigurasi pytest, daftar marker, laporan HTML otomatis
├── requirements.txt                  <- daftar dependency Python
├── README.md                         <- dokumentasi proyek (file ini)
├── .gitignore                        <- pola file yang tidak di-commit
├── run_cek_incident.txt              <- log verifikasi ulang (riwayat 31 Agustus)
├── run_cek_master_alat.txt           <- log verifikasi ulang (riwayat 31 Agustus)
├── config/
│   └── config.py                     <- URL, timeout, profil Chrome, mode headless
├── data/
│   └── test_data.json                <- seluruh data uji (menu, tab, filter, penanda)
├── locators/
│   ├── hss_safety.md                 <- dokumentasi locator hasil scan halaman Safety
│   └── login.md                      <- dokumentasi locator alur login
├── pages/
│   ├── base_page.py                  <- fungsi dasar Selenium (klik, ketik, tunggu)
│   ├── login_page.py                 <- Login
│   ├── hss_safety_page.py            <- locator & alur umum seluruh halaman Safety
│   └── safety_*_page.py              <- 19 page object, satu per sub-halaman Safety
├── tests/
│   ├── test_e2e_opel.py              <- alur Login
│   └── test_safety.py                <- seluruh test modul HSS > Safety
├── tools/                            <- skrip bantu manual (bukan pytest), lihat tools/README.md
│   ├── README.md                     <- daftar & kegunaan tiap skrip
│   ├── cek_simpan_inline.py          <- cek edit inline benar-benar tersimpan (baca lewat Reload Data)
│   ├── cek_grid_semua_halaman.py     <- daftar tabel grid yang dirender tiap halaman
│   ├── cleanup_dummy_master_alat.py  <- hapus baris dummy di Master Alat (--dry-run)
│   ├── cleanup_dummy_semua.py        <- hapus baris dummy di semua halaman Safety
│   ├── probe_columns.py              <- diagnosa item dropdown Columns
│   ├── probe_menu_href.py            <- diagnosa link menu sidebar
│   ├── scan_locators_opel.py         <- scan locator halaman aktif (Chrome port 9222)
│   ├── scan_safety_batch.py          <- scan ulang seluruh 19 halaman Safety
│   ├── scan_form_safety.py           <- scan field form create
│   ├── generate_safety_pages.py      <- pembuat page object dari hasil scan
│   ├── locator.py                    <- ringkasan ID stabil per halaman
│   └── opel_drive.py                 <- helper eksplorasi interaktif
└── reports/
    ├── bugs/                         <- laporan bug aplikasi + indeks status (bugs/README.md)
    ├── scan/                         <- output skrip scan di tools/
    ├── report.html                   <- laporan pytest-html run TERAKHIR (ditimpa tiap run, tidak di-commit)
    ├── run_<tanggal>.html / .txt     <- arsip run penting, mis. run_20260907_1626
    ├── laporan_safety.html           <- laporan formal hasil pengujian
    ├── dummy_upload.png              <- file dummy untuk field upload form
    ├── screenshots/                  <- screenshot saat test gagal/skip + potret saat kejadian
    └── downloads/                    <- file export/template hasil test (dibuat ulang otomatis)
```

| Bagian | Fungsi |
|---|---|
| `pages/` | Menyimpan locator serta aksi/interaksi pada setiap halaman |
| `tests/` | Berisi skenario pengujian |
| `conftest.py` | Mengatur driver, fixture, hasil PASS/FAIL, dan screenshot |
| `data/` | Menyimpan data yang digunakan untuk pengujian |
| `config/` | Menyimpan URL, timeout, dan konfigurasi lainnya |
| `locators/` | Dokumentasi locator hasil scan website |
| `tools/` | Skrip bantu manual: diagnosa, pembersih data DEV, scanner locator — lihat [`tools/README.md`](tools/README.md) |
| `reports/` | Menyimpan hasil dan laporan pengujian |

## Setup

### 1. Install

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

> **Versi yang teruji pada proyek ini:** Python 3.12.10 · Selenium
> 4.47.0 · Pytest 8.4.2 · pytest-html 4.2.0 · openpyxl 3.1.5
> (Windows 11; Python & Pytest sesuai metadata run 7 September).
>
> **Prasyarat:** Google Chrome terinstal, dan akun Google yang
> terdaftar di OPEL. Login (termasuk di DEV) harus dilakukan **manual
> sekali** di profil Chrome yang dipakai automation — lihat bagian
> Login.

### 2. Environment Variables (Opsional)

Proyek ini tidak menggunakan file `.env`. Seluruh konfigurasi dibaca
dari environment variable melalui `os.getenv()` di `config/config.py`.
Karena setiap variabel memiliki nilai default, proyek dapat langsung
dijalankan tanpa konfigurasi tambahan:

| Variable | Default | Fungsi |
|---|---|---|
| `OPEL_BASE_URL` | `https://dev-opel.antm.tech/` | URL aplikasi yang diuji |
| `OPEL_CHROME_PROFILE` | `D:\selenium-chrome-profile-opel` | Path profil Chrome (untuk sesi login) |
| `OPEL_B2C_DOMAIN` | `antamapps.b2clogin.com` | Domain Azure AD B2C, dipakai `login_page.py` untuk menunggu redirect login selesai |
| `OPEL_HEADLESS` | `false` | `true` → Chrome tanpa jendela (untuk CI/CD) |
| `OPEL_TIMEOUT` | `15` | Timeout default WebDriverWait (detik) |
| `OPEL_LONG_TIMEOUT` | `60` | Timeout proses lambat (render grid, redirect SSO) |
| `OPEL_ACTION_PACE` | `2.0` | Jeda antar-aksi (detik) — hanya untuk kebutuhan visual, bukan untuk menunggu elemen |

Satu variabel lagi, `OPEL_MUTASI_PERIODE`, **khusus uji mutasi** dan
tidak boleh disetel saat run biasa — lihat bagian *Membuktikan test
benar-benar bisa gagal*.

Cara menyetel:

```powershell
# Windows PowerShell
$env:OPEL_HEADLESS = "true"
$env:OPEL_CHROME_PROFILE = "D:\selenium-chrome-profile-opel"
```

```bash
# Mac/Linux
export OPEL_HEADLESS=true
export OPEL_CHROME_PROFILE="/Users/nama_kamu/selenium-chrome-profile-opel"
```

> **Catatan:** variabel hanya berlaku pada sesi terminal tempat
> variabel tersebut disetel. Untuk membuatnya permanen, tuliskan pada
> profil shell (misalnya `$PROFILE` pada PowerShell).

### 3. Login (Manual, Sekali per Sesi Profil)

> **Kondisi saat ini:** DEV **tidak lagi login otomatis**. Chrome
> dengan profil tanpa sesi aktif diarahkan ke Azure AD B2C
> (`antamapps.b2clogin.com`) lalu ke **Google SSO**
> (`accounts.google.com`). Catatan lama "DEV auto-auth" (eksplorasi
> 2026-08-20) sudah tidak berlaku, walau docstring di
> `pages/login_page.py` masih menyebutnya.

Selenium **tidak pernah** mengisi form login (Google maupun B2C) —
rawan diblokir dan bisa meminta MFA. Solusinya: Chrome memakai folder
profil yang sesi login-nya sudah aktif.

1. Tutup semua jendela Chrome.
2. Jalankan Chrome dengan folder profil khusus:
   `"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="D:\selenium-chrome-profile-opel"`
3. Login secara manual lewat Google SSO dengan akun yang terdaftar di
   OPEL, pastikan sampai di Dashboard, lalu **tutup Chrome** (profil
   yang sedang terbuka tidak bisa dipakai Selenium).
4. Setel environment variable `OPEL_CHROME_PROFILE` ke path yang sama
   (lihat tabel di atas), atau ubah nilai default `CHROME_PROFILE_PATH`
   pada `config/config.py`.

Skrip eksplorasi di `tools/` (mis. `opel_drive.py`,
`scan_locators_opel.py`) memakai cara lain: menempel ke Chrome yang
sudah dibuka manual dengan `--remote-debugging-port=9222` dan sudah
login.

> **Catatan:** profil Chrome berisi data sesi pribadi. Pastikan path
> profil tidak ikut ter-commit (berada di luar repositori). Kalau sesi
> profil kedaluwarsa, browser berhenti di halaman login Google dan test
> pertama gagal karena halaman OPEL tidak kunjung tampil (timeout
> `OPEL_LONG_TIMEOUT`). Pesan "form login Azure AD B2C" hanya muncul
> kalau yang tertahan adalah form B2C sendiri. Login manual sekali
> lagi, lalu jalankan ulang test.

### 4. Menjalankan Test

```bash
# Seluruh alur (Login + seluruh modul Safety, 1 browser session)
pytest

# Hanya modul Safety (117 test)
pytest -m safety

# Hanya halaman View/Reporting (5 test)
pytest -m safety_view

# Hanya halaman Transaction (41 test)
pytest -m safety_transaction

# Hanya alur Halaman Lengkap (navigasi menu + tab + seluruh tombol, 19 test)
pytest -m safety_toolbar

# Kelompok test tambahan
pytest -m safety_datatables      # 18 test -- sort, pagination, search, kolom
pytest -m safety_export          # 17 test -- isi file .xlsx vs grid
pytest -m safety_negatif         #  9 test -- validasi form wajib
pytest -m safety_extra           # 71 test -- semua test tambahan di atas + leading/filter/inline

# Satu halaman saja (contoh: SMK3)
pytest -k safety_smk3

# Satu test spesifik
pytest "tests/test_safety.py::TestSafetyHss::test_safety_halaman_lengkap[SMK3]"

# Headless (untuk CI/CD)
$env:OPEL_HEADLESS = "true"; pytest        # Windows PowerShell
OPEL_HEADLESS=true pytest                  # Mac/Linux

# Per TEMPLATE laporan (marker ditempel otomatis dari URL halaman)
pytest -m MonthlyReport          # semua halaman MonthlyReport (22 test)
pytest -m MonthlyReport_Edit     # mode Edit saja (18 test)
pytest -m YearlyReport           # 44 test
pytest -m DailyReport            # 17 test
pytest -m StaticReport           # 11 test
pytest -m Custom                 #  1 test (Safety Recap)

# Lebih cepat: pace antar-aksi cuma jeda VISUAL, bukan tunggu elemen
$env:OPEL_ACTION_PACE = "0.5"; pytest -m safety   # ~30 menit, bukan ~50

# Simpan hasilnya sebagai arsip (report.html default ditimpa tiap run)
$stamp = Get-Date -Format "yyyyMMdd_HHmm"
pytest -m safety --html="reports/run_$stamp.html"
```

### Menjalankan per template

19 halaman Safety sebenarnya cuma **7 kombinasi template+mode**, dan
sebagian besar perilaku yang diuji (toolbar, tab, grid, tombol, Submit)
milik TEMPLATE — bukan milik halaman. Marker template ditempel otomatis
oleh `pytest_collection_modifyitems()` di `conftest.py`, dibaca dari URL
halaman, **tanpa mengubah nama test**.

Gunanya: menjawab *"kegagalan ini kena satu halaman atau satu
template?"* dalam satu perintah. Terbukti 2026-09-08 — bug Submit
Changes di Id=1317 dipastikan **bukan** bug template hanya dengan
`pytest -m MonthlyReport_Edit` (1 failed, 15 passed), tanpa perlu
menelusuri manual. (Belakangan terjawab: Id=1317 memang seharusnya
YearlyReport. Sejak 2026-09-10 aplikasi memindahkannya, jadi halaman
itu kini ber-marker `YearlyReport_Edit` dan `MonthlyReport_Edit` tinggal
3 halaman: 1316, 1312, 1319.)

> **Catatan:** durasi full suite berkisar sekitar 30 menit (run 7
> September, 107 test) hingga lebih dari 1 jam (run 9 September),
> tergantung `OPEL_ACTION_PACE` dan beban server DEV, karena setiap
> halaman diuji seluruh tombolnya pada setiap tab (bukan sekadar
> membuka halaman). Apabila hanya sebagian test yang dijalankan,
> browser tetap memerlukan sesi login yang aktif.

### 5. Data Uji

Seluruh data uji terpusat di `data/test_data.json`:

- Daftar menu dan URL relatif 19 halaman Safety (`hss_safety.halaman`).
- Daftar tab internal untuk halaman bertab (Incident Investigation,
  Data Rekap Statistik K3, Witness Statement, Safety Recap).
- Nilai default filter unit (`[AT10] KANTOR PUSAT`), unit alternatif
  untuk test ganti filter (`[AT02] UBP NIKEL SULTRA`), filter bulan
  (`2026-08`), dan filter tahun (`2026`).
- Tanggal filter halaman DailyReport (`filter_tanggal_harian`, saat ini
  `2026-09-08`). Tanpa tanggal, grid DailyReport selalu 0 baris —
  **ganti kalau tanggal ini sudah tidak relevan**.
- Penanda baris dummy untuk halaman Master Alat
  (`AUTO-TEST-<HHMMSS>`).

Untuk mengubah data uji, cukup mengubah file JSON tersebut tanpa perlu
mengubah kode.

### 6. Laporan

Setelah pytest selesai dijalankan, buka `reports/report.html`. Laporan
ini bersifat self-contained dan berisi ringkasan PASS/FAIL, detail
setiap langkah, serta screenshot otomatis apabila terdapat test yang
gagal. Selain itu tersedia `reports/laporan_safety.html`, laporan
formal pengujian yang berisi ringkasan, arsitektur, cakupan halaman,
hasil, dan temuan.

## Bug Aplikasi yang Ditemukan

Ringkasan status ada di [`reports/bugs/README.md`](reports/bugs/README.md)
— **baca itu dulu** sebelum mengirim laporan ke tim dev, karena
sebagian sudah ditutup.

| Laporan | Status |
|---|---|
| [Witness Statement: Submit membuang semua baris pending](reports/bugs/witness-statement-submit-membuang-semua-baris-pending.md) (Id=1336) | **TERBUKA** (intermiten) — satu-satunya yang aktif |
| [Submit Changes redirect tanpa menyimpan](reports/bugs/submit-changes-redirect-tanpa-menyimpan.md) (Id=1317) | **DITUTUP 2026-09-10** — Id=1317 dipindah aplikasi ke YearlyReport, tidak ada redirect lagi |
| [Statistic Safety Recap tidak menyimpan](reports/bugs/statistic-safety-recap-inline-edit-tidak-tersimpan.md) | Gejala dari laporan Id=1317 — ikut selesai |
| [Master Alat: Submit membuang baris baru](reports/bugs/master-alat-submit-drops-new-row.md) | Sudah diperbaiki aplikasi |
| [Cancel tidak membuang perubahan](reports/bugs/lagging-cancel-does-not-discard-edit.md) | BUKAN BUG — asumsi test yang keliru |

### Verifikasi penyimpanan: jangan tertipu draft lokal

Pelajaran termahal dari penyelidikan 2026-09-08, dan **wajib dipahami
sebelum menulis test yang memverifikasi data tersimpan**:

OPEL menyimpan perubahan yang belum di-Submit ke `localStorage` dan
**memulihkannya saat halaman dimuat ulang** — itu fitur perlindungan,
supaya kerja user tidak hilang kalau halaman ter-reload atau koneksi
putus. Akibatnya:

| Cara baca | Yang terbaca |
|---|---|
| Reload browser (F5) / `buka_halaman()` | **draft lokal** — nilai yang baru saja diketik |
| Tombol **Reload Data** | **data server** yang sebenarnya |

Membaca lewat reload biasa akan "membuktikan" penyimpanan yang belum
tentu terjadi. Tiga kesimpulan keliru — termasuk satu laporan bug yang
sempat ditutup salah — lahir dari kekeliruan ini.

Selain itu, `buka_halaman()` mengembalikan filter periode ke DEFAULT.
Nilai yang ditulis di Agustus bisa terbaca di September yang kosong,
lalu disimpulkan "tidak tersimpan". `_muat_ulang()` di
`test_safety_lagging_deep` memulihkan periode sebelum DAN sesudah
Reload Data.

Alat yang menerapkan semua ini dengan benar:
[`tools/cek_simpan_inline.py`](tools/README.md).

### Membuktikan test benar-benar bisa gagal

`OPEL_MUTASI_PERIODE=1` mematikan pemulihan periode di
`test_safety_lagging_deep`, meniru bug lama. Dipakai memastikan
assertion-nya hidup, bukan lulus karena dilemahkan:

```powershell
$env:OPEL_MUTASI_PERIODE = "1"
pytest -k "lagging_deep and statistic"   # HARUS gagal
Remove-Item Env:\OPEL_MUTASI_PERIODE
pytest -k "lagging_deep and statistic"   # HARUS lulus
```

## Catatan Teknis

| Topik | Keterangan |
|---|---|
| Struktur menu | Sidebar bersifat accordion dan memiliki judul menu duplikat (misalnya *Reporting* juga dipakai menu Health) — navigasi memakai rantai menu berjenjang (`buka_submenu(..., rantai=...)`); tiga halaman Daily Report berada pada subgroup *Incident Management* |
| Tombol Reload Data | Ada **dua** tombol. `#btnReloadData` di toolbar hanya ditampilkan di Master Alat Keselamatan Operasi (di halaman lain dirender tersembunyi, jadi tidak masuk daftar harapan toolbar). Tombol kedua ada **di dalam banner *"stored locally"*** yang muncul saat ada perubahan pending — itu yang dipakai manusia. Sejak 2026-09-10 `reload_data()` mengklik tombol banner lebih dulu, menjawab dialog **sebelum** menunggu pemuatan ulang, lalu mengembalikan `True/False` apakah tombolnya benar-benar diklik. Kalau `False`, ia jatuh ke navigasi biasa yang justru **memulihkan** draft — `test_safety_lagging_deep` lalu skip, tidak menuduh aplikasi |
| Statistic Safety Recapitulation | **(2026-09-10)** Id=1317 berpindah dari `MonthlyReport/Edit` ke `YearlyReport/Edit` — filter periodenya kini tahun (`2026`), bukan bulan. Sebelumnya aplikasi inkonsisten (halaman Monthly, link sidebar & Submit ke Yearly) sehingga Submit Changes terlihat redirect tanpa menyimpan. Pemeriksaan penyimpanan di halaman ini kembali di-assert penuh |
| Export Incident Investigation | Tidak menghasilkan file unduhan (perilaku aplikasi) — tombol tetap diklik, verifikasi file dilewati |
| Delete Master Alat | **(2026-08-31, perilaku berubah dari temuan sebelumnya)** Delete + Yes kini dua tahap: awalnya cuma menandai pending change lokal (baris belum hilang), lalu Submit Changes benar-benar menghapus DAN penghapusan bertahan setelah reload. `test_safety_master_alat_delete` diupdate jadi verifikasi cleanup sungguhan |
| Upload Import | File dummy (template resmi) dipasang pada input upload untuk menguji widget pemilih file, namun tombol Import tidak diklik sehingga tidak ada data yang dikirim ke server |
| Sesi panjang | SPA dapat "stuck" pada sesi panjang (handler tombol mati, deteksi modal negatif palsu) — helper sudah dilengkapi retry, deteksi berbasis computed style JS, dan navigasi ulang |
| Search DataTables kolom Month/Date | Token pencarian dari kolom `Month`/`Date` bisa false-fail di search API server-side — nilai yang DITAMPILKAN dilokalkan (mis. "Januari") sementara backend mencocokkan nilai mentah (mis. "January"). `test_safety_datatables_interaksi` melewati kolom itu saat memilih token pencarian |
| Create with Form (Master Alat) kehilangan baris baru | Kalau ada draft kosong lain nyangkut di grid, Submit Changes membuang SEMUA baris pending — bug aplikasi (2026-08-31), **sudah diperbaiki** (diverifikasi manual 2026-09-07), detail di `reports/bugs/master-alat-submit-drops-new-row.md`. `_hapus_baris_kosong()` tetap dipanggil di awal alur Create sebagai pengaman; sejak 2026-09-08 ia mengabaikan checkbox/radio/hidden saat menilai baris kosong (dulu `value='on'` bawaan checkbox membuat baris tak pernah terdeteksi kosong) |
| Modal Import di halaman grid berat | Halaman dengan grid berat (banyak kolom per district, mis. Leading Indicator Static Input) bisa bikin modal terdeteksi terlambat oleh Selenium walau sudah terbuka di browser (main thread sibuk render ulang) — percobaan terakhir `_klik_dan_tunggu_modal()` memakai `LONG_TIMEOUT`, bukan `DEFAULT_TIMEOUT` |
| Redundansi dipangkas | **(2026-09-08)** Export sempat diklik **3×** per halaman (`halaman_lengkap`, `leading_deep`, `export_isi_file`) dan Import **2×**, tanpa menambah cakupan — sementara menunggu file terunduh adalah bagian paling lambat dari suite. Export & Import dikeluarkan dari `leading_deep`; yang tersisa di situ hanya pemeriksaan filter tanggal mengubah data, yang tidak diuji test lain. `test_safety_incident_investigation_tab` juga dihapus: ia memeriksa 1 tab, sedangkan `halaman_lengkap` sudah memutar keenam tab beserta isinya |
| Test berdiri sendiri di luar Halaman Lengkap | `test_safety_datatables_interaksi`, `test_safety_export_isi_file`, `test_safety_create_form_validasi`, `test_safety_filter_unit_ganti` dipertahankan terpisah (2026-08-31, digabung saat merge branch) karena mencakup hal yang tidak diuji `test_safety_halaman_lengkap`: interaksi DataTables, isi file export, validasi form wajib, dan penggantian filter unit sungguhan |
| Kedalaman assertion (2026-09-04) | Sebelumnya 28 dari 80 assertion suite ini adalah `tabel_report_tampil()` — artinya suite membuktikan halaman **tampil**, bukan halaman **benar**. Empat penambahan menutup celah itu: kontrak kolom grid, filter wajib mengubah data, isi file export dicocokkan dengan grid, dan verifikasi perhitungan rasio K3 |
| Filter wajib mengubah data | `_assert_data_berubah()` membandingkan *sidik jari* grid (jumlah record + nilai sel beberapa baris pertama) sebelum vs sesudah filter diganti. Kalau dropdown berpindah tapi isi grid identik, itu tanda filter tidak diteruskan ke query backend. Sengaja **tidak** gagal kalau kedua sisi sama-sama kosong — dua unit/periode tanpa data memang wajar terlihat sama |
| Kerangka template ≠ data | **(2026-09-07, false positive nyata)** `test_safety_leading_deep[Data Rekap Statistik K3]` sempat gagal: tahun 2025 dan 2026 sama-sama Target kosong / Actual `0`, tapi grid tetap merender 12 baris berlabel January–December bernomor 1–12. Label & nomor itu semula terhitung sebagai "isi", sehingga dua tahun kosong salah dinilai punya data dan test menuduh filter tidak jalan. `_grid_punya_data()` sekarang menilai lewat **nama kolom** (`dt_baris_dict()`), membuang kolom kerangka lewat `_KOLOM_KERANGKA`, lalu menghitung sisa kolom berisi kalau ada angka bukan-nol atau teks non-kosong |
| Ambang cocok isi export menyesuaikan data | **(2026-09-07, false skip nyata)** Master Alat cuma punya 1 baris berisi `1`, `4`, `3`, `tess` — nilai khas (≥3 karakter) cuma satu, jadi test langsung skip padahal datanya ADA dan bisa diperiksa. Sekarang ambangnya adaptif: ≥3 nilai khas → toleran 50%; kurang dari itu → pakai **semua** nilai non-kosong dan wajib ketemu 100%. Skip hanya kalau grid benar-benar tidak menampilkan satu nilai pun |
| Bug aplikasi yang sudah dilaporkan tidak bikin suite merah permanen | Kegagalan yang selalu ada membuat orang berhenti membaca hasil, sehingga regresi **baru** ikut tenggelam. Halaman yang terkena bug terkonfirmasi didaftar di registry `HssSafetyPage` (saat ini `SUBMIT_REDIRECT_TANPA_SIMPAN`) — hanya pemeriksaan yang terkena dilonggarkan jadi peringatan `[BUG DIKENAL]`, langkah lain tetap di-assert. Sengaja **bukan** `@pytest.mark.xfail`: xfail berlaku ke seluruh kasus parametrize, jadi regresi di langkah lain (edit+submit, filter, export, import) ikut tertelan. Kalau OPEL memperbaikinya, test mencetak `[BUG SUDAH DIPERBAIKI?]` supaya halaman itu dikeluarkan dari set. **Kondisi 2026-09-10: registry itu kosong** (bug Id=1317 sudah diperbaiki). Registry lama `CANCEL_TIDAK_MEMBUANG_PENDING` dan `CREATE_INLINE_TIDAK_TERSIMPAN` sudah dihapus karena ternyata bukan bug |
| Nilai tanggal dikecualikan dari pencocokan export | Excel menyimpan tanggal sebagai objek `datetime`, jadi grid yang menampilkan `01/08/2026` terbaca `2026-08-01 00:00:00` di file dan tidak akan pernah cocok sebagai teks. Di ambang longgar (50%) ini tidak masalah, tapi di ambang **ketat** (100%, dipakai saat grid cuma punya sedikit nilai) satu kolom tanggal saja sudah menggagalkan test yang sebenarnya benar. `_POLA_TANGGAL` membuangnya lebih dulu — pemisah titik sengaja mewajibkan 3 bagian (`01.08.2026`) supaya angka desimal seperti `12.5` tidak ikut terbuang |
| State pending bertahan LINTAS SESI | Banner *"The data has been stored locally"* muncul di halaman yang test-nya belum mengedit apa pun. Dugaan awal "sisa test sebelumnya di sesi yang sama" **terbantah** pada run 2026-09-07 10:06 — banner sudah menyala di test **pertama** sesi itu. Jadi state-nya bertahan antar-run. `_bersihkan_draft_lokal()` (dipanggil di `buka_halaman()` dan `buka_via_menu()`) hanya menghapus `localStorage` berpola `dr_<Id>_*`, dan terbukti tidak menjangkau ini. Dua kandidat tersisa: key penyimpanan browser dengan pola lain, atau perubahan pending yang benar-benar tersimpan di server untuk user tsb. `ada_pending_lokal()` + `daftar_key_penyimpanan()` mencetak `[STATE PENDING]` berikut daftar key browser saat banner menyala — daftar kosong berarti sumbernya server |
| Kotak ringkasan sempat menghitung kurang | **(2026-09-07)** Run 29 test (23 passed, 6 skipped) tapi kotak "AUTOMATION TESTING RESULT" cuma mencatat 18 — 11 `test_safety_leading_deep` raib karena belum punya entri di `STEP_LABELS`, dan `_label_for_step()` mengembalikan `None` sehingga test tanpa label dibuang diam-diam. Sekarang label yang tidak ketemu jatuh ke nama test mentahnya, jadi jumlah di kotak selalu sama dengan jumlah yang benar-benar dijalankan pytest |
| Rasio K3 tidak diuji rumusnya | **(2026-09-07, keputusan akhir)** Sempat dibuat test yang menghitung ulang Frequency/Severity/Fatality Rate di Statistic Safety Recapitulation (Id=1317). Test itu **dihapus** setelah terbukti dari DOM bahwa ketiga kolom rasio adalah `<input>` aktif — nilainya **diketik operator**, bukan dihitung aplikasi. Kebenaran rumusnya soal mutu data, bukan tanggung jawab aplikasi, jadi tidak layak jadi assertion regresi. Sebagai catatan: audit sekali jalan atas periode 2026-08 (AT10 KANTOR PUSAT) menunjukkan datanya konsisten pada pengali **≈1.000.000** (ILO/Permenaker) di 7 baris, tanpa satu pun baris janggal |
| Pencocokan isi export | Ambangnya toleran (mayoritas nilai contoh, bukan semua) karena export wajar memformat ulang nilai: tanggal jadi objek `datetime`, angka jadi `float`, kolom tersembunyi bisa ikut atau tidak. Yang disasar adalah kegagalan besar — file template kosong, data unit/periode lain, atau file basi sisa export sebelumnya |
| Anchor baris otomatis | **(2026-09-10)** Entri `LAGGING_DEEP` dengan anchor kosong (Data Rekap Statistik K3, Leading Indicator) mencari sendiri baris yang kolom editnya berisi angka bukan-nol **dan** anchornya unik (`_cari_anchor_otomatis()`). Anchor yang di-hardcode dari nilai data (mis. `{'CSD': '123'}`) patah begitu data DEV berubah. Kalau tidak ada baris yang layak, test skip |
| Bukti pada saat kejadian | Screenshot otomatis conftest diambil **sesudah** blok pemulihan data, jadi selalu memperlihatkan nilai yang sudah dikembalikan. `_potret()` mengambil screenshot tepat saat kejadian (mis. `reload_tidak_buang_draft_<halaman>_*.png`), dan `test_safety_lagging_deep` mencetak blok `[BUKTI RELOAD DATA]` (banner, status klik, bacaan langsung vs stabil, key draft) sebelum assert — supaya bisa dibedakan bug aplikasi dari bug skrip |
| Input inline lengkap | **(2026-09-08)** `isi_baris_kosong_inline()` kini ikut mengisi kolom tanggal (dari `filter_tanggal_harian` atau periode harian), `<select>` (opsi pertama yang punya value), dan `<textarea>`. Tanpa tanggal, baris DailyReport tersimpan tapi tidak muncul di filter. Penolakan validasi ditangkap `pesan_validasi_halaman()` segera sesudah Submit — baris yang ditolak validasi di-skip, bukan dilaporkan gagal simpan |
| Link menu belum ter-render | **(2026-09-09)** `buka_via_menu()` dulu tidak benar-benar retry: `TimeoutException` langsung keluar dari loop. Sekarang rantai submenu dibuka ulang lalu dicoba sekali lagi. Gejala lamanya: `halaman_lengkap[Statistic Safety Recap]` gagal di sesi 1 jam walau link terlihat di screenshot |

## Kesimpulan

Secara keseluruhan, proyek ini menerapkan Page Object Model dengan data
uji terpusat dan satu sesi browser untuk seluruh alur pengujian modul
Safety. Ringkasan poin-poin utamanya adalah sebagai berikut:

| Aspek | Penerapan |
|---|---|
| **Pola desain** | Page Object Model (POM) — setiap halaman memiliki kelas halaman sendiri |
| **Cakupan** | 19 halaman HSS > Safety (5 Reporting + 14 Transaction), 118 test |
| **Kedalaman pengujian** | Seluruh tab dan seluruh tombol fitur dicoba pada setiap halaman (bukan sekadar membuka halaman) |
| **Navigasi** | Melalui menu sidebar (dashboard → HSS → Safety → sub Reporting/Transaction), bukan URL langsung |
| **Data uji** | Terpusat di `data/test_data.json` — data dapat diganti tanpa mengubah kode |
| **Keamanan data** | Upload file dummy tidak pernah dikirim ke server; edit grid selalu di-revert |
| **Sesi browser** | `scope="session"` — Chrome dibuka sekali untuk seluruh alur |
| **Laporan** | HTML otomatis (`reports/report.html`), laporan formal (`reports/laporan_safety.html`), dan screenshot saat test gagal |
| **Fleksibilitas** | Tujuh environment variable untuk menyesuaikan URL, profil Chrome, domain login, timeout, dan lainnya |

Dokumentasi ini diperbarui mengikuti kondisi repositori
`Automation-Testing` (branch `dev`) per **11 September 2026**, termasuk
perubahan lokal di `pages/hss_safety_page.py` dan `tests/test_safety.py`
yang belum di-commit.
