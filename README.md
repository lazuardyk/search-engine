# Search Engine

Aplikasi search engine yang dibuat dengan menggunakan crawler, document ranking, dan page ranking.

## Susunan Folder Root Project

    .
    ├── docs              # Sebagai tempat dokumentasi file seperti diagram, product backlog, dll
    ├── html              # Berisi dokumentasi kode yang di-generate dari library pdoc3
    ├── services          # Kumpulan konfigurasi background service yang dipakai di systemd/systemctl
    ├── src               # Source code search engine yang terdiri dari crawling, document ranking, dan page ranking

## Susunan Folder Source Code ```src```

    .
    ├── crawling          # Berisi kode yang berhubungan dengan proses crawling dan metodenya
    ├── database          # Berisi kode untuk pengoperasian database seperti koneksi, query, dll
    ├── document_ranking  # Berisi kode untuk perankingan dokumen dan metodenya seperti tf idf
    ├── page_ranking      # Berisi kode untuk perankingan halaman dan metodenya seperti page rank
