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

    def save_tfidf(self, db_connection, keyword, url, tf, idf, tfidf):
        """
        Fungsi untuk menyimpan ranking dan nilai TF IDF yang sudah dihitung ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Kata
            url (str): Url halaman
            tfidf (double): Score tf idf
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = (
            "INSERT INTO `tfidf` (`keyword`, `url`, `tf_score`, `idf_score`, `tfidf_score`) VALUES (%s, %s, %s, %s, %s)"
        )
        db_cursor.execute(query, (keyword, url, tf, idf, tfidf))
        db_cursor.close()

    def save_call_log(self, db_connection, keywords, duration_call):
        """
        Fungsi untuk menyimpan waktu yang diperlukan saat pemanggilan fungsi TF-DF.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keywords (str): Kata pencarian (bisa lebih dari satu kata dipisah dengan spasi)
            duration_call (int): Waktu yang diperlukan saat pemanggilan fungsi TF IDF dari awal hingga selesai
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `tfidf_log` (`keywords`, `duration_call`) VALUES (%s, SEC_TO_TIME(%s))"
        db_cursor.execute(query, (keywords, duration_call))
        db_cursor.close()

    def get_saved_tfidf(self, db_connection, keyword):
        """
        Fungsi untuk mengambil nilai TF IDF yang disimpan di database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Kata

        Returns:
            list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `tfidf` WHERE `keyword` = %s ORDER BY `tfidf_score` DESC", (keyword))
        rows = db_cursor.fetchall()
        db_cursor.close()
        return rows

    def run(self, keywords):
        """
        Fungsi utama yang digunakan untuk melakukan perangkingan dokumen TF-IDF.

        Args:
            keywords (str): Kata pencarian (bisa lebih dari satu kata dipisah dengan spasi)

        Returns:
            list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall()
        """

        # Catat waktu mulai
        start_time_call = time.time()
        db_connection = self.db.connect()

        # Cek apakah table tfidf sudah terisi, jika kosong hitung dari awal menggunakan sklearn
        if self.db.count_rows(db_connection, "tfidf") < 1:
            # Ambil semua data halaman yang sudah di crawl ke dalam pandas dataframe
            query = "SELECT * FROM `page_information`"
            df = pd.read_sql(query, db_connection)
            text_content = df["content_text"]  # Konten teks dari halaman yang sudah dicrawl

            # Buat model menggunakan TfidfVectorizer
            vectorizer = TfidfVectorizer(
                lowercase=True,  # Untuk konversi ke lower case
                use_idf=True,  # Untuk memakai idf
                norm="l2",  # Normalisasi
                smooth_idf=True,  # Untuk mencegah divide-by-zero errors
            )

            tfidf_matrix = vectorizer.fit_transform(text_content)
            tfidf_matrix_array = tfidf_matrix.toarray()
            words = vectorizer.get_feature_names()
            idf_vector = vectorizer.idf_

            for i in range(len(tfidf_matrix_array)):
                tf_idf_vector = tfidf_matrix_array[i]
                url = df["url"].loc[i]

                for j in range(len(words)):
                    word = words[j]
                    idf = idf_vector[j]
                    tf_idf = tf_idf_vector[j]
                    tf = tf_idf / idf

                    # print(url, word, tf, idf, tf_idf)
                    self.save_tfidf(db_connection, word, url, tf, idf, tf_idf)

        # Ambil nilai tf idf dari database
        results = []
        if keywords:
            keywords_array = keywords.split(" ")
            for keyword in keywords_array:
                tfidf_data = self.get_saved_tfidf(db_connection, keyword)
                results + tfidf_data

        # Simpan waktu yang diperlukan saat run TF IDF
        duration_call = time.time() - start_time_call
        self.save_call_log(db_connection, keywords, int(duration_call))
        self.db.close_connection(db_connection)

        return results
