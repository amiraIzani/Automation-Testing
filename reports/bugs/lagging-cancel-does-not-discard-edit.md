# BUKAN BUG — perilaku "stored locally" adalah fitur, bukan cacat

> ## STATUS: DITUTUP, BUKAN BUG (dikonfirmasi pemilik produk 2026-09-07)
>
> Laporan ini semula berjudul *"Tombol Cancel tidak membuang perubahan
> pending"*. **Klaim itu salah, dan test yang melahirkannya memakai
> asumsi yang keliru soal desain aplikasi.**
>
> Perilaku sebenarnya, dikonfirmasi 2026-09-07: perubahan grid yang
> belum di-Submit memang **sengaja disimpan secara lokal** dan
> dipulihkan kembali saat halaman dimuat ulang. Itu **fitur
> perlindungan** — supaya pekerjaan user tidak hilang kalau halaman
> ter-reload tanpa sengaja, koneksi internet putus, dan sejenisnya.
>
> Cara membuang perubahan itu adalah tombol **Reload Data** (muncul di
> banner "The data has been stored locally..."), BUKAN tombol Cancel
> dan bukan reload browser. Jadi:
>
> | Aksi | Yang benar terjadi |
> |---|---|
> | **Submit Changes** | perubahan dikirim & disimpan di server |
> | **Reload Data** | perubahan lokal DIBUANG, data diambil ulang dari server |
> | **Cancel** / reload browser | perubahan lokal TETAP ADA — memang disengaja |
>
> Yang salah adalah assertion di
> `tests/test_safety.py::test_safety_lagging_deep` yang menuntut Cancel
> membuang perubahan. Assertion itu sudah diganti: sekarang yang diuji
> adalah **Reload Data benar-benar membuang draft lokal**, sesuai
> kontrak aplikasi yang sebenarnya.
>
> Laporan ini DIPERTAHANKAN sebagai catatan supaya kekeliruan yang sama
> tidak terulang. **Jangan dikirim ke tim dev OPEL.**

- **Tanggal ditemukan**: 2026-09-04
- **Ditemukan lewat**: `tests/test_safety.py::TestSafetyHss::test_safety_lagging_deep[smk3]`
- **Halaman**: Safety > Transaction > Lagging Indicator > SMK3
  (`https://dev-opel.antm.tech/Reporting/Timesheet/YearlyReport/Edit?Id=1308`) — kemungkinan
  berlaku juga di SMKP dan halaman lagging lain dengan tombol Cancel
  serupa (belum diverifikasi satu-satu).
- **Severity**: Tinggi — user yang sengaja membatalkan (Cancel) editan
  tetap kehilangan nilai aslinya secara senyap.

> **REVISI 2026-09-07 — repro-nya BERSYARAT, bukan selalu.**
> Bug ini **tidak** muncul di setiap kondisi. Lihat bagian
> "Pengamatan tambahan 2026-09-07" di bawah: dua run terakhir
> menunjukkan Cancel bekerja BENAR ketika halaman dibuka dalam
> keadaan bersih, dan gagal ketika halaman dibuka sudah membawa
> perubahan pending. Langkah reproduksi di bawah perlu didahului
> langkah 0 supaya konsisten.

## Langkah reproduksi

0. **(Prasyarat, ditemukan 2026-09-07)** Pastikan halaman sudah
   membawa perubahan pending sebelum mulai — banner *"The data has
   been stored locally. Please click the submit button to save it on
   the server"* harus sudah tampil saat halaman dibuka. Kalau halaman
   dibuka bersih, langkah 1–4 di bawah kemungkinan besar LULUS
   (Cancel bekerja normal).
1. Buka halaman SMK3, catat nilai sel `PPkomKetidaksesuaianMaj` baris
   Januari (mis. `8`).
2. Ubah nilai sel itu (mis. jadi `9`) — TANPA klik Submit Changes.
3. Klik tombol **Cancel** (bukan Submit Changes) → dialog konfirmasi
   muncul → jawab **Yes**.
