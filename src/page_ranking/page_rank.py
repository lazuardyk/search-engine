# Reference: https://github.com/nicholaskajoh/devsearch/blob/f6d51fc478e5bae68e4ba32f3299ab20c0ffa033/devsearch/pagerank.py#L2

from src.database.database import Database

import pymysql


class PageRank:
    """Kelas yang digunakan untuk melakukan perankingan halaman dengan metode Page Rank."""

    def __init__(self):
        self.db = Database()
        self.max_iterations = 20

    def save_pagerank(self, db_connection, url, pagerank):
        """Fungsi untuk menyimpan ranking dan nilai Page Rank yang sudah dihitung ke dalam database."""
        db_connection.ping()
        db_cursor = db_connection.cursor()

        query = "UPDATE `page_rank` SET `pagerank_score` = %s WHERE `url` = %s"
        db_cursor.execute(query, (pagerank, url))

        db_cursor.close()

    def get_crawled_pages(self, db_connection):
        db_connection.ping()

        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT * FROM `page_information`")
        rows = db_cursor.fetchall()

        db_cursor.close()
        return rows

    def save_initial_pagerank(self, db_connection, initial_pr):
        pages = self.get_crawled_pages(db_connection)

        db_connection.ping()
        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)

        for page_row in pages:
            url = page_row["url"]

            if not self.db.check_value_in_table(db_connection, "page_rank", "url", url):
                query = "INSERT INTO `page_rank` (`url`, `pagerank_score`) VALUES (%s, %s)"
                db_cursor.execute(query, (url, initial_pr))
            else:
                query = "UPDATE `page_rank` SET `pagerank_score` = %s WHERE `url` = %s"
                db_cursor.execute(query, (initial_pr, url))

        db_cursor.close()

    def get_pagerank(self, db_connection, url):
        db_connection.ping()

        db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
        db_cursor.execute("SELECT pagerank_score FROM `page_rank` WHERE `url` = %s", (url))
        row = db_cursor.fetchone()

        db_cursor.close()
        return row["pagerank_score"]

    def run(self):
        """Fungsi utama yang digunakan untuk melakukan perangkingan halaman Page Rank."""

        db_connection = self.db.connect()
        N = self.db.count_rows(db_connection, "page_information")
        initial_pr = 1 / N
        self.save_initial_pagerank(db_connection, initial_pr)
        self.db.close_connection(db_connection)

        for iteration in range(self.max_iterations):
            pr_change_sum = 0

            db_connection = self.db.connect()
            pages = self.get_crawled_pages(db_connection)

            for page_row in pages:
                db_connection.ping()

                page_url = page_row["url"]
                current_pagerank = self.get_pagerank(db_connection, page_url)

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

                damping_factor = 0.85
                new_pagerank = ((1 - damping_factor) / N) + (damping_factor * new_pagerank)

                print(page_url, new_pagerank)
                self.save_pagerank(db_connection, page_url, new_pagerank)

                pr_change = abs(new_pagerank - current_pagerank) / current_pagerank
                pr_change_sum += pr_change

            self.db.close_connection(db_connection)

            average_pr_change = pr_change_sum / N
            if average_pr_change < 0.0001:
                # click.echo(click.style('Converged at iteration: %d' % iteration, fg='blue'))
                break
