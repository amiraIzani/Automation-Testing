# Submit Changes redirect Monthly → Yearly (Id=1317) — SUDAH DIPERBAIKI

> ## STATUS: DITUTUP — sudah diperbaiki aplikasi (2026-09-10)
>
> Penyebabnya akhirnya jelas: laporan **Id=1317 seharusnya YearlyReport,
> bukan MonthlyReport**. Waktu bug ini dilaporkan, aplikasinya sedang
> **inkonsisten** — halamannya masih dirender sebagai `MonthlyReport/Edit`
> sementara link sidebar dan tujuan Submit sudah mengarah ke
> `YearlyReport/Edit`. Redirect yang terlihat "membuang data" itu
> sebenarnya aplikasi melompat ke template yang benar di tengah alur
> simpan.
>
> Per 2026-09-10 aplikasi sudah konsisten: link sidebar, halaman, dan
> Submit semuanya YearlyReport. Tidak ada lagi redirect di tengah jalan.
>
> ### Kenapa sifatnya terlihat INTERMITEN
>
> Karena perbaikannya berlangsung saat pengujian: sebagian percobaan
> mengenai versi lama (redirect), sebagian versi baru (normal). Itu
> menjelaskan kenapa reproduksinya tidak konsisten — bukan karena
> race condition seperti yang sempat diduga.
>
> ### Dampak ke automation
>
> Konfigurasi test ikut diperbarui 2026-09-10:
>
> - `HssSafetyPage.HALAMAN` dan `data/test_data.json`:
>   `MonthlyReport/Edit?Id=1317` → `YearlyReport/Edit?Id=1317`
> - `LAGGING_DEEP`: `tanggal_uji` `'2026-07'` → `'2026'` (filter tahun,
>   bukan bulan)
> - Marker template halaman ini otomatis berubah dari
>   `MonthlyReport` ke `YearlyReport`
>
> Gejala terakhir sebelum ketahuan: `test_safety_halaman_lengkap
> [Statistic Safety Recap]` gagal karena mencari link sidebar ber-href
> `MonthlyReport/Edit?Id=1317` yang sudah tidak ada.
>
> Laporan DIPERTAHANKAN sebagai riwayat. **Jangan dikirim ke tim dev.**
>
> ---
>
> ## Isi laporan asli (kondisi sebelum perbaikan)

- **Tanggal ditemukan**: 2026-09-08
- **Ditemukan lewat**: pengecekan MANUAL oleh pemilik produk, saat
  memverifikasi temuan automation test
- **Halaman utama**: Safety > Transaction > Lagging Indicator >
  Statistic Safety Recapitulation
  (`https://dev-opel.antm.tech/Reporting/Timesheet/MonthlyReport/Edit?Id=1317`)
- **Severity**: TINGGI — perubahan yang diketik user hilang tanpa pesan
  error apa pun, dan user tidak punya cara tahu bahwa datanya gagal
  tersimpan.
- **Status**: **TERKONFIRMASI BUG APLIKASI** (2026-09-08)

## Konfirmasi: bukan efek automation testing

Halaman ini paling sering ditulis-submit oleh automation test, jadi
sempat dicurigai state lokalnya yang rusak, bukan aplikasinya.
Kecurigaan itu SUDAH DISINGKIRKAN:

| Kondisi uji | Hasil |
|---|---|
| Browser biasa, profil yang dipakai automation | redirect |
| **Jendela incognito** (nol localStorage, nol draft) | **redirect** |
| **Mesin Windows lain** (nol jejak automation) | **redirect** |

Selain itu, dari empat halaman bertemplate `MonthlyReport/Edit`, **hanya
Id=1317 yang terkena**:

| Halaman | Id | Submit Changes |
|---|---|---|
| **Statistic Safety Recapitulation** | **1317** | **REDIRECT, tidak menyimpan** |
| Golden Rules | 1316 | normal |
| MWT Daily | 1312 | normal |
| EMERGENCY DRILL Daily | 1319 | normal |

Kalau penyebabnya beban/state dari testing, halaman lain akan ikut
terganggu. Nyatanya tidak. Jadi ini **bug konfigurasi/routing pada
laporan Id=1317**, bukan bug template dan bukan efek pengujian.

## Hasil pengamatan manual (2026-09-08)

1. Buka halaman, set **Month = August 2026**, **District = [AT10] KANTOR PUSAT**.
2. Ubah nilai salah satu sel angka di grid.
3. Klik **Submit Changes**.

**Yang terjadi:** halaman **langsung berpindah** — dialog konfirmasi
bahkan **belum sempat muncul**, apalagi dijawab.

Tujuan redirect-nya:

```
DARI : .../Reporting/Timesheet/MonthlyReport/Edit?Id=1317
KE   : .../Reporting/Timesheet/YearlyReport/Edit?Id=1317&DistrictCode=AT10
```

Perhatikan: **Id-nya SAMA (1317)**, yang berubah adalah TEMPLATE
(`MonthlyReport` → `YearlyReport`), dan `DistrictCode` ikut
ditambahkan. Jadi ini bukan "reload halaman", melainkan **salah
routing**: user dilempar ke varian Yearly dari laporan yang sama,
padahal Id=1317 adalah laporan BULANAN.

Dugaan: handler Submit Changes membangun URL tujuan dengan template
yang salah (hard-coded `YearlyReport`, atau salah membaca jenis
laporan dari konfigurasi Id).

4. Di halaman Yearly yang dituju, klik **Submit Changes** lagi.

**Yang terjadi:** halaman **memuat ulang terus**, submit tidak pernah
selesai.

## Hasil yang diharapkan

