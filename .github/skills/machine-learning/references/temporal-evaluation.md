# Evaluasi temporal

Baca saat membentuk target/fitur, menetapkan split, atau melakukan tuning.

1. **Kontrak waktu:** tentukan `prediction_time`, interval target, dan waktu
   tiap input benar-benar tersedia. Ringkasan aktivitas sehari penuh belum
   tersedia saat prediksi pada awal hari tersebut.
2. **Horizon:** bedakan sesi berikutnya dan hari kalender berikutnya.
   `shift(-1)` pada data bergap berarti observasi berikutnya, bukan otomatis
   H+1 kalender. Selaraskan melalui waktu terverifikasi dan tandai target hilang.
3. **Riwayat:** lag/rolling berakhir sebelum waktu prediksi; rolling pada target
   biasanya perlu shift lebih dahulu. Riwayat train boleh menjadi konteks
   validation jika tersedia pada saat inferensi.
4. **Split:** simpan periode terakhir sebagai test; gunakan expanding/rolling
   validation sebelumnya. Purge baris train dengan interval label melintasi
   awal validation/test. Tentukan gap berdasarkan overlap label dan ketersediaan
   data; data tidak berjarak seragam perlu split tanggal, bukan asumsi gap
   baris sama dengan gap hari.
5. **Fit:** imputasi, scaler, encoding, seleksi fitur, dan tuning hanya fit pada
   train tiap fold melalui pipeline. Hindari interpolasi dua arah/backward fill
   yang mengambil nilai masa depan untuk input prediksi.
6. **Baseline/metrik:** untuk regresi durasi, pertimbangkan persistensi/median
   historis dengan MAE dalam menit dan RMSE pelengkap. Untuk klasifikasi dengan
   label valid, gunakan baseline kelas serta metrik sesuai ketidakseimbangan;
   ambang dipilih pada train/validation.
7. **Bukti:** periksa timestamp di batas fold dengan fixture sintetis berlabel.
   Nyatakan evaluasi fixed-origin atau walk-forward; pembaruan label/fitur
   mengikuti informasi yang sudah tersedia pada saat itu.