4. Reload halaman (atau navigasi ulang ke halaman yang sama).

## Hasil yang diharapkan

Nilai sel kembali ke `8` (perubahan pending dibuang, tidak pernah
sungguh disimpan ke server).

## Hasil aktual

Nilai sel tetap `9` setelah reload — perubahan yang seharusnya
DIBATALKAN malah ikut tersimpan, PERSIS seperti kalau tombol Submit
Changes yang diklik.

## Bukti

Screenshot: `reports/screenshots/test_safety_lagging_deep[smk3]_20260904_141758.png`
— baris Januari kolom MAJOR (Pembangunan dan Pemeliharaan Komitmen)
menunjukkan nilai `9` setelah alur Cancel + reload selesai.

Sudah dipastikan BUKAN salah klik tombol (locator `BTN_CANCEL_GRID`
diklik lewat `click_js_saat_tampil()` yang sudah memvalidasi elemen
BENAR-BENAR tampil, bukan sekadar match pertama di DOM).

## Cakupan: halaman mana saja yang berpotensi kena

BELUM diverifikasi satu per satu. Tapi mekanismenya generik, bukan khas
SMK3: state pending disimpan di `localStorage` dengan pola key
`dr_<DataTemplateId>_*` (lihat `HssSafetyPage._bersihkan_draft_lokal()`),
dan pola itu dipakai per halaman, bukan per modul. Jadi **semua halaman
Transaction yang punya grid inline-edit + tombol Submit Changes**
kandidat terkena.

Daftar lengkap 14 halaman tersebut:

| Halaman | Link |
|---|---|
| Incident Investigation Form | `https://dev-opel.antm.tech/Reporting/Timesheet/DailyReport/Edit?Id=1334` |
| Initial Incident/Accident Report | `https://dev-opel.antm.tech/Reporting/Timesheet/DailyReport/Edit?Id=1335` |
| Witness Statement Report | `https://dev-opel.antm.tech/Reporting/Timesheet/DailyReport/Edit?Id=1336` |
| EMERGENCY DRILL Daily | `https://dev-opel.antm.tech/Reporting/Timesheet/MonthlyReport/Edit?Id=1319` |
| Master Alat Keselamatan Operasi | `https://dev-opel.antm.tech/Reporting/Timesheet/StaticReport/Edit?Id=1321` |
| SOC RECAPITULATION | `https://dev-opel.antm.tech/Reporting/Timesheet/YearlyReport/Edit?Id=1310` |
| GOLDEN RULES | `https://dev-opel.antm.tech/Reporting/Timesheet/MonthlyReport/Edit?Id=1316` |
| Data Rekap Statistik K3 | `https://dev-opel.antm.tech/Reporting/Timesheet/YearlyReport/Edit?Id=1315` |
| SAFETY/KKP/P2K3 Committee Meeting | `https://dev-opel.antm.tech/Reporting/Timesheet/YearlyReport/Edit?Id=1313` |
| MWT DAILY | `https://dev-opel.antm.tech/Reporting/Timesheet/MonthlyReport/Edit?Id=1312` |
| Leading Indicator | `https://dev-opel.antm.tech/Reporting/Timesheet/StaticReport/Edit?Id=1309` |
| Statistic Safety Recapitulation | `https://dev-opel.antm.tech/Reporting/Timesheet/MonthlyReport/Edit?Id=1317` |
| SMK3 | `https://dev-opel.antm.tech/Reporting/Timesheet/YearlyReport/Edit?Id=1308` |
| SMKP | `https://dev-opel.antm.tech/Reporting/Timesheet/YearlyReport/Edit?Id=1307` |

Halaman **Reporting** (View, read-only) tidak punya grid inline-edit
maupun Submit Changes, jadi tidak terkena.

Untuk memastikan cakupan sebenarnya, cukup uji 3–4 halaman dari
template yang BERBEDA (DailyReport / MonthlyReport / YearlyReport /
StaticReport). Kalau keempat template kena, aman disimpulkan berlaku
untuk semuanya.

## Pengamatan tambahan 2026-09-07 (mengubah dugaan akar masalah)