Klik Submit Changes → dialog konfirmasi muncul → dijawab → perubahan
tersimpan ke server → tetap di halaman yang sama.

## Kenapa ini menjelaskan banyak hal sekaligus

Temuan ini menjelaskan tiga gejala yang sebelumnya dikira masalah
terpisah:

| Gejala | Penjelasan |
|---|---|
| Nilai tidak tersimpan di halaman ini | Submit terputus oleh redirect sebelum request terkirim |
| Automation melaporkan `KONFIRMASI SUBMIT TIDAK TERJAWAB` | Dialog konfirmasi ikut lenyap bersama halaman lama — tidak ada yang bisa diklik |
| Halaman lain (smk3/smkp, YearlyReport) tampak aman | Belum tentu aman — pengamatan manual menunjukkan Yearly pun bermasalah saat Submit |

## PENTING: bug ini INTERMITEN, tidak terjadi di setiap percobaan

Run `pytest -k "lagging_deep and statistic"` (2026-09-08, sesudah run
`-m MonthlyReport_Edit` yang gagal) justru menunjukkan Submit Changes
**BERHASIL menyimpan**:

```
[BUG SUDAH DIPERBAIKI?] Submit Changes kali ini MENYIMPAN dengan benar.
```

Padahal beberapa menit sebelumnya, halaman yang sama, kolom yang sama,
gagal:

```
FAILED ... Edit 'PenyakitAkibatKerja' = '5' tidak tersimpan
           -- setelah reload terbaca '1'
```

Jadi perilakunya **tidak deterministik**. Ini WAJIB disebut saat
laporan dikirim ke tim dev: kalau mereka mencoba sekali dan berhasil,
bukan berarti bug-nya tidak ada. Bug intermiten yang dilaporkan sebagai
deterministik biasanya ditutup sebagai "cannot reproduce".

Yang belum diketahui: apa pemicunya. Kandidat yang belum diuji —
apakah redirect muncul hanya saat ada draft lokal tersisa, hanya pada
periode tertentu, atau bergantung waktu/urutan aksi.

## Konfirmasi automation: bug KONFIGURASI, bukan bug template

Run `pytest -m MonthlyReport_Edit` (2026-09-08) — 20 test di keempat
halaman `MonthlyReport/Edit`:

```
1 failed, 15 passed, 4 skipped
FAILED test_safety_lagging_deep[statistic_safety_recapitulation]
  - Edit 'PenyakitAkibatKerja' = '5' tidak tersimpan setelah Submit
    Changes -- setelah reload terbaca '1'
```

Satu-satunya yang gagal adalah Id=1317. Golden Rules (1316), MWT Daily
(1312), dan Emergency Drill Daily (1319) — template yang sama persis —
lulus semua.

Jadi bug ini melekat pada **konfigurasi laporan Id=1317**, bukan pada
template `MonthlyReport`. Itu mempersempit sasaran perbaikan buat tim
dev: bandingkan konfigurasi Id=1317 dengan 1316/1312/1319.

## Status verifikasi automation

`tools/cek_simpan_inline.py` sudah dilengkapi perekaman URL sebelum dan
sesudah Submit (2026-09-08). Kalau perpindahan ini terjadi juga saat
dijalankan otomatis, laporannya akan memuat:

```
| URL BERPINDAH saat submit: '...MonthlyReport/Edit?Id=1317' -> '...YearlyReport/...'
   bukti saat submit: cek_simpan_..._PINDAH_URL_....png
```

**BELUM dijalankan ulang setelah penambahan itu** — konfirmasi otomatis
masih tertunda.

## Catatan penting soal hasil automation sebelumnya

Run `tools/cek_simpan_inline.py` 2026-09-08 melaporkan 11 halaman
`TERSIMPAN`, termasuk halaman ini untuk kolom
`AkibatPenyakitTenagaKerja`. **Hasil itu perlu ditinjau ulang** dalam
terang temuan manual di atas: kalau Submit selalu redirect tanpa
menyimpan, status `TERSIMPAN` itu kemungkinan berasal dari pembacaan
draft lokal yang lolos, bukan dari data server.

Kolom `PenyakitAkibatKerja` di halaman yang sama dilaporkan
`TIDAK TERSIMPAN` oleh alat yang sama. Perbedaan antar-kolom itu belum
dijelaskan dan tidak boleh dianggap sebagai fakta sebelum bug redirect
ini diperbaiki — selama Submit tidak pernah benar-benar terkirim,
perbandingan antar-kolom tidak bermakna.

## Yang sudah terjawab

- **Tujuan redirect**: `YearlyReport/Edit?Id=1317&DistrictCode=AT10`
  — Id sama, template salah.
- **Cakupan**: khusus Id=1317. Tiga halaman `MonthlyReport/Edit`
  lainnya normal.
- **Bukan efek testing**: terulang di incognito dan di mesin lain.

## Yang masih perlu dipastikan

- Apakah "reload terus" di halaman Yearly tujuan berhenti sendiri, atau
  tab harus ditutup?
- Apakah redirect juga terjadi untuk district selain AT10?

## Saran perbaikan (untuk tim dev OPEL)

- Tombol Submit Changes tidak boleh menavigasi. Alur yang benar:
  konfirmasi → kirim ke server → tetap di halaman, tampilkan hasil.
- Kalau navigasi memang disengaja setelah submit berhasil, pastikan
  request penyimpanan **selesai lebih dulu**, dan jangan berpindah
  sebelum konfirmasi dijawab.
- Minimal: tampilkan error eksplisit kalau submit gagal, supaya
  kegagalannya tidak senyap.
