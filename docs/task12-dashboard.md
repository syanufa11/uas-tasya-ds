# TASK 12 — Integrasi skill dan dashboard analitik

## Research dan scope

Framework tetap **Streamlit**, tanpa React/Next.js, autentikasi, CRUD, role,
database, atau API tambahan. Pengolahan data tetap di `src/samsung_health/`.
Pipeline pembersihan dan dokumen TASK 01–11 dipertahankan.

Referensi [admin panel Owais232](https://github.com/Owais232/Admin-Panel-Skill-LLM-Models)
ditelaah bersama kedua referensinya. Izin penyalinan belum dapat ditetapkan;
skill `.github/skills/build-admin-panel/` ditulis orisinal, tanpa menyalin teks,
skrip, atau aset upstream. Atribusi dan keputusan penggunaan ada di
[references/attribution.md](../.github/skills/build-admin-panel/references/attribution.md).
Skill tidak membutuhkan dependensi runtime tambahan.

`tailwind-4-docs` TASK 09 tetap satu instalasi dengan lisensi BSD-3-Clause.
Panduan engineering yang sudah tersedia digunakan untuk keputusan token dan
reuse. Snapshot dokumentasi belum diinisialisasi dan tidak diunduh. Tidak ada
persetujuan lisensi snapshot yang diasumsikan. Tailwind v4 tidak ditambahkan ke
runtime Streamlit karena aplikasi tidak memiliki entrypoint/build CSS sendiri;
tidak ada CDN atau migrasi frontend. Apabila kelak dibutuhkan komponen Tailwind,
inisialisasi dokumentasi harus mengikuti izin dalam skill tersebut.

## Design dan build

Enam tujuan navigasi memakai sidebar native yang dapat dilipat:

| Halaman | Komponen |
|---|---|
| Overview | KPI tidur, tren Plotly, tabel periode |
| Sleep Analytics | Pilihan pola/konsistensi, seluruh analisis tidur lama |
| Physical Activity | KPI langkah/menit aktif, pilihan metrik, grafik dan tabel |
| Sleep & Activity Relationship | Pilihan variabel, Pearson r, scatter dan tabel pasangan |
| Data Quality | Pemeriksaan yang dihitung, jumlah temuan, kamus enam kolom inti |
| Methodology | CRISP-DM, metode, privasi, keterbatasan interpretasi |

Tema native terang/gelap memakai navy, indigo, cyan, dan netral. Pilih melalui
menu ⋮ → Settings → Appearance. Kartu KPI native menggunakan baris yang dapat
membungkus; grafik mengikuti lebar panel. Helper CSS lama tetap tersedia untuk
kompatibilitas, tetapi tidak disuntikkan ke UI. Tema widget tidak ditimpa CSS.
Plotly melengkapi Altair yang dipertahankan pada analisis tidur lama.

Kontrol bersama pada entrypoint bertahan ketika berganti halaman: periode awal/
akhir, jendela 30/60/90 hari mundur dari akhir periode, serta jenis hari. Filter
diterapkan pada satu seri sintetis 90 hari yang tetap, sehingga nilai tanggal
yang sama tidak berubah ketika jendela dipilih. Rata-rata bergerak Overview
memakai tujuh observasi setelah filter, bukan selalu tujuh hari kalender.

Spinner, kondisi tanggal belum lengkap, data kosong, skema tidak valid, dan
korelasi tidak dapat dihitung ditangani eksplisit. Grafik baru memiliki deskripsi
aksesibilitas. Pemeriksaan browser tetap diperlukan untuk keyboard, kontras,
tooltip, dan responsivitas nyata.

## Integrasi data dan privasi

Data publik sepenuhnya sintetis: tanggal tahun 2000, seed tetap, aktivitas dibuat
independen dari tidur. Tidak ada loader ekspor pribadi dalam jalur dashboard.
Korelasi demo memakai tanggal yang sama dan tidak menggantikan alignment
temporal penelitian TASK 11A; nilai r tidak menjadi kesimpulan atau sebab-akibat.
Score, stage, dan efficiency tidak ditampilkan sebagai hasil nyata.

`validate_dataset()` memeriksa skema demo terpisah dari kelayakan data asli.
Pemeriksaan lokal:

```powershell
.venv/Scripts/python.exe scripts/check_dashboard_schema.py
```

Skrip hanya membaca ekspor lokal, memvalidasi struktur CSV dan sedikitnya lima
kolom aktivitas nonkosong. Pemeriksaan 2026-11-18 lulus. Tidak ada baris, nilai,
rentang tanggal pribadi, atau hasil statistik kesehatan yang dimasukkan ke Git.
Pemeriksaan ini tidak membuktikan kualitas setiap observasi atau alignment.

## Bukti QA lokal

- Ruff seluruh proyek: lulus.
- Pytest: 31 lulus untuk berkas yang dipublikasikan; seluruh workspace 33 lulus
  termasuk dua test lokal TASK 11A yang sudah ada. Cakupan mencakup keenam renderer,
  perubahan jendela/jenis hari, kedua analisis tidur, pilihan metrik aktivitas/
  hubungan, tanggal tidak lengkap, data kosong, dan kegagalan skema.
- Konfigurasi TOML, compileall, validasi skill, dan `pip check`: lulus.
- Server lokal port 8512 dan alamat pengguna `localhost:8501`: endpoint
  `/_stcore/health` mengembalikan `ok`. Ini hanya bukti kesehatan server.
- AppTest tidak memerlukan ekspor asli. Pengujian privasi memeriksa file Git;
  guard dijalankan lagi terhadap index sebelum commit.
- Browser tidak tersedia: inventori tool mengembalikan `browser access host is
  unavailable` dan native pipe tidak tersedia. Tidak ada klaim QA visual desktop/
  mobile, interaksi navigasi browser, console, atau network browser lulus.

## GitHub dan hosting

Gunakan workflow CI yang ada; versi minimum Streamlit menjadi 1.67 untuk API UI
yang dipakai dan Plotly 6 ditambahkan pada kedua requirements. Commit dan push
TASK 12 hanya mencakup file task ini; perubahan bawaan `.gitignore` dan berkas
verifikasi TASK 11A lokal tidak dicampurkan.

URL produksi Streamlit belum tercatat di repository dan API GitHub deployments
tidak menampilkan deployment saat audit. Keberhasilan CI tidak membuktikan
Streamlit sudah redeploy. Periksa URL publik serta revision pada Manage app
sesudah push; jika akses hosting tidak tersedia, nyatakan belum terverifikasi.
Alamat `http://localhost:8501/` yang diberikan pengguna adalah server lokal,
bukan URL hosting publik. Metadata homepage GitHub juga belum diisi.
