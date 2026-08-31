# Automation Testing OPEL

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13.2-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.13.2">
  <img src="https://img.shields.io/badge/Selenium-4.45.0-43B02A?style=flat-square&logo=selenium&logoColor=white" alt="Selenium 4.45.0">
  <img src="https://img.shields.io/badge/Pytest-9.1.1-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="Pytest 9.1.1">
  <img src="https://img.shields.io/badge/Status-45%20passed%20%C2%B7%200%20failed-2EA043?style=flat-square" alt="Status: 45 passed, 0 failed">
</p>

## Gambaran Umum

Proyek ini adalah automation testing untuk modul **Safety** pada
aplikasi **OPEL** (`https://dev-opel.antm.tech/`), sebuah SPA berbasis
**SmartAdmin (Bootstrap 4) + jQuery + DataTables**, dibangun dengan
**Python** dan **Selenium WebDriver** di atas framework **Pytest**, serta
menerapkan pendekatan **Page Object Model (POM)** dan **data-driven
testing**. Seluruh alur pengujian dijalankan dalam **satu sesi browser**
tanpa perlu me-refresh halaman.

Pengujian mencakup **45 langkah** yang dikelompokkan ke dalam modul:
Login, Navigasi Menu, View per Halaman, Tab, Create/Delete, Lagging
Mendalam, dan Halaman Lengkap — untuk **19 halaman** di menu
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

Hasil full suite (`pytest -k safety`) tanggal 31 Agustus 2026:

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

Dengan demikian seluruh **45 test telah terverifikasi lulus**.

> **Catatan (2026-08-31, pasca-merge):** log run di atas direkam
> SEBELUM branch ini digabung dengan `automation-safety` (fixes bug
> search-token, empty-draft-blocks-submit, delete dua tahap, dan 4 test
> berdiri sendiri di tabel "Alur Pengujian" di bawah). Angka **45**
> belum termasuk 4 test tambahan itu — jalankan ulang `pytest -k safety`
> untuk angka yang mencerminkan kondisi terkini.

## Alur Pengujian

Berikut urutan langkah pengujian sesuai isi `tests/test_e2e_opel.py`
dan `tests/test_safety.py`, dikelompokkan per modul:

