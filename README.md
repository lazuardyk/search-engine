# :beginner: Search Engine

Aplikasi search engine yang dibuat dengan menggunakan crawler, document ranking, dan page ranking

## :zap: Cara Penggunaan

1. Pastikan komputer/server sudah terinstall Python 3.6+ dan MySQL
2. Buka file `.env` dan ubah konfigurasinya dengan benar (akses database, konfigurasi crawler, dll)
3. Install library python yang diperlukan dengan menjalankan `pip install -r requirements.txt`
4. Jalankan program sesuai dengan perintah di bawah

## :package: Perintah

**General**

- `Python run_crawl.py` untuk menjalankan crawler
- `Python run_page_rank.py` untuk menjalankan page rank
- `Python run_tf_idf.py` untuk menjalankan tf idf
- `Python run_api.py` untuk menjalankan REST API
- `Python run_search_engine_console.py` untuk menjalankan search engine berbasis console

**Background Services**

- Gunakan `crawl.service` di folder services untuk menjalankan crawler, page rank, dan tf idf di background [menggunakan systemd](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) pada server

## :notebook: File Dokumentasi

- [Entity Relationship Diagram (ERD)](https://dbdiagram.io/d/62622c031072ae0b6acb52f0)
- [Class Diagram](docs/class_diagram_simplified.png)
- [Postman API Documentation](https://documenter.getpostman.com/view/11687432/2s8YerLWtg)
- [Routing Table](docs/routing_table.png)

## :wrench: Dokumentasi API

<details>
<summary><b>[GET]</b> Get Similarity Overall Ranking</summary>

- **URL**: `/api/v1.0/overall_ranking/similarity?keyword=barcelona&sort=similarity&start=0&length=10`

- **Params Detail**: sort options: `similarity`, `tfidf`, or `pagerank`. start and length are optional.

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "id_page": 5,
      "pagerank_score": 0.05263157894736842,
      "similarity_score": 0.49220540497550275,
      "tfidf_total": 0.06595637671355718,
      "url": "https://20.detik.com/live"
    },
    {
      "id_page": 1,
      "pagerank_score": 0.05263157894736842,
      "similarity_score": 0.45263157894736844,
      "tfidf_total": 0.0,
      "url": "https://detik.com"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[GET]</b> Get TF-IDF Document Ranking</summary>

- **URL**: `/api/v1.0/document_ranking/tf_idf?keyword=barcelona&start=0&length=10`

- **Params Detail**: start and length are optional.

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "id_tfidf": 18,
      "keyword": "klub barcelona",
      "tfidf_total": 0.9,
      "url": "https://detik.com/barcelona"
    },
    {
      "id_tfidf": 19,
      "keyword": "klub barcelona",
      "tfidf_total": 0.8,
      "url": "https://www.detik.com/?tagfrom=klub"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[GET]</b> Get Page-Rank Page Ranking</summary>

- **URL**: `/api/v1.0/page_ranking/page_rank?start=0&length=10`

- **Params Detail**: start and length are optional.

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "id_pagerank": 7,
      "pagerank_score": 0.006093279237620995,
      "url": "https://news.detik.com"
    },
    {
      "id_pagerank": 15,
      "pagerank_score": 0.005689670500678926,
      "url": "https://news.detik.com/x"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[GET]</b> Run Crawling</summary>

- **URL**: `/api/v1.0/crawling/crawl?duration=10`

- **Method**: `GET`

- **Response**:

```json
{
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[GET]</b> Get Crawled Pages</summary>

- **URL**: `/api/v1.0/crawling/pages?start=0&length=10`

- **Params Detail**: start and length are optional.

- **Method**: `GET`

- **Response**:

```json
{
  "data": [
    {
      "content_text": "",
      "crawl_id": 1,
      "created_at": "2022-09-29 19:39:13",
      "description": "Indeks berita terkini dan terbaru hari ini dari peristiwa, kecelakaan, kriminal, hukum, berita unik, Politik, dan liputan khusus di Indonesia dan Internasional",
      "duration_crawl": "0:00:03",
      "hot_url": 0,
      "html5": 1,
      "id_information": 1,
      "keywords": "berita hari ini, berita terkini, berita terbaru, info berita, peristiwa, kecelakaan, kriminal, hukum, berita unik, Politik, liputan khusus, Indonesia, Internasional",
      "model_crawl": "BFS crawling",
      "size_bytes": 252595,
      "title": "detikcom - Informasi Berita Terkini dan Terbaru Hari Ini",
      "url": "https://detik.com"
    },
    {
      "content_text": "",
      "crawl_id": 1,
      "created_at": "2022-09-29 19:39:16",
      "description": "Indeks berita terkini dan terbaru hari ini dari peristiwa, kecelakaan, kriminal, hukum, berita unik, Politik, dan liputan khusus di Indonesia dan Internasional",
      "duration_crawl": "0:00:02",
      "hot_url": 0,
      "html5": 1,
      "id_information": 2,
      "keywords": "berita hari ini, berita terkini, berita terbaru, info berita, peristiwa, kecelakaan, kriminal, hukum, berita unik, Politik, liputan khusus, Indonesia, Internasional",
      "model_crawl": "BFS crawling",
      "size_bytes": 252607,
      "title": "detikcom - Informasi Berita Terkini dan Terbaru Hari Ini",
      "url": "https://www.detik.com/?tagfrom=framebar"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[POST]</b> Get Page Information</summary>

- **URL**: `/api/v1.0/crawling/page_information`

- **Method**: `POST`

- **Request Payload**:

```json
{
  "id_pages": [1]
}
```

- **Response**:

```json
{
  "data": [
    {
      "content_text": "",
      "crawl_id": 2,
      "created_at": "2022-10-06 06:47:17",
      "description": "Indeks berita terkini dan terbaru hari ini dari peristiwa, kecelakaan, kriminal, hukum, berita unik, Politik, dan liputan khusus di Indonesia dan Internasional",
      "duration_crawl": "0:00:00",
      "hot_url": 0,
      "html5": 1,
      "id_page": 1,
      "keywords": "berita hari ini, berita terkini, berita terbaru, info berita, peristiwa, kecelakaan, kriminal, hukum, berita unik, Politik, liputan khusus, Indonesia, Internasional",
      "model_crawl": "BFS crawling",
      "size_bytes": 244796,
      "title": "detikcom - Informasi Berita Terkini dan Terbaru Hari Ini",
      "url": "https://detik.com"
    }
  ],
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[POST]</b> Start Insert Crawled Pages</summary>

- **URL**: `/api/v1.0/crawling/start_insert`

- **Method**: `POST`

- **Request Payload**:

```json
{
  "start_urls": "https://www.indosport.com https://detik.com https://www.curiouscuisiniere.com",
  "keyword": "",
  "duration_crawl": 28800
}
```

- **Response**:

```json
{
  "data": {
    "id_crawling": 6
  },
  "message": "Sukses",
  "ok": true
}
```

</details>

<details>
<summary><b>[POST]</b> Insert Crawled Page</summary>

- **URL**: `/api/v1.0/crawling/insert_page`

- **Method**: `POST`

- **Request Payload**:

```json
{
  "page_information": {
    "crawl_id": 3,
    "url": "https://www.indosport.com",
    "html5": 0,
    "title": "INDOSPORT - Berita Olahraga Terkini dan Sepak Bola Indonesia",
    "description": "INDOSPORT.com – Portal Berita Olahraga dan Sepakbola. Menyajikan berita bola terkini, hasil pertandingan, prediksi dan jadwal pertandingan, Liga 1, Liga Inggris, Liga Spanyol, Liga Italia, Liga Champions.",
    "keywords": "Jadwal Pertandingan, Hasil Pertandingan, Klasemen, Prediksi Pertandingan, Liga 1, Liga Inggris, Sepakbola, Liga Champions, Liga Spanyol, Liga Italia, Badminton, Bulutangkis, Link Live Streaming, MotoGP, Berita Sepakbola, Piala Dunia, Tempat Olahraga, Olahraga, Berita Bola, Esport, Basketball.",
    "content_text": "Jumat,19 Agustus 2022 21:05 WIB 3 Bintang Murah dengan Statistik Lebih Mentereng dari Casemiro yang Bisa Dilirik Man United Jumat,19 Agustus 2022 19:32 WIB 4 Kali Dipecat Termasuk saat Latih Timnas Indonesia,Mampukah Luis Milla Bawa Persib Berprestasi? Jumat,19 Agustus 2022 18:42 WIB Resmi Latih Persib,Ini 3 Prestasi Mentereng Luis 13:45 WIB Potret Kemenangan Dramatis PSM Makassar Atas RANS Nusantara di Liga 1 Liga Indonesia |  Minggu,24 Juli 2022 21:13 WIB Kemegahan dan Fasilitas Mewah Stadion JIS di Hari Launching       Tentang Indosport Redaksi Karir Pedoman Media Siber SOP Perlindungan Wartawan Iklan & Kerjasama RSS Copyright © 2012 - 2022 INDOSPORT. All rights reserved",
    "hot_url": 0,
    "size_bytes": 121345,
    "model_crawl": "BFS Crawling",
    "duration_crawl": 28800
  },
  "page_forms": [
    {
      "url": "https://www.indosport.com",
      "form": "<form action='https://www.indosport.com/search' method='get'></form>"
    },
    {
      "url": "https://www.indosport.com",
      "form": "<form action='https://www.indosport.com/searchv2' method='post'></form>"
    }
  ],
  "page_images": [
    {
      "url": "https://www.indosport.com",
      "image": "<img alt='' height='1' src='https://certify.alexametrics.com/atrk.gif?account=/HVtm1akKd607i' style='display:none' width='1'/>"
    },
    {
      "url": "https://www.indosport.com",
      "image": "<img alt='' height='1' src='https://sb.scorecardresearch.com/blabla.jpeg' style='display:none' width='1'/>"
    }
  ],
  "page_linking": [
    {
      "crawl_id": 3,
      "url": "https://www.indosport.com",
      "outgoing_link": "https://www.indosport.com/sepakbola"
    },
    {
      "crawl_id": 1,
      "url": "https://www.indosport.com",
      "outgoing_link": "https://www.indosport.com/liga-spanyol"
    }
  ],
  "page_list": [
    {
      "url": "https://www.indosport.com",
      "list": "<li class='bc_home'><a href='https://www.indosport.com'><i class='sprite sprite-mobile sprite-icon_home icon-sidebar'></i></li>"
    },
    {
      "url": "https://www.indosport.com",
      "list": "<li class='bc_home'><a href='https://www.indosport.com'><i class='sprite sprite-mobile sprite-icon_home icon-sidebar'></i></li>"
    }
  ],
  "page_scripts": [
    {
      "url": "https://www.indosport.com",
      "script": "<script type='text/javascript'>window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;</script>"
    },
    {
      "url": "https://www.indosport.com",
      "script": "<script type='text/javascript'>window.ga=window.bc||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;</script>"
    }
  ],
  "page_styles": [
    {
      "url": "https://www.indosport.com",
      "style": "<style>.bn_skin{z-index: 2 !important;}</style>"
    },
    {
      "url": "https://www.indosport.com",
      "style": "<style>.bn_skin{z-index: 115 !important;}</style>"
    }
  ],
  "page_tables": [
    {
      "url": "https://www.indosport.com",
      "table_str": "<table class='table'><thead><tr><th class='waktu'>Waktu</th><th class='pertandingan'>Pertandingan</th><th class='tv'>Live TV</th></tr></thead><tbody></tr></tbody></table>"
    },
    {
      "url": "https://www.indosport.com",
      "table_str": "<table class='table'><thead><tr><th class='waktu'>Waktu</th><th class='pertandingan'>Pertandingan</th><th class='tv'>Live TV</th></tr></thead><tbody></tr></tbody></table>"
    }
  ]
}
```

- **Response**:

```json
{
  "message": "Sukses",
  "ok": true
}
```

</details>

## :file_folder: Struktur Direktori & File

    .
    ├── docs                                          # Sebagai tempat dokumentasi file seperti diagram, product backlog, dll
    ├── html                                          # Berisi dokumentasi class dan fungsi yang di-generate dari library pdoc3
    ├── services                                      # Kumpulan konfigurasi background service yang dipakai di systemd/systemctl
    ├── src                                           # Source code search engine
    │   ├── api                                       # Folder untuk kodingan REST API
    │   |   ├── app.py                                # Untuk run Flask dan menggabungkan routes
    │   |   ├── crawling.py                           # Routes dan fungsi API untuk crawling
    │   |   ├── document_ranking.py                   # Routes dan fungsi API untuk document ranking
    │   |   ├── overall_ranking.py                    # Routes dan fungsi API untuk overall ranking
    │   |   └── page_ranking.py                       # Routes dan fungsi API untuk page ranking
    |   |
    │   ├── crawling                                  # Folder untuk kodingan crawling
    │   |   ├── methods                               # Folder untuk berbagai metode crawling
    │   |   |   ├── breadth_first_search.py           # Fungsi-fungsi crawling metode BFS
    |   |   |   └── modified_similarity_based.py      # Fungsi-fungsi crawling metode MSB
    │   |   ├── crawl.py                              # Untuk run crawling dengan menggabungkan metode yang ada
    │   |   ├── page_content.py                       # Fungsi-fungsi yang menghubungkan ke database dan halaman html
    │   |   └── util.py                               # Fungsi-fungsi pendukung crawling
    |   |
    │   ├── database                                  # Folder untuk kodingan database
    │   |   └── database.py                           # Berisi kode untuk pengoperasian database seperti koneksi, query, dll
    |   |
    │   ├── document_ranking                          # Folder untuk kodingan document ranking
    │   |   └── tf_idf.py                             # Implementasi dari TF-IDF
    |   |
    │   ├── overall_ranking                           # Folder untuk kodingan overall ranking
    │   |   └── similarity.py                         # Implementasi dari similarity score
    |   |
    │   ├── page_ranking                              # Folder untuk kodingan page ranking
    │   |   └── page_rank.py                          # Implementasi dari Google PageRank
    |
    ├── .env                                          # Konfigurasi credentials database dan crawler
    ├── run_api.py                                    # Script utama untuk run REST API
    ├── run_crawl.py                                  # Script utama untuk run crawling
    ├── run_page_rank.py                              # Script utama untuk run page rank
    ├── run_search_engine_console.py                  # Script utama untuk run search engine console
    ├── run_tf_idf.py                                 # Script utama untuk run TF IDF
    ├── requirements.txt                              # Berisi list library yang diperlukan

## :page_facing_up: Referensi

- [Cara set up background service di systemd](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267)
- [Contoh kodingan TF-IDF untuk mencari artikel yang mirip sesuai keyword](https://www.kaggle.com/code/yclaudel/find-similar-articles-with-tf-idf)
- [Contoh kodingan Page Rank](https://github.com/nicholaskajoh/devsearch/blob/f6d51fc478e5bae68e4ba32f3299ab20c0ffa033/devsearch/pagerank.py)
