---
name: jupyter-colab
description: >-
  Membuat atau merapikan notebook UAS Samsung Health untuk Jupyter dan Google
  Colab, termasuk konfigurasi Drive, urutan eksekusi, dan output. Gunakan untuk
  artefak ipynb serta runtime; metode statistik/model mengikuti tahapnya.
---

# Jupyter dan Colab

## Kondisi penggunaan

Gunakan ketika membuat, mengubah, atau memverifikasi notebook proyek.

## Workflow

1. Periksa notebook/modul yang tersedia. Susun Markdown sesuai tahap CRISP-DM
   yang dikerjakan; pertahankan pekerjaan yang sudah ada dan gunakan modul
   processing/model proyek bila tersedia.
2. Pusatkan import, seed, path, versi dependensi, dan pilihan input di awal.
   Untuk Colab/Drive, baca [runtime Colab](references/colab-runtime.md).
3. Buat sel berurutan dengan input/output eksplisit; validasi skema, cakupan,
   serta batas waktu sebelum analisis/modeling.
4. Tulis interpretasi setelah output tersedia. Buat judul, satuan, sumbu,
   dan legenda yang terbaca pada viewport notebook.
5. Jalankan dari kernel bersih bila runtime/data tersedia; jika tidak, validasi
   struktur/sintaks dan catat sel belum dieksekusi. Bersihkan output/metadata
   sensitif pada versi yang dibagikan.

## Aturan validasi

- Format notebook valid, cell ID unik, kode dapat dikompilasi dengan penanganan
  magic/IPython yang sesuai, dan tidak bergantung pada eksekusi acak.
- Bedakan validasi statis, eksekusi lokal, dan eksekusi penuh Colab; hasil lokal
  tidak membuktikan mounting Drive atau grafik Colab sudah benar.
- Periksa render aktual grafik yang diubah; laporkan jika QA visual runtime
  tujuan belum tersedia.

## Output yang diharapkan

Notebook `.ipynb`, konfigurasi runtime/data, petunjuk eksekusi singkat, dan status
pemeriksaan beserta kendala yang tersisa.
