# Referensi: https://www.kaggle.com/code/yclaudel/find-similar-articles-with-tf-idf

from src.database.database import Database

import pymysql
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import time


class TfIdf:
    """Kelas yang digunakan untuk melakukan perankingan dokumen dengan metode TF IDF."""

    def __init__(self):
        self.db = Database()

    def search(self, tfidf_matrix, model, keyword):
        """
        Fungsi untuk menentukan similarity score dari model TF-IDF yang sudah dibuat oleh TfidfVectorizer berdasarkan keyword tertentu.

        Args:
            tfidf_matrix (Any): Matriks TF IDF yang dihasilkan dari TfidfVectorizer.fit_transform()
            model (Any): Model TF IDF yang dihasilkan dari TfidfVectorizer()
            keyword (str): Keyword pencarian

        Returns:
            list: List yang berisi 2 list yaitu: list index dan list score.
        """
        request_transform = model.transform([keyword])
        similarity = np.dot(request_transform, np.transpose(tfidf_matrix))
        x = np.array(similarity.toarray()[0])
        indices = np.argsort(x)[::][::-1]
        score = x[indices]

        return [indices, score]

    def save_tfidf(self, db_connection, keyword, url, tfidf):
        """
        Fungsi untuk menyimpan ranking dan nilai TF IDF yang sudah dihitung ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Keyword pencarian
            url (str): Url halaman
            tfidf (double): Score tf idf
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `tfidf` (`keyword`, `url`, `tfidf_score`) VALUES (%s, %s, %s)"
        db_cursor.execute(query, (keyword, url, tfidf))
        db_cursor.close()

    def save_call_log(self, db_connection, keyword, duration_call):
        """
        Fungsi untuk menyimpan waktu yang diperlukan saat pemanggilan fungsi TF-DF.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Keyword pencarian
            duration_call (int): Waktu yang diperlukan saat pemanggilan fungsi TF IDF dari awal hingga selesai
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `tfidf_log` (`keyword`, `duration_call`) VALUES (%s, SEC_TO_TIME(%s))"
        db_cursor.execute(query, (keyword, duration_call))
        db_cursor.close()

    def get_saved_tfidf(self, db_connection, keyword):
        """
        Fungsi untuk mengambil nilai TF IDF yang disimpan di database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Keyword pencarian

        Returns:
            list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `tfidf` WHERE `keyword` = %s ORDER BY `tfidf_score` DESC", (keyword))
        rows = db_cursor.fetchall()
        db_cursor.close()
        return rows

    def run(self, keyword):
        """
        Fungsi utama yang digunakan untuk melakukan perangkingan dokumen TF-IDF.

        Args:
            keyword (str): Keyword pencarian

        Returns:
            list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall()
        """

        # Catat waktu mulai
        start_time_call = time.time()
        db_connection = self.db.connect()

        # Cek di database apakah skor TF IDF pernah disimpan dengan keyword yang diinput
        saved_data = self.get_saved_tfidf(db_connection, keyword)

        # Jika tidak ada di database, maka hitung menggunakan TfidfVectorizer
        if len(saved_data) < 1:
            # Ambil semua data halaman yang sudah di crawl ke dalam pandas dataframe
            query = "SELECT * FROM `page_information`"
            df = pd.read_sql(query, db_connection)
            text_content = df["content_text"]  # Konten teks dari halaman yang sudah dicrawl

            # Buat model menggunakan TfidfVectorizer
            vector = TfidfVectorizer(
                lowercase=True,  # Convert everything to lower case
                use_idf=True,  # Use idf
                norm="l2",  # Normalization
                smooth_idf=True,  # Prevents divide-by-zero errors
            )
            tfidf = vector.fit_transform(text_content)

            # Ambil indeks dan similarity score
            result_indices, result_score = self.search(tfidf, vector, keyword)

            # Ambil url dari dataframe setelah dapat similarity score
            urls = []
            for ind in result_indices:
                urls.append(df["url"].loc[ind])

            # Simpan similarity score tersebut ke database
            for i in range(len(urls)):
                url = urls[i]
                score = result_score[i]
                self.save_tfidf(db_connection, keyword, url, score)

            # Setelah disimpan, ambil dari database
            saved_data = self.get_saved_tfidf(db_connection, keyword)

        # Simpan waktu yang diperlukan saat run TF IDF
        duration_call = time.time() - start_time_call
        self.save_call_log(db_connection, keyword, int(duration_call))
        self.db.close_connection(db_connection)

        # Return data harus sesuai dengan output dokumentasi API
        return saved_data
