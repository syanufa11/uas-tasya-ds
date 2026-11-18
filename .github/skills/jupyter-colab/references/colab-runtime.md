# Runtime Google Colab

Baca ketika notebook memakai Colab atau Google Drive.

- **Sekali per rancangan:** pusatkan path di satu sel. Pertahankan
  `drive.mount('/content/drive')` dan path Drive pilihan pengguna; jangan
  menggantinya dengan path mesin Windows sebagai jalur utama Colab.
- **Setiap runtime baru:** install dependensi yang diperlukan, mount Drive jika
  perlu, cek file/kolom wajib, dan jalankan sel berurutan. Catat versi aktual;
  jangan mengklaim setup berhasil sebelum dicoba.
- **Otomatis dalam notebook:** bangun path dengan `pathlib`, validasi input,
  panggil modul processing, dan simpan hasil terpisah. Jika modul berasal dari
  repo, jelaskan cara menyediakannya di runtime tanpa mengunggah ekspor pribadi.
- Jangan membuat fallback unduhan publik untuk data kesehatan. Autentikasi
  interaktif dilakukan pemilik akun; token tidak disimpan di sel/output.
- **Verifikasi:** restart runtime dan Run all ketika akses data tersedia.
  Periksa render Colab aktual untuk clipping legenda/label dan plot terlalu
  besar. Pemeriksaan lokal saja harus diberi batas verifikasi.
- Simpan bukti eksekusi privat jika diperlukan, lalu bersihkan output/metadata
  sensitif pada salinan yang dibagikan tanpa menghapus kode analisis.