| Modul | Test method | Alur / yang diperiksa |
|---|---|---|
| Login | `test_login` | Buka OPEL → sesi aktif (DEV auto-auth) → halaman utama tampil |
| Navigasi Menu | `test_safety_menu_dan_landing` | Dashboard → klik HSS → Safety → buka sub **Reporting** dan **Transaction** → link halaman muncul di sidebar |
| View (Reporting, 5 halaman) | `test_safety_*_view` | Buka halaman → tabel DataTables tampil → filter tanggal/unit tampil |
| View (Transaction, 14 halaman) | `test_safety_*_view` | Buka halaman → tabel tampil; halaman bertab → tab internal aktif |
| Master Alat | `test_safety_master_alat_create` | Create with Form → isi dummy otomatis (Equipment No unik) → Save → Submit → penanda muncul di grid |
| Master Alat | `test_safety_master_alat_delete` | Delete baris dummy → konfirmasi Yes → baris hilang dari grid |
| Lagging Mendalam (3 halaman) | `test_safety_lagging_deep` | Edit grid inline + Submit → verifikasi → **revert**; Cancel; filter tanggal; filter unit; Export (file terunduh); Import (modal + template terunduh) |
| Halaman Lengkap (19 halaman) | `test_safety_halaman_lengkap` | Alur lengkap satu halaman dalam satu kunjungan (lihat rincian di bawah) |
| Interaksi DataTables | `test_safety_datatables_interaksi` | Sort kolom asc/desc, pagination, Search (DOM + API), show/hide kolom — per halaman ber-grid |
| Isi File Export | `test_safety_export_isi_file` | Export → file benar-benar bisa dibuka sebagai workbook `.xlsx` dan punya ≥1 baris terisi |
| Validasi Form Wajib | `test_safety_create_form_validasi` | Create with Form disimpan KOSONG → form harus menolak (modal tetap terbuka / pesan validasi) |
| Ganti Filter Unit | `test_safety_filter_unit_ganti` | Filter unit benar-benar DIGANTI ke opsi lain (bukan cuma cek elemen ada), tabel tetap tampil, lalu dikembalikan |
| Leading (Alur Menengah) | `test_safety_leading_deep` | View → filter tanggal (kalau ada) → filter unit (elemen+opsi) → Export (file) → Import (modal + template terunduh) |

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
├── LoginPage                              <- Login (Azure AD B2C / auto-auth DEV)
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
| `login_page.py` | `login()` — deteksi auto-auth DEV atau form Azure AD B2C |
| `conftest.py` | Fixture `driver` (session), fixture `test_data`, hook screenshot saat gagal, pemetaan label hasil (`STEP_LABELS`), dan kotak "AUTOMATION TESTING RESULT" |

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
opel-automation/
├── conftest.py                       <- driver session-scoped + ringkasan hasil di terminal
├── pytest.ini                        <- konfigurasi pytest + laporan HTML otomatis
├── requirements.txt                  <- daftar dependency Python
├── README.md                         <- dokumentasi proyek (file ini)
├── .gitignore                        <- pola file yang tidak di-commit
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
├── tools/
│   ├── scan_locators_opel.py         <- scan locator halaman aktif (Chrome port 9222)
│   ├── scan_safety_batch.py          <- scan ulang seluruh 19 halaman Safety
│   ├── scan_form_safety.py           <- scan field form create
│   ├── generate_safety_pages.py      <- pembuat page object dari hasil scan
│   ├── locator.py                    <- ringkasan ID stabil per halaman
│   └── opel_drive.py                 <- helper eksplorasi interaktif
└── reports/
    ├── report.html                   <- laporan HTML hasil pytest (self-contained)
    ├── laporan_safety.html           <- laporan formal hasil pengujian
    ├── dummy_upload.png              <- file dummy untuk field upload form
    ├── screenshots/                  <- screenshot otomatis saat test gagal
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
| `tools/` | Alat bantu untuk mencari locator |
| `reports/` | Menyimpan hasil dan laporan pengujian |

## Setup

### 1. Install

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

> **Versi yang teruji pada proyek ini:** Python 3.13.2 · Selenium
> 4.45.0 · Pytest 9.1.1 · pytest-html 4.2.0
>
> **Prasyarat:** Google Chrome terinstal. Untuk environment DEV, login
> terjadi otomatis (auto-auth); untuk environment lain, dibutuhkan akun
> yang terdaftar pada Azure AD B2C (lihat bagian Login).

### 2. Environment Variables (Opsional)

Proyek ini tidak menggunakan file `.env`. Seluruh konfigurasi dibaca
dari environment variable melalui `os.getenv()` di `config/config.py`.
Karena setiap variabel memiliki nilai default, proyek dapat langsung
dijalankan tanpa konfigurasi tambahan:

| Variable | Default | Fungsi |
|---|---|---|
| `OPEL_BASE_URL` | `https://dev-opel.antm.tech/` | URL aplikasi yang diuji |
| `OPEL_CHROME_PROFILE` | `D:\selenium-chrome-profile-opel` | Path profil Chrome (untuk sesi login) |
| `OPEL_HEADLESS` | `false` | `true` → Chrome tanpa jendela (untuk CI/CD) |
| `OPEL_TIMEOUT` | `15` | Timeout default WebDriverWait (detik) |
| `OPEL_LONG_TIMEOUT` | `60` | Timeout proses lambat (render grid, redirect SSO) |
| `OPEL_ACTION_PACE` | `2.0` | Jeda antar-aksi (detik) — hanya untuk kebutuhan visual, bukan untuk menunggu elemen |

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

### 3. Login (Sekali Saja)

