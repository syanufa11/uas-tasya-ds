---
name: python-reproducibility
description: >-
  Menjamin reproduktibilitas pipeline Python dan eksperimen data science:
  manajemen environment, pemrosesan deterministik, logging, provenance, dan
  kompatibilitas Colab/Streamlit. Gunakan saat menyiapkan pipeline atau dependensi.
---

# Python Reproducibility

Adaptasi dari *Intermediate Research Software Development Skills (Python)* (The Carpentries Incubator, CC BY 4.0).

## Kondisi penggunaan

Gunakan saat mengelola dependensi proyek, membangun pipeline cleaning/analisis yang harus menghasilkan output konsisten, atau mendokumentasikan eksperimen dan provenance data.

## Workflow

1. **Kelola environment dan dependensi secara minimal**: Catat paket yang benar-benar diperlukan di `requirements.txt` / `dashboard/requirements.txt`; pertahankan kompatibilitas Python di `.venv`, Google Colab, dan Streamlit.
2. **Pastikan pemrosesan deterministik**:
   - Tetapkan `seed` eksplisit untuk generator acak (`np.random.default_rng(seed)`).
   - Gunakan pengurutan deterministik sebelum operasi sensitif urutan (seperti deteksi overlap atau deduplikasi).
3. **Catat provenance dan jejak transformasi**:
   - Simpan data olahan terpisah dari ekspor mentah `samsunghealth_*`.
   - Rekam jumlah baris masuk, dikarantina, dan keluar serta alasan/aturan yang diterapkan (tanpa mengekspor PII ke log publik).
4. **Dokumentasikan eksperimen dan keterbatasan**: Catat versi pustaka utama, asumsi waktu/satuan, dan cakupan data yang digunakan.

## Aturan validasi

- Eksekusi ulang pipeline pada input dan konfigurasi sama menghasilkan output identik.
- Tidak ada dependensi baru yang ditambahkan tanpa alasan jelas dan kompatibel dengan Colab/Streamlit.
- Log dan artefak publik bebas dari data kesehatan pribadi maupun path sensitif.

## Output yang diharapkan

Pipeline deterministik, daftar dependensi minimal yang terverifikasi, serta catatan provenance dan asumsi yang jelas.
