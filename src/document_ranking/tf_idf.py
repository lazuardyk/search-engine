# Reference: https://www.kaggle.com/code/yclaudel/find-similar-articles-with-tf-idf
from src.database.database import Database

import pymysql
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class TfIdf:
    """Kelas yang digunakan untuk melakukan perankingan dokumen dengan metode TF IDF."""

    def __init__(self):
        self.db = Database()

    def search(self, tfidf_matrix, model, request):
        """Fungsi untuk mengambil hasil dengan bobot tertinggi."""
        request_transform = model.transform([request])
        similarity = np.dot(request_transform, np.transpose(tfidf_matrix))
        x = np.array(similarity.toarray()[0])
        indices = np.argsort(x)[::][::-1]
        score = x[indices]

        return [indices, score]

    def print_result(self, request_content, indices, X):
        """Fungsi untuk mencetak (print) hasil."""
        print("\nKeyword: " + request_content)
        print("\nBest Results:")
        for i in indices:
            print("id = {0:5d} - title = {1} - url = {2}".format(i, X["title"].loc[i], X["url"].loc[i]))

    def save_tfidf(self, db_connection, keyword, url, tfidf):
        """Fungsi untuk menyimpan ranking dan nilai TF IDF yang sudah dihitung ke dalam database."""
        db_connection.ping()
        db_cursor = db_connection.cursor()
        query = "INSERT INTO `tf_idf` (`keyword`, `url`, `tfidf_score`) VALUES (%s, %s, %s)"
        db_cursor.execute(query, (keyword, url, tfidf))
        db_cursor.close()

    def get_saved_tfidf(self, db_connection, keyword):
        """Fungsi untuk mengambil data TF IDF dari database jika suatu keyword sudah pernah dihitung."""
        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `tf_idf` WHERE `keyword` = %s", (keyword))
        rows = db_cursor.fetchall()
        db_cursor.close()
        return rows

    def run(self, keyword):
        """Fungsi utama yang digunakan untuk melakukan perangkingan dokumen TF-IDF."""
        db_connection = self.db.connect()

        saved_data = self.get_saved_tfidf(db_connection, keyword)
        if len(saved_data) < 1:
            query = "SELECT * FROM `page_information`"
            df = pd.read_sql(query, db_connection)

            text_content = df["content_text"]
            vector = TfidfVectorizer(
                lowercase=True,  # Convert everything to lower case
                use_idf=True,  # Use idf
                norm="l2",  # Normalization
                smooth_idf=True,  # Prevents divide-by-zero errors
            )
            tfidf = vector.fit_transform(text_content)

            result_indices, result_score = self.search(tfidf, vector, keyword)

            urls = []
            for ind in result_indices:
                urls.append(df["url"].loc[ind])

            for i in range(len(urls)):
                url = urls[i]
                score = result_score[i]
                self.save_tfidf(db_connection, keyword, url, score)

            saved_data = self.get_saved_tfidf(db_connection, keyword)
            # self.print_result(keyword, result_indices, df)

        print(saved_data)
        self.db.close_connection(db_connection)
