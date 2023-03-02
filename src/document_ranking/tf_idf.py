# Referensi: https://www.kaggle.com/code/yclaudel/find-similar-articles-with-tf-idf

from src.database.database import Database

import pymysql
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time

import Sastrawi
import nltk
import string
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.tokenize import word_tokenize

def remove_tfidf_rows(db_connection):
    """Fungsi untuk mengosongkan table "tfidf" pada database.

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL
    """
    db_connection.ping()
    db_cursor = db_connection.cursor()

    query = "TRUNCATE TABLE `tfidf`"
    db_cursor.execute(query)

    db_cursor.close()


def save_one_tfidf(db_connection, keyword, page_id, tfidf_total):
    """
    Fungsi untuk menyimpan nilai total TF IDF terhadap suatu keyword (bisa lebih dari satu kata) ke database pada table "tfidf".

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL
        keyword (str): Kata pencarian (bisa lebih dari satu kata)
        page_id (int): ID page dari table page_information
        tfidf_total (double): Score tf idf
    """
    db_connection.ping()
    db_cursor = db_connection.cursor()

    query = "INSERT INTO `tfidf` (`keyword`, `page_id`, `tfidf_total`) VALUES (%s, %s, %s)"
    db_cursor.execute(query, (keyword, page_id, tfidf_total))

    db_cursor.close()


def save_one_tfidf_word(db_connection, word, page_id, tfidf_score):
    """
    Fungsi untuk menyimpan bobot kata terhadap satu halaman ke database pada table "tfidf_word".

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL
        word (str): Kata
        page_id (int): ID page dari table page_information
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


def get_all_saved_tfidf(db_connection, keyword, start=None, length=None):
    """
    Fungsi untuk mengambil total skor TF-IDF yang sudah dihitung di dalam database pada table "tfidf".

    Args:
        db_connection (pymysql.Connection): Koneksi database MySQL
        keyword (str): Kata pencarian (bisa lebih dari satu kata dipisah dengan spasi)
        start (int): Indeks awal (optional, untuk pagination)
        length (int): Total data (optional, untuk pagination)

    Returns:
        list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
    """
    db_connection.ping()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    if start is None or length is None:
        db_cursor.execute(
            "SELECT `tfidf`.`id_tfidf`,`tfidf`.`keyword`,`tfidf`.`tfidf_total`,`tfidf`.`page_id`,`page_information`.`url` FROM `tfidf` INNER JOIN `page_information` ON `tfidf`.`page_id` = `page_information`.`id_page` WHERE `tfidf`.`keyword` = %s ORDER BY `tfidf`.`tfidf_total` DESC",
            (keyword),
        )
    else:
        db_cursor.execute(
            "SELECT `tfidf`.`id_tfidf`,`tfidf`.`keyword`,`tfidf`.`tfidf_total`,`tfidf`.`page_id`,`page_information`.`url` FROM `tfidf` INNER JOIN `page_information` ON `tfidf`.`page_id` = `page_information`.`id_page` WHERE `tfidf`.`keyword` = %s ORDER BY `tfidf`.`tfidf_total` DESC LIMIT %s, %s",
            (keyword, start, length),
        )
    rows = db_cursor.fetchall()
    db_cursor.close()
    return rows


def get_all_tfidf_for_api(keyword, start=None, length=None):
    """
    Fungsi untuk mendapatkan total skor TF-IDF dari suatu keyword (untuk keperluan API).

    Args:
        keyword (str): Kata pencarian (bisa lebih dari satu kata)
        start (int): Indeks awal (optional, untuk pagination)
        length (int): Total data (optional, untuk pagination)

    Returns:
        list: List berisi dictionary skor TF IDF yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
    """

    db_connection = Database().connect()

    # Return data langsung jika total skor pada keyword ini sudah pernah dihitung
    saved_tfidf = get_all_saved_tfidf(db_connection, keyword, start, length)
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
    for page_id, total_score in pages_with_total_score.items():
        db_connection.ping()
        save_one_tfidf(db_connection, keyword, page_id, total_score)

    saved_tfidf = get_all_saved_tfidf(db_connection, keyword, start, length)
    return saved_tfidf

def calcDocWithWord(word, docs):
    docWithWord = 0
    for doc in docs:
        if word in doc:
            docWithWord += 1
    return docWithWord


def run_background_service():
    """
    Fungsi utama yang digunakan untuk melakukan pembobotan kata pada dokumen menggunakan metode TF-IDF.
    """
    stopword_factory = StopWordRemoverFactory()
    stopword = stopword_factory.create_stop_word_remover()
    stemmer_factory = StemmerFactory()
    stemmer = stemmer_factory.create_stemmer()

    db_connection = Database().connect()
    db_connection.ping()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

    # Ambil semua data halaman yang sudah di crawl ke dalam pandas dataframe
    query = "SELECT * FROM `page_information`"
    db_cursor.execute(query)
    df = db_cursor.fetchall()
    text_content = df["content_text"]  # Konten teks dari halaman yang sudah dicrawl
    page_id = df["id_page"]

    for x in text_content:
    # konversi tuple ke dalam string
        x = ''.join([str(value) for value in x])
    # menghilangkan tanda baca dan menjadikan dokumen lowercase
        x = x.translate(str.maketrans('','',string.punctuation)).lower()
    # menghilangkan angka pada dokumen
        x = x.translate(str.maketrans('','',string.digits))
    # menghilangkan stopword pada dokumen
        x = stopword.remove(x)
    # menghilangkan imbuhan pada kata di dalam dokumen
        x = stemmer.stem(x) 

docWithWord = 0
for i in range(len(text_content)):  
    sentences = text_content[i]
    index_page_id = page_id[i]
    for j in range(len(sentences)):
        tf_value = sentences.count(sentences[j])
        
        doc_with_word = calcDocWithWord(sentences[j], text_content)
        
        if doc_with_word != 0:
            idf_value = math.log(float(len(text_content)/doc_with_word))
        else:
            idfValue = float(0)
        tf_idf_value = tf_value*idf_value

            print(f"word: {sentences[j]}, page_id: {index_page_id}, tfidf score: {tf_idf_value}")
            # Simpan setiap bobot/score pada kata ke table "tfidf_word"
            save_one_tfidf_word(db_connection, sentences[j], index_page_id, tf_idf_value)
            data_tfidf.append(
                {
                    "kata": sentences[j],
                    "page_id": index_page_id,
                    "tf": tf_value,
                    "idf": idf_value,
                    "tfidf": tf_idf_value,
                }
            )

    new_df = pd.DataFrame(data_tfidf)
    # new_df.to_excel("output.xlsx")

    # Hapus semua hasil keyword yang sudah pernah dihitung sebelumnya pada table tfidf (keperluan API), karena bobot pada tiap kata berubah
    remove_tfidf_rows(db_connection)

    print("TFIDF Background Service - Completed.")


def get_cosine_similarity(keyword):

    # Ambil semua data halaman yang sudah di crawl ke dalam pandas dataframe
    db_connection = Database().connect()
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
    words = vectorizer.get_feature_names()
    idf_vector = vectorizer.idf_

    query_tfidf_matrix = vectorizer.transform([keyword])

    # print(query_tfidf_matrix)
    cosine_similarities = cosine_similarity(query_tfidf_matrix, tfidf_matrix).flatten()
    page_with_cosine = {}
    for i in range(len(cosine_similarities)):
        page_id = df["id_page"].loc[i]
        page_with_cosine[page_id] = cosine_similarities[i]

    # print(page_with_cosine)

    return page_with_cosine