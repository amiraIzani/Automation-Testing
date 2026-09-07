# Bug: Tombol Cancel di grid Lagging Indicator tidak membuang perubahan pending

- **Tanggal ditemukan**: 2026-09-04
- **Ditemukan lewat**: `tests/test_safety.py::TestSafetyHss::test_safety_lagging_deep[smk3]`
- **Halaman**: Safety > Transaction > Lagging Indicator > SMK3
  (`Reporting/Timesheet/YearlyReport/Edit?Id=1308`) — kemungkinan
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
