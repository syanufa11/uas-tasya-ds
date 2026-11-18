---
name: python-software-design
description: >-
  Menerapkan prinsip desain perangkat lunak Python tingkat intermediate:
  modularisasi, separation of concerns, fungsi reusable, dan refactoring aman.
  Gunakan saat merancang modul di src/, memisahkan logika dari UI Streamlit,
  atau merapikan skrip analisis.
---

# Python Software Design

Adaptasi dari *Intermediate Research Software Development Skills (Python)* (The Carpentries Incubator, CC BY 4.0).

## Kondisi penggunaan

Gunakan saat membuat modul baru di `src/`, memecah skrip monolitik, atau memisahkan logika pemrosesan/analisis data dari tampilan Streamlit dan notebook.

## Workflow

1. **Identifikasi tanggung jawab**: Pisahkan pembacaan I/O, validasi skema/waktu, transformasi data, perhitungan metrik, dan antarmuka UI ke fungsi atau modul berbeda.
2. **Rancang fungsi kecil dan murni**: Gunakan input/output eksplisit (hindari state global tersembunyi), parameter konfigurasi eksplisit, dan `pathlib.Path` untuk path file.
3. **Ekstrak logika reusable**: Tempatkan fungsi inti yang dipakai ulang oleh skrip, notebook Colab, dan dashboard di `src/` agar konsisten dan mudah diuji.
4. **Lakukan refactoring aman secara bertahap**:
   - Pastikan ada test atau pemeriksaan perilaku sebelum mengubah struktur kode.
   - Ubah satu tanggung jawab per langkah tanpa mengubah keputusan metodologi.
   - Verifikasi ulang hasil setelah setiap perubahan kecil.
5. **Hindari overengineering**: Jangan membuat abstraksi, hierarki class, atau pola desain kompleks jika fungsi sederhana sudah mencukupi.

## Aturan validasi

- Fungsi pemrosesan data tidak bergantung pada `streamlit` atau widget UI.
- Tidak ada path absolut lokal mesin yang ditanam langsung dalam kode.
- Perilaku fungsi tetap identik setelah refactoring dan lolos pengujian unit.

## Output yang diharapkan

Modul/fungsi modular dengan tanggung jawab tunggal, antarmuka bersih, dan kompatibel untuk dipakai ulang di skrip, Colab, maupun Streamlit.
