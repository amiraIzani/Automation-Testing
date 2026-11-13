# Indeks Laporan Bug — HSS Safety

Ringkasan status semua laporan di folder ini. **Baca ini dulu** sebelum
mengirim apa pun ke tim dev OPEL — sebagian laporan sudah ditutup dan
tidak boleh dikirim.

Terakhir diperbarui: **2026-09-11**

| Laporan | Status | Kirim ke dev? |
|---|---|---|
| [submit-changes-redirect-tanpa-menyimpan](submit-changes-redirect-tanpa-menyimpan.md) | **DITUTUP** — sudah diperbaiki aplikasi (2026-09-10) | Tidak |
| [witness-statement-submit-membuang-semua-baris-pending](witness-statement-submit-membuang-semua-baris-pending.md) | **TERBUKA** (intermiten) | **YA** |
| [statistic-safety-recap-inline-edit-tidak-tersimpan](statistic-safety-recap-inline-edit-tidak-tersimpan.md) | Gejala dari laporan Id=1317 — ikut selesai | Tidak |
| [master-alat-submit-drops-new-row](master-alat-submit-drops-new-row.md) | Sudah diperbaiki aplikasi | Tidak |
| [lagging-cancel-does-not-discard-edit](lagging-cancel-does-not-discard-edit.md) | BUKAN BUG (salah asumsi test) | Tidak |

---

## 1. Submit Changes redirect tanpa menyimpan — **DITUTUP (2026-09-10)**

**Sudah diperbaiki aplikasi.** Id=1317 memang seharusnya
`YearlyReport`; saat bug dilaporkan, halamannya masih dirender sebagai
`MonthlyReport/Edit` sementara link sidebar dan tujuan Submit sudah
`YearlyReport/Edit`. Per 2026-09-10 semuanya konsisten Yearly dan tidak
ada lagi redirect. Sifat "intermiten"-nya berasal dari perbaikan yang
berlangsung saat pengujian. **Jangan dikirim ke tim dev.**

Riwayat saat laporan masih terbuka:

- **Halaman**: Statistic Safety Recapitulation, `MonthlyReport/Edit?Id=1317`
- **Gejala**: klik Submit Changes langsung me-redirect ke
  `YearlyReport/Edit?Id=1317&DistrictCode=...` **sebelum dialog
  konfirmasi muncul**. Request penyimpanan tidak pernah terkirim.
- **Cakupan**: hanya Id=1317. Tiga halaman `MonthlyReport/Edit` lain
  (1316, 1312, 1319) normal — jadi bug konfigurasi, bukan bug template.
- **Sifat**: **INTERMITEN.** Tidak muncul di setiap percobaan. Ini
  WAJIB disebut saat melapor, supaya tidak ditutup sebagai
  "cannot reproduce".
- **Bukan efek testing**: terulang di incognito dan di mesin lain.
- **Di suite**: sempat didaftar di
  `HssSafetyPage.SUBMIT_REDIRECT_TANPA_SIMPAN` supaya suite tidak merah
  permanen (pemeriksaan penyimpanan dilonggarkan jadi peringatan
  `[BUG DIKENAL]`). **Set itu dikosongkan 2026-09-10** — pemeriksaan
  penyimpanan halaman ini kembali di-assert penuh.

## 2. Witness Statement — Submit membuang SEMUA baris pending — **TERBUKA**

Satu-satunya bug aplikasi yang masih terbuka.

- **Halaman**: Witness Statement Report, `DailyReport/Edit?Id=1336`
- **Gejala**: user mengisi field wajib yang diminta validasi, klik
  Submit, jawab konfirmasi — lalu **semua input hilang**, baik yang
  diketik manual maupun sisa baris automation.
- **Kenapa serius**: kehilangan terjadi SETELAH user memenuhi validasi
  dan mengonfirmasi. Dari sudut pandang user, ia sudah melakukan semua
  yang diminta aplikasi.
- **Dugaan**: sama dengan pola batch di
  `master-alat-submit-drops-new-row.md` — satu baris pending tidak
  valid membuat SELURUH batch dibuang, termasuk baris yang sudah valid.
  Di Master Alat pola itu sudah diperbaiki; di sini belum.

