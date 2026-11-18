---
name: machine-learning
description: >-
  Melatih dan mengevaluasi prediksi Samsung Health dengan baseline, pipeline,
  dan validasi temporal. Gunakan setelah target dan horizon terverifikasi;
  tidak menetapkan sleep score yang tidak tersedia sebagai target.
---

# Machine Learning

## Kondisi penggunaan

Gunakan ketika pertanyaan prediktif, dataset, dan waktu ketersediaan fitur jelas.

## Workflow

1. Baca brief dan kamus fitur. Pastikan target memiliki observasi valid memadai
   untuk train/validation/test; jika tidak, laporkan kelayakan sebelum melatih.
   Bedakan prediksi durasi interval dari pengukuran kualitas tidur.
2. Tetapkan waktu prediksi, horizon, metrik utama, dan baseline sederhana.
   Untuk split/fit fitur, baca [evaluasi temporal](references/temporal-evaluation.md).
3. Buat pembagian kronologis dan pipeline preprocessing/model; mulai dari model
   sederhana. Catat seed, parameter, versi, dan periode tiap split.
4. Bandingkan baseline/kandidat pada fold waktu yang sama. Batasi tuning pada
   data pengembangan; pilih model sebelum evaluasi test terakhir.
5. Analisis error, stabilitas antarperiode, dan generalisasi. Simpan pipeline,
   kontrak fitur, konfigurasi, serta ringkasan evaluasi secara lokal.

## Aturan validasi

- Tidak ada target atau informasi masa depan di input; operasi yang belajar
  dari data berada dalam split/fold, termasuk seleksi fitur dan imputasi.
- Baseline/model memakai target, unit, horizon, serta tanggal evaluasi sama;
  laporkan jumlah sampel dan metrik yang benar-benar dihitung.
- Uji batas waktu fitur dan muat pipeline untuk inferensi dengan kontrak sama.
  Data kecil atau model kalah baseline tetap dilaporkan apa adanya.

## Output yang diharapkan

Kode eksperimen reproducible, definisi split/fitur, tabel baseline/model, analisis
error, pipeline lokal, dan keterbatasan. Tidak mencakup deploy.
