from src.database.database import Database
from src.document_ranking.tf_idf import get_all_tfidf_for_api
import pymysql


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

    tf_idf_percentage = 0.6
    page_rank_percentage = 0.4

    if sort == "tfidf":
        order_by = "`tfidf`.`tfidf_total`"
    elif sort == "pagerank":
        order_by = "`pagerank`.`pagerank_score`"
    else:
        order_by = "`similarity_score`"

    get_all_tfidf_for_api(keyword, start, length)

    query = f'SELECT `tfidf`.`page_id` AS `id_page`, `page_information`.`url`, ({tf_idf_percentage} * `tfidf`.`tfidf_total`) + ({page_rank_percentage} * `pagerank`.`pagerank_score`) AS `similarity_score`, `tfidf`.`tfidf_total`, `pagerank`.`pagerank_score` FROM `tfidf` LEFT JOIN `pagerank` ON `tfidf`.`page_id` = `pagerank`.`page_id` LEFT JOIN `page_information` ON `tfidf`.`page_id` = `page_information`.`id_page` WHERE `tfidf`.`keyword` = "{keyword}" ORDER BY {order_by} DESC'

    if start is not None and length is not None:
        query += f" LIMIT {start}, {length}"

    db_connection = Database().connect()
    db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
    db_cursor.execute(query)
    rows = db_cursor.fetchall()
    db_cursor.close()

    return rows
