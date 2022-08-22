# :beginner: Search Engine

Aplikasi search engine yang dibuat dengan menggunakan crawler, document ranking, dan page ranking

## :zap: Cara Penggunaan

1. Pastikan komputer/server sudah terinstall Python 3.6+ dan MySQL
2. Buka file `.env` dan ubah konfigurasi sesuai keinginan (akses database, konfigurasi crawler, dll)
3. Install library python yang diperlukan dengan menjalankan `pip install -r requirements.txt`
4. Jalankan program dengan kumpulan perintah di bawah

## :package: Perintah

**General**

- `Python api.py` untuk menjalankan REST API

**Background Services**

- `Python crawl.py` untuk menjalankan crawler atau gunakan `crawl.service` sebagai background di systemd
- `Python page_rank.py` untuk menjalankan page rank atau gunakan `page_rank.service` sebagai background di systemd

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
<summary><b>Get TF-IDF Document Ranking</b></summary>

- **URL**: `/api/v1.0/document_ranking/tf_idf?keyword=barcelona`

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

<details>
<summary><b>Get Page-Rank Page Ranking</b></summary>

- **URL**: `/api/v1.0/page_ranking/page_rank`

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "id_pagerank": 1,
      "pagerank_score": 0.0017783111027720113,
      "url": "https://www.indosport.com"
    },
    {
      "id_pagerank": 256,
      "pagerank_score": 0.0002961208172934557,
      "url": "https://www.curiouscuisiniere.com/about/privacy-policy"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>Get Crawled Pages</b></summary>

- **URL**: `/api/v1.0/crawling/pages`
- **URL**: `/api/v1.0/crawling/pages?start=0&end=999`

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "content_text": "Anies Siapkan Hunian Kelas Menengah,Alaspadu dan Rumapadu,",
      "crawl_id": 1,
      "created_at": "2022-08-20 02:41:49",
      "description": "CNNIndonesia.com menyajikan berita Terbaru, Terkini Indonesia seputar nasional, politik, ekonomi, internasional, olahraga, teknologi, hiburan, gaya hidup.",
      "duration_crawl": "0:00:00",
      "hot_url": 0,
      "html5": 1,
      "id_information": 2682,
      "keywords": "cnn, cnn indonesia, indonesia, berita, berita terbaru, berita terkini, berita indonesia, berita dunia, berita nasional, berita politik, berita ekonomi, berita internasional, berita olahraga",
      "model_crawl": "BFS crawling",
      "title": "CNN Indonesia | Berita Terbaru, Terkini Indonesia, Dunia",
      "url": "https://www.cnnindonesia.com/features"
    },
    {
      "content_text": "Anies Siapkan Hunian Kelas Menengah,Alaspadu dan Rumapadu,",
      "crawl_id": 1,
      "created_at": "2022-08-20 02:41:50",
      "description": "CNNIndonesia.com menyajikan berita terbaru, terkini Indonesia, dunia, seputar politik, hukum kriminal, peristiwa",
      "duration_crawl": "0:00:01",
      "hot_url": 0,
      "html5": 1,
      "id_information": 2683,
      "keywords": "berita nasional terbaru, berita politik nasional, Berita Terkini, Berita Hari Ini, Breaking News, News Today, News, Hot News, Berita Nasional, Berita politik, Berita kriminal, Berita Hukum, Berita Pemerintahan, Berita Harian, Berita Akurat, Berita Tepercaya",
      "model_crawl": "BFS crawling",
      "title": "CNN Indonesia | Berita Terkini Nasional",
      "url": "https://www.cnnindonesia.com/nasional"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>