**Catatan proses:** laporan pertama soal halaman ini
(`witness-statement-submit-membuang-baris-baru.md`) ditarik pada hari
yang sama karena dikira sekadar penolakan validasi biasa. Penarikan itu
**keliru** — urutan lengkapnya baru terungkap sesudahnya. Yang benar:
gejala pertama (baris test hilang) memang penolakan validasi, tapi ada
bug TERPISAH yang muncul setelah validasi dipenuhi.

Perlu dibedakan:

| Kejadian | Status |
|---|---|
| Baris test automation ditolak karena lookup wajib kosong | **Bukan bug** — aplikasi benar |
| Semua input hilang setelah field wajib dipenuhi + konfirmasi | **BUG** — laporan ini |

`test_safety_create_inline` melewati (skip) halaman bervalidasi karena
`isi_baris_kosong_inline()` tidak bisa mengisi lookup/select. Skip itu
tidak berhubungan dengan bug di atas.

## 3. Statistic Safety Recap tidak menyimpan — gejala, bukan akar

Temuan asli 2026-08-26. **Gejalanya nyata**, tapi akar masalahnya
ternyata laporan nomor 1. Dipertahankan sebagai riwayat.

Catatan proses: laporan ini sempat ditutup sebagai "BUKAN BUG" pada
2026-09-08 berdasarkan hasil automation yang ternyata membaca **draft
lokal**, bukan data server. Koreksinya datang dari pengecekan manual.

## 4. Master Alat — Submit membuang baris baru — SUDAH DIPERBAIKI

Ditemukan 2026-08-31, diverifikasi manual 2026-09-07: sudah tidak
terjadi lagi. Ditutup.

## 5. Cancel tidak membuang perubahan — BUKAN BUG

Laporan yang keliru. Draft lokal memang **sengaja** dipertahankan OPEL
sebagai fitur perlindungan (kalau halaman ter-reload atau koneksi
putus). Yang membuangnya adalah tombol **Reload Data**, bukan Cancel.

Test yang melahirkan laporan ini memakai asumsi salah dan sudah
diperbaiki: sekarang yang diuji adalah Reload Data.

---

## Pelajaran yang berlaku untuk laporan berikutnya

Empat laporan di atas menghasilkan tiga pelajaran yang mahal:

1. **Jangan tutup laporan bug berdasarkan hasil automation sebelum cara
   pembacaan automation-nya sendiri tervalidasi.** Laporan 1 & 2 sempat
   ditutup keliru karena alatnya membaca draft lokal.
2. **Verifikasi penyimpanan HARUS lewat Reload Data**, bukan reload
   browser atau `buka_halaman()` — keduanya memulihkan draft lokal dan
   menampilkan nilai yang baru saja diketik, seolah tersimpan.
3. **Sebutkan kalau bug-nya intermiten.** Bug tidak deterministik yang
   dilaporkan seolah pasti terjadi biasanya ditutup sebagai
   "cannot reproduce".
4. **Kegagalan menyimpan belum tentu bug — cek validasi field wajib
   dulu.** Kalau test mengisi baris otomatis tapi melewati kolom
   lookup/select, baris ditolak validasi dan dibuang. Itu aplikasi yang
   BENAR.
5. **Tapi jangan menarik laporan secepat menulisnya.** Laporan nomor 2
   ditarik karena penjelasan "validasi" terdengar meyakinkan — padahal
   di balik gejala yang sama ada bug terpisah yang baru terungkap
   setelah urutan lengkapnya ditanyakan.

Dua kesalahan berlawanan, sumbernya sama: **menyimpulkan sebelum
urutan kejadiannya lengkap.** Yang benar bukan "jangan cepat menuduh"
atau "jangan cepat menarik", tapi: minta reproduksi manual langkah demi
langkah dulu — termasuk apa yang terjadi SESUDAH tiap klik — baru
tulis atau tutup laporan.

Alat bantu yang memverifikasi hal-hal ini: `tools/cek_simpan_inline.py`.
