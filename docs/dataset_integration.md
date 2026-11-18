# Integrasi dataset lokal — TASK 13

Pipeline membaca ekspor asli tanpa mengubahnya dan menghasilkan satu CSV privat:
`data_processed/samsung_health_merged.csv`. Laporan berisi hasil aktual berada di
`reports/dataset_integration_report.md`; bukti agregat di
`data_audit/task13_validation.json`. Semua artefak tersebut diabaikan Git.

Jalankan dari root proyek dengan environment dependensi proyek:

```powershell
python scripts/build_merged_dataset.py
python -m pytest -q
python -m ruff check src/samsung_health/merged.py scripts/build_merged_dataset.py tests/test_merged_dataset.py
```

Satu baris mewakili tanggal kalender kandidat. Tidur diatribusikan ke tanggal bangun
Asia/Jakarta, dengan asumsi teks ekspor UTC dan offset +07:00. Sesi overlap
dikarantina seluruhnya; sesi utama adalah interval terpanjang pada tanggal bangun,
dengan awal UTC lebih awal sebagai pemecah seri. Sesi sekunder tidak dijumlahkan.
Durasi tersimpan tetap missing bila kosong; interval end-start tersedia terpisah.
Langkah dan durasi aktif hanya dari activity.day_summary, tanpa menjumlahkan sumber
langkah alternatif. Tanggal aktivitas harus unik; join memakai one_to_one dan outer
calendar. Kalender tanpa observasi tidak diisi nol.

`date` menggunakan **dd/mm/yyyy**, sesuai arahan terbaru. Baca dengan
`pd.to_datetime(df['date'], format='%d/%m/%Y')`. Timestamp tidur memakai ISO 8601
dengan offset. active_time_minutes memakai konversi empiris milidetik/60000.
Kolom turunan jam dan kalender bukan pengukuran independen. Jarak tidak disertakan
karena satuan ekspor belum terkonfirmasi.

CSV berstatus **kandidat**, karena waktu sumber, batas hari aktivitas, dan satuan
aktivitas belum dikonfirmasi sepenuhnya. EDA boleh mengeksplorasi kandidat dengan
keterbatasan tersebut; regresi/clustering final memerlukan penyelesaian validasi.
Tidak ada model atau klaim performa dari pipeline ini.

Join tanggal sama bukan rancangan prediksi. Untuk asosiasi aktivitas sebelum tidur,
gunakan `prior_activity_dates`: tanggal UTC mulai tidur dikurangi satu hari, dengan
batas akhir konservatif D+1 00:00 UTC <= awal tidur. Lookup berdasarkan tanggal,
bukan pergeseran posisi baris. Pemilihan sesi terpanjang bersifat retrospektif;
prediksi memerlukan target yang ditetapkan di awal, ketersediaan fitur, split
kronologis, dan preprocessing hanya pada train. Fitur akhir/jam bangun/durasi
interval target dilarang menjadi prediktor durasi target.

Dataset asli tidak dihubungkan ke dashboard demo publik. Publikasikan hanya kode,
dokumentasi metode tanpa statistik pribadi, serta fixture sintetis. Validasi
kritis yang belum selesai menghalangi push publik untuk tugas ini.

Pemeriksaan implementasi yang dijalankan: Ruff seluruh proyek lulus; suite lengkap
42 tes lulus dengan Python `.venv` (pandas 2.2.3, Plotly 6.9.0), menggunakan pytest
dari instalasi Python lokal melalui tambahan `sys.path`. Eksekusi awal dengan
Python sistem menghasilkan 35 lulus dan 7 gagal karena Plotly tidak terpasang di
environment tersebut. Sembilan tes baru memakai fixture sintetis. Pemeriksaan
tracked-file privacy lulus; CSV kandidat, laporan privat, dan JSON diagnostik
terbukti ignored dan tidak tracked. Eksekusi ulang menghasilkan CSV identik
secara byte; hash seluruh file sumber tidak berubah. Tidak ada commit atau push.