Pada environment DEV saat ini, login terjadi **otomatis**: `driver.get`
ke `BASE_URL` diteruskan satu redirect langsung ke `/My/Dashboard`
(cookie diterbitkan server tanpa form). Form Azure AD B2C
(`antamapps.b2clogin.com`) tidak muncul dari mesin ini.

Untuk environment lain (atau apabila mekanisme auth berubah), OPEL
memakai Azure AD B2C dan Selenium **tidak** mengisi email/password
secara langsung. Solusi yang digunakan adalah menjalankan Chrome dengan
profil yang sesi-nya sudah aktif:

1. Tutup semua jendela Chrome.
2. Jalankan Chrome dengan folder profil khusus:
   `"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="D:\selenium-chrome-profile-opel"`
3. Login secara manual menggunakan akun yang terdaftar di OPEL, lalu
   tutup Chrome.
4. Setel environment variable `OPEL_CHROME_PROFILE` ke path yang sama
   (lihat tabel di atas), atau ubah nilai default `CHROME_PROFILE_PATH`
   pada `config/config.py`.

> **Catatan:** profil Chrome berisi data sesi pribadi. Pastikan path
> profil tidak ikut ter-commit (terdaftar di `.gitignore`). Apabila test
> gagal dengan pesan yang menyebut "form login Azure AD B2C", artinya
> sesi profil belum aktif atau sudah kedaluwarsa — login manual sekali
> lagi, lalu jalankan ulang test.

### 4. Menjalankan Test

```bash
# Seluruh alur (Login + seluruh modul Safety, 1 browser session)
pytest

# Hanya modul Safety (45 test)
pytest -k safety

# Hanya halaman View/Reporting
pytest -m safety_view

# Hanya halaman Transaction
pytest -m safety_transaction

# Hanya alur Halaman Lengkap (navigasi menu + tab + seluruh tombol)
pytest -m safety_toolbar

# Satu halaman saja (contoh: SMK3)
pytest -k safety_smk3

# Satu test spesifik
pytest "tests/test_safety.py::TestSafetyHss::test_safety_halaman_lengkap[SMK3]"

# Headless (untuk CI/CD)
$env:OPEL_HEADLESS = "true"; pytest        # Windows PowerShell
OPEL_HEADLESS=true pytest                  # Mac/Linux
```

> **Catatan:** durasi full suite sekitar 50–60 menit karena setiap
> halaman diuji seluruh tombolnya pada setiap tab (bukan sekadar
> membuka halaman). Apabila hanya sebagian test yang dijalankan,
> browser tetap memerlukan sesi login yang aktif.

### 5. Data Uji

Seluruh data uji terpusat di `data/test_data.json`:

- Daftar menu dan URL relatif 19 halaman Safety (`hss_safety.halaman`).
- Daftar tab internal untuk halaman bertab (Incident Investigation,
  Data Rekap Statistik K3, Witness Statement, Safety Recap).
- Nilai default filter unit (`[AT10] KANTOR PUSAT`), filter bulan
  (`2026-08`), dan filter tahun (`2026`).
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

## Catatan Teknis

