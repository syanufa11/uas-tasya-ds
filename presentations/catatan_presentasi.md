# Catatan presentasi proposal UAS Data Science

Analisis Pola dan Keteraturan Tidur Berdasarkan Data Historis Samsung Health Menggunakan Pendekatan Data Science

## Slide 1 · sekitar 30–45 detik

Pemahaman pola dan keteraturan tidur dapat membantu evaluasi rutinitas pribadi. Namun, ingatan sehari-hari sulit memberikan gambaran objektif mengenai perubahan durasi maupun jadwal tidur. Proposal ini memanfaatkan riwayat pencatatan Samsung Health untuk menelaah kebiasaan tersebut secara sistematis. Masalah utamanya adalah belum tersedianya gambaran berbasis data mengenai durasi, jadwal, dan konsistensi tidur yang tercatat. Penelitian berfokus pada satu individu dan menggunakan pendekatan deskriptif. Temuannya akan menjadi bahan refleksi pribadi, bukan diagnosis medis atau ukuran kualitas tidur fisiologis.

## Slide 2 · sekitar 30–45 detik

Penelitian ini memiliki tiga tujuan. Pertama, memetakan durasi dan jadwal tidur untuk menjawab bagaimana pola durasi dalam riwayat pencatatan. Kedua, menelaah keteraturan dari waktu ke waktu untuk mengetahui konsistensi jadwal mulai dan selesai tidur. Ketiga, membandingkan hari kerja dan akhir pekan apabila cakupan datanya memadai. Pengelompokan tersebut perlu memperhatikan kalender karena akhir pekan belum tentu sama dengan hari libur aktual. Hasil yang diharapkan adalah gambaran kebiasaan tidur berbasis data sebagai dasar evaluasi pribadi secara nonmedis. Seluruh poin ini merupakan rencana, belum hasil penelitian.

## Slide 3 · sekitar 30–45 detik

Data berasal dari ekspor pribadi Samsung Health dalam format CSV dan JSON. Tabel utama com.samsung.shealth.sleep memuat 653 catatan sesi dengan rentang timestamp ekspor 1 Februari 2025 hingga 17 November 2026. Rentang ini belum menyatakan tanggal lokal final. Variabel utama mencakup waktu mulai, waktu selesai, dan durasi bila tersedia. Alurnya meliputi ekspor, identifikasi file tidur, parsing, audit kualitas, cleaning, kemudian analisis. Audit sudah tersedia, sedangkan laporan cleaning belum ditemukan. Validasi zona waktu, nilai kosong, dan sesi tumpang-tindih perlu diselesaikan sebelum analisis.

## Sumber dan status

Narasi mengacu pada brief TASK 11, README.md, data_audit/audit_report.md, data_audit/inventory.csv, dan data_audit/sleep_data_dictionary.csv. Periode mengikuti timestamp teks ekspor, bukan tanggal lokal final. Laporan cleaning belum tersedia pada saat penyusunan. Proposal belum menyajikan hasil analisis penelitian. Tidak ada catatan sesi individual atau identitas akun dalam slide.
