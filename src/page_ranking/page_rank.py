# Reference: https://github.com/nicholaskajoh/devsearch/blob/f6d51fc478e5bae68e4ba32f3299ab20c0ffa033/devsearch/pagerank.py#L2

from src.database.database import Database

import pymysql


class PageRank:
    """Kelas yang digunakan untuk melakukan perankingan halaman dengan metode Page Rank."""

    def __init__(self):
        self.db = Database()
        self.max_iterations = 20
        self.damping_factor = 0.85

    def save_initial_pagerank(self, db_connection, initial_pr):
        """
        Fungsi untuk menyimpan nilai initial pagerank ke database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            initial_pr (double): Initial page rank
        """
        pages = self.get_all_crawled_pages(db_connection)

        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

        for page_row in pages:
            url = page_row["url"]

            if not self.db.check_value_in_table(db_connection, "pagerank", "url", url):
                query = "INSERT INTO `pagerank` (`url`, `pagerank_score`) VALUES (%s, %s)"
                db_cursor.execute(query, (url, initial_pr))
            else:
                query = "UPDATE `pagerank` SET `pagerank_score` = %s WHERE `url` = %s"
                db_cursor.execute(query, (initial_pr, url))

        db_cursor.close()

    def save_one_pagerank(self, db_connection, url, pagerank):
        """
        Fungsi untuk menyimpan ranking dan nilai Page Rank yang sudah dihitung ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            url (str): Url halaman
            pagerank (double): Score page rank
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()

        query = "UPDATE `pagerank` SET `pagerank_score` = %s WHERE `url` = %s"
        db_cursor.execute(query, (pagerank, url))

        db_cursor.close()

    def get_all_crawled_pages(self, db_connection):
        """
        Fungsi untuk mengambil semua halaman yang sudah dicrawl dari database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL

        Returns:
            list: List berisi dictionary table page_information yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection.ping()

        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `page_information`")
        rows = db_cursor.fetchall()

        db_cursor.close()
        return rows

    def get_one_pagerank(self, db_connection, url):
        """
        Fungsi untuk mengambil skor pagerank dari database untuk satu halaman.

        Returns:
            double: Berisi nilai skor page rank
        """
        db_connection.ping()

        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT pagerank_score FROM `pagerank` WHERE `url` = %s", (url))
        row = db_cursor.fetchone()

        db_cursor.close()
        return row["pagerank_score"]

    def get_all_pagerank_for_api(self):
        """
        Fungsi untuk mengambil semua data pagerank dari database (untuk keperluan API).

        Returns:
            list: List berisi dictionary table pagerank yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection = self.db.connect()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `pagerank` ORDER BY `pagerank_score` DESC")
        rows = db_cursor.fetchall()
        db_cursor.close()
        self.db.close_connection(db_connection)
        return rows

    def run_background_service(self):
        """
        Fungsi utama yang digunakan untuk melakukan perangkingan halaman Page Rank.
        """
        db_connection = self.db.connect()
        N = self.db.count_rows(db_connection, "page_information")
        initial_pr = 1 / N
        self.save_initial_pagerank(db_connection, initial_pr)
        self.db.close_connection(db_connection)

        for iteration in range(self.max_iterations):
            pr_change_sum = 0

            db_connection = self.db.connect()
            pages = self.get_all_crawled_pages(db_connection)

            for page_row in pages:
                db_connection.ping()

                page_url = page_row["url"]
                current_pagerank = self.get_one_pagerank(db_connection, page_url)

                new_pagerank = 0
                backlink_urls = set()
                db_cursor2 = db_connection.cursor(pymysql.cursors.DictCursor)

                db_cursor2.execute("SELECT * FROM `page_linking` WHERE `outgoing_link` = %s", (page_url))
                for page_linking_row in db_cursor2.fetchall():
                    backlink_urls.add(page_linking_row["url"])

                db_cursor2.execute(
                    "SELECT url, COUNT(*) FROM `page_linking` WHERE `url` IN %s GROUP by url", [backlink_urls]
                )
                for backlink_link_count in db_cursor2.fetchall():
                    new_pagerank += initial_pr / backlink_link_count["COUNT(*)"]
                db_cursor2.close()

                new_pagerank = ((1 - self.damping_factor) / N) + (self.damping_factor * new_pagerank)

                print(page_url, new_pagerank)
                self.save_one_pagerank(db_connection, page_url, new_pagerank)

                pr_change = abs(new_pagerank - current_pagerank) / current_pagerank
                pr_change_sum += pr_change

            self.db.close_connection(db_connection)

            average_pr_change = pr_change_sum / N
            if average_pr_change < 0.0001:
                # Convergent
                break

        print("PageRank Background Service - Completed.")
