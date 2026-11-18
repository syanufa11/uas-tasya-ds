# Catatan presentasi proposal: tidur dan aktivitas harian

Analisis Pola Tidur dan Aktivitas Harian Berdasarkan Data Historis Samsung Health Menggunakan Pendekatan Data Science

## Slide 1

Penelitian ini membahas pola tidur dan aktivitas harian berdasarkan riwayat pencatatan Samsung Health dari satu individu. Data tidur digunakan untuk menelaah durasi, jadwal, dan keteraturan tidur, sedangkan data aktivitas mencakup jumlah langkah dan durasi aktif. Kedua kelompok data dapat membantu menggambarkan rutinitas secara lebih sistematis dibandingkan ingatan sehari-hari. Masalah penelitian adalah belum tersedianya gambaran terpadu mengenai pola tidur dan aktivitas harian dari riwayat pribadi tersebut. Pendekatan penelitian bersifat deskriptif dan eksploratif untuk evaluasi rutinitas pribadi secara nonmedis. Hubungan antarvariabel yang mungkin ditemukan tidak membuktikan sebab-akibat maupun kondisi kesehatan tertentu.

## Slide 2

Terdapat tiga tujuan penelitian. Pertama, memetakan durasi, jadwal, dan keteraturan tidur yang tercatat. Kedua, menggambarkan pola jumlah langkah dan durasi aktivitas harian. Ketiga, mengeksplorasi hubungan aktivitas dengan pola tidur berikutnya setelah validasi waktu, batas hari aktivitas, dan satuan durasi aktif selesai. Aktivitas sebelum tidur harus dipasangkan berdasarkan tanggal sumber dan batas waktu yang telah diverifikasi, bukan otomatis memakai aktivitas pada tanggal bangun. Aturan konservatif pipeline memakai tanggal UTC mulai tidur dikurangi satu hari dan memastikan akhir hari aktivitas tidak melewati awal tidur. Analisis hubungan bersifat asosiasi retrospektif, bukan klaim kausal atau prediksi. Perbandingan hari kerja dan akhir pekan dapat menjadi rincian analisis deskriptif jika cakupan data memadai; akhir pekan tidak selalu sama dengan hari libur aktual. Seluruh tujuan ini masih berupa rencana penelitian, bukan hasil analisis yang telah dibuktikan.

## Slide 3

Data berasal dari ekspor pribadi Samsung Health dalam format CSV dan JSON. Sumber tidur memuat 653 sesi, sedangkan activity.day_summary memuat 740 catatan harian. Pipeline parsing, audit, cleaning, dan integrasi telah dijalankan. Dua record pada interval tidur yang overlap dikarantina; sesi terpanjang dipilih per tanggal bangun, dan sesi tambahan tidak dijumlahkan. Hasilnya adalah dataset kandidat 740 baris harian dan 12 kolom, dengan cakupan kalender 9 November 2024 sampai 18 November 2026. Sebanyak 649 tanggal memiliki data tidur dan aktivitas, sedangkan 91 tanggal hanya memiliki data aktivitas. Cakupan tersebut bukan 740 hari pengamatan tidur lengkap. Durasi tidur tersimpan kosong pada 321 baris dan tidak diimputasi; interval end-start tersedia terpisah dan tidak membuktikan durasi tidur fisiologis. Waktu tidur menggunakan asumsi UTC yang dikonversi ke Asia/Jakarta; batas hari aktivitas dan satuan durasi aktif masih perlu konfirmasi. Dua belas kolom mencakup variabel turunan dan bukan dua belas pengukuran independen. EDA dapat dilakukan secara eksploratif dengan keterbatasan tersebut; regresi dan clustering final belum layak sebelum validasi kritis selesai. Belum ada model atau metrik performa yang dijalankan. Dashboard publik menggunakan data sintetis, terpisah dari dataset pribadi.

## Sumber dan status

Sumber pembaruan: reports/dataset_integration_report.md; data_audit/task13_validation.json; docs/dataset_integration.md; data_processed/samsung_health_merged.csv (hanya validasi agregat, tidak disematkan). Status diperiksa 18 November 2026. Angka merupakan hasil persiapan data, bukan hasil pemodelan atau temuan klinis.