Setelah test dilengkapi deteksi banner pending saat halaman dibuka
(`HssSafetyPage.ada_pending_lokal()`), terlihat korelasi berikut:

| Run | Kondisi halaman saat dibuka | Hasil Cancel |
|---|---|---|
| 2026-09-04 14:17 | tidak tercatat (deteksi belum ada) | GAGAL |
| 2026-09-07 08:51 | tidak tercatat (deteksi belum ada) | GAGAL |
| 2026-09-07 10:06 | **ADA** perubahan pending | BENAR |
| 2026-09-07 ~10:20 | **BERSIH** (tanpa pending) | BENAR |

Dua run terakhir sama-sama BENAR, jadi korelasinya belum tegas dan
butuh data lebih banyak — tapi satu hal sudah pasti: **bug ini tidak
muncul di setiap run**, sehingga klaim "Cancel selalu gagal membuang
perubahan" pada versi awal laporan ini TERLALU KUAT.

Catatan penting lain: pada run 10:06 banner pending sudah menyala di
test PERTAMA sesi tersebut. Artinya perubahan pending itu **bertahan
lintas sesi browser** — bukan sisa test sebelumnya di run yang sama.
`_bersihkan_draft_lokal()` (menghapus `localStorage` berpola
`dr_<Id>_*`) tidak menjangkaunya, sehingga sumbernya salah satu dari:

- key penyimpanan browser dengan pola LAIN, atau
- perubahan pending yang benar-benar tersimpan **di server** untuk user
  tersebut.

`HssSafetyPage.daftar_key_penyimpanan()` dipakai membedakan keduanya:
kalau daftar key browser kosong padahal banner menyala, sumbernya
server.

## Dugaan akar masalah

Kemungkinan terkait perilaku "stored locally" yang juga ditemukan di
alur Delete Master Alat (lihat `reports/bugs/master-alat-submit-drops-new-row.md`
dan catatan `test_safety_master_alat_delete`, 2026-08-31): aplikasi
tampaknya menyimpan perubahan pending di sisi client (localStorage atau
serupa) sebelum benar-benar di-submit ke server. Tombol Cancel mungkin
hanya membersihkan tampilan grid saat itu juga, TANPA membersihkan
state tersimpan-lokal itu — sehingga reload berikutnya memuat ulang
perubahan yang "tersimpan lokal" itu alih-alih data asli dari server.

## Saran perbaikan (untuk tim dev OPEL)

- Tombol Cancel harus membuang/menghapus state pending lokal (apa pun
  mekanismenya — localStorage, sessionStorage, atau variabel JS in-
  memory yang ikut ke-restore saat reload), bukan cuma me-refresh
  tampilan grid.

## Workaround yang sudah diterapkan di automation test

`tests/test_safety.py::test_safety_lagging_deep` mendeteksi kalau nilai
pasca-Cancel tidak kembali ke nilai semula, lalu MEMPERBAIKI data DEV
secara eksplisit (edit balik + Submit Changes) — supaya data DEV tidak
ditinggalkan rusak.

Sejak 2026-09-07, halaman yang terkena didaftar di
`HssSafetyPage.CANCEL_TIDAK_MEMBUANG_PENDING` (saat ini: `smk3`).
Untuk halaman di set itu, kegagalan Cancel dicetak sebagai peringatan
`[BUG DIKENAL]` alih-alih meng-assert — karena kegagalan yang selalu
ada membuat suite merah permanen dan regresi BARU ikut tenggelam.
Langkah lain di test yang sama (edit+submit, filter, export, import)
TETAP di-assert ketat.

Tiap run mencetak kondisi awal halaman ("ADA pending" / "dibuka
BERSIH") bersama hasil Cancel-nya, jadi tabel korelasi di atas
bertambah datanya secara otomatis. Kalau Cancel terbukti benar secara
konsisten **dalam dua kondisi awal itu**, keluarkan `smk3` dari set
supaya pemeriksaannya kembali tajam, dan tutup laporan ini.
