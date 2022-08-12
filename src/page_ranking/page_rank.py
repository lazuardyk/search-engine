# Reference: https://www.kaggle.com/code/yclaudel/find-similar-articles-with-tf-idf
# Reference: https://github.com/nicholaskajoh/devsearch/blob/f6d51fc478e5bae68e4ba32f3299ab20c0ffa033/devsearch/pagerank.py#L2

from src.database.database import Database

import pymysql


class PageRank:
    """Kelas yang digunakan untuk melakukan perankingan halaman dengan metode Page Rank."""

    def __init__(self):
        self.db = Database()
        self.max_iterations = 1

    def run(self):
        """Fungsi utama yang digunakan untuk melakukan perangkingan halaman Page Rank."""
        db_connection = self.db.connect()
        N = self.db.count_rows(db_connection, "page_information")
        initial_pr = 1 / N
        self.db.close_connection(db_connection)

        for iteration in range(self.max_iterations):
            pr_change_sum = 0
            db_connection = self.db.connect()
            db_cursor = db_connection.cursor(pymysql.cursors.DictCursor)
            db_cursor.execute("SELECT * FROM `page_information`")
            for page_row in db_cursor.fetchall():
                db_cursor2 = db_connection.cursor(pymysql.cursors.DictCursor)
                new_pagerank = 0
                page_url = page_row["url"]
                backlink_urls = set()

                db_cursor2.execute("SELECT * FROM `page_linking` WHERE `outgoing_link` = %s", (page_url))
                for page_linking_row in db_cursor2.fetchall():
                    backlink_urls.add(page_linking_row["url"])

                db_cursor2.execute(
                    "SELECT url, COUNT(*) FROM `page_linking` WHERE `url` IN %s GROUP by url", [backlink_urls]
                )
                # print(db_cursor2.fetchall())
                for backlink_link_count in db_cursor2.fetchall():
                    new_pagerank += initial_pr / backlink_link_count["COUNT(*)"]
                    # print(new_pagerank)
                # for backlink_url in backlink_urls:
                #     db_cursor2.execute("SELECT COUNT(*) FROM `page_linking` WHERE `url` = %s", (backlink_url))
                #     outlink_count = db_cursor2.fetchone()["COUNT(*)"]
                #     new_pagerank += (initial_pr / outlink_count)
                #     print(new_pagerank)

                damping_factor = 0.85
                new_pagerank = ((1 - damping_factor) / N) + (damping_factor * new_pagerank)

                print(page_url, new_pagerank)
                db_cursor2.close()
            db_cursor.close()
            self.db.close_connection(db_connection)

            average_pr_change = pr_change_sum / N
            if average_pr_change < 0.0001:
                # click.echo(click.style('Converged at iteration: %d' % iteration, fg='blue'))
                break
