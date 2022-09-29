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

    # def save_one_tf(self, db_connection, page_id, word, tf_score):
    #     """
    #     Fungsi untuk menyimpan nilai TF ke dalam table tf pada database.

    #     Args:
    #         db_connection (pymysql.Connection): Koneksi database MySQL
    #         word (str): Kata (satu kata)
    #         page_id (int): Id page atau id page_information
    #         tf (int): Nilai tf
    #     """
    #     db_connection.ping()
    #     db_cursor = db_connection.cursor()

    #     query = "INSERT INTO `tf` (`page_id`, `word`, `tf_score`) VALUES (%s, %s, %s)"
    #     db_cursor.execute(query, (page_id, word, tf_score))

    #     db_cursor.close()

    # def save_one_idf(self, db_connection, word, idf_score):
    #     """
    #     Fungsi untuk menyimpan nilai IDF ke dalam table idf pada database.

    #     Args:
    #         db_connection (pymysql.Connection): Koneksi database MySQL
    #         word (str): Kata (satu kata)
    #         page_id (int): Id page atau id page_information
    #         idf (int): Nilai idf
    #     """
    #     db_connection.ping()
    #     db_cursor = db_connection.cursor()

    #     query = "INSERT INTO `idf` (`word`, `idf_score`) VALUES (%s, %s)"
    #     db_cursor.execute(query, (word, idf_score))

    #     db_cursor.close()

    #     def get_one_saved_idf(self, db_connection, word):
    #     """
    #     Fungsi untuk mengambil nilai IDF yang disimpan di database.

    #     Args:
    #         db_connection (pymysql.Connection): Koneksi database MySQL
    #         word (str): Kata

    #     Returns:
    #         double: Berisi nilai idf
    #     """
    #     db_connection.ping()
    #     db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    #     db_cursor.execute("SELECT document_term FROM `idf` WHERE `word` = %s", (word))
    #     rows = db_cursor.fetchone()
    #     db_cursor.close()
    #     return rows["idf_score"]

    # def get_all_saved_tf(self, db_connection, word):
    #     """
    #     Fungsi untuk mengambil nilai IDF yang disimpan di database.

    #     Args:
    #         db_connection (pymysql.Connection): Koneksi database MySQL
    #         word (str): Kata

    #     Returns:
    #         list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
    #     """
    #     db_connection.ping()
    #     db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    #     db_cursor.execute("SELECT * FROM `idf` WHERE `word` = %s", (word))
    #     rows = db_cursor.fetchone()
    #     db_cursor.close()
    #     return rows

    def remove_tfidf_rows(self, db_connection):
        """Fungsi untuk mengosongkan table "tfidf" pada database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()

        query = "TRUNCATE TABLE `tfidf`"
        db_cursor.execute(query)

        db_cursor.close()

    def save_one_tfidf(self, db_connection, keyword, url, tfidf_total):
        """
        Fungsi untuk menyimpan nilai total TF IDF terhadap suatu keyword (bisa lebih dari satu kata) ke database pada table "tfidf".

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Kata pencarian (bisa lebih dari satu kata)
            url (str): Url halaman
            tfidf_total (double): Score tf idf
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()

        query = "INSERT INTO `tfidf` (`keyword`, `url`, `tfidf_total`) VALUES (%s, %s, %s)"
        db_cursor.execute(query, (keyword, url, tfidf_total))

        db_cursor.close()

    def save_one_tfidf_word(self, db_connection, word, page_id, tfidf_score):
        """
        Fungsi untuk menyimpan bobot kata terhadap satu halaman ke database pada table "tfidf_word".

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            word (str): Kata
            page_id (int): ID dari table page_information
            tfidf_score (double): Bobot/skor tf idf
        """
        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

        query = "SELECT `id_word` FROM `tfidf_word` WHERE `word` = %s AND `page_id` = %s"
        db_cursor.execute(query, (word, page_id))
        results = db_cursor.fetchall()
        row_count = db_cursor.rowcount

        if row_count < 1:
            query = "INSERT INTO `tfidf_word` (`word`, `page_id`, `tfidf_score`) VALUES (%s, %s, %s)"
            db_cursor.execute(query, (word, page_id, tfidf_score))
        else:
            id_word = results[0]["id_word"]
            query = "UPDATE `tfidf_word` SET `tfidf_score` = %s WHERE `id_word` = %s"
            db_cursor.execute(query, (tfidf_score, id_word))

        db_cursor.close()

    def get_one_url(self, db_connection, page_id):
        """
        Fungsi untuk mengambil url dari database untuk satu halaman.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            page_id (int): Page ID
        """
        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT `url` FROM `page_information` WHERE `id_information` = %s", (page_id))
        row = db_cursor.fetchone()

        db_cursor.close()
        return row["url"]

    def save_call_log(self, db_connection, keyword, duration_call):
        """
        Fungsi untuk menyimpan waktu yang diperlukan saat pemanggilan fungsi TF-DF.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Kata pencarian (bisa lebih dari satu kata dipisah dengan spasi)
            duration_call (int): Waktu yang diperlukan saat pemanggilan fungsi TF IDF dari awal hingga selesai
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `tfidf_log` (`keyword`, `duration_call`) VALUES (%s, SEC_TO_TIME(%s))"
        db_cursor.execute(query, (keyword, duration_call))
        db_cursor.close()

    def get_all_saved_tfidf(self, db_connection, keyword):
        """
        Fungsi untuk mengambil total skor TF-IDF yang sudah dihitung di dalam database pada table "tfidf".

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            keyword (str): Kata pencarian (bisa lebih dari satu kata dipisah dengan spasi)

        Returns:
            list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `tfidf` WHERE `keyword` = %s ORDER BY `tfidf_total` DESC", (keyword))
        rows = db_cursor.fetchall()
        db_cursor.close()
        return rows

    def get_all_tfidf_for_api(self, keyword):
        """
        Fungsi untuk mendapatkan total skor TF-IDF dari suatu keyword (untuk keperluan API).

        Args:
            keyword (str): Kata pencarian (bisa lebih dari satu kata)

        Returns:
            list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """

        db_connection = self.db.connect()

        # Return data langsung jika total skor pada keyword ini sudah pernah dihitung
        saved_tfidf = self.get_all_saved_tfidf(db_connection, keyword)
        if len(saved_tfidf) > 1:
            return saved_tfidf

        # Buat dictionary dengan page id sebagai keynya dan valuenya adalah total score tf idf
        pages_with_total_score = {}

        keyword_arr = keyword.split(" ")
        for word in keyword_arr:
            db_connection.ping()
            db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

            # Kumpulkan semua page id dan nilai bobot kata
            query = "SELECT `page_id`, `tfidf_score` FROM `tfidf_word` WHERE `word` = %s"
            db_cursor.execute(query, (word))
            results = db_cursor.fetchall()

            for result in results:
                page_id = result["page_id"]
                tfidf_score = result["tfidf_score"]

                # Cek pada dictionary, jika sudah ada maka di jumlah
                if page_id in pages_with_total_score:
                    pages_with_total_score[page_id] = pages_with_total_score[page_id] + tfidf_score
                else:
                    pages_with_total_score[page_id] = tfidf_score

        # Simpan hasil perhitungan yang ada di dictionary ke table "tfidf"
        for key, value in pages_with_total_score.items():
            db_connection.ping()
            url = self.get_one_url(db_connection, key)
            self.save_one_tfidf(db_connection, keyword, url, value)

        saved_tfidf = self.get_all_saved_tfidf(db_connection, keyword)
        return saved_tfidf

    def run_background_service(self):
        """
        Fungsi utama yang digunakan untuk melakukan pembobotan kata pada dokumen menggunakan metode TF-IDF.
        """
        db_connection = self.db.connect()

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
            page_id = df["id_information"].loc[i]

            for j in range(len(words)):
                word = words[j]
                idf = idf_vector[j]
                tf_idf = tf_idf_vector[j]
                tf = tf_idf / idf

                print(word, page_id, tf_idf)
                # Simpan setiap bobot/score pada kata ke table "tfidf_word"
                self.save_one_tfidf_word(db_connection, word, page_id, tf_idf)

        # Hapus semua hasil keyword yang sudah pernah dihitung sebelumnya pada table tfidf (keperluan API), karena bobot pada tiap kata berubah
        self.remove_tfidf_rows(db_connection)

        print("TFIDF Background Service - Completed.")
