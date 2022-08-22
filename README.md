# :beginner: Search Engine

Aplikasi search engine yang dibuat dengan menggunakan crawler, document ranking, dan page ranking

## :zap: Cara Penggunaan

1. Pastikan komputer/server sudah terinstall Python 3.6+ dan MySQL
2. Buka file `.env` dan ubah konfigurasi sesuai keinginan (akses database, konfigurasi crawler, dll)
3. Install library python yang diperlukan dengan menjalankan `pip install -r requirements.txt`
4. Jalankan program dengan kumpulan perintah di bawah

## :package: Perintah

- `Python crawl.py` untuk menjalankan crawler
- `Python search.py` untuk menjalankan document ranking
- `Python rank.py` untuk menjalankan page ranking

## :file_folder: Struktur Direktori

    .
    ├── docs                    # Sebagai tempat dokumentasi file seperti diagram, product backlog, dll
    ├── html                    # Berisi dokumentasi kode yang di-generate dari library pdoc3
    ├── services                # Kumpulan konfigurasi background service yang dipakai di systemd/systemctl
    ├── src                     # Source code search engine yang terdiri dari crawling, document ranking, dan page ranking
    │   ├── crawling            # Berisi kode yang berhubungan dengan proses crawling dan metodenya
    │   ├── database            # Berisi kode untuk pengoperasian database seperti koneksi, query, dll
    │   ├── document_ranking    # Berisi kode untuk perankingan dokumen dan metodenya seperti tf idf
    │   └── page_ranking        # Berisi kode untuk perankingan halaman dan metodenya seperti page rank

## :page_facing_up: Dokumentasi API

<details>
<summary><b>Get Document Ranking</b></summary>

- **URL**: `/api/v1.0/document_ranking/tf_idf?keyword=rumah`

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "id_tfidf": 3378,
      "keyword": "barcelona",
      "tfidf_score": 0.3666888423866252,
      "url": "https://www.indosport.com/sepakbola/20220818/kejam-demi-bisa-daftarkan-pemain-baru-barcelona-bakal-phk-2-pemain-terbuangnya"
    },
    {
      "id_tfidf": 3379,
      "keyword": "barcelona",
      "tfidf_score": 0.3543321877907969,
      "url": "https://www.indosport.com/tag/194/barcelona"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```
</details>
