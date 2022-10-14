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
            page_id = page_row["id_page"]

            if not self.db.check_value_in_table(db_connection, "pagerank", "page_id", page_id):
                query = "INSERT INTO `pagerank` (`page_id`, `pagerank_score`) VALUES (%s, %s)"
                db_cursor.execute(query, (page_id, initial_pr))
            else:
                query = "UPDATE `pagerank` SET `pagerank_score` = %s WHERE `page_id` = %s"
                db_cursor.execute(query, (initial_pr, page_id))

        db_cursor.close()

    def save_one_pagerank(self, db_connection, page_id, pagerank):
        """
        Fungsi untuk menyimpan ranking dan nilai Page Rank yang sudah dihitung ke dalam database.

        Args:
            db_connection (pymysql.Connection): Koneksi database MySQL
            page_id (int): ID page dari table page_information
            pagerank (double): Score page rank
        """
        db_connection.ping()
        db_cursor = db_connection.cursor()

        query = "UPDATE `pagerank` SET `pagerank_score` = %s WHERE `page_id` = %s"
        db_cursor.execute(query, (pagerank, page_id))

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

    def get_one_pagerank(self, db_connection, page_id):
        """
        Fungsi untuk mengambil skor pagerank dari database untuk satu halaman.

        Returns:
            double: Berisi nilai skor page rank
        """
        db_connection.ping()

        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT pagerank_score FROM `pagerank` WHERE `page_id` = %s", (page_id))
        row = db_cursor.fetchone()

        db_cursor.close()
        return row["pagerank_score"]

    def get_all_pagerank_by_page_ids(self, page_ids: list):
        """
        Fungsi untuk mengambil semua data pagerank dari database pada ID page tertentu.

        Returns:
            list: List berisi dictionary table pagerank yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection = self.db.connect()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        page_ids_string = ",".join(map(str, page_ids))
        query = "SELECT * FROM `pagerank` WHERE `page_id` IN ({}) ORDER BY `pagerank_score` DESC".format(
            page_ids_string
        )
        db_cursor.execute(query)
        rows = db_cursor.fetchall()
        db_cursor.close()
        self.db.close_connection(db_connection)
        return rows

    def get_all_pagerank_for_api(self, start=None, length=None):
        """
        Fungsi untuk mengambil semua data pagerank dari database (untuk keperluan API).

        Args:
            start (int): Indeks awal (optional, untuk pagination)
            length (int): Total data (optional, untuk pagination)

        Returns:
            list: List berisi dictionary table pagerank yang didapatkan dari fungsi cursor.fetchall(), berisi empty list jika tidak ada datanya
        """
        db_connection = self.db.connect()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        if start is None or length is None:
            db_cursor.execute(
                "SELECT `pagerank`.`id_pagerank`,`pagerank`.`pagerank_score`,`pagerank`.`page_id`,`page_information`.`url` FROM `pagerank` INNER JOIN `page_information` ON `pagerank`.`page_id` = `page_information`.`id_page` ORDER BY `pagerank`.`pagerank_score` DESC"
            )
        else:
            db_cursor.execute(
                "SELECT `pagerank`.`id_pagerank`,`pagerank`.`pagerank_score`,`pagerank`.`page_id`,`page_information`.`url` FROM `pagerank` INNER JOIN `page_information` ON `pagerank`.`page_id` = `page_information`.`id_page` ORDER BY `pagerank`.`pagerank_score` DESC LIMIT %s, %s",
                (start, length),
            )
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

                page_id = page_row["id_page"]
                page_url = page_row["url"]
                current_pagerank = self.get_one_pagerank(db_connection, page_id)

                new_pagerank = 0
                backlink_urls = set()
                db_cursor2 = db_connection.cursor(pymysql.cursors.DictCursor)

                db_cursor2.execute(
                    "SELECT `page_information`.`url` FROM `page_linking` INNER JOIN `page_information` ON `page_linking`.`page_id` = `page_information`.`id_page` WHERE `outgoing_link` = %s",
                    (page_url),
                )
                for page_linking_row in db_cursor2.fetchall():
                    backlink_urls.add(page_linking_row["url"])

                db_cursor2.execute(
                    "SELECT `page_information`.`url`, COUNT(*) FROM `page_linking` INNER JOIN `page_information` ON `page_linking`.`page_id` = `page_information`.`id_page` WHERE `page_information`.`url` IN %s GROUP by `page_information`.`url`",
                    [backlink_urls],
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
