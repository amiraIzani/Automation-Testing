# Bug: Witness Statement — Submit Changes membuang SEMUA baris pending setelah konfirmasi

- **Tanggal**: 2026-09-08
- **Ditemukan lewat**: pengecekan MANUAL oleh pemilik produk
- **Halaman**: Safety > Transaction > Leading Indicator > Witness Statement Report
  (`https://dev-opel.antm.tech/Reporting/Timesheet/DailyReport/Edit?Id=1336`)
- **Severity**: **TINGGI** — pekerjaan user hilang total setelah ia
  justru MEMENUHI validasi dan mengonfirmasi penyimpanan.
- **Status**: **TERBUKA**

## Langkah reproduksi (urutan persis dari pengamatan manual)

1. Di grid sudah ada **beberapa baris pending** hasil automation test
   (sebagian field wajibnya belum terisi).
2. User menambahkan **input manual** sendiri.
3. Klik **Submit Changes** → muncul **peringatan validasi field wajib**.
4. User **mengisi field wajib** yang diminta.
5. Klik **Submit Changes** lagi → **jawab konfirmasi**.

## PENTING: INTERMITEN — tidak selalu terjadi

Percobaan ulang pada 2026-09-08 (tak lama setelah kejadian di atas)
**tidak lagi mereproduksi** kehilangan data: alurnya berjalan normal.

Jadi perilakunya **tidak deterministik**. Ini WAJIB disebut saat
laporan dikirim ke tim dev — kalau mereka mencoba sekali dan berhasil,
bukan berarti bug-nya tidak ada. Bug intermiten yang dilaporkan seolah
pasti terjadi biasanya ditutup sebagai "cannot reproduce".

Kandidat pemicu yang belum diuji: apakah kehilangan hanya terjadi kalau
grid memuat baris pending yang TIDAK VALID (sisa automation) bersamaan
dengan baris valid — yaitu skenario batch campuran seperti pada dugaan
akar masalah di bawah. Kalau benar, kuncinya bukan halamannya melainkan
**kombinasi baris valid + tidak valid dalam satu Submit**.

Bug kedua di proyek ini yang ternyata intermiten; yang pertama
`submit-changes-redirect-tanpa-menyimpan.md`.

## Hasil yang diharapkan

Baris yang sudah valid tersimpan. Kalau masih ada baris lain yang tidak
valid, baris itu saja yang ditolak — dengan pesan yang menunjuk baris
mana.

## Hasil aktual

Setelah konfirmasi, **SEMUA input hilang** — baik yang diketik manual
oleh user maupun yang dibuat automation. Grid kembali kosong. Tidak ada
pesan error yang menjelaskan.

Yang membuat ini serius: kehilangan terjadi **setelah** user memperbaiki
validasi dan menekan konfirmasi. Dari sudut pandang user, ia sudah
melakukan semua yang diminta aplikasi, lalu pekerjaannya lenyap.

## Dugaan akar masalah

Pola ini identik dengan bug yang pernah dilaporkan di halaman lain —
lihat `master-alat-submit-drops-new-row.md` (ditutup 2026-09-07 karena
tidak lagi terjadi di Master Alat):

> Endpoint Submit Changes tampaknya memvalidasi/mem-proses SEMUA baris
> pending sebagai satu batch. Kalau salah satu baris pending gagal
> validasi, kemungkinan seluruh batch — termasuk baris lain yang VALID —
> ikut dibuang, bukan cuma baris yang bermasalah.

Di kasus ini baris pending dari automation kemungkinan masih belum
lengkap saat Submit terakhir, sehingga seluruh batch — termasuk baris
manual yang sudah valid — ikut terbuang.

Kalau dugaan ini benar, bug-nya **bukan khusus Witness Statement**
melainkan perilaku batch Submit Changes secara umum, yang di Master
Alat sudah diperbaiki tapi di halaman ini belum.

## Yang perlu dipastikan tim dev

- Apakah seluruh batch memang dibuang saat satu baris gagal validasi?
- Kenapa tidak ada pesan error setelah konfirmasi, padahal penyimpanan
  gagal?
- Apakah halaman `DailyReport/Edit` lain (Id=1334, Id=1335) berperilaku
  sama kalau ada baris pending yang tidak valid?

## Saran perbaikan

- Validasi tiap baris pending **secara independen**: baris valid tetap
  tersimpan meski ada baris lain yang gagal.
- Kalau batch memang harus utuh, **jangan buang input user** — kembalikan
  ke grid dengan penanda baris mana yang bermasalah.
- Wajib ada pesan error eksplisit. Kehilangan data yang senyap jauh
  lebih berbahaya daripada pesan gagal.

## Catatan untuk automation test

`test_safety_create_inline` melewati (skip) halaman yang menerapkan
validasi field wajib — `isi_baris_kosong_inline()` tidak bisa mengisi
kolom lookup/select, jadi barisnya memang tidak akan pernah valid.
Skip itu TIDAK berhubungan dengan bug ini; bug ini muncul justru ketika
field wajib SUDAH dipenuhi.

**Catatan proses:** laporan awal soal halaman ini sempat ditarik pada
2026-09-08 karena dikira sekadar penolakan validasi. Penarikan itu
keliru — urutan lengkapnya (validasi dipenuhi → konfirmasi → semua
hilang) baru terungkap sesudahnya. Pelajarannya sudah dicatat di
`README.md` folder ini.
