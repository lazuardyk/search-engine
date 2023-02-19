from src.database.database import Database
from src.document_ranking.tf_idf import get_all_tfidf_for_api, get_cosine_similarity
import pymysql
import os


def get_all_similarity_for_api(keyword, sort, start=None, length=None):
    """
    Fungsi untuk mendapatkan perankingan keseluruhan berdasarkan keyword tertentu.

    Args:
        keyword (str): Kata pencarian (bisa lebih dari satu kata)
        sort (str): Sort by similarity/pagerank/tfidf
        start (int): Indeks awal (optional, untuk pagination)
        length (int): Total data (optional, untuk pagination)

    Returns:
        list: List berisi dictionary yang terdapat url dan total skor keseluruhan, empty list jika tidak ada datanya
    """

    get_all_tfidf_for_api(keyword, start, length)
    use_cosine = os.getenv("USE_COSINE_SIMILARITY")

    if use_cosine == "true":
        page_with_cosine = get_cosine_similarity(keyword)
        query = f'SELECT `tfidf`.`page_id` AS `id_page`, `page_information`.`url`, `pagerank`.`pagerank_score` FROM `tfidf` LEFT JOIN `pagerank` ON `tfidf`.`page_id` = `pagerank`.`page_id` LEFT JOIN `page_information` ON `tfidf`.`page_id` = `page_information`.`id_page` WHERE `tfidf`.`keyword` = "{keyword}"'

        if start is not None and length is not None:
            query += f" LIMIT {start}, {length}"

        db_connection = Database().connect()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        db_cursor.close()

        for row in rows:
            row["tfidf_total"] = page_with_cosine[row["id_page"]]
            row["similarity_score"] = page_with_cosine[row["id_page"]] + row["pagerank_score"]

    else:
        tf_idf_percentage = 0.6
        page_rank_percentage = 0.4

        query = f'SELECT `tfidf`.`page_id` AS `id_page`, `page_information`.`url`, ({tf_idf_percentage} * `tfidf`.`tfidf_total`) + ({page_rank_percentage} * `pagerank`.`pagerank_score`) AS `similarity_score`, `tfidf`.`tfidf_total`, `pagerank`.`pagerank_score` FROM `tfidf` LEFT JOIN `pagerank` ON `tfidf`.`page_id` = `pagerank`.`page_id` LEFT JOIN `page_information` ON `tfidf`.`page_id` = `page_information`.`id_page` WHERE `tfidf`.`keyword` = "{keyword}"'

        if start is not None and length is not None:
            query += f" LIMIT {start}, {length}"

        db_connection = Database().connect()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        db_cursor.close()

    if sort == "tfidf":
        rows = sorted(rows, key=lambda x: x["tfidf_total"], reverse=True)
    elif sort == "pagerank":
        rows = sorted(rows, key=lambda x: x["pagerank_score"], reverse=True)
    else:
        rows = sorted(rows, key=lambda x: x["similarity_score"], reverse=True)

    return rows
