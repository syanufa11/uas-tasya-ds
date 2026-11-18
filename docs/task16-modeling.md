# TASK 16 — kesiapan pemodelan

Status penelitian: **tertahan validasi data; belum ada model yang dilatih**.
Laporan integrasi masih menyatakan batas hari aktivitas, satuan aktivitas,
dan atribusi zona waktu sebagai kandidat. CSV memilih sesi terpanjang per
tanggal bangun secara retrospektif; ini belum memenuhi target prospektif
“sesi tidur berikutnya”. Tidak ada asumsi yang diubah menjadi konfirmasi.

## Artefak

- `notebooks/16_samsung_health_modeling.ipynb`: notebook diagnostik lokal/Colab.
- `src/modeling/`: audit, EDA privat, pengunci pelatihan, spesifikasi Pipeline
  Dummy median, Linear Regression dan Random Forest yang belum fit.
- `reports/model_evaluation.md`: laporan aktual privat, diabaikan Git.
- `artifacts/task16/`: audit JSON, ringkasan CSV, grafik dan notebook hasil
  eksekusi privat; seluruh direktori diabaikan Git.
- Halaman dashboard `Model Evaluation`: status dan metrik belum tersedia;
  tidak membaca dataset privat dan tidak menyajikan performa sintetis.

## Reproduksi

Sekali per environment lokal:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-modeling.txt
```

Setiap input berubah, jalankan diagnostik dan notebook dari kernel bersih:

```powershell
.venv\Scripts\python.exe scripts/run_modeling_readiness.py
.venv\Scripts\python.exe scripts/execute_modeling_notebook.py
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pytest -q
```

Notebook publik sengaja tidak menyimpan output kesehatan. Salinan hasil
eksekusi tetap lokal. Di Colab, simpan kode repo dan data privat di Drive,
sesuaikan `PROJECT_ROOT`, install requirements pada runtime, lalu Run all.
Tidak ada unduhan dataset kesehatan dari URL publik. Eksekusi lokal tidak
membuktikan mounting Drive atau tampilan Colab.

## Langkah yang diperlukan sebelum pelatihan

1. Konfirmasikan semantik timestamp tidur, batas hari aktivitas dan satuan
   dari bukti sumber/aplikasi; perbaiki integrasi dan kamus data bila perlu.
2. Definisikan waktu prediksi dan sesi berikutnya tanpa memilih sesi melalui
   durasi masa depan. Bentuk ulang dari seluruh sesi jika diperlukan.
3. Catat waktu tersedia setiap fitur. Riwayat harus selesai sebelum prediksi;
   jangan memakai durasi interval, akhir tidur atau jam bangun target.
4. Setelah gate data direvisi berdasarkan bukti, implementasikan split 80/20
   kronologis dengan purge overlap label dan validasi temporal pada train.
   Fit imputasi/scaling di dalam fold Pipeline; tuning RF terbatas hanya train.
5. Hitung MAE/RMSE/R² pada test identik, grafik prediksi/residual, importance
   dan analisis error. Belum ada model terbaik atau bukti mengungguli baseline.
6. Evaluasi kelayakan K-Means terpisah setelah satuan/semantik jelas;
   gunakan scaling dan silhouette/stabilitas tanpa memaksakan cluster.

Implementasi evaluasi, tuning, lag prediktif dan clustering belum dijalankan
atau dianggap selesai. Pengunci pelatihan sengaja tidak memiliki flag override.
Temuan pribadi dan tanggal sumber tidak disertakan dalam dokumentasi publik.

## Pemeriksaan lokal

Notebook diagnostik dieksekusi dari kernel bersih; salinan publik tanpa output.
Kelima grafik EDA diperiksa visual. Audit, laporan dan tabel yang dijalankan
ulang identik, dan hash CSV masukan tidak berubah. Ruff, compileall, pip check
dan pytest dijalankan; hasil rinci dilaporkan saat penyerahan. AppTest memeriksa
halaman baru dan navigasi tujuh halaman, tanpa membaca data penelitian.
Tampilan browser dashboard dan Google Colab belum diverifikasi.

Windows App Control menolak DLL PyZMQ 27.3.0 pada lingkungan lokal. Wheel
26.3.0 terverifikasi dapat menjalankan kernel; pin khusus Windows disertakan
di requirements-modeling.txt. Runner memakai direktori runtime privat di
artifacts/ dan tidak mengubah kebijakan keamanan Windows.
