# Catatan presentasi proposal UAS Data Science — terbaru

Analisis Pola dan Keteraturan Tidur Berdasarkan Data Historis Samsung Health Menggunakan Pendekatan Data Science

## Slide 1 · sekitar 30–45 detik

Pemahaman pola dan keteraturan tidur dapat membantu evaluasi rutinitas pribadi. Namun, ingatan sehari-hari sulit memberikan gambaran objektif mengenai perubahan durasi maupun jadwal tidur. Proposal ini memanfaatkan riwayat pencatatan Samsung Health untuk menelaah kebiasaan tersebut secara sistematis. Masalah utamanya adalah belum tersedianya gambaran berbasis data mengenai durasi, jadwal, dan konsistensi tidur yang tercatat. Penelitian berfokus pada satu individu dan menggunakan pendekatan deskriptif. Temuannya akan menjadi bahan refleksi pribadi, bukan diagnosis medis atau ukuran kualitas tidur fisiologis.

## Slide 2 · sekitar 30–45 detik

Penelitian ini memiliki tiga tujuan. Pertama, memetakan durasi dan jadwal tidur untuk menjawab bagaimana pola durasi dalam riwayat pencatatan. Kedua, menelaah keteraturan dari waktu ke waktu untuk mengetahui konsistensi jadwal mulai dan selesai tidur. Ketiga, membandingkan hari kerja dan akhir pekan apabila cakupan datanya memadai. Pengelompokan tersebut perlu memperhatikan kalender karena akhir pekan belum tentu sama dengan hari libur aktual. Hasil yang diharapkan adalah gambaran kebiasaan tidur berbasis data sebagai dasar evaluasi pribadi secara nonmedis. Seluruh poin ini merupakan rencana, belum hasil penelitian.

## Slide 3 · sekitar 30–45 detik

Data berasal dari ekspor pribadi Samsung Health dalam format CSV dan JSON. Sumber tidur memuat 653 sesi, sedangkan activity.day_summary memuat 740 catatan harian. Pipeline parsing, audit, cleaning, dan integrasi telah dijalankan. Dua record pada interval tidur yang overlap dikarantina; sesi terpanjang dipilih per tanggal bangun, dan sesi tambahan tidak dijumlahkan. Hasilnya adalah dataset kandidat 740 baris harian dan 12 kolom, dengan cakupan kalender 9 November 2024 sampai 18 November 2026. Sebanyak 649 tanggal memiliki data tidur dan aktivitas, sedangkan 91 tanggal hanya memiliki data aktivitas. Cakupan tersebut bukan 740 hari pengamatan tidur lengkap. Durasi tidur tersimpan kosong pada 321 baris dan tidak diimputasi; interval end-start tersedia terpisah dan tidak membuktikan durasi tidur fisiologis. Waktu tidur menggunakan asumsi UTC yang dikonversi ke Asia/Jakarta; batas hari aktivitas dan satuan durasi aktif masih perlu konfirmasi. Dua belas kolom mencakup variabel turunan dan bukan dua belas pengukuran independen. EDA dapat dilakukan secara eksploratif dengan keterbatasan tersebut; regresi dan clustering final belum layak sebelum validasi kritis selesai. Belum ada model atau metrik performa yang dijalankan. Dashboard publik menggunakan data sintetis, terpisah dari dataset pribadi.

## Sumber dan status

Sumber pembaruan: reports/dataset_integration_report.md; data_audit/task13_validation.json; docs/dataset_integration.md; data_processed/samsung_health_merged.csv (hanya validasi agregat, tidak disematkan). Status diperiksa 18 November 2026. Angka merupakan hasil persiapan data, bukan hasil pemodelan atau temuan klinis.
