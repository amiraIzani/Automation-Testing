# Locator Login & Topbar OPEL

Hasil scan website OPEL (2026-08-20, `https://dev-opel.antm.tech/`, v2.6.7).

## Alur login (dikonfirmasi dari browser asli)

Di environment DEV, login terjadi **otomatis**:

1. `driver.get(BASE_URL)` → 1 redirect → langsung `/My/Dashboard`.
2. Server menerbitkan cookie `.AspNetCore.Cookies` tanpa form apapun
   (auth internal dev / integrated auth domain).
3. Form Azure AD B2C (`antamapps.b2clogin.com`) **tidak pernah muncul**
   dari mesin ini. Locator B2C di `pages/login_page.py` hanya cadangan
   untuk deteksi "stuck di form login" kalau mekanisme auth berubah.

## Elemen penting halaman utama (My/Dashboard)

| Nama | Locator | Catatan |
|---|---|---|
| HOME_LOADED_MARKER | `a.header-icon[data-toggle='dropdown'] img.profile-image` | Avatar user di header kanan-atas, selalu tampil. Logo header TIDAK bisa dipakai: ukurannya 0x0 di viewport <1600px |
| Trigger dropdown avatar | `a.header-icon[data-toggle='dropdown']` | `title`-nya = email user (`poetri4y@gmail.com`) |
| Nama user di dropdown | `.dropdown-menu .info-card-text` | Berisi nama + email |
| Tombol Logout | `a.dropdown-item[href="javascript: signOut()"]` | Di dalam dropdown avatar, teks "Logout" |
| Bell notifikasi | `#linkNotificationCount` | Header kanan, `data-toggle="dropdown"` |
| Badge jumlah notifikasi | `#bdgNotificationCount` | Angka notifikasi baru |
| Dropdown notifikasi | `#dropdownNotification` | Dibuka oleh bell |
| Daftar notifikasi | `#lstNotification` | `<ul>` isi notifikasi |
| Tombol settings | `a.header-icon[data-toggle='modal'][data-target='.js-modal-settings']` | Ikon gear di header |
| User di sidebar | `.info-card` (dalam `#js-primary-nav`) | Avatar + nama + role |
| Input filter menu sidebar | `#nav_filter_input` | Placeholder "Filter menu" |

### Item dropdown avatar (selain logout)

- Reset Layout : `a.dropdown-item[data-action='app-reset']`
- Settings     : `a.dropdown-item[data-toggle='modal'][data-target='.js-modal-settings']`
- Fullscreen   : `a.dropdown-item[data-action='app-fullscreen']`
- Print        : `a.dropdown-item[data-action='app-print']`

## Form Azure AD B2C (cadangan — BELUM terverifikasi, tidak muncul di DEV)

| Nama | Locator | Status |
|---|---|---|
| B2C_EMAIL_INPUT | `#email` | Asumsi template default B2C Microsoft — belum bisa diverifikasi |
| B2C_PASSWORD_INPUT | `#password` | idem |
| B2C_SIGNIN_BUTTON | `#next` | idem |

## Menu sidebar utama (urutan tampil)

Home, My Dashboard (`/My/Dashboard`), My Task (`/My/UserTask`),
Chat Room (`/Chat`), Ticketing, Master, Transaction, Reporting &
Dashboard, Calculator, Supersafe, System, Configuration, HSS.

- Setiap item menu: `<a href="#">` dengan `<span class="nav-link-text">Teks</span>`
  → XPath klik: `//span[normalize-space(text())='Teks']`
- Submenu item memakai `href` asli (mis. `/Reporting/...`).
- Sidebar bersifat kontekstual: halaman Timesheet menampilkan submenu
  Timesheet tambahan (Daily/Monthly/Yearly/Static Input).

## Framework terdeteksi

SmartAdmin (template Bootstrap 4) + jQuery + DataTables (tabel
`table.reportData.dataTable`) + SignalR (chat kolaborasi
`#collab-chat-window`, launcher `#collab-chat-launcher`).
