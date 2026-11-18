---
applyTo: "**/app.py,**/streamlit_app.py,**/dashboard.py,app/**/*.py,dashboard/**/*.py,streamlit_app/**/*.py,pages/**/*.py"
---

# Streamlit dashboard

- Pisahkan komponen UI dari pemrosesan dan inferensi; gunakan fungsi/modul proyek agar hasil dashboard konsisten dengan analisis.
- Validasi sumber data dan filter; tangani data kosong, kolom tidak tersedia, serta kegagalan pemuatan dengan pesan yang jelas tanpa membocorkan data sensitif.
- Tampilkan periode, satuan, definisi metrik, dan keterbatasan. Jangan menampilkan metrik tidur yang belum diverifikasi atau menyajikan prediksi sebagai diagnosis.
- Gunakan Plotly bila interaksi membantu; jaga keterbacaan grafik dan tata letak pada layar kecil.
- Gunakan cache hanya bila aman; cegah pencampuran data kesehatan antar pengguna/sesi, hindari cache global untuk data privat, dan simpan rahasia melalui konfigurasi yang tidak masuk Git.
- Lindungi tampilan, unduhan, dan deployment dari kebocoran data pribadi; verifikasi perilaku filter dan perhitungan sebelum menyatakan dashboard berjalan.
