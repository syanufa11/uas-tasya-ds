# Sistem ikon dashboard — TASK 15

Dashboard tetap memakai Streamlit, tanpa React atau dependensi ikon tambahan.
Audit menemukan emoji pada favicon, Overview, Data Quality, Methodology, banner
demo dan empty state, serta campuran Material Symbols pada tiga tujuan lain.
Tidak ditemukan stiker, ilustrasi AI, atau screenshot sebagai navigasi di sumber
dashboard/README. Grafik Plotly dan Altair serta perhitungan tetap dipertahankan.

## Library dan lisensi

- **Lucide 0.468.0**: SVG outline lokal dari repositori resmi, ketebalan 2 dan
  viewBox 24×24. Lisensi ISC serta pemberitahuan Feather/MIT disertakan di
  `dashboard/assets/icons/LICENSE-Lucide.txt` dan `LICENSE-Feather.txt`.
- **Skill Icons**: logo Python dan GitHub di README, bukan ikon navigasi.
  Aset resmi dipin pada commit yang dicatat dalam `sources.json`; lisensi MIT
  disertakan di `dashboard/assets/icons/technology/LICENSE.txt`.
- Tidak ada logo scikit-learn atau Tailwind yang ditambahkan karena keduanya
  bukan dependensi runtime dashboard ini. Tidak ada permintaan aset/CDN saat
  dashboard berjalan. Logo merek tidak dimodifikasi.

Sumber resmi: [Lucide SVG](https://lucide.dev/guide/packages/lucide-static),
[lisensi Lucide](https://lucide.dev/license),
[Skill Icons](https://github.com/tandpfun/skill-icons).
File SVG upstream dipertahankan; ukuran/aksesibilitas ditambahkan saat render.

## Pemetaan dan integrasi

| Penggunaan | Nama SVG Lucide |
|---|---|
| Overview | layout-dashboard |
| Sleep Analytics | moon |
| Physical Activity | footprints |
| Sleep & Activity Relationship | chart-no-axes-combined |
| Data Quality | shield-check |
| Methodology | book-open |
| Kalender | calendar-days |
| Petunjuk pengaturan tampilan | settings |
| Filter | sliders-horizontal |
| Unduh (helper tersedia, belum ada tombol unduh baru) | download |
| KPI durasi/aktivitas | clock |
| KPI jam bangun | sunrise |
| Provenance sintetis | flask-conical |
| Empty state | info |

`dashboard/icons.py` adalah sumber helper tunggal. `st.Page(icon=...)` tidak
menerima SVG arbitrer pada versi yang terpasang. Routing tetap `st.navigation`,
dengan posisi hidden; sidebar menampilkan `st.page_link` native dengan teks
dan status aktif. SVG dipasang sebagai CSS mask pada tautan dalam container
ber-key publik, tanpa menarget private class atau data-testid Streamlit.
Mask memakai currentColor sehingga langsung mengikuti light/dark dan status
tautan tanpa mengandalkan theme Python yang dapat terlambat satu rerun.

Ukuran sidebar 21 px, caption 18 px, status 20 px dan judul/KPI 24 px. Helper
SVG juga mendukung ukuran tombol 16–20 px; tidak ditambahkan tombol/fitur baru.
Navigasi dan kontrol tetap memiliki label teks, fokus keyboard dan perilaku
native. Ikon dekoratif inline memakai aria-hidden dan focusable=false; helper
mendukung label aksesibel yang di-escape jika ikon digunakan mandiri.

Hanya nama pada allowlist yang dapat dibaca. SVG lokal diperiksa sebagai XML:
primitive geometri dan atribut terbatas, tanpa script, event handler, href,
foreignObject, atau referensi eksternal. `st.html` tetap menggunakan sanitasi
bawaan dan JavaScript tidak diaktifkan. Favicon berupa SVG data URI lokal.
Kalender popup, menu Streamlit, toolbar grafik, spinner, dan kontrol native
yang sudah sesuai dipertahankan; tidak dilakukan penggantian DOM internal.

## Validasi

Tes berbasis fixture sintetis memeriksa geometri, aset lokal, penolakan nama
ilegal, escape label, data URI dan ketidakadaan emoji dalam kode dashboard.
AppTest menguji enam halaman, filter bersama, dua analisis tidur, pilihan
metrik, dan keadaan kosong/error. Pemeriksaan visual browser desktop/mobile
dan light/dark harus dilaporkan terpisah dari AppTest dan agent API.

Tidak ada pembacaan CSV privat, perubahan dataset, algoritma, atau hasil
analisis. Perubahan TASK 13 yang sudah ada tidak disertakan dalam commit ikon.

Hasil eksekusi lokal: Ruff seluruh proyek lulus, 63 tes lulus menggunakan
dependensi `.venv` dan pytest dari instalasi Python lokal. Enam halaman pada
Streamlit 1.67.0 agent API berstatus ready tanpa exception; server tidak
mencatat warning/traceback baru. Tidak ditemukan emoji pada kode dashboard.
Layanan browser/computer-use tidak tersedia (native pipe dan browser host
tidak dapat diakses), sehingga tampilan SVG, perpindahan tema, keyboard,
desktop dan mobile belum diverifikasi secara visual. AppTest/agent API tidak
membuktikan hasil render CSS mask. Push ditahan sampai QA visual selesai.