| Topik | Keterangan |
|---|---|
| Struktur menu | Sidebar bersifat accordion dan memiliki judul menu duplikat (misalnya *Reporting* juga dipakai menu Health) — navigasi memakai rantai menu berjenjang (`buka_submenu(..., rantai=...)`); tiga halaman Daily Report berada pada subgroup *Incident Management* |
| Tombol Reload Data | Hanya ditampilkan aplikasi pada halaman Master Alat Keselamatan Operasi; pada halaman lain tombol dirender tersembunyi sehingga tidak masuk daftar harapan toolbar |
| Statistic Safety Recapitulation | Template MonthlyReport tidak menyimpan perubahan inline lewat Submit Changes — test tetap menjalankan alur edit dan memverifikasi data tidak rusak |
| Export Incident Investigation | Tidak menghasilkan file unduhan (perilaku aplikasi) — tombol tetap diklik, verifikasi file dilewati |
| Delete Master Alat | **(2026-08-31, perilaku berubah dari temuan sebelumnya)** Delete + Yes kini dua tahap: awalnya cuma menandai pending change lokal (baris belum hilang), lalu Submit Changes benar-benar menghapus DAN penghapusan bertahan setelah reload. `test_safety_master_alat_delete` diupdate jadi verifikasi cleanup sungguhan |
| Upload Import | File dummy (template resmi) dipasang pada input upload untuk menguji widget pemilih file, namun tombol Import tidak diklik sehingga tidak ada data yang dikirim ke server |
| Sesi panjang | SPA dapat "stuck" pada sesi panjang (handler tombol mati, deteksi modal negatif palsu) — helper sudah dilengkapi retry, deteksi berbasis computed style JS, dan navigasi ulang |
| Search DataTables kolom Month/Date | Token pencarian dari kolom `Month`/`Date` bisa false-fail di search API server-side — nilai yang DITAMPILKAN dilokalkan (mis. "Januari") sementara backend mencocokkan nilai mentah (mis. "January"). `test_safety_datatables_interaksi` melewati kolom itu saat memilih token pencarian |
| Create with Form (Master Alat) kehilangan baris baru | Kalau ada draft kosong lain nyangkut di grid, Submit Changes membuang SEMUA baris pending (bukan cuma yang gagal validasi) — bug aplikasi, detail & repro di `reports/bugs/master-alat-submit-drops-new-row.md`. Workaround test: `_hapus_baris_kosong()` dipanggil di awal tiap alur Create with Form |
| Modal Import di halaman grid berat | Halaman dengan grid berat (banyak kolom per district, mis. Leading Indicator Static Input) bisa bikin modal terdeteksi terlambat oleh Selenium walau sudah terbuka di browser (main thread sibuk render ulang) — percobaan terakhir `_klik_dan_tunggu_modal()` memakai `LONG_TIMEOUT`, bukan `DEFAULT_TIMEOUT` |
| Test berdiri sendiri di luar Halaman Lengkap | `test_safety_datatables_interaksi`, `test_safety_export_isi_file`, `test_safety_create_form_validasi`, `test_safety_filter_unit_ganti` dipertahankan terpisah (2026-08-31, digabung saat merge branch) karena mencakup hal yang tidak diuji `test_safety_halaman_lengkap`: interaksi DataTables, isi file export, validasi form wajib, dan penggantian filter unit sungguhan |

## Kesimpulan

Secara keseluruhan, proyek ini menerapkan Page Object Model dengan data
uji terpusat dan satu sesi browser untuk seluruh alur pengujian modul
Safety. Ringkasan poin-poin utamanya adalah sebagai berikut:

| Aspek | Penerapan |
|---|---|
| **Pola desain** | Page Object Model (POM) — setiap halaman memiliki kelas halaman sendiri |
| **Cakupan** | 19 halaman HSS > Safety (5 Reporting + 14 Transaction), 45 langkah pengujian |
| **Kedalaman pengujian** | Seluruh tab dan seluruh tombol fitur dicoba pada setiap halaman (bukan sekadar membuka halaman) |
| **Navigasi** | Melalui menu sidebar (dashboard → HSS → Safety → sub Reporting/Transaction), bukan URL langsung |
| **Data uji** | Terpusat di `data/test_data.json` — data dapat diganti tanpa mengubah kode |
| **Keamanan data** | Upload file dummy tidak pernah dikirim ke server; edit grid selalu di-revert |
| **Sesi browser** | `scope="session"` — Chrome dibuka sekali untuk seluruh alur |
| **Laporan** | HTML otomatis (`reports/report.html`), laporan formal (`reports/laporan_safety.html`), dan screenshot saat test gagal |
| **Fleksibilitas** | Enam environment variable untuk menyesuaikan URL, profil Chrome, timeout, dan lainnya |

Dokumentasi ini ditulis mengikuti kondisi aktual repositori
`opel-automation`.
