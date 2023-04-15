# Generalized Suffix Tree based Indexing Module
Untuk membuat search engine diperlukan banyak komponen yang mendukung kebutuhan arsitektur search engine. Pada penelitian sebelumnya, komponen crawler berhasil dibuat oleh Muhammad Fathan Qoriiba dalam penelitiannya yang berjudul "Perancangan Crawler Sebagai Pendukung Pada Search Engine". Salah satu komponen dari search engine yang belum diimplementasikan adalah modul pengindeks atau indexer. Penelitian ini bertujuan untuk membuat modul pengindeks menggunakan struktur data Generalized Suffix Tree untuk keperluan pemeringkatan dokumen sekaligus melanjutkan rangkaian penelitian search engine. Proses pembentukan Generalized Suffix Tree dan seluruh program dibuat menggunakan bahasa Python. Hasil akhir dari penelitian ini adalah modul pengindeks berupa program console yang digunakan untuk melakukan pencarian dengan nilai Mean Average Precision dari 3 tester sebesar 0.658 dan struktur data Generalized Suffix Tree dengan kedalaman maksimal 11 level dan total jumlah daun sebanyak 34.573
daun yang tersimpan dalam direktori yang sama.
### Requirement
- Python 3.5+
- Apache, MySQL
- Library Python : anytree, pymysql, time, pickle, dan re

### How to use
1. Unduh atau clone repository ini.
2. Jalankan Apache dan MySQL pada XAMPP Anda
3. Import database yang tersedia yaitu pada folder data/page_information.sql pada localhost
4. Install python dan library yang diperlukan. Untuk library dapat diinstall melalui cmd: ```pip install <nama library>```
5. Pastikan nama dan koneksi database sesuai pada fungsi getResult() dan getTitle()
6. Jalankan script gst.py
7. Masukkan kalimat atau kata yang ingin dicari
8. Lihat hasil pada terminal atau console
9. Jika ingin membuat tree dari awal maka hapus file yang bernama gst pada folder data lalu uncomment 3 line teratas pada fungsi main pada script src/indexing/gst.py
10. Jalankan script gst.py

