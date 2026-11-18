---
name: streamlit-dashboard
description: >-
  Membuat atau memperbarui dashboard Streamlit UAS Samsung Health untuk
  eksplorasi agregat dan inferensi terverifikasi. Gunakan untuk UI, filter,
  grafik interaktif, dan validasi dashboard; deploy hanya bila diminta.
---

# Streamlit Dashboard

## Kondisi penggunaan

Gunakan setelah kontrak data olahan atau pipeline inferensi tersedia.

## Workflow

1. Pilih halaman/metrik sesuai tujuan penelitian. Muat hasil olahan atau
   pipeline dari modul proyek; jangan melatih ulang model pada rerun UI.
2. Pisahkan UI, loader, perhitungan, dan inferensi. Validasi skema, periode,
   satuan, dan versi fitur/model saat pemuatan.
3. Tambahkan filter periode/grafik relevan, jumlah data valid, dan definisi
   metrik. Sediakan empty state serta error aman untuk input hilang, perubahan
   skema, dan filter tanpa hasil.
4. Hindari cache global untuk data kesehatan privat; isolasikan state sesi.
   Jika ada unduhan, gunakan agregat/hasil tersamarkan yang telah ditinjau.
5. Uji interaksi, konsistensi angka, rerun, dan layar kecil. Jika deploy diminta,
   pisahkan rahasia/data dari kode; laporkan status berdasarkan pemeriksaan
   lingkungan tujuan.

## Aturan validasi

- Cocokkan ringkasan dengan fungsi analisis pada filter sama; periksa batas
  tanggal, data kosong, missing, dan kegagalan pemuatan.
- Prediksi memakai kontrak fitur/pipeline yang dievaluasi; metrik tidur yang
  tidak tersedia tidak diisi nilai contoh atau skor buatan.
- Jalankan smoke check aplikasi dan periksa UI aktual bila memungkinkan;
  kompilasi Python saja tidak membuktikan interaksi bekerja.
- Tinjau kebocoran melalui log, state/cache, grafik, dan unduhan sebelum berbagi.

## Output yang diharapkan

Aplikasi Streamlit lokal, konfigurasi input, perintah menjalankan, hasil
pemeriksaan perhitungan/UI, dan keterbatasan. Status deploy dilaporkan terpisah.
