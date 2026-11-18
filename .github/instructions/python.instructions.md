---
applyTo: "**/*.py"
---

# Python dan pemrosesan data

- Pisahkan pembacaan data, validasi, transformasi, pemodelan, dan penyimpanan; gunakan `pathlib`, fungsi dengan input/output eksplisit, serta type hints pada antarmuka utama.
- Validasi kolom, dtype, missing values, duplikasi, satuan, zona waktu, dan urutan waktu; jangan menebak format tanggal atau diam-diam membuang baris bermasalah.
- Catat aturan pembersihan dan agregasi; pertahankan data mentah dan cegah penimpaan sumber oleh output.
- Bentuk fitur lag/rolling hanya dari informasi yang tersedia saat prediksi. Pisahkan waktu sebelum imputasi, scaling, seleksi fitur, atau tuning; gunakan pipeline scikit-learn dan validasi temporal dengan gap sesuai horizon bila diperlukan.
- Gunakan baseline dan metrik sesuai tujuan penelitian. Uji transformasi penting, kasus batas, dan batas waktu fitur dengan fixture sintetis berlabel; jangan menyajikannya sebagai data atau hasil penelitian.
- Hindari path mesin yang ditanam langsung, state global tersembunyi, dan penanganan exception yang menyembunyikan kegagalan.
